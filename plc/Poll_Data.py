import json
from pyModbusTCP.client import ModbusClient
from pyModbusTCP.utils import word_list_to_long, decode_ieee

# Dictionary to map raw data types to human-readable equivalents
DATA_TYPE_MAP = {
    1: "integer",
    2: "boolean",
    3: "float"
}

def apply_mask(bits, mask_value):
    # Define a dictionary to map mask values to index
    mask_mapping = {
        256: 0,
        512: 1,
        1024: 2,
        2048: 3,
        4096: 4,
        8192: 5,
        16384: 6,
        32768: 7,
        1: 8,
        2: 9,
        4: 10,
        8: 11,
        16: 12,
        32: 13,
        64: 14,
        128: 15
    }

    # Check if mask_value exists in the mapping
    if mask_value not in mask_mapping:
        return None

    # Retrieve the index corresponding to the mask value
    index = mask_mapping[mask_value]

    # Return the value from the bits list at the specified index
    return bits[index]

def read_json_and_poll(json_file_path, modbus_host, modbus_port):
    # Read the JSON file
    with open(json_file_path, 'r') as file:
        data = json.load(file)


    polled_data = {}  # Initialize dictionary to store polled data

    # Connect to Modbus TCP server
    client = ModbusClient(host=modbus_host, port=modbus_port)
    client.open()

    # Poll data from Modbus
    for key, value in data.items():
        if key.startswith("object"):
            address = int(value["Address"]) - 1  # Subtract 1 from the address
            data_type = int(value["DataType"])
            description = value["Description"]
            mask_value = int(value.get("Mask"))
            parmater = value["ParameterName"]
            alarm_id = value["AlarmID"]


            # Example: Read holding register at address `address`
            result = client.read_holding_registers(address, 2 if data_type == 3 else 1)

            if result:
                if data_type == 3:
                    float_value = [decode_ieee(f) for f in word_list_to_long(result)]
                    polled_data[key] = {
                        "Description": "111",
                        "ParameterName": parmater,
                        "value": float_value[0],
                        "AlarmID": {alarm_id}

                    }
                elif data_type == 2:
                    # Extract individual bits from the result
                    bits = [bool(result[0] & (1 << i)) for i in range(16)]
                    masked_value = apply_mask(bits, mask_value)  # Apply mask
                    polled_data[key] = {
                        "Description": "111",
                        "ParameterName": parmater,
                        "value": masked_value,
                        "AlarmID": alarm_id
                    }
                else:
                    polled_data[key] = {
                        "Description": "111",
                        "ParameterName": parmater,
                        "value": result[0],
                        "AlarmID": alarm_id
                    }
            else:
                polled_data[key] = {
                    "Description": "111",
                    "ParameterName": parmater,
                    "value": "Error from PLC",
                    "AlarmID": alarm_id
                }

    client.close()

    # Convert polled_data dictionary to JSON format
    json_output = json.dumps(polled_data, indent=4)
    print(json_output)

if __name__ == "__main__":
    json_file_path = "../dummy_data/sample.json"
    modbus_host = "192.168.3.1"
    modbus_port = 502
    read_json_and_poll(json_file_path, modbus_host, modbus_port)
