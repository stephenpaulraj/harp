import netifaces
import requests
import subprocess
from gsm import cavili, sim_com
import os
from log_helper import log_config
import psutil
from pyroute2 import IPDB
import socket


def check_internet_connection():
    try:
        response = requests.get("http://www.google.com", timeout=5)
        return response.status_code == 200
    except requests.ConnectionError:
        return False


def get_active_network_interface():
    interfaces = psutil.net_if_stats()
    active_interface = None

    for interface, stats in interfaces.items():
        if stats.isup and stats.speed > 0:
            active_interface = interface
            break

    return active_interface


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


def check_tun_status():
    command = "cat /sys/class/net/tun0/operstate"
    output = subprocess.check_output(command, shell=True)
    output = (output.decode('ascii'))


def connect_gsm():
    usb_devices = [f"/dev/ttyUSB{i}" for i in range(1, 21)]
    amc_devices = [f"/dev/ttyAMC{i}" for i in range(1, 21)]
    connected_device_type = find_gsm_device_type(usb_devices + amc_devices)

    if connected_device_type == 'simcom':
        pass
        # sim_com.connect_sim_com()
    elif connected_device_type == 'cavili':
        pass
        # cavili.connect_caili_com()
    elif connected_device_type == 'Unknown':
        pass


def main():
    eth_interface = "eth0"
    gsm_interface = "usb0"
    eth_local_interface = "eth1"

    while True:
        if psutil.net_if_stats():
            internet_source = find_internet_source()

            if internet_source == eth_interface:
                pass
            elif internet_source == gsm_interface:
                pass
                if not is_interface_connected(gsm_interface):
                    connect_gsm()
            else:
                pass

        else:
            pass
