"""
mqtt_alert_subscriber.py
------------------------
Runs on Laptop 1 (the "Cloud Server" in the architecture).

Responsibilities:
  1. Subscribes to the MQTT broker on the temperature topic
  2. Receives every temperature reading published by the Edge Device
  3. Sends a Telegram alert message if the temperature exceeds the threshold

Run this FIRST, before edge_device.py and socket_sensor.py.
"""

import paho.mqtt.client as mqtt
import requests

# ── Configuration ──────────────────────────────────────────────────────────────
MQTT_BROKER   = "broker.emqx.io"
MQTT_PORT     = 1883
MQTT_TOPIC    = "savonia/iot/temperature"
MQTT_CLIENT_ID = "alert_subscriber_savonia"

# Telegram Bot credentials
TELEGRAM_TOKEN   = "8550022968:AAGO-mAPTahJFfaWA9ZQqED9ovdph28KTcU"
TELEGRAM_CHAT_ID = "1820460614"

# Alert threshold in degrees Celsius
TEMPERATURE_THRESHOLD = 28.0
# ───────────────────────────────────────────────────────────────────────────────


def send_telegram_alert(message):
    """
    Sends a text message to your Telegram chat via the Bot API.

    Args:
        message (str): The alert text to send.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }

    try:
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code == 200:
            print(f"   [Telegram] Alert sent successfully!")
        else:
            print(f"   [Telegram] Failed to send. Status: {response.status_code} | Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"   [Telegram] Network error: {e}")


def on_connect(client, userdata, flags, rc):
    """Called when the subscriber connects to the MQTT broker."""
    if rc == 0:
        print(f"[MQTT] Connected to broker: {MQTT_BROKER}")
        # Subscribe to the temperature topic right after connecting
        client.subscribe(MQTT_TOPIC)
        print(f"[MQTT] Subscribed to topic: {MQTT_TOPIC}")
        print(f"[MQTT] Alert threshold set to: {TEMPERATURE_THRESHOLD} °C\n")
        print("-" * 50)
        print("  Waiting for temperature readings...")
        print("-" * 50)
    else:
        print(f"[MQTT] Connection failed. Return code: {rc}")


def on_message(client, userdata, msg):
    """
    Called every time a new message arrives on the subscribed topic.

    Decodes the temperature, prints it, and triggers a Telegram alert
    if it exceeds the threshold.
    """
    try:
        # Decode the raw bytes to a float
        temperature = float(msg.payload.decode("utf-8"))

        print(f"\n[Reading] Temperature received: {temperature} °C")

        if temperature > TEMPERATURE_THRESHOLD:
            alert_message = (
                f"🚨 ALERT: High Temperature Detected!\n"
                f"Temperature: {temperature} °C\n"
                f"Threshold:   {TEMPERATURE_THRESHOLD} °C\n"
                f"Topic:       {MQTT_TOPIC}"
            )
            print(f"   [!] ALERT TRIGGERED — {temperature} °C exceeds {TEMPERATURE_THRESHOLD} °C")
            send_telegram_alert(alert_message)
        else:
            print(f"   [OK] Temperature is within safe range.")

    except ValueError:
        print(f"[WARNING] Received non-numeric payload: '{msg.payload.decode()}' — ignoring.")


def run_subscriber():
    """
    Sets up and starts the MQTT subscriber loop.
    """
    print("=" * 50)
    print("  MQTT Alert Subscriber - Starting up")
    print(f"  Broker : {MQTT_BROKER}:{MQTT_PORT}")
    print(f"  Topic  : {MQTT_TOPIC}")
    print(f"  Threshold: {TEMPERATURE_THRESHOLD} °C")
    print("=" * 50)

    # Create MQTT client
    client = mqtt.Client(client_id=MQTT_CLIENT_ID)
    client.on_connect = on_connect
    client.on_message = on_message

    print(f"\n[MQTT] Connecting to {MQTT_BROKER}:{MQTT_PORT} ...")
    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)

    try:
        # Blocking loop — keeps the subscriber running until Ctrl+C
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n\n[!] Subscriber stopped by user.")
    finally:
        client.disconnect()
        print("[*] Disconnected from broker. Goodbye!")


if __name__ == "__main__":
    run_subscriber()
