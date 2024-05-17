from asyncio.windows_events import NULL
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import difflib

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

def compare_configs(config_file_today, config_file_yesterday):
    try:
        with open(config_file_today, 'r') as f_today, open(config_file_yesterday, 'r') as f_yesterday:
            today_lines = f_today.readlines()[50:]  # Skip the first 20 lines
            yesterday_lines = f_yesterday.readlines()[50:]  # Skip the first 20 lines
    except FileNotFoundError:
        return None, 10

    diff = difflib.unified_diff(yesterday_lines, today_lines, lineterm='')
    diff_lines = list(diff)
    formatted_diff = format_diff(diff_lines)

    formatted_diff = check_changes(formatted_diff)

    if formatted_diff == []:
        return None, 11

    return formatted_diff, 12

web_switch_check = Blueprint('web_switch_check', __name__)
@web_switch_check.route('/switch_check', methods=['GET'])
@cross_origin()
def switch_check_main():
    new_date = request.args.get('new_date')
    old_date = request.args.get('old_date')
    check_switch = request.args.get('check_switch')
    if check_switch == NULL or new_date == NULL or old_date == NULL:
        return jsonify("Error missing params"), 400
    past_config = "/mnt/sda/switch-configs/{}/{}_config-{}.txt".format(old_date, check_switch, old_date)
    curr_config = "/mnt/sda/switch-configs/{}/{}_config-{}.txt".format(new_date, check_switch, new_date)
    formatted_diff, status = compare_configs(curr_config, past_config)
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