import subprocess
import json


class ModemManager:
    def __init__(self):
        self.modem_index = self.get_modem_index()

    def run_mmcli_command(self, args):
        try:
            result = subprocess.run(["mmcli"] + args, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return f"Error: {e.stderr}"

    def get_modem_index(self):
        output = self.run_mmcli_command(["-L"])
        lines = output.split('\n')
        if len(lines) > 1:
            # Assuming the first line contains the modem index
            return int(lines[1].split()[0])
        return None

    def enable_modem(self):
        if self.modem_index is not None:
            return self.run_mmcli_command(["-m", str(self.modem_index), "--enable"])
        else:
            return "Error: Modem not found"

    def get_modem_info(self):
        if self.modem_index is not None:
            output = self.run_mmcli_command(["-m", str(self.modem_index)])
            return json.loads(output)
        else:
            return {"error": "Modem not found"}

    def get_internet_status(self):
        if self.modem_index is not None:
            output = self.run_mmcli_command(["-m", str(self.modem_index)])
            modem_info = json.loads(output)
            return {"internet_status": modem_info.get("Status", {}).get("state", "Unknown")}
        else:
            return {"error": "Modem not found"}
