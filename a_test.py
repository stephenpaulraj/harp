import paho.mqtt.client as mqtt
import uuid
import ssl
import json
import time

broker_address = "b-4d9d7a54-2795-4ab2-b1e7-c40ddf1113f7-1.mq.us-east-1.amazonaws.com"
port = 8883
user = "ehashmq1"
password = "eHash@12mqtt34!"

context = ssl.create_default_context()
context.load_verify_locations(cafile="AmazonRootCA1.pem")  # Specify the CA file if needed


def on_message(client, userdata, msg):
    topic = msg.topic
    print(f"Received message on topic '{topic}': {msg.payload.decode()}")


def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe('web-Alarms')
    client.subscribe('web-hardwarestatus')


def on_publish(client, userdata, mid):
    print(f"Data published with message id: {mid}")


def publish_data(client):
    payload = json.dumps({
        "HardWareID": 34,
        "object": {
            "ParameterName": "Connection",
            "Value": "1111",
            "AlarmID": "9999"
        }
    })
    client.publish('iot-data3', payload)


client = mqtt.Client(str(uuid.uuid1()))
client.username_pw_set(user, password=password)

client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish
client.tls_set_context(context=context)

try:
    client.connect(broker_address, port=port, keepalive=1000)
    client.loop_start()

    while True:
        publish_data(client)
        time.sleep(1)

except KeyboardInterrupt:
    print("Interrupted. Disconnecting...")
    client.disconnect()
