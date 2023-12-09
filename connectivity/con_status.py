import netifaces


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


def connect_gsm():
    # GSM init
    print("Connecting to GSM...")


def main():
    eth_interface = "eth1"
    gsm_interface = "usb1"

    while True:
        is_eth_connected = is_interface_connected(eth_interface)

        if is_eth_connected:
            print(f"{eth_interface} is connected. Internet access via {eth_interface}.")
        else:
            print(f"{eth_interface} is not available. Switching to GSM...")
            connect_gsm()

        if not is_eth_connected:
            is_gsm_connected = is_interface_connected(gsm_interface)
            if is_gsm_connected:
                print(f"{gsm_interface} is connected. Internet access via {gsm_interface}.")


if __name__ == "__main__":
    main()
