from kafka import KafkaConsumer, errors
#from pymongo import MongoClient
import json, time

def wait_for_kafka_consumer(topic, max_retries=10, delay=5):
    for i in range(max_retries):
        try:
            return KafkaConsumer(
                topic,
                bootstrap_servers='kafka:9092',
                value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                auto_offset_reset='earliest',
                group_id='purchase-consumers',
                enable_auto_commit=True
            )
        except errors.NoBrokersAvailable:
            print(f"[KafkaConsumer] Kafka not available, retry {i + 1}/{max_retries}")
            time.sleep(delay)
    raise RuntimeError("Kafka is not available after multiple retries.")

# Connect to Kafka
consumer = wait_for_kafka_consumer("purchase_requests")

# Connect to MongoDB
#mongo = MongoClient("mongodb://mongodb:27017/")
#collection = mongo["shopping"]["purchases"]

print("Consumer is running...")

for message in consumer:
    data = message.value
    print(f"Received message: {data}")
