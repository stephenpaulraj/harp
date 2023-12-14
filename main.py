import os
from sim_modem import Modem
from connectivity import con_status
from connectivity.con_status import check_internet_connection, get_active_network_interface
from gsm.cavili import is_valid_apn_configured
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
            if active_interface == 'usb0':
                usb_device = ["/dev/ttyUSB2"]
                amc_device = ["/dev/ttyACM0"]

                check_usb = find_gsm_device_type(usb_device)
                check_amc = find_gsm_device_type(amc_device)
                if check_usb:
                    logger.info(f'GSM Device attached to - {usb_device[0]}')
                elif check_amc:
                    dev = Modem('/dev/ttyACM0')
                    apn_res = is_valid_apn_configured(dev)
                    logger.info(f'GSM Device attached to - {amc_device[0]}')
                    logger.info(f'APN - {apn_res}')
                else:
                    logger.info(f'No GSM Device Connected')
        else:
            logger.info("No active network interface found.")
    elif not internet_status:
        logger.info(f'Not connected to Internet')
    else:
        logger.info(f'Internet status not known')