import json
import os
import threading
import time

from connectivity.ModemManagerClass import ModemManager
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


def publish_payload_periodically(mqtt_ins, logg):
    hw_id = get_hw_id(logg)
    while not mqtt_ins.should_exit:
        payload = json.dumps({
            "HardWareID": hw_id,
            "object": {
                "ParameterName": "Connection",
                "Value": "1111",
                "AlarmID": "9999"
            }
        })
        mqtt_instance.client.publish('iot-data3', payload=payload, qos=1, retain=True)
        logger.info("Payload sent successfully.")
        time.sleep(10)


if __name__ == '__main__':
    logger, file_handler = log_config.setup_logger()
    internet_status = check_internet_connection()

    info_collector = SystemInfoCollector()
    info_collector.collect_info()
    json_data = info_collector.to_json()

    if internet_status:
        mqtt_instance = MQTTClient(logger)
        publish_thread = threading.Thread(target=publish_payload_periodically, args=(mqtt_instance, logger))
        publish_thread.start()

        try:
            while True:
                mqtt_instance.client.loop_forever()

        except KeyboardInterrupt:
            logger.info("Exiting gracefully...")

        finally:
            mqtt_instance.should_exit = True
            publish_thread.join()
            mqtt_instance.client.disconnect()
            mqtt_instance.client.loop_stop()

        # active_interface = get_active_network_interface()
        # if active_interface:
        #     logger.info(f"Active network interface: {active_interface}")
        #     if active_interface == 'usb0':
        #         modem_manager = ModemManager()
        #         logger.info("Modem Index:", modem_manager.modem_index)
        #         enable_result = modem_manager.enable_modem()
        #         logger.info("Enable Result:", enable_result)
        #         modem_info = modem_manager.get_modem_info()
        #         logger.info("Modem Information:")
        #         logger.info(json.dumps(modem_info, indent=2))
        #
        #         internet_status = modem_manager.get_internet_status()
        #         logger.info("Internet Status:")
        #         logger.info(json.dumps(internet_status, indent=2))
        #
        #         usb_device = ["/dev/ttyUSB2"]
        #         amc_device = ["/dev/ttyACM0"]
        #         check_usb = find_gsm_device_type(usb_device)
        #         check_amc = find_gsm_device_type(amc_device)
        #         if check_usb:
        #             logger.info(f'GSM Device attached to - {usb_device[0]}')
        #         elif check_amc:
        #             logger.info(f'GSM Device attached to - {amc_device[0]}')
        #         else:
        #             logger.info(f'No GSM Device Connected')
        # else:
        #     logger.info("No active network interface found.")
    elif not internet_status:
        logger.info(f'Not connected to Internet')
    else:
        logger.info(f'Internet status not known')
