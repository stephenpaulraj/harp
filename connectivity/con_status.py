import netifaces
from gsm import cavili, sim_com


def get_default_gateway_interface():
    gateways = netifaces.gateways()
    for gateway_info in gateways.get(netifaces.AF_INET, []):
        if gateway_info[1] is not None:
            return gateway_info[1]


def is_interface_connected(interface_name):
    try:
        addresses = netifaces.ifaddresses(interface_name)
        return netifaces.AF_INET in addresses
    except ValueError:
        return False


def connect_gsm(dev_type):
    print("Connecting to GSM...")
    if dev_type == 'sim_com':
        sim_com.connect_sim_com()
    elif dev_type == 'cavili':
        cavili.connect_caili_com()


def main(dev_type):
    eth_interface = "eth0"
    gsm_interface = "usb0"

    while True:
        is_eth_connected = is_interface_connected(eth_interface)

        if is_eth_connected:
            # what interfcae
            # system up time
            # network up time
            # memory
            # Storage
            # local ip
            # public ip
            # dataplicty is active or not
            # pushed to a topic (create an topic)
            print(f"{eth_interface} is connected. Internet access via {eth_interface}.")
        else:
            print(f"{eth_interface} is not available. Switching to GSM...")
            connect_gsm(dev_type)

        if not is_eth_connected:
            is_gsm_connected = is_interface_connected(gsm_interface)
            if is_gsm_connected:
                # what interfcae
                # system up time
                # network up time
                # memory
                # Storage
                # local ip
                # public ip
                # dataplicty is active or not
                # pushed to a topic (create an topic)
                # apn
                # Mobile No
                # reboot the machine
                # gsm modem staus (R
                # SignalQuality
                print(f"{gsm_interface} is connected. Internet access via {gsm_interface}.")
            else:
                # sms.py (apn,
                pass
