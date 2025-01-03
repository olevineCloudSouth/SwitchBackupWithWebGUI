from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import difflib
import configparser

from .get_int_status import get_info, get_curr_int
from .compare_help import format_diff, check_changes

passwords = []

def compare_int(int_file_today, int_file_yesterday, switch_name):

    if int_file_today != 'current':
        try:
            with open(int_file_today, 'r') as f_today, open(int_file_yesterday, 'r') as f_yesterday:
                today_lines = f_today.readlines() 
                yesterday_lines = f_yesterday.readlines()  
        except FileNotFoundError:
            return None, 10
    else:
        try:
            with open(int_file_yesterday, 'r') as f_yesterday:
                    yesterday_lines = f_yesterday.readlines() 
        except FileNotFoundError:
            return None, 10

        f_today = get_curr_int(switch_name, get_info())
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


web_compare_int = Blueprint('web_compare_int', __name__)
@web_compare_int.route('/compare_int', methods=['GET'])
@cross_origin()
def compare_int_main():
    #config = configparser.ConfigParser()
    #config.read('/opt/backup-script/pwds.ini')

    #for key in config['pwds']:
    #    passwords.append(config['pwds'][key])

    new_date = request.args.get('new_date')
    old_date = request.args.get('old_date')

    check_switch = request.args.get('switch_name')
    if check_switch == None or new_date == None or old_date == None:
        return jsonify("Error missing params"), 400
    past_int = ".\\switch-backups\\{}_int-{}.txt".format(check_switch, old_date)
    #past_int = "/mnt/sda/switch-configs/{}/{}_int-{}.txt".format(old_date, check_switch, old_date)
    curr_int = ".\\switch-backups\\{}_int-{}.txt".format(check_switch, new_date)
    #curr_int = "/mnt/sda/switch-configs/{}/{}_int-{}.txt".format(new_date, check_switch, new_date)
    if new_date == 'current': 
        curr_int = 'current'
    formatted_diff, status = compare_int(curr_int, past_int, check_switch)
    if status == 12 and formatted_diff != None:
        #case where there are differences
        return jsonify(formatted_diff), 200
    elif status == 11:
        #case where there is no differences
        return jsonify([[["none","No Changes Found"]]]), 200
    elif status == 10:
        #case where one of the int isn't found
        return jsonify([[["none","Interface statuses not found error"]]])
    else: 
        print("error")
        return jsonify([[["none","Unexpected error"]]]), 400
