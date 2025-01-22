from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import difflib
import configparser

from .get_mac import get_info, get_curr_mac
from .helpers.compare_help import format_diff, check_changes
from .helpers.find_recent import find_recent

passwords = []

def compare_mac(mac_file_today, mac_file_yesterday, switch_name):

    if mac_file_today != 'current':
        try:
            with open(mac_file_today, 'r') as f_today, open(mac_file_yesterday, 'r') as f_yesterday:
                today_lines = f_today.readlines() # Skip the first 50 lines
                yesterday_lines = f_yesterday.readlines()  # Skip the first 50 lines
        except FileNotFoundError:
            return None, 10
    else:
        try:
            with open(mac_file_yesterday, 'r') as f_yesterday:
                    yesterday_lines = f_yesterday.readlines() # Skip the first 50 lines
        except FileNotFoundError:
            return None, 10

        f_today = get_curr_mac(switch_name, get_info())
        today_lines = f_today.splitlines(keepends=True)
    today_lines = [line.strip() + "\n" for line in today_lines]
    today_lines[0] = "\n" + today_lines[0]
    yesterday_lines = [line.strip() + "\n" for line in yesterday_lines]
    yesterday_lines[0] =  "\n" + yesterday_lines[0]
    diff = difflib.unified_diff(yesterday_lines, today_lines, lineterm='')
    diff_lines = list(diff)
    formatted_diff = format_diff(diff_lines)

    formatted_diff = check_changes(formatted_diff)

    if formatted_diff == []:
        return None, 11

    return formatted_diff, 12


web_compare_mac = Blueprint('web_compare_mac', __name__)
@web_compare_mac.route('/compare_mac', methods=['GET'])
@cross_origin()
def compare_mac_main():
    config = configparser.ConfigParser()
    config.read('/opt/backup-script/pwds.ini')

    for key in config['pwds']:
        passwords.append(config['pwds'][key])

    new_date = request.args.get('new_date')
    old_date = request.args.get('old_date')

    check_switch = request.args.get('switch_name')
    if check_switch == None or new_date == None or old_date == None:
        return jsonify("Error missing params"), 400
    mainpath_old = "/mnt/sda/switch-backups/{}/".format(old_date)
    mainpath_curr = "/mnt/sda/switch-backups/{}/".format(new_date)

    if request.args.get('old_hour'):
        old_hour = request.args.get('old_hour')
        past_mac = f'/mnt/sda/switch-backups/{old_date}/{check_switch}_mac-{old_date}-{old_hour}.txt'
    else:
        past_mac = find_recent(mainpath_old, check_switch, 'mac')
    if request.args.get('new_hour'):
        new_hour = request.args.get('new_hour')
        curr_mac = f'/mnt/sda/switch-backups/{new_date}/{check_switch}_mac-{new_date}-{new_hour}.txt'
    else:
        if new_date == 'current': 
            curr_mac = 'current'
        else:
            curr_mac = find_recent(mainpath_curr, check_switch, 'mac')

    formatted_diff, status = compare_mac(curr_mac, past_mac, check_switch)
    if status == 12 and formatted_diff != None:
        #case where there are differences
        return jsonify(formatted_diff), 200
    elif status == 11:
        #case where there is no differences
        return jsonify([[["none","No Changes Found"]]]), 200
    elif status == 10:
        #case where one of the mac isn't found
        return jsonify([[["none","Mac address list not found error"]]])
    else: 
        print("error")
        return jsonify([[["none","Unexpected error"]]]), 400
