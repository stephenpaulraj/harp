import json
import os
import threading
import time

from pyModbusTCP.client import ModbusClient

from pyModbusTCP.utils import word_list_to_long, decode_ieee
from pyroute2 import IPRoute
import paho.mqtt.client as mqtt
import ssl
import uuid
from connectivity.con_status import check_internet_connection, get_active_network_interface

from log_helper import log_config
from plc.Rough import test_function_ss


class MQTTClient:
    def __init__(self, logger):
        self.last_checked_time = 0
        self.cached_result = None
        self.cached_data = None
        self.cache_refresh_interval = 180
        self.modbus_client = None
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
        self.c = ModbusClient(host='192.168.3.1', port=502, auto_open=True, debug=False)
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

    def is_tun0_interface_present(self):
        with IPRoute() as ipr:
            try:
                tun0_interface = ipr.link_lookup(ifname='tun0')
                return bool(tun0_interface)
            except Exception as e:
                self.logger.error(f"Error checking tun0 interface: {e}")
                return False

    def process_web_alarms(self, msg):
        m_decode = str(msg.payload.decode("UTF-8", "ignore"))
        data = json.loads(m_decode)

        if int(data.get("HardwareID")) == self.get_hw_id():
            with open("dummy_data/sample.json", "w") as outfile:
                json.dump(data, outfile)

    def get_serial_id(self):
        try:
            with open('/home/pi/serialid.txt', 'r') as f:
                SerialNumber = f.read()
            return SerialNumber
        except FileNotFoundError:
            self.logger.error("File not found: /home/pi/serialid.txt")
            return None
        except Exception as e:
            self.logger.error(f"Error reading serial id: {e}")
            return None

    def get_hw_id(self):
        try:
            with open('/home/pi/hardwareid.txt', 'r') as f:
                HwId = f.read()
            return int(HwId)
        except FileNotFoundError:
            self.logger.error("File not found: /home/pi/hardwareid.txt")
            return None
        except Exception as e:
            self.logger.error(f"Error reading hardware id: {e}")
            return None

    def find_hardware_id(self, json_data, serial_number):
        try:
            if isinstance(json_data, bytes):
                json_data = json_data.decode('utf-8')

            data = json.loads(json_data)

            for obj_name, obj_data in data.items():
                if int(obj_data["SerialNumber"]) == int(serial_number):
                    self.logger.info(f"SerialNo Match: True")
                    return obj_data["HardwareID"]

        except json.JSONDecodeError as e:
            self.logger.info(f"Error decoding JSON: {e}")
            return None

    def periodic_update(self):
        while not self.should_exit:
            time.sleep(10)
            if self.connection_flag:
                payload = json.dumps(
                    {
                        "HardWareID": self.get_hw_id(),
                        "object": {
                            "ParameterName": "Connection",
                            "Value": "1111",
                            "AlarmID": "9999"
                        }
                    }
                )
                self.client.publish("iot-data3", payload=payload, qos=1, retain=True)
                self.logger.info(f"Connection Payload send!")
                if self.is_eth1_interface_present():
                    self.client.publish("iot-data3", payload=test_function_ss(self.c), qos=1, retain=True)
                    self.logger.info(f"PLC Payload send!")

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

    def process_remote_access(self, msg):
        m_decode = str(msg.payload.decode("UTF-8", "ignore"))
        access_value, hardware_id = self.get_remote(m_decode)
        if hardware_id == self.get_hw_id():
            self.logger.info(f"The HW is: {self.get_hw_id()}")
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
                                "HardWareID": int(self.get_hw_id()),
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

    def process_hardware_list(self, msg):
        serial_id = self.get_serial_id()
        m_decode = str(msg.payload.decode("UTF-8", "ignore"))
        hw_id = self.find_hardware_id(m_decode, str(serial_id))

        self.logger.info(f"Serial Id : {serial_id}")
        self.logger.info(f"Hardware Id : {hw_id}")
        f = open('/home/pi/hardwareid.txt', 'w')
        # f = open('dummy_data/hardwareid.txt', 'w')
        f.write(str(hw_id))
        f.close()

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
            self.process_hardware_list(msg)
        elif topic == "web-Alarms":
            self.process_web_alarms(msg)
        elif topic == "remote-access":
            self.process_remote_access(msg)

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
