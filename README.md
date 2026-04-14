# MQTT Alert System with Telegram Notifications

**Course:** IoT Systems — Lab 4  
**MQTT Broker:** `broker.emqx.io`  
**MQTT Topic:** `savonia/iot/temperature`  
**Alert Threshold:** 28 °C

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          LAPTOP 1                                   │
│                                                                     │
│   ┌───────────────────┐               ┌────────────────────────┐   │
│   │  socket_sensor.py │               │ mqtt_alert_subscriber  │   │
│   │                   │               │        .py             │   │
│   │  Generates random │               │                        │   │
│   │  temperature data │               │  Subscribes to MQTT    │   │
│   │  (24 – 32 °C)     │               │  Checks threshold      │   │
│   └────────┬──────────┘               └────────────┬───────────┘   │
│            │ TCP Socket                            │               │
│            │ Port 5005                             │               │
└────────────┼──────────────────────────────────────┼───────────────┘
             │                                       │ Telegram API
             ▼                                       ▼
┌─────────────────────────┐               ┌──────────────────────┐
│        LAPTOP 2         │               │   Telegram Server    │
│                         │               │                      │
│   ┌─────────────────┐   │  MQTT Publish │  ┌────────────────┐  │
│   │  edge_device.py │───┼───────────────┼─►│   Your Bot     │  │
│   │                 │   │               │  └────────────────┘  │
│   │  Receives data  │   │               │          │           │
│   │  from sensor    │   │               │          ▼           │
│   │  Publishes to   │   │               │  ┌────────────────┐  │
│   │  MQTT broker    │   │               │  │  Your Phone /  │  │
│   └─────────────────┘   │               │  │  Telegram App  │  │
│                         │               │  └────────────────┘  │
└─────────────────────────┘               └──────────────────────┘
             │
             ▼
  ┌──────────────────────┐
  │    MQTT Broker       │
  │   broker.emqx.io     │
  │   Port 1883          │
  │                      │
  │  Topic:              │
  │  savonia/iot/        │
  │  temperature         │
  └──────────────────────┘
```

---

## How the System Works (Simple English)

1. **socket_sensor.py** runs on Laptop 1. It pretends to be a temperature sensor. Every 3 seconds, it generates a random temperature reading between 24 °C and 32 °C and sends that number to Laptop 2 over a direct network connection called a TCP socket.

2. **edge_device.py** runs on Laptop 2. It sits waiting for a connection from the sensor. When it receives a temperature reading, it immediately publishes that value to a public MQTT broker (broker.emqx.io) under the topic `savonia/iot/temperature`. Think of MQTT like a radio channel — the edge device broadcasts the reading to anyone tuned to that channel.

3. **mqtt_alert_subscriber.py** runs back on Laptop 1 (or any machine). It is subscribed to that same MQTT channel. Every time a new temperature value arrives, it checks whether the value is above 28 °C. If it is, it sends a Telegram message to your phone using the Telegram Bot API to warn you about the high temperature.

---

## MQTT Topic Used

```
savonia/iot/temperature
```

All three components use this topic. The edge device **publishes** to it. The alert subscriber **subscribes** to it.

---

## Prerequisites — Install Required Libraries

Run these on **both laptops** before starting:

```bash
pip install paho-mqtt requests
```

---

## Step-by-Step Instructions to Run the System

> **Important:** Start the programs in this exact order.

### Step 1 — Start the Alert Subscriber (Laptop 1)

```bash
python mqtt_alert_subscriber.py
```

You should see:

```
==================================================
  MQTT Alert Subscriber - Starting up
  Broker : broker.emqx.io:1883
  Topic  : savonia/iot/temperature
  Threshold: 28.0 °C
==================================================

[MQTT] Connecting to broker.emqx.io:1883 ...
[MQTT] Connected to broker: broker.emqx.io
[MQTT] Subscribed to topic: savonia/iot/temperature
[MQTT] Alert threshold set to: 28.0 °C

--------------------------------------------------
  Waiting for temperature readings...
--------------------------------------------------
```

Leave this running.

---

### Step 2 — Start the Edge Device (Laptop 2)

```bash
python edge_device.py
```

You should see:

```
==================================================
  Edge Device - Starting up
  Listening for sensor on port 5005
  MQTT topic: savonia/iot/temperature
==================================================
[MQTT] Connecting to broker at broker.emqx.io:1883 ...
[MQTT] Connected to broker: broker.emqx.io

[Socket] Waiting for sensor connection on 0.0.0.0:5005 ...
```

Leave this running.

---

### Step 3 — Start the Sensor (Laptop 1)

> If running on **two separate laptops**, open `socket_sensor.py` and change `EDGE_DEVICE_HOST` from `"127.0.0.1"` to Laptop 2's actual IP address (e.g. `"192.168.1.50"`).

```bash
python socket_sensor.py
```

You should see:

```
==================================================
  Temperature Sensor - Starting up
  Connecting to Edge Device at 127.0.0.1:5005
