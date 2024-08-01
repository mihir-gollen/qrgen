import qrcode
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
import io
import json
import os

# MongoDB connection details
uri = "mongodb+srv://aashish:test123@qrdb.he13git.mongodb.net/?retryWrites=true&w=majority&appName=qrDB"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Database and collection
db = client['AgricultureDB']
collection = db['qr_DB']

# Create a directory to save QR codes locally
os.makedirs('qr_codes', exist_ok=True)

def serialize_record(record):
    """Convert MongoDB record to JSON serializable format."""
    serialized_record = {}
    for key, value in record.items():
        if isinstance(value, ObjectId):
            serialized_record[key] = str(value)
        else:
            serialized_record[key] = value
    return serialized_record

# Generate QR codes for each record
for record in collection.find():
    record_id = str(record['_id'])
    print(f"Processing record with ID: {record_id}")

    # Prepare data for the QR code, excluding the 'qr_code_path' field itself
    record_data = serialize_record(record)  # Convert record to JSON serializable format
    record_data.pop('qr_code_path', None)  # Remove 'qr_code_path' field if present
    data_to_encode = json.dumps(record_data)  # Convert data to JSON string

    # Generate the QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data_to_encode)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')

    # Save QR code as a blob
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_blob = img_byte_arr.getvalue()

    # Update record with QR code blob
    collection.update_one({'_id': ObjectId(record['_id'])}, {'$set': {'qr_code_path': img_blob}})
