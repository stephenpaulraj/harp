from pyModbusTCP.client import ModbusClient
from pyModbusTCP.utils import word_list_to_long, decode_ieee
import json


def read_json_and_poll(json_file_path, modbus_host, modbus_port):
    # Read the JSON file
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    addresses = []
    data_types = []
    for key, value in data.items():
        if key.startswith("object"):
            addresses.append(int(value["Address"]))  # Extract Modbus addresses
            data_types.append(int(value["DataType"]))  # Extract data types

    # Connect to Modbus TCP server
    client = ModbusClient(host=modbus_host, port=modbus_port)
    client.open()

    # Poll data from Modbus
    for address, data_type in zip(addresses, data_types):
        # Example: Read holding register at address `address`
        result = client.read_holding_registers(address, 2 if data_type == 3 else 1)
        if result:
            if data_type == 3:
                float_value = [decode_ieee(f) for f in word_list_to_long(result)]
                print(f"Data from address {address}: {float_value}")
            else:
                print(f"Data from address {address}: {result[0]}")
        else:
            print(f"Error reading data from address {address}")

    client.close()


if __name__ == "__main__":
    json_file_path = "../dummy_data/sample.json"
    modbus_host = "192.168.3.1"
    modbus_port = 502
    read_json_and_poll(json_file_path, modbus_host, modbus_port)
