import re
import socket
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import requests
import shutil


try:
    import scapy
    print("Scapy:", scapy.__version__)

    from scapy.all import sniff, get_if_list

    from scapy.arch.windows import get_windows_if_list


    print("sniff import OK")

    count = 0
    
    print(f"Packets captured: {count}")

    from scapy.contrib.lldp import LLDPDUPortID, LLDPDUSystemName
    print("LLDP import OK")

    SCAPY_AVAILABLE = True

except Exception as e:
    print("IMPORT FAILURE:", repr(e))
    SCAPY_AVAILABLE = False

APP_TITLE = "Network Information Pro"


def get_ip_address():
    try:
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)
    except Exception as e:
        return f"Error: {e}"


def get_gateway():
    try:
        result = subprocess.run(["ipconfig"], capture_output=True, text=True)
        match = re.search(r"Default Gateway[. ]*: *([\d.]+)", result.stdout)
        return match.group(1) if match else "Not Found"
    except Exception as e:
        return f"Error: {e}"


def get_public_ip():
    try:
        return requests.get("https://api.ipify.org", timeout=5).text
    except Exception as e:
        return f"Error: {e}"


def ping_test(host="8.8.8.8"):
    try:
        result = subprocess.run(
            ["ping", "-n", "4", host],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return result.stdout
    except Exception as e:
        return f"Error: {e}"


def get_bandwidth():
    try:
        ps = [
            "powershell",
            "-NoProfile",
            "-Command",
            "Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | Select-Object -First 1 Name,LinkSpeed | ConvertTo-Csv -NoTypeInformation"
        ]

        result = subprocess.run(ps, capture_output=True, text=True, timeout=10)

        lines = result.stdout.strip().splitlines()
        if len(lines) >= 2:
            return lines[1].replace('"', '')

        return "Unknown"

    except Exception as e:
        return f"Error: {e}"


def get_lldp_info():
    data = {
        "switch": "No LLDP Detected",
        "port": "No LLDP Detected"
    }

    def process(pkt):
        try:
            print("LLDP RECEIVED")

            # Walk through all layers
            current = pkt

            while current:
                cls = current.__class__.__name__

                if cls == "LLDPDUPortID":
                    port = current.id

                    if isinstance(port, bytes):
                        port = port.decode(errors="ignore")

                    data["port"] = port
                    print("PORT FOUND:", port)

                elif cls == "LLDPDUSystemName":
                    name = current.system_name
                        
                    if isinstance(name, bytes):
                        name = name.decode(errors="ignore")

                    data["switch"] = name
                    print("SWITCH FOUND:", name)

                current = current.payload

        except Exception as e:
            print("PROCESS ERROR:", e)

        
    for iface in get_windows_if_list():

        name = iface["name"]
        desc = iface["description"]

        print(f"Checking: {name}")
        print(f"Description: {desc}")
        print("-" * 50)

        desc_lower = desc.lower()

        # Skip non-physical adapters
        if any(x in desc for x in [
            "loopback",
            "vmware",
            "hyper-v",
            "virtual",
            "vpn",
            "wireless",
            "wi-fi"
        ]):
            print(f"Skipping: {iface['description']}")
            continue

        try:

            print(f"Listening on {name}")

            sniff(
                iface=name,
                filter="ether proto 0x88cc",
                timeout=3,
                store=False,
                prn=process
            )

            if (data["port"] != "No LLDP Detected" and
                data["switch"] != "No LLDP Detected"):

                print(f"LLDP FOUND ON {name}")

                return data["port"], data["switch"]

        except Exception as e:
            print(f"{name} ERROR: {e}")

    return data["port"], data["switch"]



class NetworkTester:

    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1000x700")

        self.build_ui()

    def build_ui(self):

        style = ttk.Style()

        try:
            style.theme_use("vista")
        except Exception:
            pass

        top = ttk.Frame(self.root, padding=10)
        top.pack(fill="x")

        ttk.Label(
            top,
            text="Network Information Pro",
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w")

        cards = ttk.LabelFrame(self.root, text="Network Information", padding=10)
        cards.pack(fill="x", padx=10, pady=10)

        self.ip_var = tk.StringVar(value="-")
        self.gateway_var = tk.StringVar(value="-")
        self.public_var = tk.StringVar(value="-")
        self.speed_var = tk.StringVar(value="-")
        self.port_var = tk.StringVar(value="-")
        self.switch_var = tk.StringVar(value="-")

        fields = [
            ("IP Address", self.ip_var),
            ("Gateway", self.gateway_var),
            ("Public IP", self.public_var),
            ("Link Speed", self.speed_var),
            ("Switch Port", self.port_var),
            ("LLDP Switch", self.switch_var),
        ]

        for row, (label, var) in enumerate(fields):
            ttk.Label(cards, text=label + ":", font=("Segoe UI", 10, "bold")).grid(row=row, column=0, sticky="w", pady=3)
            ttk.Label(cards, textvariable=var).grid(row=row, column=1, sticky="w", padx=10)

        buttons = ttk.Frame(self.root)
        buttons.pack(fill="x", padx=10)

        ttk.Button(buttons, text="Refresh", command=self.refresh).pack(side="left", padx=5)
        ttk.Button(buttons, text="Ping Google DNS", command=self.run_ping).pack(side="left", padx=5)
        ttk.Button(buttons, text="Pulse Cable", command=self.pulse_cable).pack(side="left", padx=5)
      

        log_frame = ttk.LabelFrame(self.root, text="Activity Log", padding=5)
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.log = tk.Text(log_frame, height=20)
        self.log.pack(fill="both", expand=True)

    def write_log(self, text):
        self.log.insert(tk.END, text + "\n")
        self.log.see(tk.END)

    def refresh(self):
        threading.Thread(target=self._refresh_worker, daemon=True).start()

    def _refresh_worker(self):
        self.ip_var.set(get_ip_address())
        self.gateway_var.set(get_gateway())
        self.public_var.set(get_public_ip())
        self.speed_var.set(get_bandwidth())

        port, switch = get_lldp_info()

        self.port_var.set(port)
        self.switch_var.set(switch)

        self.write_log("Network information refreshed")

    def run_ping(self):
        threading.Thread(target=self._ping_worker, daemon=True).start()

    def _ping_worker(self):
        result = ping_test()
        self.write_log(result)

    def pulse_cable(self):
        messagebox.showinfo(
            "Not Implemented",
            "Cable pulse feature requires vendor-specific hardware support."
        )


if __name__ == '__main__':
    root = tk.Tk()
    app = NetworkTester(root)
    root.mainloop()
