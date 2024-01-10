import json
import os
import subprocess
import threading
import time

from pyModbusTCP.client import ModbusClient
from pyroute2 import IPRoute
import paho.mqtt.client as mqtt
import ssl
import uuid
from connectivity.con_status import check_internet_connection, get_active_network_interface

from log_helper import log_config
from plc.Rough import test_function_ss

from plc.Write_rough import process_web_hw_status
from system.SytemInfoClass import DeviceInformation


class MQTTClient:
    def __init__(self, logger):
        self.retry_interval = 10
        self.retry_count = 0
        self.max_retries = 5

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

        self.client.on_disconnect = self.on_disconnect
        self.client.on_log = self.on_log

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

    def check_sample_json(self):
        json_file_path = 'dummy_data/sample.json'
        try:
            if os.path.exists(json_file_path):
                with open(json_file_path, 'r') as json_file:
                    data = json.load(json_file)

                    if "HardwareID" not in data:
                        self.logger.error(f"'{json_file_path}' does not have the 'HardwareID' object.")
                        return False

                    object_count = sum(1 for key in data.keys() if key.startswith("object"))
                    if object_count < 2:
                        self.logger.error(f"'{json_file_path}' does not have at least two objects.")
                        return False
                    return True
            else:
                self.logger.error(f"'{json_file_path}' not found.")
                return False
        except Exception as e:
            self.logger.error(f"Error checking '{json_file_path}': {e}")
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

                result, mid = self.client.publish("iot-data3", payload=payload, qos=1, retain=True)
                if result == mqtt.MQTT_ERR_SUCCESS:
                    self.logger.info(f"Connection Payload send! Message ID: {mid}")
                else:
                    self.logger.error(f"Error sending Connection Payload! MQTT Error Code: {result}")

    def process_remote_access(self, msg):
        m_decode = str(msg.payload.decode("UTF-8", "ignore"))
        data = json.loads(m_decode)
        hardware_id = int(data.get("HardWareID", 0))
        access = int(data.get("object", {}).get("Access", 0))
        if hardware_id == self.get_hw_id():
            self.logger.info(f"The From portal HW is: {access}")
            self.logger.info(f"The From Local HW is: {self.get_hw_id()}")
            self.logger.info(f"Session: {access}")
            if access == 0:
                os.popen('/home/pi/rmoteStop.sh')
                self.logger.info(f"Remote Access (VPN) Stopped")
            elif access == 1:
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
                os.popen('/home/pi/rmoteStart.sh')
                self.logger.info(f"Remote Access (VPN) Started")
        else:
            self.logger.info("Access value not found in the JSON.")

    def process_operation(self, msg):
        try:
            m_decode = str(msg.payload.decode("UTF-8", "ignore"))
            data = json.loads(m_decode)
            hw_id = int(data.get("hw_id"))
            operation = data.get("operation")

            if hw_id == self.get_hw_id():
                if operation == 'reboot':
                    logger.info(f"Executing {operation}")
                    self.execute_command("sudo reboot")
                elif operation == 'net_restart':
                    logger.info(f"Executing {operation}")
                    self.execute_command("sudo systemctl restart networking")
                elif operation == 'dataplicity_restart':
                    logger.info(f"Executing {operation}")
                    self.execute_command("sudo supervisorctl restart tuxtunnel")
                elif operation == 'harp_restart':
                    logger.info(f"Executing {operation}")
                    self.execute_command("sudo systemctl restart harp")
                elif operation == 'enable_gsm':
                    logger.info(f"Executing {operation}")
                    self.execute_command("sudo mmcli -m 0 -e")

        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}")

    def execute_command(self, command):
        try:
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Error executing command: {e}")

    def process_hardware_list(self, msg):
        serial_id = self.get_serial_id()
        m_decode = str(msg.payload.decode("UTF-8", "ignore"))
        hw_id = self.find_hardware_id(m_decode, str(serial_id))

        self.logger.info(f"Serial Id : {serial_id}")
        self.logger.info(f"Hardware Id : {hw_id}")
        f = open('/home/pi/hardwareid.txt', 'w')
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
        client.subscribe('operation')

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        self.logger.info(f"Received message on topic {topic}")
        if topic == "hardwarelist":
            self.process_hardware_list(msg)
        elif topic == "web-Alarms":
            self.process_web_alarms(msg)
        elif topic == "remote-access":
            self.process_remote_access(msg)
        elif topic == "web-hardwarestatus":
            process_web_hw_status(msg, self.c, self.logger)
        elif topic == "operation":
            self.process_operation(msg)

    def on_publish(self, client, userdata, mid):
        # self.logger.info("Message Published")
        pass

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            self.logger.error(f"Disconnected from MQTT broker with result code {rc}")
            self.retry_connect()

    def on_log(self, client, userdata, level, buf):
        self.logger.debug(buf)

    def retry_connect(self):
        self.retry_count += 1
        if self.retry_count <= self.max_retries:
            self.logger.info(
                f"Retrying connection in {self.retry_interval} seconds (Attempt {self.retry_count}/{self.max_retries})")
            time.sleep(self.retry_interval)
            try:
                self.client.reconnect()
            except Exception as e:
                self.logger.error(f"Error during reconnection attempt: {e}")
                self.retry_connect()  # Retry again on failure
        else:
            self.logger.error("Maximum retries reached. Exiting...")
            self.should_exit = True


if __name__ == '__main__':
    logger, file_handler = log_config.setup_logger()
    mqtt_instance = MQTTClient(logger)
    try:
        while not mqtt_instance.should_exit:
            mqtt_instance.periodic_update()
            time.sleep(10)

    except KeyboardInterrupt:
        mqtt_instance.should_exit = True
        mqtt_instance.client.disconnect()
        mqtt_instance.client.loop_stop()
        logger.info("Exiting gracefully...")
