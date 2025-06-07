from flask import Flask, request, jsonify
from kafka import KafkaProducer
from pymongo import MongoClient
import uuid, json, datetime

app = Flask(__name__)

# Kafka Setup
producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# MongoDB Setup
mongo = MongoClient("mongodb://mongodb:27017/")
query_results = mongo["shopping"]["query_results"]

@app.route("/buy", methods=["POST"])
def buy():
    data = request.json
    data["id"] = str(uuid.uuid4())
    data["timestamp"] = datetime.datetime.utcnow().isoformat()
    producer.send("purchase_requests", data)
    return jsonify({"status": "queued", "id": data["id"]})


@app.route("/purchases", methods=["GET"])
def purchases():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    query_id = str(uuid.uuid4())
    query_msg = {"query_id": query_id, "user_id": user_id}
    producer.send("purchase_queries", query_msg)

    return jsonify({"status": "queued", "query_id": query_id})


@app.route("/results", methods=["GET"])
def get_results():
    query_id = request.args.get("query_id")
    if not query_id:
        return jsonify({"error": "Missing query_id"}), 400

    result = query_results.find_one({"query_id": query_id}, {"_id": 0})
    if result:
        return jsonify(result)
    return jsonify({"status": "pending"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

