from pyModbusTCP.client import ModbusClient
import json


def read_json_and_poll(json_file_path, modbus_host, modbus_port):
    # Read the JSON file
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    addresses = []
    for key, value in data.items():
        if key.startswith("object"):
            addresses.append(int(value["Address"]))  # Extract Modbus addresses

    # Connect to Modbus TCP server
    client = ModbusClient(host=modbus_host, port=modbus_port)
    client.open()

    # Poll data from Modbus
    for address in addresses:
        # Example: Read holding register at address `address`
        result = client.read_holding_registers(address, 2)
        if result:
            print(f"Data from address {address}: {result}")
        else:
            print(f"Error reading data from address {address}")

    client.close()


if __name__ == "__main__":
    json_file_path = "dummy_data/sample.json"
    modbus_host = "192.168.3.1"
    modbus_port = 502
    read_json_and_poll(json_file_path, modbus_host, modbus_port)
