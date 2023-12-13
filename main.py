from connectivity import con_status
# from connectivity.con_status import is_interface_connected
from log_helper import log_config

if __name__ == '__main__':
    logger, file_handler = log_config.setup_logger()
    usb_devices = [f"/dev/ttyUSB{i}" for i in range(1, 21)]
    amc_devices = [f"/dev/ttyAMC{i}" for i in range(1, 21)]
    gsm_device_type = con_status.find_gsm_device_type(usb_devices + amc_devices)
    logger.info(f'GSM Device attached to - {gsm_device_type}')
