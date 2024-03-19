import json
from pyModbusTCP.utils import word_list_to_long, decode_ieee


def apply_mask(bits, mask_value):
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
    return json_output


