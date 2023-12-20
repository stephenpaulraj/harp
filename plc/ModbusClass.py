from pyModbusTCP.client import ModbusClient

class ModbusClientClass:
    def __init__(self, logger, data):
        self.logger = logger
        self.data = data

    def extract_addresses(self):
        addresses = []
        for key, value in self.data.items():
            if key.startswith("object") and "Address" in value:
                addresses.append(int(value["Address"]))
        return addresses

    def read_modbus_data(self, addresses):
        client = ModbusClient(host='192.168.3.1', port=502, auto_open=True)
        result = []
        for address in addresses:
            try:
                data_type = int(self.data[f"object{addresses.index(address)}"]["DataType"])
                if data_type in (1, 2):
                    values = client.read_holding_registers(address - 1, 1)
                elif data_type == 3:
                    values = client.read_holding_registers(address - 1, 2)
                else:
                    self.logger.warning(f"Unsupported DataType for address {address}")
                    continue

                if values:
                    result.append((address, values[0] if data_type in (1, 2) else values))
                else:
                    self.logger.warning(f"Empty Modbus response for address {address}")
            except Exception as e:
                self.logger.warning(f"Modbus read error for address {address}: {e}")
        return result


    def process_data(self):
        self.logger.info("Processing Modbus data...")

        # Step 1: Extract addresses
        addresses = self.extract_addresses()
        self.logger.info(f"Extracted addresses: {addresses}")

        # Step 2: Read Modbus data
        modbus_data = self.read_modbus_data(addresses)
        self.logger.info(f"Read Modbus data: {modbus_data}")

        # Step 3: Update the original data
        for address, value in modbus_data:
            key = f"object{addresses.index(address)}"
            self.data[key]["Value"] = value

        self.logger.info("Updated data with Modbus values.")
