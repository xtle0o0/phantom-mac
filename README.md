# PHANTOM MAC 👻

An advanced MAC address ghosting tool that works across Windows, Linux, and macOS.

## Features ✨

- Cross-platform support (Windows, Linux, macOS)
- Beautiful terminal UI with animations
- Random MAC address generation from common vendors
- MAC address validation
- Backup and restore original MAC addresses
- Administrative privilege checking
- Colored output and status indicators

## Prerequisites 📋

- Python 3.7 or higher
- Administrative privileges (sudo/admin)
- Network interface with MAC changing capability
- Git (for installation)

## Installation 🚀

1. Clone the repository:
    ```bash
    git clone https://github.com/xtle0o0/phantom-mac.git
    cd phantom-mac
    ```

2. Create and activate virtual environment (recommended):
    ```bash
    # Linux/macOS
    python -m venv env
    source env/bin/activate

    # Windows
    python -m venv env
    .\env\Scripts\activate
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage 💻

### Show current MAC address:
- **Linux/macOS**
    ```bash
    sudo python phantom_mac.py -i wlan0 -s
    ```
- **Windows (Run as Administrator)**
    ```bash
    python phantom_mac.py -i "Wi-Fi" -s
    ```

### Change to random MAC address:
- **Linux/macOS**
    ```bash
    sudo python phantom_mac.py -i wlan0
    ```
- **Windows (Run as Administrator)**
    ```bash
    python phantom_mac.py -i "Wi-Fi"
    ```

### Change to specific MAC address:
- **Linux/macOS**
    ```bash
    sudo python phantom_mac.py -i wlan0 -m 00:11:22:33:44:55
    ```
- **Windows (Run as Administrator)**
    ```bash
    python phantom_mac.py -i "Wi-Fi" -m 00:11:22:33:44:55
    ```

### Restore original MAC address:
- **Linux/macOS**
    ```bash
    sudo python phantom_mac.py -i wlan0 -r
    ```
- **Windows (Run as Administrator)**
    ```bash
    python phantom_mac.py -i "Wi-Fi" -r
    ```

## Common Interface Names 🔌

- **Linux**: `wlan0`, `eth0`, `wlp3s0`
- **macOS**: `en0`, `en1`
- **Windows**: `"Wi-Fi"`, `"Ethernet"` (use quotes if the name contains spaces)

## ⚠️ Important Warnings

1. **Administrative Privileges**:
   - Always run with sudo (Linux/macOS) or as Administrator (Windows)
   - Incorrect usage may require system restart to recover network functionality

2. **Network Interruption**:
   - MAC address changes will temporarily disconnect your network
   - Ensure you have an alternative way to restore connectivity if needed
   - Some operations may require system restart

3. **Hardware Compatibility**:
   - Not all network interfaces support MAC address changes
   - Some devices may revert changes after restart
   - Virtual interfaces may have additional restrictions

4. **Legal Considerations**:
   - MAC address spoofing may be restricted in some networks/organizations
   - Check your local network policies before use
   - Use responsibly and ethically

5. **Backup**:
   - Original MAC addresses are backed up automatically
   - Keep note of your original MAC address before making changes
   - Some changes may persist after system restart

## Troubleshooting 🔧

1. If the network doesn't reconnect:
   - Wait 30 seconds for the interface to stabilize
   - Try disabling and re-enabling the network interface
   - Restart your system as a last resort

2. If changes don't apply:
   - Verify administrative privileges
   - Check the interface name is correct
   - Ensure the interface supports MAC changes
   - Try disabling the network manager temporarily

3. If restore fails:
   - Use a hardware reset (restart)
   - Check the backup file in `src/mac_backup.json`
   - Use the device manager to reset the network adapter


## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author 👨‍💻

Created with ❤️ by LEO

## Disclaimer ⚖️

This tool is provided for educational and ethical testing purposes only. Users are responsible for complying with all applicable laws and network policies. The author assumes no liability for misuse or any damages that may occur.

