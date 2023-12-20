from pyModbusTCP.client import ModbusClient
from concurrent.futures import ThreadPoolExecutor, as_completed


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

        try:
            with ThreadPoolExecutor() as executor:
                futures = {executor.submit(self.read_single_address, client, address): address for address in addresses}
                for future in as_completed(futures):
                    address = futures[future]
                    try:
                        values = future.result()

                        if values is not None:
                            self.logger.info(f"Received Modbus response for address {address}: {values}")
                            result.append((address, values))
                        else:
                            self.logger.warning(f"Empty Modbus response for address {address}")

                    except Exception as e:
                        self.logger.warning(f"Error processing Modbus response for address {address}: {e}")

        except Exception as e:
            self.logger.error(f"Error during Modbus communication: {e}")

        finally:
            client.close()

        return result

    def read_single_address(self, client, address):
        data_type = int(self.data[f"object{self.extract_addresses().index(address)}"]["DataType"])
        if data_type in (1, 2):
            return client.read_holding_registers(address - 1, 1)
        elif data_type == 3:
            return client.read_holding_registers(address - 1, 2)
        else:
            self.logger.warning(f"Unsupported DataType for address {address}")
            return None

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