==================================================
[+] Connected to Edge Device at 127.0.0.1:5005

[1] Sent temperature: 29.3 °C
[2] Sent temperature: 25.8 °C
[3] Sent temperature: 31.1 °C
```

---

## Expected Output

### mqtt_alert_subscriber.py terminal

```
[Reading] Temperature received: 25.8 °C
   [OK] Temperature is within safe range.

[Reading] Temperature received: 29.3 °C
   [!] ALERT TRIGGERED — 29.3 °C exceeds 28.0 °C
   [Telegram] Alert sent successfully!

[Reading] Temperature received: 31.1 °C
   [!] ALERT TRIGGERED — 31.1 °C exceeds 28.0 °C
   [Telegram] Alert sent successfully!
```

### Telegram message (on your phone)

```
🚨 ALERT: High Temperature Detected!
Temperature: 29.3 °C
Threshold:   28.0 °C
Topic:       savonia/iot/temperature
```

---

## Testing Instructions

### Verify the Telegram bot works before the full test:

Open a browser and visit:
```
https://api.telegram.org/bot8550022968:AAGO-mAPTahJFfaWA9ZQqED9ovdph28KTcU/getUpdates
```
You should see your chat ID in the JSON response.

### Verify MQTT broker is reachable:

```bash
ping broker.emqx.io
```

### Force an alert immediately:

In `socket_sensor.py`, change the temperature range to always generate values above 28:
```python
return round(random.uniform(29.0, 32.0), 1)
```
This guarantees every reading triggers a Telegram alert for testing.

### Check all three terminals are active simultaneously:

| Terminal | File | Expected status |
|----------|------|----------------|
| Laptop 1 Terminal A | mqtt_alert_subscriber.py | Showing incoming readings |
| Laptop 2 Terminal | edge_device.py | Showing published values |
| Laptop 1 Terminal B | socket_sensor.py | Sending a reading every 3 seconds |

---

## Reflection: Why is MQTT Useful for IoT Monitoring and Alert Systems?

MQTT (Message Queuing Telemetry Transport) is a lightweight messaging protocol designed specifically for environments where bandwidth and power are limited — exactly the conditions found in most IoT deployments.

Here is why it is well suited for monitoring and alert systems:

**1. Lightweight and low overhead**  
MQTT messages have a very small header (as little as 2 bytes), which means sensors running on battery or low-power hardware can communicate efficiently without draining energy or consuming much network bandwidth.

**2. Publish/Subscribe decoupling**  
The sensor (publisher) and the alert system (subscriber) do not need to know about each other directly. They only share a topic name. This makes it easy to add new subscribers (more alert services, dashboards, loggers) without changing any of the existing components.

**3. Broker-based reliability**  
The MQTT broker (broker.emqx.io in this project) sits in the middle and manages message delivery. If a subscriber temporarily disconnects, the broker can hold messages (using Quality of Service levels) and deliver them when it reconnects. This is essential for alert systems where missing a critical reading could be dangerous.

**4. Scales easily**  
A single MQTT broker can handle thousands of devices publishing and subscribing simultaneously. Adding more sensors or more alert subscribers requires no changes to existing code — just connect and subscribe to the right topic.

**5. Real-time delivery**  
Messages are pushed to subscribers immediately as they arrive. This means alerts are triggered within milliseconds of a threshold being exceeded, which is critical in safety-critical monitoring scenarios such as temperature, pressure, or machine fault detection.

In summary, MQTT provides the right balance of simplicity, efficiency, and reliability that IoT systems need — making it the industry standard for monitoring and alerting at scale.

---

## GitHub Repository Structure

```
mqtt-alert-system/
├── socket_sensor.py
├── edge_device.py
├── mqtt_alert_subscriber.py
└── README.md
```

---

## How to Push to GitHub

### Step 1 — Create the repository on GitHub

1. Go to [https://github.com](https://github.com) and log in
2. Click the **+** icon (top right) → **New repository**
3. Name it: `mqtt-alert-system`
4. Set visibility to **Public**
5. Do NOT check "Add a README" (we already have one)
6. Click **Create repository**

### Step 2 — Set up Git locally and push

Run these commands in the folder where your 4 files are saved:

```bash
# Step 1: Initialise a git repository in this folder
git init

# Step 2: Add all files to staging
git add .

# Step 3: Commit with a message
git commit -m "Initial commit: MQTT alert system with Telegram notifications"

# Step 4: Connect to your GitHub repo (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/mqtt-alert-system.git

# Step 5: Push to GitHub
git branch -M main
git push -u origin main
```

After this, visit `https://github.com/YOUR_USERNAME/mqtt-alert-system` and you will see all four files live.

---

*Lab 4 — IoT Systems | Savonia University of Applied Sciences*
