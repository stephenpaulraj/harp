import paho.mqtt.client as mqtt
import ssl
import uuid


class MQTTClient:
    def __init__(self):
        self.client = mqtt.Client(str(uuid.uuid1()))
        self.broker_address = "b-4d9d7a54-2795-4ab2-b1e7-c40ddf1113f7-1.mq.us-east-1.amazonaws.com"
        self.port = 8883
        self.user = "ehashmq1"
        self.password = "eHash@12mqtt34!"

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_publish = self.on_publish

        self.context = ssl.create_default_context()
        self.context.check_hostname = False
        self.context.verify_mode = ssl.CERT_NONE
        self.client.tls_set_context(context=self.context)

        self.client.connect(self.broker_address, port=self.port, keepalive=1000)

        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        pass

    def on_message(self, client, userdata, msg):
        pass

    def on_publish(self, client, userdata, mid):
        pass
