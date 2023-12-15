import json
import os

from connectivity.ModemManagerClass import ModemManager
from connectivity.con_status import check_internet_connection, get_active_network_interface
from log_helper import log_config
from mqtt_broker.MqttClass import MQTTClient


def find_gsm_device_type(device_paths):
    return any(os.path.exists(path) for path in device_paths)


if __name__ == '__main__':
    logger, file_handler = log_config.setup_logger()
    internet_status = check_internet_connection()
    if internet_status:
        mqtt_instance = MQTTClient()
        logger.info(f'Connected to Internet {mqtt_instance}')
        active_interface = get_active_network_interface()
        if active_interface:
            logger.info(f"Active network interface: {active_interface}")
            if active_interface == 'usb0':
                modem_manager = ModemManager()
                logger.info("Modem Index:", modem_manager.modem_index)
                enable_result = modem_manager.enable_modem()
                logger.info("Enable Result:", enable_result)
                modem_info = modem_manager.get_modem_info()
                logger.info("Modem Information:")
                logger.info(json.dumps(modem_info, indent=2))

                internet_status = modem_manager.get_internet_status()
                logger.info("Internet Status:")
                logger.info(json.dumps(internet_status, indent=2))

                usb_device = ["/dev/ttyUSB2"]
                amc_device = ["/dev/ttyACM0"]
                check_usb = find_gsm_device_type(usb_device)
                check_amc = find_gsm_device_type(amc_device)
                if check_usb:
                    logger.info(f'GSM Device attached to - {usb_device[0]}')
                elif check_amc:
                    logger.info(f'GSM Device attached to - {amc_device[0]}')
                else:
                    logger.info(f'No GSM Device Connected')
        else:
            logger.info("No active network interface found.")
    elif not internet_status:
        logger.info(f'Not connected to Internet')
    else:
        logger.info(f'Internet status not known')
