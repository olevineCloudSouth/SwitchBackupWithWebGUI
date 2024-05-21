from flask import Blueprint, jsonify, request
from flask_cors import cross_origin


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



web_get_config = Blueprint('web_get_config', __name__)
@web_get_config.route('/get_config', methods=['GET'])
@cross_origin()
def config_check_main():
    date = request.args.get('date')
    check_switch = request.args.get('switch_name')
    if check_switch == None or date == None:
        return jsonify("Error missing params"), 400
    config_path = "/mnt/sda/switch-configs/{}/{}_config-{}.txt".format(date, check_switch, date)
    return jsonify(get_config(config_path)), 200
