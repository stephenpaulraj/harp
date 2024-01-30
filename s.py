# import os
# import paho.mqtt.client as mqtt
# import uuid
# import ssl
# import json
# import time
#
# broker_address = "b-4d9d7a54-2795-4ab2-b1e7-c40ddf1113f7-1.mq.us-east-1.amazonaws.com"
# port = 8883
# user = "ehashmq1"
# password = "eHash@12mqtt34!"
#
# context = ssl.create_default_context()
# context.load_verify_locations(cafile="AmazonRootCA1.pem")
#
#
# def on_message(client, userdata, msg):
#     topic = msg.topic
#     print(msg)
#     print(topic)
#
#
# def on_connect(client, userdata, flags, rc):
#     print(f"Connected with result code {rc}")
#     client.subscribe('web-Alarms')
#     client.subscribe('remote-access')
#     client.subscribe('web-hardwarestatus')
#
#
# def on_publish(client, userdata, mid):
#     print(f"Data published with message id: {mid}")
#
#
# def publish_data(client):
#     payload = json.dumps({
#         "HardWareID": 34,
#         "object": {
#             "ParameterName": "Connection",
#             "Value": "1111",
#             "AlarmID": "9999"
#         }
#     })
#     client.publish('iot', payload)
#
#
# client = mqtt.Client(str(uuid.uuid1()))
# client.username_pw_set(user, password=password)
# client.on_connect = on_connect
# client.on_message = on_message
# client.on_publish = on_publish
# client.tls_set_context(context=context)
#
# try:
#     client.connect(broker_address, port=port, keepalive=1000)
#     client.loop_start()
#
#     while True:
#         publish_data(client)
#         time.sleep(1)
#
# except KeyboardInterrupt:
#     print("Interrupted. Disconnecting...")
#     client.disconnect()
import subprocess
import time

import psutil


def check_tun0_available():
    try:
        interfaces = psutil.net_if_stats()
        s = 'tun0' in interfaces and interfaces['tun0'].isup
        print(s)
        return s
    except Exception as e:
        print(f"Error checking tun0 availability: {e}")
        return False


def is_service_running(service_name):
    try:
        result = subprocess.run(['systemctl', 'is-active', service_name], check=True, capture_output=True, text=True)
        return result.stdout.strip() == 'active'
    except subprocess.CalledProcessError:
        return False


def start_vpn():
    result = subprocess.run('sudo systemctl start openvpn_start', shell=True, check=True)
    start_command_executed_successfully = (result.returncode == 0)
    time.sleep(5)
    if start_command_executed_successfully:
        if is_service_running('openvpn_start'):
            print("VPN Start Service is running, Waiting 10Sec for the tun0 to come up.")
            time.sleep(10)
            print(check_tun0_available())


def stop_vpn():
    result = subprocess.run('sudo systemctl stop openvpn_start', shell=True, check=True)
    start_command_executed_successfully = (result.returncode == 0)
    time.sleep(5)
    if start_command_executed_successfully:
        if not is_service_running('openvpn_start'):
            print("VPN stopped, Waiting 10Sec for the tun0 to come up.")
            time.sleep(10)
            print(check_tun0_available())


start_vpn()
#stop_vpn()
