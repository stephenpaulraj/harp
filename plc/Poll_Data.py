def read_json_and_poll(json_file_path, modbus_host, modbus_port):
    # Read the JSON file
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    addresses = []
    data_types = []
    descriptions = []
    for key, value in data.items():
        if key.startswith("object"):
            address = int(value["Address"]) - 1  # Subtract 1 from the address
            addresses.append(address)  # Extract Modbus addresses
            data_types.append(int(value["DataType"]))  # Extract data types
            descriptions.append(value["Description"])  # Extract descriptions

    # Connect to Modbus TCP server
    client = ModbusClient(host=modbus_host, port=modbus_port)
    client.open()

    # Create a dictionary to store polled data
    polled_data = {}

    # Poll data from Modbus
    for address, data_type, description in zip(addresses, data_types, descriptions):
        # Poll data only if not already polled for boolean data types (DataType == 2)
        if data_type != 2 or address not in polled_data:
            # Example: Read holding register at address `address`
            result = client.read_holding_registers(address, 2 if data_type == 3 else 1)
            if result:
                if data_type == 3:
                    float_value = [decode_ieee(f) for f in word_list_to_long(result)]
                    print(f"Data from address {address + 1} ({description}) - DataType: {DATA_TYPE_MAP[data_type]}: {float_value}")
                    polled_data[address] = float_value
                elif data_type == 2:
                    # Extract individual bits from the result
                    bits = [bool(result[0] & (1 << i)) for i in range(16)]
                    print(f"Data from address {address + 1} ({description}) - DataType: {DATA_TYPE_MAP[data_type]}: {bits}")
                    polled_data[address] = bits
                else:
                    print(f"Data from address {address + 1} ({description}) - DataType: {DATA_TYPE_MAP[data_type]}: {result[0]}")
                    polled_data[address] = result[0]
            else:
                print(f"Error reading data from address {address + 1} ({description})")
        else:
            # Use previously polled data for boolean data types
            print(f"Using previously polled data from address {address + 1} ({description})")

    client.close()


if __name__ == "__main__":
    json_file_path = "../dummy_data/sample.json"
    modbus_host = "192.168.3.1"
    modbus_port = 502
    read_json_and_poll(json_file_path, modbus_host, modbus_port)
