from flask import Flask, request, jsonify
from kafka import KafkaProducer, KafkaConsumer, errors
import uuid, json, datetime, time

app = Flask(__name__)

# ----- Kafka Setup -----

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

producer = wait_for_kafka_producer()

# ----- Routes -----

@app.route("/buy", methods=["POST"])
def buy():
    data = request.json
    data["id"] = str(uuid.uuid4())
    data["timestamp"] = datetime.datetime.utcnow().isoformat()

    try:
        producer.send("purchase_requests", data)
        return jsonify({"status": "queued", "id": data["id"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def wait_for_query_response(query_id, timeout=3):
    """ Waits for a Kafka message on 'purchase_responses' with the matching query_id """
    consumer = KafkaConsumer(
        'purchase_responses',
        bootstrap_servers='kafka:9092',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='latest',
        group_id=f"query-listener-{query_id}",
        enable_auto_commit=True,
        consumer_timeout_ms=int(timeout * 1000)
    )

    start = time.time()
    for msg in consumer:
        data = msg.value
        if data.get("query_id") == query_id:
            return data.get("results", [])
        if time.time() - start > timeout:
            break
    return []


@app.route("/purchases", methods=["GET"])
def get_purchases():
    user_id = request.args.get("user_id")
    query_id = str(uuid.uuid4())

    query_msg = {
        "query_id": query_id,
        "user_id": user_id
    }

    try:
        producer.send("purchase_queries", query_msg)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    results = wait_for_query_response(query_id)
    return jsonify(results)


# ----- Entrypoint -----

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

