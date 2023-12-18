import json
import os
import threading
import time

from pyModbusTCP.client import ModbusClient
from pyroute2 import IPRoute
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

    def is_eth1_interface_present(self):
        with IPRoute() as ipr:
            try:
                eth1_interface = ipr.link_lookup(ifname='eth1')
                return bool(eth1_interface)
            except Exception as e:
                self.logger.error(f"Error checking eth1 interface: {e}")
                return False

    def process_web_alarms(self, msg):
        m_decode = str(msg.payload.decode("UTF-8", "ignore"))
        data = json.loads(m_decode)
        self.logger.info(f'The HW : {data.get("HardwareID")}')

        if int(data.get("HardwareID")) == 34:
            with open("dummy_data/sample.json", "w") as outfile:
                json.dump(data, outfile)

    def web_alarm_get_data(self):
        c = ModbusClient(host='192.168.3.1', port=502, auto_open=True, auto_close=False, debug=False)
        with open('dummy_data/sample.json', 'r') as file:
            json_data = file.read()
        data = json.loads(json_data)
        for key, value in data.items():
            if isinstance(value, dict) and "DataType" in value:
                data_type = int(value["DataType"])
                if data_type == 1:
                    mod_data = c.read_holding_registers(int(value['Address']), 1)
                    self.logger.info(f"DataType 1 is {mod_data}")
                # elif data_type == 2:
                #     # mod_data = c.read_holding_registers(int(value['Address']), 1)
                #     self.logger.info(f"DataType 2 is {int(value['Address'])}")
                elif data_type == 3:
                    mod_data = c.read_holding_registers(int(value['Address']), 1)
                    self.logger.info(f"DataType 3 is {mod_data} ")
                else:
                    self.logger.info(f"{key} has an unknown DataType: {data_type}")

    def periodic_update(self):
        while not self.should_exit:
            time.sleep(10)
            if self.connection_flag:
                payload = json.dumps(
                    {
                        "HardWareID": 36,
                        "object": {
                            "ParameterName": "Connection",
                            "Value": "1111",
                            "AlarmID": "9999"
                        }
                    }
                )
                self.client.publish("iot-data3", payload=payload, qos=1, retain=True)
                self.web_alarm_get_data()
                self.logger.info(f"Connection Payload send: {payload}")

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
        if topic == "web-Alarms":
            self.process_web_alarms(msg)

    def on_publish(self, client, userdata, mid):
        # self.logger.info("Message Published")
        pass


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
