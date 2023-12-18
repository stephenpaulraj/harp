import json
import threading
import time

import paho.mqtt.client as mqtt
import ssl
import uuid
from connectivity.con_status import check_internet_connection, get_active_network_interface
from log_helper import log_config


class MQTTClient:
    def __init__(self, logger):
        self.should_exit = False

        self.logger = logger
        self.client = mqtt.Client(str(uuid.uuid1()), reconnect_on_failure=True)
        self.broker_address = "b-4d9d7a54-2795-4ab2-b1e7-c40ddf1113f7-1.mq.us-east-1.amazonaws.com"
        self.port = 8883
        self.user = "ehashmq1"
        self.password = "eHash@12mqtt34!"

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_publish = self.on_publish

        self.connection_flag = False

        self.client.username_pw_set(self.user, password=self.password)

        self.context = ssl.create_default_context()
        self.context.check_hostname = False
        self.context.verify_mode = ssl.CERT_REQUIRED
        self.context.load_verify_locations(cafile="AmazonRootCA1.pem")

        self.client.tls_set_context(context=self.context)
        self.client.connect(self.broker_address, port=self.port, keepalive=60)

        self.client.loop_start()

        self.periodic_update_thread = threading.Thread(target=self.periodic_update, daemon=True)
        self.periodic_update_thread.start()

    def periodic_update(self):
        while not self.should_exit:
            time.sleep(10)
            if self.connection_flag:
                id = int(36)
                payload = json.dumps(
                    {
                        "HardWareID": id,
                        "object": {
                            "ParameterName": "Connection",
                            "Value": "1111",
                            "AlarmID": "9999"
                        }
                    }
                )
                self.client.publish("iot-data3", payload=payload, qos=1, retain=True)
                self.logger.info(f"Message send: {payload}")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connection_flag = True
            self.logger.info("Connected to MQTT broker")
        else:
            self.logger.error(f"Failed to connect to MQTT broker with result code {rc}")

        client.subscribe('hardwarelist')
        client.subscribe('remote-access')
        client.subscribe('network')
        client.subscribe('web-Alarms')
        client.subscribe('web-hardwarestatus')

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        self.logger.info(f"Received message on topic {topic}")

    def on_publish(self, client, userdata, mid):
        self.logger.info("Message Published")


if __name__ == '__main__':
    logger, file_handler = log_config.setup_logger()
    internet_status = check_internet_connection()

    if internet_status:
        mqtt_instance = MQTTClient(logger)
        try:
            while True:
                pass

        except KeyboardInterrupt:
            mqtt_instance.should_exit = True
            mqtt_instance.periodic_update_thread.join()
            logger.info("Exiting gracefully...")

