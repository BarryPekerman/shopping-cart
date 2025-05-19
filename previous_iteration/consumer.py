from kafka import KafkaConsumer
from pymongo import MongoClient
import json

# MongoDB client
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["shopping"]
purchases_collection = db["purchases"]

# Kafka consumer
consumer = KafkaConsumer(
    'purchase_requests',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='mongo-writer-group',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

print("Listening for purchases and saving to MongoDB...")
for msg in consumer:
    purchase = msg.value
    purchases_collection.insert_one(purchase)
    print(f"✅ Stored purchase: {purchase}")
