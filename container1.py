from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Directory to store files, mounted to a Kubernetes Persistent Volume
FILE_DIRECTORY = "/path_to_your_persistent_volume"
CONTAINER_2_ENDPOINT_VALIDATE_CSV = 'http://container2:4000/validate-csv'
CONTAINER_2_ENDPOINT_SUM_PROCESS = 'http://container2:4000/processSum'

@app.route('/store-file', methods=['POST'])
def store_file():
    data = request.get_json()
    if not data or 'file' not in data or 'data' not in data:
        return jsonify({"file": None, "error": "Invalid JSON input."}), 400
    
    filename = data['file']
    content = data['data']
    filepath = os.path.join(FILE_DIRECTORY, filename)
    
    try:
        with open(filepath, 'w') as file:
            file.write(content)
        return jsonify({"file": filename, "message": "Success."}), 200
    except Exception as e:
        return jsonify({"file": filename, "error": f"Error while storing the file to the storage: {str(e)}"}), 500

@app.route('/calculate', methods=['POST'])
def calculate():
    input_data = request.get_json()
    
   
    if 'file' not in input_data or not input_data['file']:
        return jsonify({"file": None, "error": "Invalid JSON input."}), 400
    
    try:
        response = requests.post(CONTAINER_2_ENDPOINT_CHECK_FILE_EXISTS, json=input_data)
        check_file_exists = response.json().get('exists', False)
        if not check_file_exists:
            return jsonify({"file": input_data["file"], "error": "File not found."}), 404
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500
    
    try:
        sum_response = requests.post(CONTAINER_2_ENDPOINT_SUM_PROCESS, json=input_data)
        return sum_response.json(), sum_response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)