from flask import Flask, request, jsonify
from kafka import KafkaProducer, errors
from pymongo import MongoClient
import uuid, json, datetime, time

app = Flask(__name__)

# Retry Kafka connection logic
def wait_for_kafka_producer(max_retries=10, delay=5):
    for i in range(max_retries):
        try:
            return KafkaProducer(
                bootstrap_servers='kafka:9092',
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
        except errors.NoBrokersAvailable:
            print(f"[KafkaProducer] Kafka not available, retry {i + 1}/{max_retries}")
            time.sleep(delay)
    raise RuntimeError("Kafka is not available after multiple retries.")

# Connect to Kafka
producer = wait_for_kafka_producer()

# Connect to MongoDB
mongo = MongoClient("mongodb://mongodb:27017/")
collection = mongo["shopping"]["purchases"]

@app.route("/buy", methods=["POST"])
def buy():
    data = request.json
    data["id"] = str(uuid.uuid4())
    data["timestamp"] = datetime.datetime.utcnow().isoformat()
    producer.send("purchase_requests", data)
    return jsonify({"status": "queued", "id": data["id"]})

@app.route("/purchases", methods=["GET"])
def get_purchases():
    user_id = request.args.get("user_id")
    query = {"user_id": user_id} if user_id else {}
    results = list(collection.find(query, {"_id": 0}))
    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
