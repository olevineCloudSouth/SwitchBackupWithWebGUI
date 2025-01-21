from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import pandas as pd
import re
import ipaddress
from .helpers.find_recent import find_recent

def get_info():
    #df = pd.read_csv("/opt/backup-script/switch_ips.csv") #prod server csv location
    df = pd.read_csv(".\\switch_ips.csv") #for testing purposes
    return df

def subnet_str_to_array(subnet_str):
    # Regular expression to check the format of the input string
    regex = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\s255\.255\.255\.(?:0|128|192|224|240|248|252|254|255)\b'
    # Check if the string matches the expected format which is "ip.v4.gateway.address 255.255.255.xxx"
    match = re.match(regex, subnet_str)
    if not match:
        raise ValueError("Input does not match the required format: 'IP MASK'")
    #split subnet mask and gateway ip from string
    gateway_ip,subnet = subnet_str.split(' ')
    #use ipaddress lib to make network object
    network = ipaddress.IPv4Network(f"{gateway_ip}/{subnet}", strict=False)
    #use .hosts to get all ips in network
    ips = [str(ip) for ip in network]
    #return the array of ips and the /xx notation for the subnet
    return ips, network.prefixlen

def check_ip(ip,date):
    #regex for gateway subnet strings
    regex = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\s255\.255\.255\.(?:0|128|192|224|240|248|252|254|255)\b'
    #grab dataframe of csv with switch name and ips
    switch_info = get_info() 
    #split the input ip into each octet as a seperate entry into an array
    ip_octets = [ip.split('.')[0], ip.split('.')[1], ip.split('.')[2], ip.split('.')[3]]
    #create a string of the first three octets
    first_3_octets = ".".join([ip_octets[0], ip_octets[1], ip_octets[2]])
    switches_with_ip = []
    #iterate through every switch
    for index, row in switch_info.iterrows():
        switch_name = row['name']
        #grab its config file
        config_location = find_recent('/mnt/sda/switch-backups/', switch_name, 'config')
        try:
            with open(config_location, 'r') as config:
                config_text = config.read()
                #if the first three octet string is in the text then we'll searhc it, if not, we'll skip
                #this is for effeciency so we doing the more computationally expensive task of checking every ip in every subnet for configs that just don't have the /24
                #this approach wouldn't work for networks where larger than /24 subnets are routed places
                if first_3_octets in config_text:
                    #find all the gateway subnet mask strings in the config
                    subnets = re.findall(regex, config_text)
                    #go through each subnet
                    for subnet in subnets:
                        #join array to string
                        subnet = "".join(subnet) 
                        #get array of all ips in subnet and its /xx notation
                        ips, notation = subnet_str_to_array(subnet)
                        if ip in ips:
                            #if ip in the array of ips that we got then we found a switch that the ip is in so we grab the vlan and add it to our result list
                            vlan_regex = rf"interface Vlan(\d{{3}})[^!]*{re.escape(subnet)}"
                            vlan_match = re.findall(vlan_regex, config_text)
                            if vlan_match:
                                temp_octets = ips[0].split('.')[0], ips[0].split('.')[1], ips[0].split('.')[2], ips[0].split('.')[3]
                                subnet_ip = ".".join([temp_octets[0], temp_octets[1], temp_octets[2], str(int(temp_octets[3]))])
                                switches_with_ip.append({"switch_name": switch_name, "subnet": f"{subnet_ip}/{notation}","vlan": vlan_match[0]})
        except FileNotFoundError:
            print(f"File not found: {config_location}. Skipping...")
        except Exception as e:
            print(f"An error occurred while processing {config_location}: {e}. Skipping...")

    return switches_with_ip

#flow of check_ip function
    #get date to check
    #grab all configs from that date
    #for config in configs
    #if config contains first three octets of our ip
    #send to 'grab subnet_str from config function'
    #send subnetstr to subnet_str_to_array
    #if ip in subnet_str_to_array result, add switch_name to switch_with_ip_in_config result array
    #exit loop
    #return result array

track_ip = Blueprint('track_ip', __name__)
@track_ip.route('/track_ip', methods=['GET'])
@cross_origin()
def track_ip_main():
    date = request.args.get('date')
    ip = request.args.get('ip')
    #input validation
    regex_ip = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
    if not re.match(regex_ip, ip):
        return jsonify("That IP is not the correct format. ERROR!"), 400
    regex_date = r'\b\d{2}-\d{2}-\d{4}\b'
    if not re.match(regex_date, date):
        return jsonify("That date is not the correct format. ERROR!"), 400
    #return json list of results
    return jsonify(check_ip(ip, date)), 200

