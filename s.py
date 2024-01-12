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

VPN_SCRIPT_START = "/home/pi/rmoteStart.sh"
VPN_SCRIPT_STOP = "/home/pi/rmoteStop.sh"
CHECK_VPN_INTERVAL = 30  # seconds


def check_vpn():
    return os.system("ifconfig tun0") == 0


def restart_vpn():
    os.popen(VPN_SCRIPT_STOP)
    print("Remote Access (VPN) Stopped")

    for _ in range(CHECK_VPN_INTERVAL):
        if not check_vpn():
            os.popen(VPN_SCRIPT_START)
            print("Remote Access (VPN) Started")
            break
        time.sleep(1)


def on_message(client, userdata, msg):
    topic = msg.topic
    if topic == "remote-access":
        print('Handling remote-access message')
        m_decode = str(msg.payload.decode("UTF-8", "ignore"))
        data = json.loads(m_decode)
        access = int(data.get("object", {}).get("Access", 0))
        if access == 0:
            restart_vpn()
        elif access == 1:
            os.popen(VPN_SCRIPT_START)
            print("Remote Access (VPN) Started")
            payload = json.dumps(
                {
                    "HardWareID": 34,
                    "object": {
                        "ParameterName": "Remote",
                        "Value": "1111",
                        "AlarmID": "8888"
                    }
                }
            )
            client.publish('iot-data3', payload=payload, qos=1, retain=True)


def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe('web-Alarms')
    client.subscribe('remote-access')
    client.subscribe('web-hardwarestatus')


def on_publish(client, userdata, mid):
    print(f"Data published with message id: {mid}")


def publish_data(client):
    payload = json.dumps({
        "HardWareID": 34,
        "object": {
            "ParameterName": "Connection",
            "Value": "1111",
            "AlarmID": "9999"
        }
    })
    client.publish('iot', payload)


client = mqtt.Client(str(uuid.uuid1()))
client.username_pw_set(user, password=password)

client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish
client.tls_set_context(context=context)


def establish_mqtt_connection():
    if not check_vpn():
        restart_vpn()

    client.connect(broker_address, port=port, keepalive=1000)
    client.loop_start()


try:
    while True:
        establish_mqtt_connection()
        publish_data(client)
        time.sleep(1)

        # Additional sleep to avoid aggressive reconnection attempts
        time.sleep(10)

except KeyboardInterrupt:
    print("Interrupted. Disconnecting...")
    client.disconnect()
