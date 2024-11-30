#!/usr/bin/env python3

import argparse
import sys
import random
import time
import re
import os
import json
import subprocess
from typing import Optional
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

# Import local modules from src
from src.logger import Logger
from src.mac_validator import MacValidator
from src.platform_handler import PlatformHandler

class MacSpoofer:
    def __init__(self):
        self.platform_handler = PlatformHandler()
        self.mac_validator = MacValidator()
        self.logger = Logger()
        self.backup_file = os.path.join(os.path.dirname(__file__), 'src', 'mac_backup.json')
        self.load_backup()

    def load_backup(self) -> None:
        """Load backed up MAC addresses from file."""
        try:
            if os.path.exists(self.backup_file):
                with open(self.backup_file, 'r') as f:
                    self.original_macs = json.load(f)
            else:
                self.original_macs = {}
        except Exception:
            self.original_macs = {}

    def save_backup(self) -> None:
        """Save MAC addresses backup to file."""
        try:
            os.makedirs(os.path.dirname(self.backup_file), exist_ok=True)
            with open(self.backup_file, 'w') as f:
                json.dump(self.original_macs, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save backup: {str(e)}")

    def generate_random_mac(self) -> str:
        common_ouis = [
            '00:0C:29', '00:50:56', '00:1A:A0', '00:16:3E', '00:15:5D',
            '00:1B:21', '00:25:90', '00:60:08', '00:0D:3A', '00:1C:14'
        ]
        oui = random.choice(common_ouis)
        nic_bytes = [random.randint(0, 255) for _ in range(3)]
        nic_part = ':'.join([f"{x:02x}" for x in nic_bytes])
        return f"{oui}:{nic_part}"

    def backup_original_mac(self, interface: str) -> None:
        if interface not in self.original_macs:
            original_mac = self.platform_handler.get_current_mac(interface)
            if original_mac:
                self.original_macs[interface] = original_mac
                self.save_backup()
                self.logger.info(f"Original MAC backed up: {original_mac}")

    def change_mac(self, interface: str, new_mac: Optional[str] = None) -> bool:
        """Change MAC address with network testing."""
        try:
            # Get gateway IP for testing
            gateway = self.platform_handler.get_default_gateway()
            
            with self.logger.status("Initializing MAC spoofer...") as status:
                self.backup_original_mac(interface)
                
                status.update("Getting current MAC address...")
                current_mac = self.platform_handler.get_current_mac(interface)
                
                if not new_mac:
                    status.update("Generating random MAC address...")
                    new_mac = self.generate_random_mac()
                
                status.update("Validating MAC address format...")
                if not self.mac_validator.is_valid_mac(new_mac):
                    self.logger.error(f"Invalid MAC address format: {new_mac}")
                    return False

                # Bring interface down
                status.update("Bringing network interface down...")
                if not self.platform_handler.set_interface_status(interface, False):
                    self.logger.error("Failed to bring interface down")
                    return False
                
                time.sleep(2)  # Wait for interface to fully down
                
                status.update("Changing MAC address...")
                if not self.platform_handler.change_mac_address(interface, new_mac):
                    self.logger.error("Failed to change MAC address")
                    # Try to bring interface back up before returning
                    self.platform_handler.set_interface_status(interface, True)
                    return False

                time.sleep(1)  # Wait for MAC change to take effect
                
                status.update("Bringing network interface up...")
                if not self.platform_handler.set_interface_status(interface, True):
                    self.logger.error("Failed to bring interface up")
                    return False
                
                time.sleep(3)  # Wait for interface to fully initialize
                
                # Test network connectivity
                if gateway:
                    status.update("Testing network connectivity...")
                    if self.platform_handler.test_connectivity(gateway):
                        self.logger.success("Network connectivity verified")
                    else:
                        self.logger.warning("Network connectivity test failed")
                
                self.logger.success("MAC address changed successfully:")
                self.logger.info(f"Interface: {interface}")
                self.logger.info(f"Old MAC: {current_mac}")
                self.logger.info(f"New MAC: {new_mac}")
                return True

        except Exception as e:
            self.logger.error(f"Error changing MAC address: {str(e)}")
            # Try to bring interface back up in case of error
            try:
                self.platform_handler.set_interface_status(interface, True)
            except:
                pass
            return False

    def restore_original_mac(self, interface: str) -> bool:
        """Restore the original MAC address and restart network interface."""
        self.load_backup()  # Reload backup before restoring
        if interface in self.original_macs:
            # Warn user about network interruption
            self.logger.warning("⚠️  Warning: This will temporarily disconnect your network interface")
            self.logger.warning("Are you sure you want to continue? (y/N)")
            
            response = input().lower()
            if response != 'y':
                self.logger.info("Operation cancelled by user")
                return False

            try:
                original_mac = self.original_macs[interface]
                
                # Bring interface down
                self.logger.info("Bringing network interface down...")
                if self.platform_handler.set_interface_status(interface, False):
                    time.sleep(2)  # Wait for interface to fully down
                    
                    # Change MAC
                    self.logger.info("Restoring original MAC address...")
                    if self.platform_handler.change_mac_address(interface, original_mac):
                        # Bring interface back up
                        self.logger.info("Bringing network interface up...")
                        if self.platform_handler.set_interface_status(interface, True):
                            time.sleep(2)  # Wait for interface to initialize
                            
                            # Test connectivity
                            gateway = self.platform_handler.get_default_gateway()
                            if gateway and self.platform_handler.test_connectivity(gateway):
                                self.logger.success("Network connectivity verified")
                            else:
                                self.logger.warning("Network connectivity test failed")
                            
                            self.logger.success(f"MAC address restored to original: {original_mac}")
                            # Remove the backup after successful restore
                            del self.original_macs[interface]
                            self.save_backup()
                            return True
                        else:
                            self.logger.error("Failed to bring interface up")
                    else:
                        self.logger.error("Failed to restore MAC address")
                        # Try to bring interface back up
                        self.platform_handler.set_interface_status(interface, True)
                else:
                    self.logger.error("Failed to bring interface down")
                
                return False
                    
            except Exception as e:
                self.logger.error(f"Error during restore: {str(e)}")
                # Try to bring interface back up in case of error
                try:
                    self.platform_handler.set_interface_status(interface, True)
                except:
                    pass
                return False
                    
        self.logger.error("No original MAC address backup found")
        return False

    def banner(self) -> None:
        banner_text = """
██████╗ ██╗  ██╗ █████╗ ███╗   ██╗████████╗ ██████╗ ███╗   ███╗    ███╗   ███╗ █████╗  ██████╗
██╔══██╗██║  ██║██╔══██╗████╗  ██║╚══██╔══╝██╔═══██╗████╗ ████║    ████╗ ████║██╔══██╗██╔════╝
██████╔╝███████║███████║██╔██╗ ██║   ██║   ██║   ██║██╔████╔██║    ██╔████╔██║███████║██║     
██╔═══╝ ██╔══██║██╔══██║██║╚██╗██║   ██║   ██║   ██║██║╚██╔╝██║    ██║╚██╔╝██║██╔══██║██║     
██║     ██║  ██║██║  ██║██║ ╚████║   ██║   ╚██████╔╝██║ ╚═╝ ██║    ██║ ╚═╝ ██║██║  ██║╚██████╗
╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝    ╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝
    """
        panel = Panel(
            banner_text, 
            style="bold magenta",
            subtitle="by LEO | The MAC Address Ghosting Tool",
            subtitle_align="right"
        )
        self.console.print(panel)

def main():
    spoofer = MacSpoofer()
    spoofer.banner()

    parser = argparse.ArgumentParser(description="PHANTOM MAC - Advanced MAC Address Ghosting Tool")
    parser.add_argument("-i", "--interface", help="Network interface to modify")
    parser.add_argument("-m", "--mac", help="New MAC address (random if not specified)")
    parser.add_argument("-s", "--show", action="store_true", help="Show current MAC address")
    parser.add_argument("-r", "--restore", action="store_true", help="Restore original MAC address")
    
    if len(sys.argv) == 1:
        spoofer.logger.show_help()
        return

    args = parser.parse_args()

    if not args.interface:
        spoofer.logger.error("Interface is required! Use -i or --interface")
        spoofer.logger.show_help()
        return
    
    if args.show:
        with spoofer.logger.status("[bold cyan]Getting current MAC address...") as status:
            time.sleep(0.5)
            current_mac = spoofer.platform_handler.get_current_mac(args.interface)
            if current_mac:
                spoofer.logger.info(f"Current MAC address for {args.interface}: {current_mac}")
            else:
                spoofer.logger.error(f"Could not get MAC address for {args.interface}")
        return

    if not spoofer.platform_handler.check_privileges():
        spoofer.logger.error("This tool requires administrative privileges!")
        spoofer.logger.info("Please run with sudo (Linux/macOS) or as Administrator (Windows)")
        sys.exit(1)

    if args.restore:
        spoofer.restore_original_mac(args.interface)
    else:
        spoofer.change_mac(args.interface, args.mac)

if __name__ == "__main__":
    main() 