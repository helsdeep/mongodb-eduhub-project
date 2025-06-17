from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


MONGO_URI = "mongodb://localhost:27017"

def mongo_connection():
    try:
        _client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
        _client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        return _client
    except Exception as e:
        print(e)
        return None

client = mongo_connection()
db = client.edu_hub
