import sqlite3
import json
import paho.mqtt.client as mqtt
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta

# --- IMPORT YOUR NEW AI BRAIN ---
from ml_inference import LiveMLInference

app = Flask(__name__)
CORS(app)

DB_NAME = "farm_data.db"

# --- INITIALIZE THE AI SYSTEM ---
# This loads all your .pkl files the moment you start the Flask server
try:
    # 🎯 DEFENSE: Loads heavy .pkl models into RAM exactly once on startup. Prevents server lag on every API call.
    ml_system = LiveMLInference(db_path=DB_NAME)
except Exception as e:
    print(f"⚠️ [Backend] AI System failed to load: {e}")

# --- GLOBAL VARIABLES ---
current_sensor_data = {} 
last_save_time = datetime.min 

def init_db():
    # 🎯 DEFENSE: Local SQLite database ensures the system runs entirely on the edge without expensive cloud (AWS) costs.
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
        # 🎯 DEFENSE: MQTT data instantly overwrites RAM. Allows the Live Dashboard to fetch data with zero database latency.
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
        # 🎯 DEFENSE: Downsampling. Only writes to the database every 5 minutes to prevent storage bloat over a long growing season.
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
# 🎯 DEFENSE: MQTT runs on a background thread (`loop_start()`). Prevents blocking the Flask HTTP server from answering Vue requests.
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

# ==========================================
# 🧠 AI DASHBOARD ROUTES
# ==========================================

# --- 1. LIVE DASHBOARD: Anomaly & Health ---
@app.route('/api/ml/live-analysis', methods=['GET'])
def get_live_analysis():
    global current_sensor_data
    if not current_sensor_data:
        return jsonify({"status": "error", "message": "No live sensor data available yet."}), 404
        
    try:
        # Pass the current MQTT RAM data directly to the AI
        result = ml_system.analyze_current_state(
            temp=float(current_sensor_data.get('temperature', 0)),
            humidity=float(current_sensor_data.get('humidity', 0)),
            soil_moisture=float(current_sensor_data.get('soilMoisture', 0)),
            ph=float(current_sensor_data.get('phLevel', 0)),
            salinity=float(current_sensor_data.get('salinity', 0)),
            light=float(current_sensor_data.get('lightIntensity', 0))
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- 2. LIVE DASHBOARD: Yield Prediction ---
@app.route('/api/ml/live-yield', methods=['GET'])
def get_live_yield():
    try:
        # Looks at the last 7 days of SQLite data to guess harvest
        result = ml_system.predict_yield_live(days_observed=7)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- 3. SIMULATION DASHBOARD: What-If Scenarios ---
@app.route('/api/ml/simulate', methods=['POST'])
def run_simulation():
    # Grabs the slider values sent from the Vue frontend
    data = request.json
    
    try:
        temp = float(data.get('temperature', 25))
        hum = float(data.get('humidity', 70))
        moist = float(data.get('soilMoisture', 25))
        ph = float(data.get('phLevel', 6.0))
        sal = float(data.get('salinity', 0.8))
        light = float(data.get('lightIntensity', 800))
        
        # 1. Get yield prediction for these fake numbers
        yield_prediction = ml_system.predict_yield_simulation(temp, hum, moist, ph, sal, light)
        
        # 2. Get health & recommendations for these fake numbers
        analysis = ml_system.analyze_current_state(temp, hum, moist, ph, sal, light)
        
        # Combine them and send back to the simulation UI!
        return jsonify({
            "status": "success",
            "yield": yield_prediction,
            "analysis": analysis
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)