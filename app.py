import sqlite3
import json
import paho.mqtt.client as mqtt
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

DB_NAME = "farm_data.db"

# --- GLOBAL VARIABLES ---
current_sensor_data = {} 
last_save_time = datetime.min 

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            temperature REAL,
            humidity REAL,
            soil_moisture REAL,
            ph_level REAL,
            salinity REAL,
            light_intensity REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- 1. MQTT BACKGROUND LISTENER ---
def on_connect(client, userdata, flags, rc):
    print("✅ [Backend] Connected to HiveMQ Broker!")
    client.subscribe("agritwin/sensors/live")

def on_message(client, userdata, msg):
    global current_sensor_data, last_save_time
    try:
        payload = json.loads(msg.payload.decode('utf-8'))
        
        # 1. Update RAM instantly (maps ESP32 keys to your DB keys)
        current_sensor_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": payload.get('temperature', 0),
            "humidity": payload.get('humidity', 0),
            "soilMoisture": payload.get('moisture', 0), 
            "phLevel": payload.get('ph', 0),
            "salinity": payload.get('salinity', 0),
            "lightIntensity": payload.get('light', 0)
        }

        # 2. Save to Database ONLY every 5 minutes
        now = datetime.now()
        if (now - last_save_time) > timedelta(minutes=5):
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO sensor_readings 
                (temperature, humidity, soil_moisture, ph_level, salinity, light_intensity)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                current_sensor_data['temperature'],
                current_sensor_data['humidity'],
                current_sensor_data['soilMoisture'],
                current_sensor_data['phLevel'],
                current_sensor_data['salinity'],
                current_sensor_data['lightIntensity']
            ))
            conn.commit()
            conn.close()
            last_save_time = now
            print(f"💾 [Backend] SAVED to Database at {now.strftime('%H:%M:%S')}")
            
    except Exception as e:
        print(f"MQTT Error: {e}")

# Start MQTT in a background thread
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect("broker.hivemq.com", 1883, 60)
mqtt_client.loop_start() 

# --- 2. GET ROUTE (Latest) ---
@app.route('/api/sensors/latest', methods=['GET'])
def get_latest_reading():
    global current_sensor_data
    if current_sensor_data:
        return jsonify(current_sensor_data)
    return jsonify({"message": "No data yet"}), 404

# --- 3. POST ROUTE (For Simulator/Manual Updates) ---
@app.route('/api/sensors/update', methods=['POST'])
def receive_sensor_data():
    # Leaving this here so your sensor_simulator.py still works!
    data = request.json
    return jsonify({"status": "live", "message": "Updated via Simulator"}), 200

# --- 4. HISTORY ROUTE ---
@app.route('/api/sensors/history', methods=['GET'])
def get_sensor_history():
    time_range = request.args.get('range', '24h')
    if time_range == '7d': cutoff_date = datetime.now() - timedelta(days=7)
    elif time_range == '30d': cutoff_date = datetime.now() - timedelta(days=30)
    else: cutoff_date = datetime.now() - timedelta(days=1)
    
    cutoff_str = cutoff_date.strftime("%Y-%m-%d %H:%M:%S")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM sensor_readings WHERE timestamp >= ? ORDER BY timestamp ASC', (cutoff_str,))
    rows = cursor.fetchall()
    conn.close()
    
    history_data = [{"timestamp": r[1], "temperature": r[2], "humidity": r[3], "soilMoisture": r[4], "phLevel": r[5], "salinity": r[6], "lightIntensity": r[7]} for r in rows]
    return jsonify(history_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)