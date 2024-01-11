import json
import os


def check_sample_json(logger):
    json_file_path = 'dummy_data/sample.json'
    try:
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as json_file:
                data = json.load(json_file)

                if "HardwareID" not in data:
                    logger.error(f"'{json_file_path}' does not have the 'HardwareID' object.")
                    return False

                object_count = sum(1 for key in data.keys() if key.startswith("object"))
                if object_count < 2:
                    logger.error(f"'{json_file_path}' does not have at least two objects.")
                    return False
                return True
        else:
            logger.error(f"'{json_file_path}' not found.")
            return False
    except Exception as e:
        logger.error(f"Error checking '{json_file_path}': {e}")
        return False


def process_web_alarms(logger, msg):
    m_decode = str(msg.payload.decode("UTF-8", "ignore"))
    data = json.loads(m_decode)

    if int(data.get("HardwareID")) == get_hw_id(logger):
        with open("dummy_data/sample.json", "w") as outfile:
            json.dump(data, outfile)


def get_serial_id(logger):
    try:
        with open('/home/pi/serialid.txt', 'r') as f:
            SerialNumber = f.read()
        return SerialNumber
    except FileNotFoundError:
        logger.error("File not found: /home/pi/serialid.txt")
        return None
    except Exception as e:
        logger.error(f"Error reading serial id: {e}")
        return None


def get_hw_id(logger):
    try:
        with open('/home/pi/hardwareid.txt', 'r') as f:
            HwId = f.read()
        return int(HwId)
    except FileNotFoundError:
        logger.error("File not found: /home/pi/hardwareid.txt")
        return None
    except Exception as e:
        logger.error(f"Error reading hardware id: {e}")
        return None


def find_hardware_id(logger, json_data, serial_number):
    try:
        if isinstance(json_data, bytes):
            json_data = json_data.decode('utf-8')

        data = json.loads(json_data)

        for obj_name, obj_data in data.items():
            if int(obj_data["SerialNumber"]) == int(serial_number):
                logger.info(f"SerialNo Match: True")
                return obj_data["HardwareID"]

    except json.JSONDecodeError as e:
        logger.info(f"Error decoding JSON: {e}")
        return None


def process_hardware_list(logger, msg):
    serial_id = get_serial_id(logger)
    m_decode = str(msg.payload.decode("UTF-8", "ignore"))
    hw_id = find_hardware_id(logger, m_decode, str(serial_id))

    logger.info(f"Serial Id : {serial_id}")
    logger.info(f"Hardware Id : {hw_id}")
    f = open('/home/pi/hardwareid.txt', 'w')
    f.write(str(hw_id))
    f.close()
