import os
from log_helper import log_config


def find_gsm_device_type(device_paths):
    return any(os.path.exists(path) for path in device_paths)


if __name__ == '__main__':
    logger, file_handler = log_config.setup_logger()
    usb_device = "/dev/ttyUSB2"
    amc_device = "/dev/ttyAMC0"

    check_usb = find_gsm_device_type(usb_device)
    check_amc = find_gsm_device_type(amc_device)

    if check_usb:
        logger.info(f'GSM Device attached to - {usb_device}')
    elif check_amc:
        logger.info(f'GSM Device attached to - {amc_device}')
    else:
        logger.info(f'No GSM Device Connected')
    # gsm_device_type = con_status.find_gsm_device_type(usb_devices + amc_devices)
