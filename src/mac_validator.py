import re

class MacValidator:
    def __init__(self):
        self.mac_pattern = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')

    def is_valid_mac(self, mac_address: str) -> bool:
        if not self.mac_pattern.match(mac_address):
            return False
        return self.is_unicast_mac(mac_address)

    def is_unicast_mac(self, mac_address: str) -> bool:
        first_byte = int(mac_address[:2], 16)
        return first_byte % 2 == 0