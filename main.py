import os

from connectivity import con_status
from connectivity.con_status import check_internet_connection, get_active_network_interface
from log_helper import log_config


def find_gsm_device_type(device_paths):
    return any(os.path.exists(path) for path in device_paths)


if __name__ == '__main__':
    logger, file_handler = log_config.setup_logger()

    internet_status = check_internet_connection()
    if internet_status:
        logger.info(f'Connected to Internet')
        active_interface = get_active_network_interface()
        if active_interface:
            logger.info(f"Active network interface: {active_interface}")
        else:
            logger.info("No active network interface found.")
    elif not internet_status:
        logger.info(f'Not connected to Internet')
    else:
        logger.info(f'Internet status not known')



    usb_device = ["/dev/ttyUSB2"]
    amc_device = ["/dev/ttyACM0"]

    check_usb = find_gsm_device_type(usb_device)
    check_amc = find_gsm_device_type(amc_device)

    if check_usb:
        logger.info(f'GSM Device attached to - {usb_device[0]}')
    elif check_amc:
        logger.info(f'GSM Device attached to - {amc_device[0]}')
    else:
        logger.info(f'No GSM Device Connected')

    # interface_connected = con_status.find_internet_source()
    # logger.info(f'Source of Internet is: {interface_connected}')

    # gsm_device_type = con_status.find_gsm_device_type(usb_devices + amc_devices)
