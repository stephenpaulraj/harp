import netifaces
import subprocess
import time

def get_default_gateway_interface():
    gateways = netifaces.gateways()
    for gateway_info in gateways.get(netifaces.AF_INET, []):
        if gateway_info[1] is not None:
            return gateway_info[1]

def is_wan_connected(interface_name):
    try:
        addresses = netifaces.ifaddresses(interface_name)
        return netifaces.AF_INET in addresses
    except ValueError:
        return False

def connect_gsm():
    # Add your code to connect to GSM module here
    print("Connecting to GSM...")

def main():
    while True:
        default_interface = get_default_gateway_interface()

        if default_interface:
            print(f"Internet access via {default_interface}.")
            if is_wan_connected(default_interface):
                print(f"{default_interface} is connected. No problem.")
            else:
                print(f"{default_interface} is not available. Connecting to GSM...")
                connect_gsm()
        else:
            print("No default gateway found. Internet access may be unavailable.")

        time.sleep(60)  # Adjust the sleep duration based on your needs

if __name__ == "__main__":
    main()
