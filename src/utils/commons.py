from bson import ObjectId
from googleapiclient.discovery import build
import isodate
from pymongo import MongoClient
import certifi
import warnings, json
from datetime import datetime, timezone  # Ensure timezone is imported
warnings.filterwarnings("ignore")


with open("config.json", "r") as data:
    config = json.load(data)


Api_key1 = config['APIKEY1']
Api_key2 = config['APIKEY2']
mongo_conn = config['MOngoDB_conn']


youtube = build('youtube', 'v3', developerKey= Api_key1)

def connect_to_mongodb(MONGO_CONNECTION_STRING):
    try:
        # Create a MongoClient instance with CA bundle specified
        client = MongoClient(MONGO_CONNECTION_STRING, tls=True, tlsCAFile=certifi.where())

        # Attempt to get server information to confirm connection
        client.server_info()  # Forces a call to the server
        print("Successfully connected to MongoDB.")

        # # Access a specific database (replace 'test' with your database name)
        db = client['Project1']
        
        return db

    except Exception as e:
        print("Error connecting to MongoDB:", e)
        return None, None


def convert_objectid_to_str(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {key: convert_objectid_to_str(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid_to_str(item) for item in obj]
    return obj


