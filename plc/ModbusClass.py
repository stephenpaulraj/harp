
class ModbusClientClass:
    def __init__(self, logger, data):
        self.logger = logger
        self.data = data

    def process_data(self):
        self.logger.info("Processing Modbus data...")
        hardware_id = self.data.get("HardwareID")
        if hardware_id is not None:
            self.logger.info(f"HardwareID: {hardware_id}")
        else:
            self.logger.warning("HardwareID not found in data.")