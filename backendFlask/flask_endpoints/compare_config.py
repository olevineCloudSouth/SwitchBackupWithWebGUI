from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import difflib
import configparser

from .get_config import get_curr_config, get_info
from .compare_help import format_diff, check_changes


passwords = []

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
        today_lines = f_today.splitlines(keepends=True)[50:]

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


web_compare_config = Blueprint('web_compare_config', __name__)
@web_compare_config.route('/compare_config', methods=['GET'])
@cross_origin()
def compare_config_main():
    config = configparser.ConfigParser()
    config.read('/opt/backup-script/pwds.ini')

    for key in config['pwds']:
        passwords.append(config['pwds'][key])

    new_date = request.args.get('new_date')
    old_date = request.args.get('old_date')

    check_switch = request.args.get('switch_name')
    if check_switch == None or new_date == None or old_date == None:
        return jsonify("Error missing params"), 400
    #past_config = "./flask_endpoints/{}/{}_config-{}.txt".format(old_date, check_switch, old_date)
    past_config = "/mnt/sda/switch-configs/{}/{}_config-{}.txt".format(old_date, check_switch, old_date)
    #curr_config = "./flask_endpoints/{}/{}_config-{}.txt".format(new_date, check_switch, new_date)
    curr_config = "/mnt/sda/switch-configs/{}/{}_config-{}.txt".format(new_date, check_switch, new_date)
    if new_date == 'current': 
        curr_config = 'current'
    formatted_diff, status = compare_configs(curr_config, past_config, check_switch)
    if status == 12 and formatted_diff != None:
        #case where there are differences
        return jsonify(formatted_diff), 200
    elif status == 11:
        #case where there is no differences
        return jsonify([[["none","No Changes Found"]]]), 200
    elif status == 10:
        #case where one of the configs isn't found
        return jsonify([[["none","Config not found error"]]])
    else: 
        print("error")
        return jsonify([[["none","Unexpected error"]]]), 400
