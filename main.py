import json
import os
import threading
import time

from connectivity.con_status import check_internet_connection, get_active_network_interface
from log_helper import log_config
from mqtt_broker.MqttClass import MQTTClient
from system.SytemInfoClass import SystemInfoCollector


def get_hw_id(logg):
    try:
        with open('/home/pi/hardwareid.txt', 'r') as f:
            HwId = f.read()
        return HwId
    except FileNotFoundError:
        logg.error("File not found: /home/pi/hardwareid.txt")
        return None
    except Exception as e:
        logg.error(f"Error reading hardware id: {e}")
        return None


def find_gsm_device_type(device_paths):
    return any(os.path.exists(path) for path in device_paths)


if __name__ == '__main__':
    logger, file_handler = log_config.setup_logger()
    internet_status = check_internet_connection()

    info_collector = SystemInfoCollector()
    info_collector.collect_info()
    json_data = info_collector.to_json()

    mqtt_instance = MQTTClient(logger)
    mqtt_thread = threading.Thread(target=lambda: mqtt_instance.client.loop_forever())
    mqtt_thread.daemon = True

    if internet_status:
        mqtt_instance = MQTTClient(logger)

        try:
            mqtt_thread.start()

            while True:
                pass

        except KeyboardInterrupt:
            logger.info("Exiting gracefully...")

        finally:
            mqtt_instance.should_exit = True
            mqtt_instance.client.disconnect()
            mqtt_instance.client.loop_stop()
            mqtt_thread.join()

    elif not internet_status:
        logger.info(f'Not connected to Internet')
    else:
        logger.info(f'Internet status not known')

