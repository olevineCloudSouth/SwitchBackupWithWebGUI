from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import difflib
import paramiko
import time
import pandas as pd
import configparser

from backendFlask.flask_endpoints.get_config import get_curr_config

passwords = []

def format_diff(diff_lines):
    formatted_diff = []
    for line in diff_lines:
        if line.startswith('--- ') or line.startswith('+++ '):
            # File names, keep them as-is
            formatted_diff.append(line)
        elif line.startswith('@@'):
            # Section header, keep it as-is
            formatted_diff.append(line)
        elif line.startswith('+'):
            # Check if line contains "ntp clock-period"
            if "ntp clock-period" in line:
                continue  # Skip this line
            # Added lines, prefix with "+"
            formatted_diff.append(f"add {line[1:]}")
        elif line.startswith('-'):
            # Check if line contains "ntp clock-period"
            if "ntp clock-period" in line:
                continue  # Skip this line
            # Removed lines, prefix with "-"
            formatted_diff.append(f"del {line[1:]}")
        else:
            # Unchanged lines, no prefix
            formatted_diff.append(f"  {line}")
    return formatted_diff

def check_changes(formatted_diff):
    sections = [[]]  # Initialize sections with an empty list
    i = 0
    for line in formatted_diff:
        if line.startswith('@@'):
            i += 1
            sections.append([])  # Append a new empty list for the next section
        sections[i].append(line)

    # Remove sections that don't contain 'del' or 'add'
    sections_to_remove = []
    for idx, section in enumerate(sections):
        contains_del_add = any('del ' in line or 'add ' in line for line in section)
        if not contains_del_add:
            sections_to_remove.append(idx)

    for idx in reversed(sections_to_remove):
        del sections[idx]

    return sections

def compare_configs(config_file_today, config_file_yesterday, switch_name):
    if config_file_today != 'current':
        try:
            with open(config_file_today, 'r') as f_today, open(config_file_yesterday, 'r') as f_yesterday:
                today_lines = f_today.readlines()[50:]  # Skip the first 50 lines
                yesterday_lines = f_yesterday.readlines()[50:]  # Skip the first 50 lines
        except FileNotFoundError:
            return None, 10
    else:
        try:
            with open(config_file_yesterday, 'r') as f_yesterday:
                    yesterday_lines = f_yesterday.readlines()[50:]  # Skip the first 50 lines
        except FileNotFoundError:
            return None, 10

        
        f_today = get_curr_config(switch_name, get_info())
        today_lines = f_today.splitlines()[50:]


    diff = difflib.unified_diff(yesterday_lines, today_lines, lineterm='')
    diff_lines = list(diff)
    formatted_diff = format_diff(diff_lines)

    formatted_diff = check_changes(formatted_diff)

    if formatted_diff == []:
        return None, 11

    return formatted_diff, 12

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

web_switch_check = Blueprint('web_switch_check', __name__)
@web_switch_check.route('/switch_check', methods=['GET'])
@cross_origin()
def switch_check_main():
    config = configparser.ConfigParser()
    config.read('/opt/backup-script/pwds.ini')

    for key in config['pwds']:
        passwords.append(config['pwds'][key])

    new_date = request.args.get('new_date')
    old_date = request.args.get('old_date')

    check_switch = request.args.get('switch_name')
    if check_switch == None or new_date == None or old_date == None:
        return jsonify("Error missing params"), 400
    past_config = "/mnt/sda/switch-configs/{}/{}_config-{}.txt".format(old_date, check_switch, old_date)
    curr_config = "/mnt/sda/switch-configs/{}/{}_config-{}.txt".format(new_date, check_switch, new_date)
    if new_date == 'current': 
        curr_config = 'current'
    formatted_diff, status = compare_configs(curr_config, past_config, check_switch)
    if status == 12 and formatted_diff != None:
        #case where there are differences
        return jsonify(formatted_diff), 200
    elif status == 11:
        #case where there is no differences
        return jsonify(""), 200
    elif status == 10:
        #case where one of the configs isn't found
        return jsonify("Config not found error")
    else: 
        print("error")
        return jsonify("Unexpected error"), 400