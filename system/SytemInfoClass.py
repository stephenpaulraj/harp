import subprocess
import json

class DeviceInformation:
    def __init__(self):
        self.device_info = {
            "device_info": {
                "License_info": {},
                "Hardware_info": {
                    "CPU": {}
                },

            }
        }

    def get_cpu_info(self):
        try:
            # Retrieve information from /proc/cpuinfo
            cpu_info = subprocess.check_output("cat /proc/cpuinfo", shell=True, text=True)
            hardware = self.extract_cpu_info(cpu_info, "Hardware")
            revision = self.extract_cpu_info(cpu_info, "Revision")
            serial = self.extract_cpu_info(cpu_info, "Serial")
            model = self.extract_cpu_info(cpu_info, "Model")

            # Retrieve information from lscpu
            lscpu_info = subprocess.check_output("lscpu", shell=True, text=True)
            architecture = self.extract_lscpu_info(lscpu_info, "Architecture")
            cpus = self.extract_lscpu_info(lscpu_info, "CPU(s)")
            model_name = self.extract_lscpu_info(lscpu_info, "Model name")

            # Populate the device_info dictionary
            self.device_info["Hardware_id"]["CPU"] = {
                "Hardware": hardware,
                "Revision": revision,
                "Serial": serial,
                "Model": model,
                "Architecture": architecture,
                "CPUs": cpus,
                "ModelName": model_name
            }

        except subprocess.CalledProcessError:
            print("Error retrieving CPU information.")

    def extract_cpu_info(self, cpu_info, key):
        lines = cpu_info.splitlines()
        for line in lines:
            if key in line:
                return line.split(":")[1].strip()
        return "Not available"

    def extract_lscpu_info(self, lscpu_info, key):
        lines = lscpu_info.splitlines()
        for line in lines:
            if key in line:
                return line.split(":")[1].strip()
        return "Not available"

    def get_device_info(self):
        self.get_cpu_info()

    def to_json(self):
        return json.dumps(self.device_info, indent=4)

# Example usage
if __name__ == "__main__":
    device_info_obj = DeviceInformation()
    device_info_obj.get_device_info()
    print(device_info_obj.to_json())
