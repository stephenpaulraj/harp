import json
import subprocess

from helpers.serial_hw_helper import get_hw_id


def process_operation(logger, msg):
    try:
        m_decode = str(msg.payload.decode("UTF-8", "ignore"))
        data = json.loads(m_decode)
        hw_id = int(data.get("hw_id"))
        operation = data.get("operation")

        if hw_id == get_hw_id(logger):
            if operation == 'reboot':
                logger.info(f"Executing {operation}")
                execute_command(logger, "sudo reboot")
            elif operation == 'net_restart':
                logger.info(f"Executing {operation}")
                execute_command(logger, "sudo systemctl restart networking")
            elif operation == 'dataplicity_restart':
                logger.info(f"Executing {operation}")
                execute_command(logger, "sudo supervisorctl restart tuxtunnel")
            elif operation == 'harp_restart':
                logger.info(f"Executing {operation}")
                execute_command(logger, "sudo systemctl restart harp")
            elif operation == 'enable_gsm':
                logger.info(f"Executing {operation}")
                execute_command(logger, "sudo mmcli -m 0 -e")

    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON: {e}")


def execute_command(logger, command):
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing command: {e}")