from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import paramiko
import time
import pandas as pd
import configparser

passwords = []
def get_config(file_path):
    try:
        with open(file_path, 'r') as file:
            text = file.read()
        return text
    except FileNotFoundError:
        print("File not found.")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def switch_touch(ip, password):
    try:

         # Create an SSH client instance
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=ip, username='netadmin', password=password, timeout=5)
        ssh_shell = ssh_client.invoke_shell()
        ssh_shell.send("terminal length 0\n")  # Set terminal length to 0 to get the entire output
        #wait until the shell is ready
        while not ssh_shell.recv_ready():
            pass
        #write mem to save the config
        ssh_shell.send("write mem\n")
        #print out config
        ssh_shell.send("show run\n")
        #wait for it to finish
        time.sleep(3)
        #load config into string to pass
        switch_output = ssh_shell.recv(65535).decode('utf-8')
        i = 0
        while not switch_output.endswith('#') or len(switch_output) < 1000:
            time.sleep(1)
            switch_output += ssh_shell.recv(65535).decode('utf-8')
            i += 1
            if i > 35:
                return "Error: Connection timed out or switch took too long to respond", 14

        switch_output = switch_output.strip()
        return switch_output, 10
    except Exception as e:
        #traceback.print_exc()
        print("Error: " + str(e) + "\n")
        error = "Error: " + str(e) + "\n"
        error = error.strip()
        return error, 12
    finally:
         # Close SSH connection properly
            ssh_client.close()

def get_info():
    df = pd.read_csv("/opt/backup-script/switch_ips.csv")
    return df

def get_curr_config (switch_name, switch_info):
    switch_ip = switch_info.loc[switch_info['name'] == switch_name, 'switch_ips']
    for pwd in passwords:
        config, status_code = switch_touch(switch_ip, pwd)
        if status_code == 10:
            break
    return config


web_get_config = Blueprint('web_get_config', __name__)
@web_get_config.route('/get_config', methods=['GET'])
@cross_origin()
def config_check_main():
    config = configparser.ConfigParser()
    config.read('/opt/backup-script/pwds.ini')

    for key in config['pwds']:
        passwords.append(config['pwds'][key])
    date = request.args.get('date')
    check_switch = request.args.get('switch_name')
    if check_switch == None or date == None:
        return jsonify("Error missing params"), 400
    if check_switch == 'current':
        switch_info = get_info()
        return jsonify(get_curr_config(check_switch, switch_info)), 200
            
    config_path = "/mnt/sda/switch-configs/{}/{}_config-{}.txt".format(date, check_switch, date)
    return jsonify(get_config(config_path)), 200
