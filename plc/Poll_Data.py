import json
import time

from pyModbusTCP.utils import word_list_to_long, decode_ieee
from pyModbusTCP.client import ModbusClient

def apply_mask(bits, mask_value):
    mask_mapping = {
        256: 8,
        512: 9,
        1024: 10,
        2048: 11,
        4096: 12,
        8192: 13,
        16384: 14,
        32768: 15,
        1: 0,
        2: 1,
        4: 2,
        8: 3,
        16: 4,
        32: 5,
        64: 6,
        128: 7
    }

    if mask_value not in mask_mapping:
        return None

    index = mask_mapping[mask_value]

    return int(bits[index])


def read_json_and_poll(c):
    json_file_path = "dummy_data/sample.json"
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    hardware_id = data.get("HardwareID")
    polled_data = {}

    for key, value in data.items():
        if key.startswith("object"):
            address = int(value["Address"]) - 1
            data_type = int(value["DataType"])
            mask_value = int(value.get("Mask"))
            parameter = value["ParameterName"]
            alarm_id = value["AlarmID"]

            result = c.read_holding_registers(address, 2 if data_type == 3 else 1)

            if result:
                if data_type == 3:
                    float_value = [decode_ieee(f) for f in word_list_to_long(result)]
                    polled_data[key] = {
                        "Description": "111",
                        "ParameterName": parameter,
                        "value": str(float_value[0]),
                        "AlarmID": alarm_id
                    }
                elif data_type == 2:
                    bits = [bool(result[0] & (1 << i)) for i in range(16)]
                    print(f'Address : {address}, Parameter : {parameter}, Actual Value : {bits}')
                    masked_value = apply_mask(bits, mask_value)
                    polled_data[key] = {
                        "Description": "111",
                        "ParameterName": parameter,
                        "value": str(masked_value),
                        "AlarmID": alarm_id
                    }
                else:
                    polled_data[key] = {
                        "Description": "111",
                        "ParameterName": parameter,
                        "value": str(result[0]),
                        "AlarmID": alarm_id
                    }
            else:
                polled_data[key] = {
                    "Description": "111",
                    "ParameterName": parameter,
                    "value": "Error from PLC",
                    "AlarmID": alarm_id
                }

    output_json = {"HardwareID": hardware_id, **polled_data}
    json_output = json.dumps(output_json, indent=4)
    print(f'{json_output}')
    return json_output



