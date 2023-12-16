import ssl
import uuid

import paho.mqtt.client as mqtt

context = ssl.create_default_context()

broker_address = "b-4d9d7a54-2795-4ab2-b1e7-c40ddf1113f7-1.mq.us-east-1.amazonaws.com"
port = 8883
user = "ehashmq1"
password = "eHash@12mqtt34!"


def on_connect(client, userdata, flags, rc):
    pass


def on_message(client, userdata, msg):
    pass


def on_publish(client, userdata, mid):
    pass


client = mqtt.Client(str(uuid.uuid1()))  # create new instance

client.username_pw_set(user, password=password)  # set username and password

client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish
client.tls_set_context(context=context)
client.connect(broker_address, port=port, keepalive=1000)

# client.connect(host=Config.MQTT_HOST, port=Config.MQTT_PORT, keepalive=60)
client.loop_start()
