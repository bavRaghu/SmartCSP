import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
if not MONGO_URI:
    raise Exception("MONGODB_URI not found in .env")

client = MongoClient(MONGO_URI)
db = client.smart_csp

scans_collection = db.scans
