import requests
import time
import random

# The URL of your Flask Backend
URL = "http://127.0.0.1:5000/api/sensors/update"

def generate_sensor_data():
    return {
        "temperature": round(random.uniform(28.0, 32.0), 1),
        "humidity": round(random.uniform(75.0, 85.0), 1),
        "soilMoisture": round(random.uniform(82.0, 95.0), 1),
        "phLevel": round(random.uniform(5.8, 6.2), 2),
        "salinity": round(random.uniform(0.1, 0.3), 2),
        "lightIntensity": round(random.uniform(65.0, 75.0), 1)
    }

print("🌱 STARTING SENSOR SIMULATOR...")
print(f"📡 Sending data to {URL} every 2 seconds...")

while True:
    try:
        # 1. Generate Data
        payload = generate_sensor_data()
        
        # 2. Send to Flask (POST request)
        response = requests.post(URL, json=payload)
        
        # 3. Print result
        if response.status_code == 200:
            print(f"✅ [LIVE] Sent: {payload['temperature']}°C | {payload['soilMoisture']}% Moisture")
        elif response.status_code == 201:
            print(f"💾 [SAVED] Data committed to Database!")
        else:
            print(f"⚠️ Error: {response.text}")
            
        time.sleep(2) # Wait 2 seconds
        
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        time.sleep(2)