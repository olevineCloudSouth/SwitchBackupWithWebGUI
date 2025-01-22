from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import paramiko
import time
import pandas as pd
import configparser
from .helpers.find_recent import find_recent

passwords = []

def get_mac(file_path):
    try:
        with open(file_path, 'r') as file:
            text = file.read()
        return text
    except FileNotFoundError:
        print("File not found.")
        return "Mac Address Table Not Found."
    except Exception as e:
        print(f"Error reading file: {e}")
        return "Unexpected Error"


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
        ssh_shell.send("sh mac address-table\n")
        #wait for it to finish
        time.sleep(5)
        #load config into string to pass
        switch_output = ssh_shell.recv(65535).decode('utf-8')
        i = 0
        while not switch_output.endswith('#') or len(switch_output) < 50:
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

def get_curr_mac (switch_name, switch_info):
    switch_ip = switch_info.loc[switch_info['name'] == switch_name, 'switch_ips'].iloc[0]
    for pwd in passwords:
        mac, status_code = switch_touch(switch_ip, pwd)
        if status_code == 10:
            break
    return mac

web_get_mac = Blueprint('web_get_mac', __name__)
@web_get_mac.route('/get_mac', methods=['GET'])
@cross_origin()
def mac_check_main():
    pwds = configparser.ConfigParser()
    pwds.read('/opt/backup-script/pwds.ini')

    for key in pwds['pwds']:
        passwords.append(pwds['pwds'][key])
    date = request.args.get('date')
    check_switch = request.args.get('switch_name')
    if request.args.get('hour'):
        hour = request.args.get('hour')
        mac_path = f'/mnt/sda/switch-backups/{date}/{check_switch}_mac-{date}-{hour}.txt'
    else:
        mac_path = find_recent(f'/mnt/sda/switch-backups/{date}/', check_switch, 'mac')
    if check_switch == None or date == None:
        return jsonify("Error missing params"), 400
    if date == 'current':
        switch_info = get_info()
        return jsonify(get_curr_mac(check_switch, switch_info)), 200
    return jsonify(get_mac(mac_path)), 200
