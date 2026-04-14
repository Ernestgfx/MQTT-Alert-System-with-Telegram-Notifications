"""
socket_sensor.py
-----------------
Simulates a temperature sensor on Laptop 1.
Generates random temperature readings and sends them to
the Edge Device (Laptop 2) over a TCP socket connection.

Run this LAST, after starting mqtt_alert_subscriber.py and edge_device.py.
"""

import socket
import time
import random

# ── Configuration ──────────────────────────────────────────────────────────────
EDGE_DEVICE_HOST = "127.0.0.1"   # Change to Laptop 2's IP address when using two machines
EDGE_DEVICE_PORT = 5005           # Must match the port in edge_device.py
SEND_INTERVAL    = 3              # Seconds between each temperature reading
# ───────────────────────────────────────────────────────────────────────────────


def generate_temperature():
    """
    Simulates a temperature sensor reading.
    Returns a value between 24.0 and 32.0 °C so that some readings
    will exceed the 28 °C alert threshold.
    """
    return round(random.uniform(24.0, 32.0), 1)


def run_sensor():
    """
    Connects to the edge device and continuously sends temperature readings.
    """
    print("=" * 50)
    print("  Temperature Sensor - Starting up")
    print(f"  Connecting to Edge Device at {EDGE_DEVICE_HOST}:{EDGE_DEVICE_PORT}")
    print("=" * 50)

    # Create a TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to the edge device
        client_socket.connect((EDGE_DEVICE_HOST, EDGE_DEVICE_PORT))
        print(f"[+] Connected to Edge Device at {EDGE_DEVICE_HOST}:{EDGE_DEVICE_PORT}\n")

        reading_count = 0

        while True:
            reading_count += 1
            temperature = generate_temperature()

            # Convert temperature to string and encode for sending over socket
            message = str(temperature).encode("utf-8")
            client_socket.sendall(message)

            print(f"[{reading_count}] Sent temperature: {temperature} °C")

            # Wait before sending the next reading
            time.sleep(SEND_INTERVAL)

    except ConnectionRefusedError:
        print("\n[ERROR] Could not connect to Edge Device.")
        print("        Make sure edge_device.py is running first.")
    except KeyboardInterrupt:
        print("\n[!] Sensor stopped by user.")
    finally:
        client_socket.close()
        print("[*] Socket closed. Goodbye!")


if __name__ == "__main__":
    run_sensor()
