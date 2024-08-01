from flask import Flask, jsonify, send_file, render_template, request
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
import io

app = Flask(__name__)

uri = "mongodb+srv://aashish:test123@qrdb.he13git.mongodb.net/?retryWrites=true&w=majority&appName=qrDB"

client = MongoClient(uri, server_api=ServerApi('1'))

db = client['AgricultureDB']
collection = db['qr_DB']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/record/<record_id>', methods=['GET'])
def get_record(record_id):
    print(f"Received request for record ID: {record_id}")
    try:
        record = collection.find_one({'_id': ObjectId(record_id)})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 400
    
    if record:
        record['_id'] = str(record['_id'])
        if 'qr_code_path' in record:
            del record['qr_code_path']
        return jsonify(record)
    else:
        print("Record not found")
        return jsonify({'error': 'Record not found'}), 404

@app.route('/qr_code/<record_id>', methods=['GET'])
def get_qr_code(record_id):
    try:
        record = collection.find_one({'_id': ObjectId(record_id)}, {'qr_code_path': 1})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 400
    
    if record and 'qr_code_path' in record:
        img_blob = record['qr_code_path']
        return send_file(io.BytesIO(img_blob), mimetype='image/png')
    else:
        return jsonify({'error': 'QR code not found'}), 404

@app.route('/fetch_qr', methods=['POST'])
def fetch_qr():
    record_id = request.form.get('record_id')
    return jsonify({'url': f'/qr_code/{record_id}'})

if __name__ == '__main__':
    app.run(debug=True)
