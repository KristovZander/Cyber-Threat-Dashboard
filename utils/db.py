import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["cti_dashboard"]
collection = db["scans"]

def save_scan(ip, vt_result, abuse_result):
    scan_doc = {
        "ip": ip,
        "virus_total": vt_result,
        "abuse_ipdb": abuse_result,
        "timestamp": datetime.now().strftime("%d-%m-%Y %I:%M %p")
    }
    collection.insert_one(scan_doc)

def get_recent_scans(limit=10):
    return list(collection.find().sort("_id", -1).limit(limit))

#def clear_all_scans():
    collection.delete_many({})
    print("✅ All scan records deleted.")
