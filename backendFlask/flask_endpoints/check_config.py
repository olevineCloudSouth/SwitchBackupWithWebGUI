from flask import Blueprint, jsonify, request

web_switch_check = Blueprint('web_switch_check', __name__)
@web_switch_check.route('/switch_check', methods=['GET'])
def switch_check_main():
    request_data = request.get_json()
    print(request_data)

    return jsonify("Hello world"), 200
