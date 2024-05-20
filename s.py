import os
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
context.load_verify_locations(cafile="AmazonRootCA1.pem")


def on_message(client, userdata, msg):
    topic = msg.topic
    print(msg)
    print(topic)
    if topic == 'web-Alarms':
        m_decode = str(msg.payload.decode("UTF-8", "ignore"))
        data = json.loads(m_decode)
        with open("dummy_data/test.json", "w") as outfile:
            json.dump(data, outfile)


def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe('web-Alarms')
    client.subscribe('remote-access')
    client.subscribe('web-hardwarestatus')


def on_publish(client, userdata, mid):
    print(f"Data published with message id: {mid}")


def publish_data(client):
    payload = json.dumps({
        "HardWareID": 58,
        "object": {
            "ParameterName": "Connection",
            "Value": "1111",
            "AlarmID": "9999"
        }
    })
    client.publish("iot-data3", payload=payload, qos=1, retain=True)


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
