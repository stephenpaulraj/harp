import paho.mqtt.client as mqtt
import uuid
import ssl
import json
import time

from helpers.operation_helpers import process_operation
from helpers.remote_helper import process_remote_access
from helpers.serial_hw_helper import process_hardware_list, process_web_alarms, get_hw_id
from log_helper import log_config

logger, file_handler = log_config.setup_logger()
SLEEP_INTERVAL = 1

BROKER_ADDRESS = "b-4d9d7a54-2795-4ab2-b1e7-c40ddf1113f7-1.mq.us-east-1.amazonaws.com"
PORT = 8883
USER = "ehashmq1"
PASSWORD = "eHash@12mqtt34!"

context = ssl.create_default_context()
context.load_verify_locations(cafile="AmazonRootCA1.pem")


def on_message(client, userdata, msg):
    topic = msg.topic
    logger.info(f"Received message on topic {topic}")
    if topic == "hardwarelist":
        process_hardware_list(logger, msg)
    elif topic == "web-Alarms":
        process_web_alarms(logger, msg)
    elif topic == "remote-access":
        process_remote_access(logger, client, msg)
    elif topic == "operation":
        process_operation(logger, msg)


def on_connect(client, userdata, flags, rc):
    logger.info(f"Connected with result code {rc}")
    client.subscribe('web-Alarms')
    client.subscribe('web-hardwarestatus')


def on_publish(client, userdata, mid):
    logger.info(f"Data published with message id: {mid}")


def publish_data(client):
    payload = json.dumps(
        {
            "HardWareID": get_hw_id(logger),
            "object": {
                "ParameterName": "Connection",
                "Value": "1111",
                "AlarmID": "9999"
            }
        }
    )
    result, mid = client.publish("iot-data3", payload=payload, qos=1, retain=True)
    if result == mqtt.MQTT_ERR_SUCCESS:
        logger.info(f"Connection Payload send! Message ID: {mid}")
    else:
        logger.error(f"Error sending Connection Payload! MQTT Error Code: {result}")


def main():
    client = mqtt.Client(str(uuid.uuid1()))
    client.username_pw_set(USER, password=PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_publish = on_publish
    client.tls_set_context(context=context)

    try:
        client.connect(BROKER_ADDRESS, port=PORT, keepalive=1000)
        client.loop_start()

        while True:
            publish_data(client)
            time.sleep(SLEEP_INTERVAL)

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        logger.info("Disconnecting...")
        client.disconnect()


if __name__ == '__main__':
    main()
