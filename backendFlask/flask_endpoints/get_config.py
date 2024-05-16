from asyncio.windows_events import NULL
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
    check_switch = request.args.get('check_switch')
    if check_switch == NULL or date == NULL:
        return jsonify("Error missing params"), 400
    config_path = "/mnt/sda/switch-configs/{}/{}_config-{}.txt".format(date, check_switch, date)
    #return jsonify(get_config(config_path)), 200
    return jsonify("CS-424-Lake-Av-1000-2#terminal length 0write memBuilding configuration...Compressed configuration from 17082 bytes to 7037 bytes[OK]CS-424-Lake-Av-1000-2show runBuilding configuration..Current configuration : 17082 bytes"), 200

