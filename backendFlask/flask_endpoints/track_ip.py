from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import pandas as pd
import re
import ipaddress


def get_info():
   #df = pd.read_csv("/opt/backup-script/switch_ips.csv") #prod server csv location
    df = pd.read_csv("./switch_ips.csv") #for testing purposes
    return df

def subnet_str_to_array(subnet_str):
    # Regular expression to check the format of the input string
    regex = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\s255\.255\.255\.(?:0|128|192|224|240|248|252|254|255)\b'
    # Check if the string matches the expected format
    match = re.match(regex, subnet_str)
    if not match:
        raise ValueError("Input does not match the required format: 'IP MASK'")
    gateway_ip,subnet = subnet_str.split(' ')
    network = ipaddress.IPv4Network(f"{gateway_ip}/{subnet}", strict=False)
    ips = [str(ip) for ip in network.hosts()]
    return ips, network.prefixlen

def check_ip(ip,date):
    regex = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\s255\.255\.255\.(?:0|128|192|224|240|248|252|254|255)\b'
    switch_info = get_info()
    ip_octets = [ip.split('.')[0], ip.split('.')[1], ip.split('.')[2], ip.split('.')[3]]
    first_3_octets = ".".join([ip_octets[0], ip_octets[1], ip_octets[2]])
    switches_with_ip = []

    for index, row in switch_info.iterrows():
        switch_name = row['name']
        #config_location = "/mnt/sda/switch-configs/{}/{}_config-{}.txt".format(date, switch_name, date) #prod server config location
        config_location = "./backups/{}/{}_config-{}.txt".format(date, switch_name, date) #for testing purposes
        try:
            with open(config_location, 'r') as config:
                config_text = config.read()
                if first_3_octets in config_text:
                    #print("found possible subnet in ", switch_name)
                    subnets = re.findall(regex, config_text)
                    #print(subnets)
                    for subnet in subnets:
                        subnet = "".join(subnet)
                        #print(subnet)
                        ips, notation = subnet_str_to_array(subnet)
                        if ip in ips:
                            temp_octets = ips[0].split('.')[0], ips[0].split('.')[1], ips[0].split('.')[2], ips[0].split('.')[3]
                            subnet_ip = ".".join([temp_octets[0], temp_octets[1], temp_octets[2], str(int(temp_octets[3]) - 1)])
                            switches_with_ip.append({"switch_name": switch_name, "subnet": f"{subnet_ip}/{notation}"})
                            break
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
    regex = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
    if not re.match(regex, ip):
        return jsonify("That IP is not the correct format. ERROR!"), 400
    return jsonify(check_ip(ip, date)), 200
