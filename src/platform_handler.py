import os
import subprocess
import sys
import socket
import time
from typing import Optional, Tuple

class PlatformHandler:
    def __init__(self):
        self.platform = sys.platform

    def check_privileges(self) -> bool:
        if self.platform.startswith('win'):
            try:
                return subprocess.run(['net', 'session'], capture_output=True).returncode == 0
            except:
                return False
        else:
            return os.geteuid() == 0

    def get_current_mac(self, interface: str) -> Optional[str]:
        try:
            if self.platform.startswith('win'):
                output = subprocess.check_output(f'getmac /v /fo csv | findstr {interface}', shell=True).decode()
                return output.split(',')[2].strip('"')
            
            elif self.platform.startswith('darwin'):
                output = subprocess.check_output(f'ifconfig {interface}', shell=True).decode()
                return output.split('ether ')[1].split()[0]
            
            else:
                output = subprocess.check_output(f'ip link show {interface}', shell=True).decode()
                return output.split('link/ether ')[1].split()[0]
                
        except Exception as e:
            return None

    def change_mac_address(self, interface: str, new_mac: str) -> bool:
        try:
            if self.platform.startswith('win'):
                subprocess.check_output(f'netsh interface set interface "{interface}" admin=disable', shell=True)
                subprocess.check_output(f'reg add HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Class\\{{4D36E972-E325-11CE-BFC1-08002BE10318}}\\0000 /v NetworkAddress /t REG_SZ /d {new_mac.replace(":", "")} /f', shell=True)
                subprocess.check_output(f'netsh interface set interface "{interface}" admin=enable', shell=True)
                
            elif self.platform.startswith('darwin'):
                subprocess.check_output(f'ifconfig {interface} ether {new_mac}', shell=True)
                
            else:
                subprocess.check_output(f'ip link set {interface} down', shell=True)
                subprocess.check_output(f'ip link set {interface} address {new_mac}', shell=True)
                subprocess.check_output(f'ip link set {interface} up', shell=True)
                
            return True
            
        except Exception as e:
            return False 

    def set_interface_status(self, interface: str, up: bool) -> bool:
        try:
            if self.platform.startswith('win'):
                status = "enable" if up else "disable"
                subprocess.check_output(
                    f'netsh interface set interface "{interface}" admin={status}',
                    shell=True,
                    stderr=subprocess.PIPE
                )
            elif self.platform.startswith('darwin'):
                status = "up" if up else "down"
                subprocess.check_output(
                    f'ifconfig {interface} {status}',
                    shell=True,
                    stderr=subprocess.PIPE
                )
            else:
                status = "up" if up else "down"
                subprocess.check_output(
                    f'ip link set {interface} {status}',
                    shell=True,
                    stderr=subprocess.PIPE
                )
            return True
        except Exception:
            return False

    def get_default_gateway(self) -> Optional[str]:
        try:
            if self.platform.startswith('win'):
                output = subprocess.check_output('ipconfig | findstr "Default Gateway"', shell=True).decode()
                return output.split(': ')[-1].strip()
            elif self.platform.startswith('darwin'):
                output = subprocess.check_output('netstat -nr | grep default', shell=True).decode()
                return output.split()[1]
            else:
                output = subprocess.check_output("ip route | grep default", shell=True).decode()
                return output.split()[2]
        except Exception:
            return None

    def test_connectivity(self, host: str, timeout: int = 5) -> bool:
        try:
            if self.platform.startswith('win'):
                param = '-n'
            else:
                param = '-c'
            
            subprocess.check_output(
                f'ping {param} 1 -w {timeout} {host}',
                shell=True,
                stderr=subprocess.PIPE
            )
            return True
        except Exception:
            return False