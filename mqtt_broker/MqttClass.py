import json
import os
import subprocess
import paho.mqtt.client as mqtt
import ssl
from pyroute2 import IPRoute
import uuid

from pyroute2 import IPDB


def get_serial_id():
    f = open('/home/pi/serialid.txt', 'r')
    # f = open('dummy_data/serialid.txt', 'r')
    SerialNumber = f.read()
    f.close()
    return SerialNumber


def get_hw_id():
    f = open('/home/pi/hardwareid.txt', 'r')
    # f = open('dummy_data/hardwareid.txt', 'r')
    HwId = f.read()
    f.close()
    return HwId


class MQTTClient:
    def __init__(self, logger):
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
        self.client.connect(self.broker_address, port=self.port, keepalive=1000)

        self.client.loop_start()

    def check_connection(self):
        return self.connection_flag and self.client.is_connected()

    def is_tun0_interface_present(self):
        with IPRoute() as ipr:
            try:
                tun0_interface = ipr.link_lookup(ifname='tun0')
                return bool(tun0_interface)
            except Exception as e:
                self.logger.error(f"Error checking tun0 interface: {e}")
                return False

    def get_hardware_id(self, serial_number, json_data):
        try:
            if isinstance(json_data, bytes):
                json_data = json_data.decode('utf-8')

            data = json.loads(json_data)

            for obj_key, obj_value in data.items():
                if obj_value["SerialNumber"] == serial_number:
                    return obj_value["HardwareID"]

        except json.JSONDecodeError as e:
            self.logger.info(f"Error decoding JSON: {e}")
        return None

    def get_remote(self, json_data):
        try:
            data = json.loads(json_data)
            if "object" in data:
                object_data = data["object"]

                if "Access" in object_data and "HardWareID" in data:
                    access_value = object_data["Access"]
                    hardware_id = data["HardWareID"]
                    hw_id = str(hardware_id)
                    return access_value, hw_id

        except json.JSONDecodeError as e:
            self.logger.info(f"Error decoding JSON: {e}")

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
        if topic == "hardwarelist":
            self.process_hardwarelist(msg)
        elif topic == "web-hardwarestatus":
            self.process_web_hardwarestatus(msg)
        elif topic == "web-Alarms":
            self.process_web_alarms(msg)
        elif topic == "remote-access":
            self.process_remote_access(msg)
        elif topic == "network":
            self.process_network(msg)

    def process_hardwarelist(self, msg):
        serial_id = get_serial_id()
        m_decode = str(msg.payload.decode("UTF-8", "ignore"))
        hw_id = self.get_hardware_id(serial_id, m_decode)
        self.logger.info(f"Serial Id : {serial_id}")
        self.logger.info(f"Hardware Id : {hw_id}")
        f = open('/home/pi/hardwareid.txt', 'r')
        # f = open('dummy_data/hardwareid.txt', 'w')
        f.write(str(hw_id))
        f.close()

    def process_web_hardwarestatus(self, msg):
        pass

    def process_web_alarms(self, msg):
        pass

    def process_remote_access(self, msg):
        m_decode = str(msg.payload.decode("UTF-8", "ignore"))
        access_value, hardware_id = self.get_remote(m_decode)
        if hardware_id == get_hw_id():
            self.logger.info(f"The HW is: {get_hw_id()}")
            if access_value is not None:
                self.logger.info(f"The Access value is: {access_value}")
                if access_value == "0":
                    os.popen('/home/pi/rmoteStop.sh')
                    self.logger.info(f"Remote Access (VPN) Stopped")
                if access_value == "1":
                    os.popen('/home/pi/rmoteStart.sh')
                    self.logger.info(f"Remote Access (VPN) Started")
                    # find Tun0 available (send Payload) tun0 i up
                    if self.is_tun0_interface_present():
                        self.logger.info("tun0 interface is present. Sending payload.")
                        payload = json.dumps(
                            {
                                "HardWareID": get_hw_id(),
                                "object": {
                                    "ParameterName": "Remote",
                                    "Value": "1111",
                                    "AlarmID": "8888"
                                }
                            }
                        )
                        self.client.publish('iot-data3', payload=payload, qos=1, retain=True)
                    else:
                        self.logger.info("tun0 interface is not present.")
        else:
            self.logger.info("Access value not found in the JSON.")

    def process_network(self, msg):
        pass

    def on_publish(self, client, userdata, mid):
        self.logger.info("Message Published")
