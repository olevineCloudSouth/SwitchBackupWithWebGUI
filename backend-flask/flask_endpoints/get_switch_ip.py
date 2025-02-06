from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import pandas as pd

web_get_switch_ip = Blueprint('web_get_switch_ip', __name__)

@web_get_switch_ip.route('/get_switch_ip', methods=['GET'])
@cross_origin()
def get_switch_ip_main():
    switch_name = request.args.get('switch_name')
    df = pd.read_csv("/opt/backup-script/switch_ips.csv")
    match = df[df['name'] == switch_name]
    
    if match.empty:
        return jsonify({"error": "No match found"}), 400
    
    # Return only the 'ip' column value
    return jsonify({"ip": match.iloc[0]['switch_ips']}), 200