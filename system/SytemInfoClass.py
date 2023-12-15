import json
import psutil
import platform
import subprocess


class SystemInfoCollector:
    def __init__(self):
        self.system_info = {}

    def get_os_info(self):
        self.system_info['OS'] = platform.system()

    def get_linux_kernel_version(self):
        if self.system_info['OS'] == 'Linux':
            uname_info = platform.uname()
            self.system_info['Linux Kernel Version'] = uname_info.release

    def get_storage_info(self):
        disk_usage = psutil.disk_usage('/')
        self.system_info['Storage'] = {
            'Used': disk_usage.used,
            'Free': disk_usage.free
        }

    def get_var_log_size(self):
        var_log_size = subprocess.check_output(['du', '-sh', '/var/log']).decode('utf-8').split()[0]
        self.system_info['/var/log Size'] = var_log_size

    def get_memory_info(self):
        virtual_memory = psutil.virtual_memory()
        self.system_info['Memory'] = {
            'Used': virtual_memory.used,
            'Free': virtual_memory.available
        }

    def check_process_status(self, process_name):
        try:
            result = subprocess.check_output(['pgrep', '-f', process_name]).decode('utf-8')
            process_id = result.strip()
            self.system_info[process_name] = {
                'Running': True,
                'Process ID': process_id
            }
        except subprocess.CalledProcessError:
            self.system_info[process_name] = {
                'Running': False,
                'Process ID': None
            }

    def get_network_info(self):
        network_info = psutil.net_if_stats()
        self.system_info['Network'] = {
            'Total Interfaces': len(network_info),
            'Ethernet Interface': [interface for interface, stats in network_info.items() if stats.isup and stats.isup],
        }

    def collect_info(self):
        self.get_os_info()
        self.get_linux_kernel_version()
        self.get_storage_info()
        self.get_var_log_size()
        self.get_memory_info()
        self.check_process_status('/harp/main.py')
        self.get_network_info()

    def to_json(self):
        return json.dumps(self.system_info, indent=2)
