from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import pandas as pd
import re


def get_info():
    df = pd.read_csv("./switch_ips.csv")
    #df = pd.read_csv("/opt/backup-script/switch_ips.csv")
    return df


def subnet_str_to_array(subnet_str):
    # Regular expression to check the format of the input string
    regex = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\s0\.0\.0\.(?:7|15|31|63|127|255)\b'
    
    # Check if the string matches the expected format
    match = re.match(regex, subnet_str)
    if not match:
        raise ValueError("Input does not match the required format: 'IP MASK'")
    subnet_count = int(subnet_str.split('.')[-1])
    ip_octets = [subnet_str.split('.')[0], subnet_str.split('.')[1], subnet_str.split('.')[2], (subnet_str.split('.')[3]).split(' ')[0]]

    #print(subnet_count)
    #print(ip_octets)
    ips = []
    for i in range(1,subnet_count):
        ip = ".".join([ip_octets[0], ip_octets[1], ip_octets[2], str(int(ip_octets[3]) + i)])
        #print(ip)
        ips.append(ip)
    #print(ips)
    return ips
#/mnt/sda/switch-configs/{}/{}_config-{}.txt".format(date, switch_name, date)


def check_ip(ip,date):
    regex = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\s0\.0\.0\.(?:7|15|31|63|127|255)\b'
    switch_info = get_info()
    ip_octets = [ip.split('.')[0], ip.split('.')[1], ip.split('.')[2], ip.split('.')[3]]
    first_3_octets = ".".join([ip_octets[0], ip_octets[1], ip_octets[2]])
    switches_with_ip = []


    for index, row in switch_info.iterrows():
        switch_name = row['name']
        config_location = "./backups/{}/{}_config-{}.txt".format(date, switch_name, date)
        #config_location = "/mnt/sda/switch-configs/{}/{}_config-{}.txt".format(date, switch_name, date)
        try:
            with open(config_location, 'r') as config:
                config_text = config.read()
                if first_3_octets in config_text:
                    subnets = re.findall(regex, config_text)
                    #print(subnets)
                    for subnet in subnets:
                        subnet = "".join(subnet)
                        #print(subnet)
                        if ip in subnet_str_to_array(subnet):
                            switches_with_ip.append(switch_name)
                            break
        except FileNotFoundError:
            print(f"File not found: {config_location}. Skipping...")
        except Exception as e:
            print(f"An error occurred while processing {config_location}: {e}. Skipping...")

    print(switches_with_ip)
    

#flow of main function
    #get date to check
    #grab all configs from that date
    #for config in configs
    #if config contains first three octets of our ip
    #send to 'grab subnet_str from config function'
    #send subnetstr to subnet_str_to_array
    #if ip in subnet_str_to_array result, add switch_name to switch_with_ip_in_config result array
    #exit loop
    #return result array

ip = "154.27.80.56"
date = "03-15-2024"
check_ip(ip, date)







#switch_list = Blueprint('track_ip', __name__)
#@switch_list.route('/track_ip', methods=['GET'])
#@cross_origin()
#def track_ip_main():
#    return
