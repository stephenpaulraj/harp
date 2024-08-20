import json
import os
import subprocess
import sys
import threading
import time
import serial
import psutil
from pyModbusTCP.client import ModbusClient
from pyroute2 import IPDB
import paho.mqtt.client as mqtt
import ssl
import uuid
from log_helper import log_config
from plc.Poll_Data import read_json_and_poll


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
        self.broker_address = "b-fba2aea8-4d42-46f9-95bf-9cf5629a8898-1.mq.eu-west-1.amazonaws.com"
        self.port = 8883
        self.user = "consoleuser"
        self.password = "ioTHw@CA2024"

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
        self.periodic_update_thread = threading.Thread(target=self.periodic_update, daemon=True)
        self.periodic_update_thread.start()

        self.first_run = True

    def exit_gracefully(self):
        self.should_exit = True
        self.periodic_update_thread.join()
        self.client.disconnect()
        sys.exit()

    def is_eth_interface_present(self):
        with IPDB() as ipr:
            try:
                # Fetch interfaces
                eth0_interface = ipr.interfaces.get('eth0', None)
                eth1_interface = ipr.interfaces.get('eth1', None)

                self.logger.debug(f"eth0_interface: {eth0_interface}")
                self.logger.debug(f"eth1_interface: {eth1_interface}")

                # Check if interfaces are up
                eth0_ip = self.get_interface_ip('eth0') if eth0_interface and eth0_interface.operstate == 'UP' else None
                eth1_ip = self.get_interface_ip('eth1') if eth1_interface and eth1_interface.operstate == 'UP' else None

                self.logger.debug(f"eth0 IP: {eth0_ip}")
                self.logger.debug(f"eth1 IP: {eth1_ip}")

                # Check if the IP is present on any interface
                eth0_ip_present = eth0_ip == '192.168.3.11'
                eth1_ip_present = eth1_ip == '192.168.3.11'

                if eth0_ip_present or eth1_ip_present:
                    self.logger.info(f"{'eth0' if eth0_ip_present else 'eth1'} IP is '192.168.3.11'.")
                    return True
                else:
                    self.logger.error("Neither eth0 nor eth1 interface found with IP '192.168.3.11'.")
                    if not self.check_sample_json():
                        self.logger.error("Problem with Web-Alarm Json File.")
                        return False
                    self.logger.info("All (Device, PLC, Network) checklist passed.")
                    return False
            except Exception as e:
                self.logger.error(f"Error checking eth interfaces: {e}")
                return False

    def get_interface_ip(self, interface_name):
        try:
            with IPDB() as ipr:
                iface = ipr.interfaces[interface_name]
                self.logger.debug(f"Interface {interface_name} details: {iface}")
                if iface:
                    # Getting the first IPv4 address
                    for ip_info in iface.ipaddr:
                        if ip_info[0].count('.') == 3:  # This checks if it's an IPv4 address
                            return ip_info[0]
        except Exception as e:
            self.logger.error(f"Error retrieving IP for {interface_name}: {e}")
        return None

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
            self.logger.debug(f"Connection Flag Status : {self.connection_flag}")
            self.logger.debug(f"Interface Flag Status : {self.is_eth_interface_present()}")
            if self.connection_flag:
                if self.is_eth_interface_present():
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

                    result, mid = self.client.publish("iot-data3", payload=read_json_and_poll(self.c), qos=1,
                                                      retain=True)
                    if result == mqtt.MQTT_ERR_SUCCESS:
                        self.logger.info(f"PLC Payload send! Message ID: {mid}")
                    else:
                        self.logger.error(f"Error sending PLC Payload! MQTT Error Code: {result}")

                    if self.check_tun0_available():
                        remote = json.dumps(
                            {
                                "HardWareID": int(self.get_hw_id()),
                                "object": {
                                    "ParameterName": "Remote",
                                    "Value": "1111",
                                    "AlarmID": "8888"
                                }
                            }
                        )
                        result, mid = self.client.publish('iot-data3', payload=remote, qos=1, retain=True)
                        if result == mqtt.MQTT_ERR_SUCCESS:
                            self.logger.info(f"Remote Access - Status Payload send! Message ID: {mid}")

                else:
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

                    if self.check_tun0_available():
                        remote = json.dumps(
                            {
                                "HardWareID": int(self.get_hw_id()),
                                "object": {
                                    "ParameterName": "Remote",
                                    "Value": "1111",
                                    "AlarmID": "8888"
                                }
                            }
                        )
                        result, mid = self.client.publish('iot-data3', payload=remote, qos=1, retain=True)
                        if result == mqtt.MQTT_ERR_SUCCESS:
                            self.logger.info(f"Remote Access - Status Payload send! Message ID: {mid}")
            #
            #     # device_info_obj = DeviceInformation()
            #     # device_info_obj.get_device_info()
            #     # dev_payload = device_info_obj.to_json()
            #
            #     if self.is_eth_interface_present():
            #         result, mid = self.client.publish("iot-data3", payload=payload, qos=1, retain=True)
            #         if result == mqtt.MQTT_ERR_SUCCESS:
            #             self.logger.info(f"Connection Payload send! Message ID: {mid}")
            #         else:
            #             self.logger.error(f"Error sending Connection Payload! MQTT Error Code: {result}")
            #

            #
            #         # result, mid = self.client.publish("dev-data", payload=dev_payload, qos=1, retain=True)
            #         # if result == mqtt.MQTT_ERR_SUCCESS:
            #         #     self.logger.info(f"Device_info Payload send! Message ID: {mid}")
            #         # else:
            #         #     self.logger.error(f"Error sending Device_info Payload! MQTT Error Code: {result}")
            #
            #         if self.check_tun0_available():
            #             remote = json.dumps(
            #                 {
            #                     "HardWareID": int(self.get_hw_id()),
            #                     "object": {
            #                         "ParameterName": "Remote",
            #                         "Value": "1111",
            #                         "AlarmID": "8888"
            #                     }
            #                 }
            #             )
            #             result, mid = self.client.publish('iot-data3', payload=remote, qos=1, retain=True)
            #             if result == mqtt.MQTT_ERR_SUCCESS:
            #                 self.logger.info(f"Remote Access - Status Payload send! Message ID: {mid}")
            #     else:
            #         result, mid = self.client.publish("iot-data3", payload=payload, qos=1, retain=True)
            #         if result == mqtt.MQTT_ERR_SUCCESS:
            #             self.logger.info(f"Connection Payload send! Message ID: {mid}")
            #         else:
            #             self.logger.error(f"Error sending Connection Payload! MQTT Error Code: {result}")
            #
            #         # result, mid = self.client.publish("iot-data3", payload=dev_payload, qos=1, retain=True)
            #         # if result == mqtt.MQTT_ERR_SUCCESS:
            #         #     self.logger.info(f"Device_info Payload send! Message ID: {mid}")
            #         # else:
            #         #     self.logger.error(f"Error sending Device_info Payload! MQTT Error Code: {result}")
            #
            #         if self.check_tun0_available():
            #             remote = json.dumps(
            #                 {
            #                     "HardWareID": int(self.get_hw_id()),
            #                     "object": {
            #                         "ParameterName": "Remote",
            #                         "Value": "1111",
            #                         "AlarmID": "8888"
            #                     }
            #                 }
            #             )
            #             result, mid = self.client.publish('iot-data3', payload=remote, qos=1, retain=True)
            #             if result == mqtt.MQTT_ERR_SUCCESS:
            #                 self.logger.info(f"Remote Access - Status Payload send! Message ID: {mid}")

    def is_service_running(self, service_name):
        try:
            result = subprocess.run(['systemctl', 'is-active', service_name], check=True, capture_output=True,
                                    text=True)
            return result.stdout.strip() == 'active'
        except subprocess.CalledProcessError:
            return False

    def process_remote_access(self, msg):
        m_decode = str(msg.payload.decode("UTF-8", "ignore"))
        data = json.loads(m_decode)
        hardware_id = int(data.get("HardWareID", 0))
        access = int(data.get("object", {}).get("Access", 0))
        self.logger.info(f"The From portal HW is: {hardware_id}")
        self.logger.info(f"The From Local HW is: {self.get_hw_id()}")
        if hardware_id == self.get_hw_id():
            self.logger.info(f"The From portal HW is: {access}")
            self.logger.info(f"The From Local HW is: {self.get_hw_id()}")
            self.logger.info(f"Session: {access}")
            if access == 0:
                self.logger.info(f"tun0 Status {self.check_tun0_available()}")
                if self.check_tun0_available():
                    result = subprocess.run('sudo systemctl stop openvpn_start', shell=True, check=True)
                    stop_command_executed_successfully = (result.returncode == 0)
                    time.sleep(5)
                    if stop_command_executed_successfully:
                        if not self.is_service_running('openvpn_start'):
                            self.logger.info("VPN Start Service is stopped, Waiting 5Sec for the tun0 to go.")
                            time.sleep(5)
                            if not self.check_tun0_available():
                                self.logger.info("tun0 removed so : Restarting Harp Services..")
                                result = subprocess.run('sudo systemctl restart harp', shell=True, check=True)
                                harp_restart_success = (result.returncode == 0)
                                if harp_restart_success:
                                    subprocess.run('sudo supervisorctl restart tuxtunnel', shell=True, check=True)
                                    self.logger.info("Harp Service restarted, exiting current process..")
                                    self.exit_gracefully()
                elif not self.check_tun0_available():
                    self.logger.info(f"No tun0 present, hence no need of any action.")
            elif access == 1:
                self.logger.info(f"tun0 Status {self.check_tun0_available()}")
                if not self.check_tun0_available():
                    self.logger.info(f"tun0 not present, Sending Payload and starting tunnel..")
                    remote = json.dumps(
                        {
                            "HardWareID": int(self.get_hw_id()),
                            "object": {
                                "ParameterName": "Remote",
                                "Value": "1111",
                                "AlarmID": "8888"
                            }
                        }
                    )
                    result, mid = self.client.publish('remote', payload=remote, qos=1, retain=True)
                    if result == mqtt.MQTT_ERR_SUCCESS:
                        self.logger.info(f"Remote Access - Status Payload send! Message ID: {mid}")
                        time.sleep(3)
                    try:
                        result = subprocess.run('sudo systemctl start openvpn_start', shell=True, check=True)
                        start_command_executed_successfully = (result.returncode == 0)
                        time.sleep(5)
                        if start_command_executed_successfully:
                            if self.is_service_running('openvpn_start'):
                                self.logger.info("VPN Start Service is running, Waiting 10Sec for the tun0 to come up.")
                                time.sleep(2)
                                if self.check_tun0_available():
                                    self.logger.info("tun0 available : Restarting Harp Services..")
                                    result = subprocess.run('sudo systemctl restart harp', shell=True, check=True)
                                    harp_restart_success = (result.returncode == 0)
                                    if harp_restart_success:
                                        subprocess.run('sudo supervisorctl restart tuxtunnel', shell=True, check=True)
                                        self.logger.info("Harp Service restarted, exiting current process..")
                                        self.exit_gracefully()
                    except subprocess.CalledProcessError as e:
                        self.logger.info(f"Error executing command: {e}")
            elif self.check_tun0_available():
                self.logger.info(f"Already tun0 opened, hence no need of any action.")
            else:
                self.logger.info(f"Problem during getting tun0 interface detail")
        else:
            self.logger.info("Access value not found in the JSON.")

    def check_tun0_available(self):
        interfaces = psutil.net_if_stats()
        if 'tun0' in interfaces:
            return True
        else:
            return False

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
        client.subscribe('ops')

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
            # process_web_hw_status(msg, self.c, self.logger)
            pass
        elif topic == "ops":
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
        if self.retry_count <= 5:
            self.logger.info(
                f"Retrying connection in {self.retry_interval} seconds "
                f"(Attempt {self.retry_count}/5)"
            )
            time.sleep(self.retry_interval)
            try:
                self.client.reconnect()
            except Exception as e:
                self.logger.error(f"Error during reconnection attempt: {e}")
                self.retry_connect()  # Retry again on failure
        else:
            self.logger.error("Maximum retries reached. Restarting the Modem and Device...")
            # serial_port = '/dev/ttyUSB2'
            # baud_rate = 115200
            # ser = serial.Serial(serial_port, baud_rate, timeout=1)
            try:
                # ser.write(b'AT+CPOF\r\n')
                # time.sleep(1)
                # response = ser.read_all().decode('utf-8')
                self.logger.info("Rebooting Device")
                # self.logger.info(response)

            finally:
                # ser.close()
                subprocess.run('sudo reboot', shell=True, check=True)
                self.exit_gracefully()


if __name__ == '__main__':
    logger, file_handler = log_config.setup_logger()
    mqtt_instance = MQTTClient(logger)
    try:
        while not mqtt_instance.should_exit:
            pass

    except KeyboardInterrupt:
        mqtt_instance.should_exit = True
        mqtt_instance.periodic_update_thread.join()
        logger.info("Exiting gracefully...")
        mqtt_instance.exit_gracefully()
