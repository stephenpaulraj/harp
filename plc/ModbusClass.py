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
        with ModbusClient('192.168.3.1', 502) as client:
            result = []
            for address in addresses:
                response = client.read_input_registers(address - 1, 2)
                if response.isError():
                    self.logger.warning(f"Modbus read error for address {address}: {response}")
                else:
                    value = response.registers[0]  # Assuming the response is a 16-bit integer
                    result.append((address, value))
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
