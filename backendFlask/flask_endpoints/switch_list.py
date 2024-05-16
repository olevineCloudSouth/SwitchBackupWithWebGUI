from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import pandas as pd


def get_info():
    df = pd.read_csv("flask_endpoints/switch_ips.csv")
    return df

switch_list = Blueprint('switch_list', __name__)
@switch_list.route('/switch_list', methods=['GET'])
@cross_origin()
def switch_list_main():
    switch_info = get_info()
    switch_names = []  # List to store switch names
    for index, row in switch_info.iterrows():
        switch_name = row['name']
        switch_names.append(switch_name)  # Append each switch name to the list
    return jsonify({'switch_names': switch_names})  # Return JSONified list