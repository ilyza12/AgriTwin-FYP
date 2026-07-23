import paho.mqtt.client as mqtt
import time
import random
import json

# HiveMQ Public Broker
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "agritwin/sensors/live"

def generate_sensor_data():
    # Notice the keys: moisture, ph, light (Exactly what the ESP32 will send!)
    return {
        "temperature": round(random.uniform(24.0, 26.0), 1), # Optimal Chili Temp
        "humidity": round(random.uniform(70.0, 80.0), 1),
        "moisture": round(random.uniform(24.0, 26.0), 1),
        "ph": round(random.uniform(6.0, 6.5), 2),
        "salinity": round(random.uniform(0.5, 1.0), 2),
        "light": round(random.uniform(600.0, 800.0), 1)
    }

#def generate_sensor_data():
    # ⚠️ TEMPORARY NUKE VALUES TO TEST AI ANOMALY BANNER
    #return {
        #"temperature": 50.0,  # Lethal heat
        #"humidity": 10.0,     # Complete dry-out
        #"moisture": 0.0,      # Absolute drought
        #"ph": 1.0,            # Pure acid
        #"salinity": 10.0,     # Toxic salt levels
        #"light": 0.0          # Pitch black
    #}

print("🌱 STARTING ESP32 MQTT SIMULATOR...")
print(f"📡 Connecting to {BROKER}...")

client = mqtt.Client()
client.connect(BROKER, PORT, 60)
client.loop_start()

print(f"✅ Connected! Publishing to topic: '{TOPIC}' every 2 seconds...\n")

try:
    while True:
        payload_dict = generate_sensor_data()
        payload_json = json.dumps(payload_dict)
        
        # Publish exactly like the physical hardware would
        client.publish(TOPIC, payload_json)
        
        print(f"✅ [MQTT PUBLISHED] {payload_json}")
        time.sleep(2) # Wait 2 seconds
        
except KeyboardInterrupt:
    print("\n🛑 Simulator stopped.")
    client.loop_stop()
    client.disconnect()