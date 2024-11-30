from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

class Logger:
    def __init__(self):
        self.console = Console()

    def _log(self, message: str, style: str = None) -> None:
        """Improved terminal compatibility."""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            text = Text()
            text.append(f"[{timestamp}] ", style="bold cyan")
            text.append(str(message), style=style)
            self.console.print(text)
        except Exception:
            # Fallback for terminals that don't support rich formatting
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] {message}")

    def info(self, message: str) -> None:
        self._log(message, "blue")

    def success(self, message: str) -> None:
        self._log(message, "green")

    def error(self, message: str) -> None:
        self._log(message, "red")

    def banner(self) -> None:
        banner_text = """
╦  ╔═╗╔═╗  ╔╦╗╔═╗╔═╗  ╔═╗╔═╗╔═╗╔═╗╔═╗╔═╗╦═╗
║  ║╣ ║ ║  ║║║╠═╣║    ╚═╗╠═╝║ ║║ ║╠╣ ║╣ ╠╦╝
╩═╝╚═╝╚═╝  ╩ ╩╩ ╩╚═╝  ╚═╝╩  ╚═╝╚═╝╚  ╚═╝╩╚═
        """
        panel = Panel(
            banner_text, 
            style="bold magenta", 
            subtitle="by LEO",
            subtitle_align="right"
        )
        self.console.print(panel)

    def show_help(self) -> None:
        table = Table(
            title="Available Commands",
            title_style="bold magenta",
            border_style="cyan",
            show_header=True,
            header_style="bold cyan"
        )
        
        table.add_column("Command", style="green", justify="left")
        table.add_column("Description", style="yellow", justify="left")
        
        table.add_row("-i, --interface", "Network interface to modify (e.g., wlan0, eth0)")
        table.add_row("-m, --mac", "New MAC address (random if not specified)")
        table.add_row("-s, --show", "Show current MAC address")
        table.add_row("-r, --restore", "Restore original MAC address")
        table.add_row("-h, --help", "Show this help message")
        
        self.console.print("\n[bold cyan]Usage Examples:[/]")
        self.console.print("[dim]# Show current MAC address[/]")
        self.console.print("sudo python mac_spoofer.py -i wlan0 -s\n")
        self.console.print("[dim]# Change to random MAC[/]")
        self.console.print("sudo python mac_spoofer.py -i wlan0\n")
        self.console.print("[dim]# Change to specific MAC[/]")
        self.console.print("sudo python mac_spoofer.py -i wlan0 -m 00:11:22:33:44:55\n")
        self.console.print("[dim]# Restore original MAC[/]")
        self.console.print("sudo python mac_spoofer.py -i wlan0 -r\n")
        
        self.console.print(table)

    def status(self, message: str):
        return self.console.status(message, spinner="dots") 

    def warning(self, message: str) -> None:
        """Add warning level logging."""
        self._log(message, "yellow")