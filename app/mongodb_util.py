import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

def init_mongo():
    mongo_uri = os.getenv('MONGO_URI')
    db_name =  os.getenv('DB_NAME')
    collection_name = os.getenv('COLLECTION_NAME')

    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        db = client[db_name]
        return db[collection_name]
    except ConnectionFailure as e:
        raise ConnectionFailure(f"Could not connect to MongoDB: {e}")