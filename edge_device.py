"""
edge_device.py
--------------
Acts as the Edge Device (Laptop 2) in the IoT pipeline.

Responsibilities:
  1. Listens for incoming TCP socket connections from the sensor (Laptop 1)
  2. Receives temperature readings from the socket
  3. Publishes each reading to the MQTT broker under the configured topic

Run this SECOND, after starting mqtt_alert_subscriber.py.
"""

import socket
import paho.mqtt.client as mqtt

# ── Configuration ──────────────────────────────────────────────────────────────
# Socket server settings (this device listens for the sensor)
LISTEN_HOST = "0.0.0.0"    # Listen on all network interfaces
LISTEN_PORT = 5005          # Must match EDGE_DEVICE_PORT in socket_sensor.py

# MQTT broker settings
MQTT_BROKER  = "broker.emqx.io"
MQTT_PORT    = 1883
MQTT_TOPIC   = "savonia/iot/temperature"
MQTT_CLIENT_ID = "edge_device_savonia"
# ───────────────────────────────────────────────────────────────────────────────


def on_connect(client, userdata, flags, rc):
    """Called when the MQTT client connects to the broker."""
    if rc == 0:
        print(f"[MQTT] Connected to broker: {MQTT_BROKER}")
    else:
        print(f"[MQTT] Connection failed. Return code: {rc}")


def on_publish(client, userdata, mid):
    """Called when a message is successfully published to the broker."""
    print(f"[MQTT] Message published successfully (mid={mid})")


def create_mqtt_client():
    """Creates and connects an MQTT client."""
    client = mqtt.Client(client_id=MQTT_CLIENT_ID)
    client.on_connect = on_connect
    client.on_publish  = on_publish

    print(f"[MQTT] Connecting to broker at {MQTT_BROKER}:{MQTT_PORT} ...")
    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)

    # Start the MQTT network loop in a background thread
    client.loop_start()
    return client


def run_edge_device():
    """
    Main loop: opens a socket server, waits for the sensor to connect,
    then forwards each received temperature reading via MQTT.
    """
    print("=" * 50)
    print("  Edge Device - Starting up")
    print(f"  Listening for sensor on port {LISTEN_PORT}")
    print(f"  MQTT topic: {MQTT_TOPIC}")
    print("=" * 50)

    # Step 1: Connect to MQTT broker
    mqtt_client = create_mqtt_client()

    # Step 2: Create TCP server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((LISTEN_HOST, LISTEN_PORT))
    server_socket.listen(1)  # Queue up to 1 connection

    print(f"\n[Socket] Waiting for sensor connection on {LISTEN_HOST}:{LISTEN_PORT} ...")

    try:
        # Step 3: Accept connection from the sensor
        conn, addr = server_socket.accept()
        print(f"[Socket] Sensor connected from {addr}\n")

        reading_count = 0

        while True:
            # Step 4: Receive data from the sensor
            data = conn.recv(1024)

            if not data:
                # Sensor disconnected
                print("[Socket] Sensor disconnected.")
                break

            # Decode the received bytes to a string
            temperature_str = data.decode("utf-8").strip()

            try:
                temperature = float(temperature_str)
                reading_count += 1

                print(f"[{reading_count}] Received from sensor: {temperature} °C")

                # Step 5: Publish temperature to MQTT broker
                result = mqtt_client.publish(MQTT_TOPIC, str(temperature))
                print(f"         Published to MQTT topic '{MQTT_TOPIC}' → {temperature} °C")

            except ValueError:
                print(f"[WARNING] Received invalid data: '{temperature_str}' — skipping.")

    except KeyboardInterrupt:
        print("\n[!] Edge Device stopped by user.")
    finally:
        conn.close()
        server_socket.close()
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        print("[*] Edge Device shut down cleanly.")


if __name__ == "__main__":
    run_edge_device()
