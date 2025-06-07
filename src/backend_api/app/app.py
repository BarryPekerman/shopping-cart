from flask import Flask, request, jsonify
from kafka import KafkaProducer, errors
from pymongo import MongoClient
import json, datetime, os, time

app = Flask(__name__)

# ───────────────────────────────────────────────────────
# Configurable retry parameters (via ENV or defaults)
# ───────────────────────────────────────────────────────
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
# how many times to retry before giving up
KAFKA_INIT_RETRIES = int(os.getenv("KAFKA_INIT_RETRIES", "5"))
# seconds to wait between retries
KAFKA_RETRY_BACKOFF = float(os.getenv("KAFKA_RETRY_BACKOFF", "2"))

# ───────────────────────────────────────────────────────
# Lazy, retriable producer
# ───────────────────────────────────────────────────────
_producer = None

def get_producer():
    global _producer
    if _producer is None:
        for attempt in range(1, KAFKA_INIT_RETRIES + 1):
            try:
                _producer = KafkaProducer(
                    bootstrap_servers=KAFKA_BOOTSTRAP,
                    value_serializer=lambda v: json.dumps(v).encode("utf-8")
                )
                app.logger.info(f"Connected to Kafka on {KAFKA_BOOTSTRAP}")
                break
            except errors.NoBrokersAvailable:
                app.logger.warning(
                    f"[{attempt}/{KAFKA_INIT_RETRIES}] "
                    f"Kafka not available at {KAFKA_BOOTSTRAP}, "
                    f"retrying in {KAFKA_RETRY_BACKOFF}s…"
                )
                time.sleep(KAFKA_RETRY_BACKOFF)
        else:
            raise RuntimeError(f"Unable to connect to Kafka at {KAFKA_BOOTSTRAP}")
    return _producer

# ───────────────────────────────────────────────────────
# Mongo client (reads)
# ───────────────────────────────────────────────────────
mongo      = MongoClient(os.getenv("MONGO_URI", "mongodb://mongodb:27017/"))
collection = mongo["shopping"]["purchases"]

# ───────────────────────────────────────────────────────
# Routes
# ───────────────────────────────────────────────────────
@app.route("/healthz", methods=["GET"])
def healthz():
    return "OK", 200

@app.route("/buy", methods=["POST"])
def buy():
    data = request.json or {}
    for f in ("user_id","item_id","price"):
        if f not in data:
            return jsonify({"error": f"Missing {f}"}), 400

    data["timestamp"] = datetime.datetime.utcnow().isoformat()
    producer = get_producer()
    producer.send("purchase_requests", data)
    return jsonify({"status": "queued"})

@app.route("/purchases", methods=["GET"])
def purchases():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    docs = collection.find(
        {"user_id": user_id},
        {"_id": 0, "user_id": 1, "item_id": 1, "price": 1, "timestamp": 1}
    )
    return jsonify(list(docs))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

