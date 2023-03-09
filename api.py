from flask import Flask, request, jsonify
import requests

app = Flask(__name__)


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


API_URL = 'https://api.baubuddy.de/dev/index.php/v1'
AUTH_TOKEN = get_auth_token()
headers = {'Authorization': AUTH_TOKEN,
                "Content-Type": "application/json"}


@app.route("/upload-csv", methods=["POST"])
def process_csv():
    
    # Check if a CSV file was uploaded
    if not request.get_json():
        return jsonify({'error': 'CSV file not found'}), 400

    csv_file = request.get_json()

    active_vehicles_url = f'{API_URL}/vehicles/select/active'

    response = requests.get(active_vehicles_url, headers=headers)

    # Check if the API request was successful
    if response.status_code != 200:
        return jsonify({'error': 'Failed to get active vehicles from API'}), 500

    api_data = response.json()
 
    #Merge the two data sets, remove duplicates, and filter out vehicles with no hu value
    merged_data = api_data + csv_file
    merged_data = remove_duplicates(merged_data)

    filtered_data = [d for d in merged_data if 'hu' in d and d['hu']]
   
    # Resolve label colors for each vehicle
    resolve_vehicle_labels(filtered_data)

    # Return the filtered and annotated data as JSON
    return filtered_data



def remove_duplicates(merged_data):
    # Create an empty list to hold the unique items
    unique_data = []

    # Loop through each item in the concatenated list, checking if it is already in the unique list
    for item in merged_data:
        if item not in unique_data:
            unique_data.append(item)

    # Convert the unique list back to JSON format
    return unique_data


def resolve_vehicle_labels(filtered_data):
     for vehicle in filtered_data:
        label_ids = vehicle.get('labelIds', [])
        print('labelsIds: ', label_ids)
        colors = get_label_color(label_ids)
        vehicle['labelColors'] = colors    
 

def get_label_color(label_ids):
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
    app.run(debug=True, port=5000, host="127.0.0.1")