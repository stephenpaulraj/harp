import netifaces
from gsm import cavili, sim_com
import os
from log_helper import log_config
import psutil

logger, file_handler = log_config.setup_logger()


def find_gsm_device_type(device_paths):
    for path in device_paths:
        if os.path.exists(path):
            if path == "/dev/ttyUSB2":
                return "simcom"
            elif path == "/dev/ttyAMC0":
                return "cavili"
    return "Unknown"


def is_interface_connected(interface_name):
    interfaces = psutil.net_if_stats()
    return interface_name in interfaces and interfaces[interface_name].isup


def find_internet_source():
    if is_interface_connected("eth0"):
        return "eth0"
    elif is_interface_connected("usb0"):
        return "usb0"
    else:
        return None


def connect_gsm():
    usb_devices = [f"/dev/ttyUSB{i}" for i in range(1, 21)]
    amc_devices = [f"/dev/ttyAMC{i}" for i in range(1, 21)]
    connected_device_type = find_gsm_device_type(usb_devices + amc_devices)

    if connected_device_type == 'simcom':
        logger.info(f'SIMCOM device found')
        # sim_com.connect_sim_com()
    elif connected_device_type == 'cavili':
        logger.info(f'CAVILI device found')
        # cavili.connect_caili_com()
    elif connected_device_type == 'Unknown':
        logger.error(f"No GSM harware found")


def main():
    eth_interface = "eth0"
    gsm_interface = "usb0"
    eth_local_interface = "eth1"

    while True:
        if psutil.net_if_stats():
            internet_source = find_internet_source()

            if internet_source == eth_interface:
                logger.info("Using WAN (eth0) for internet")
            elif internet_source == gsm_interface:
                logger.info("Using GSM (usb0) for internet")
                if not is_interface_connected(gsm_interface):
                    connect_gsm()
            else:
                logger.info("No internet source found")

        else:
            logger.info("No internet connection available")
