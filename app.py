from flask import Flask, request, render_template, redirect, url_for
from datetime import datetime
from kafka import KafkaProducer
from pymongo import MongoClient
import uuid, json

app = Flask(__name__)

# Kafka producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# MongoDB client
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["shopping"]
purchases_collection = db["purchases"]

@app.route('/')
def index():
    purchases = list(purchases_collection.find().sort("timestamp", -1))
    return render_template('index.html', purchases=purchases)

@app.route('/buy', methods=['POST'])
def buy():
    item_id = request.form['item_id']
    user_id = request.form['user_id']
    price = request.form['price']

    purchase = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "item_id": item_id,
        "price": float(price),
        "timestamp": datetime.utcnow().isoformat()
    }

    #Send to Kafka
    producer.send('purchase_requests', value=purchase)
    producer.flush()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
