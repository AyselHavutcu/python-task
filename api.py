from flask import Flask, request, jsonify
import requests
import csv

app = Flask(__name__)
API_URL = 'https://api.baubuddy.de/dev/index.php/v1'

@app.route('/proccess-csv', methods=['POST'])
def process_csv(csv_file):

    # Check if a CSV file was uploaded
    if 'csv_file' not in request.data:
        return jsonify({'error': 'CSV file not found'}), 400

    csv_file = request.data['csv_file']

    # Load the CSV file into a list of dictionaries
    csv_data = []
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        csv_data.append(row)
    AUTH_TOKEN = get_auth_token()
    active_vehicles_url = f'{API_URL}/vehicles/select/active'

    headers = {'Authorization': AUTH_TOKEN,
                "Content-Type": "application/json"}

    response = requests.get(active_vehicles_url, headers=headers)

    # Check if the API request was successful
    if response.status_code != 200:
        return jsonify({'error': 'Failed to get active vehicles from API'}), 500

    api_data = response.json()
 
    # Merge the two data sets, remove duplicates, and filter out vehicles with no hu value
    merged_data = api_data
    
    filtered_data = [d for d in merged_data if 'hu' in d and d['hu']]
   
    # Resolve label colors for each vehicle
    for vehicle in filtered_data:
        label_ids = vehicle.get('labelIds', [])
        print('labelsIds: ', label_ids)
        colors = resolve_vehicle_labels(label_ids,headers)
        vehicle['labelColors'] = colors

    # Return the filtered and annotated data as JSON
    return jsonify(filtered_data)


def get_auth_token():
    url = "https://api.baubuddy.de/index.php/login"
    payload = {
        "username": "365",
        "password": "1"
    }
    headers = {
        "Authorization": "Basic QVBJX0V4cGxvcmVyOjEyMzQ1NmlzQUxhbWVQYXNz",
        "Content-Type": "application/json"
    }
    response = requests.request("POST", url, json=payload, headers=headers)
    response_data = response.json()
    token = 'Bearer ' + response_data['oauth']['access_token']
    return token


def resolve_vehicle_labels(label_ids, headers):     
    colors = []
    if label_ids is not None:
        for label_id in label_ids:
            label_url = f'{API_URL}/labels/{label_id}'
            response = requests.get(label_url, headers=headers)
            if response.status_code == 200:
                label_json = response.json()
                color_code = label_json['data'].get('colorCode')
                if color_code:
                    colors.append(color_code)
    
    return colors


if __name__ == '__main__':
    app.run(debug=True)