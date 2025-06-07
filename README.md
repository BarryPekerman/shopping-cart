


kubectl create namespace kafka-stack
kubectl create namespace shopping-cart

helm upgrade --install mongodb bitnami/mongodb -n kafka-stack -f helm/mongodb/mongodb-values.yaml 

helm upgrade --install kafka bitnami/kafka -n kafka-stack -f helm/kafka/kafka-values.yaml

Set-up mongo sink:
1) Port-forward Connect’s REST API
kubectl port-forward svc/kafka-connect 8083:8083 -n kafka-stack &

2) Apply the connector JSON
curl -X POST http://127.0.0.1:8083/connectors \
  -H "Content-Type: application/json" \
  --data @mongo-sink.json

3) Verify status
curl http://127.0.0.1:8083/connectors/mongo-sink/status

Set-up shopping app components:

helm upgrade --install shopping-frontend helm/frontend --namespace shopping-cart

helm upgrade --install shopping-backend ./helm/backend   --namespace shopping-cart


