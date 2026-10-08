import tkinter as tk
import socket
import subprocess
import os
import requests
import shutil

def get_ip_address():
    try:
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
        ip = result.stdout.strip().split()[0]
        return ip if ip else "Not Connected"
    except Exception as e:
        return f"Error: {e}"

def get_gateway():
    try:
        result = subprocess.run(['ip', 'route'], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if 'default' in line:
                return line.split()[2]
        return "No Gateway Found"
    except Exception as e:
        return f"Error: {e}"

def ping_test(host):
    try:
        result = subprocess.run(['ping', '-c', '4', host], capture_output=True, text=True)
        return result.stdout if result.returncode == 0 else "Ping Failed"
    except Exception as e:
        return f"Error: {e}"

def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org')
        if response.status_code == 200:
            return response.text
        return "Unable to fetch public IP"
    except Exception as e:
        return f"Error: {e}"

def get_bandwidth(interface="eth0"):
    try:
        result = subprocess.run(['ethtool', interface], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if "Speed" in line:
                return line.split(":")[1].strip()
        return "Speed information not available"
    except Exception as e:
        return f"Error: {e}"

def get_lldp_info():
    if shutil.which("lldpctl") is None:
        return ("lldpctl not found", "Install lldpd and try again")
    try:
        result = subprocess.run(['lldpctl'], capture_output=True, text=True)
        port_id = "Not available"
        switch_name = "Not available"
        for line in result.stdout.splitlines():
            if "PortID:" in line or "Port ID:" in line:
                port_id = line.split(":", 1)[1].strip()
            if "System Name:" in line:
                switch_name = line.split(":", 1)[1].strip()
        return (port_id, switch_name)
    except Exception as e:
        return (f"Error: {e}", "")

def display_info():
    ip_label.config(text=f"IP Address: {get_ip_address()}")
    gateway_label.config(text=f"Gateway: {get_gateway()}")
    public_ip_label.config(text=f"Public IP: {get_public_ip()}")
    ping_result = ping_test('8.8.8.8')
    ping_label.config(text=f"Ping Result:\n{ping_result}")
    bandwidth = get_bandwidth()
    bandwidth_label.config(text=f"Bandwidth: {bandwidth}")

    port_id, switch_name = get_lldp_info()
    port_id_label.config(text=f"Port ID: {port_id}")
    switch_name_label.config(text=f"Switch Name: {switch_name}")

def pulse_cable():
    # Placeholder logic replace with GPIO logic when ready
    port_id_label.config(text="Port ID: Pulsing...")
    switch_name_label.config(text="Switch Name: Pulsing signal sent")

# ---------- UI ----------
window = tk.Tk()
window.title("Network Tester")

screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
window.geometry(f"{screen_width}x{screen_height}")

main_frame = tk.Frame(window)
main_frame.pack(fill="both", expand=True)

button_frame = tk.Frame(main_frame, width=200)
button_frame.pack(side="left", fill="y", padx=10, pady=10)

output_frame = tk.Frame(main_frame)
output_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

# Output Labels
ip_label = tk.Label(output_frame, text="IP Address: ", font=("Helvetica", 12), anchor="w")
ip_label.pack(fill='x', pady=2)

gateway_label = tk.Label(output_frame, text="Gateway: ", font=("Helvetica", 12), anchor="w")
gateway_label.pack(fill='x', pady=2)

public_ip_label = tk.Label(output_frame, text="Public IP: ", font=("Helvetica", 12), anchor="w")
public_ip_label.pack(fill='x', pady=2)

ping_label = tk.Label(output_frame, text="Ping Result: ", font=("Helvetica", 12), anchor="w", justify="left", wraplength=screen_width - 250)
ping_label.pack(fill='x', pady=2)

bandwidth_label = tk.Label(output_frame, text="Bandwidth: ", font=("Helvetica", 12), anchor="w")
bandwidth_label.pack(fill='x', pady=2)

port_id_label = tk.Label(output_frame, text="Port ID: ", font=("Helvetica", 12), anchor="w")
port_id_label.pack(fill='x', pady=2)

switch_name_label = tk.Label(output_frame, text="Switch Name: ", font=("Helvetica", 12), anchor="w")
switch_name_label.pack(fill='x', pady=2)

# Buttons
test_button = tk.Button(button_frame, text="Network Test", font=("Helvetica", 10), command=display_info)
test_button.pack(fill="x", pady=5)

pulse_button = tk.Button(button_frame, text="Pulse Cable", font=("Helvetica", 10), command=pulse_cable)
pulse_button.pack(fill="x", pady=5)

window.mainloop()
