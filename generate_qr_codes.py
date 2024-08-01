import qrcode
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
import io
import json
import os

uri = "mongodb+srv://aashish:test123@qrdb.he13git.mongodb.net/?retryWrites=true&w=majority&appName=qrDB"

client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


db = client['AgricultureDB']
collection = db['qr_DB']


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

for record in collection.find():
    record_id = str(record['_id'])
    print(f"Processing record with ID: {record_id}")

    
    record_data = serialize_record(record)  
    record_data.pop('qr_code_path', None)  
    data_to_encode = json.dumps(record_data)  

    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data_to_encode)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_blob = img_byte_arr.getvalue()
    collection.update_one({'_id': ObjectId(record['_id'])}, {'$set': {'qr_code_path': img_blob}})
