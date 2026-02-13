import sqlite3
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

# --- 1. GET ROUTE ---
@app.route('/api/sensors/latest', methods=['GET'])
def get_latest_reading():
    global current_sensor_data
    
    if current_sensor_data:
        return jsonify(current_sensor_data)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM sensor_readings ORDER BY id DESC LIMIT 1')
    row = cursor.fetchone()
    conn.close()

    if row:
        return jsonify({
            "timestamp": row[1],
            "temperature": row[2],
            "humidity": row[3],
            "soilMoisture": row[4],
            "phLevel": row[5],
            "salinity": row[6],
            "lightIntensity": row[7]
        })
    else:
        return jsonify({"message": "No data found"}), 404

# --- 2. POST ROUTE ---
@app.route('/api/sensors/update', methods=['POST'])
def receive_sensor_data():
    global current_sensor_data, last_save_time
    
    data = request.json
    
    current_sensor_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "temperature": data.get('temperature', 0),
        "humidity": data.get('humidity', 0),
        "soilMoisture": data.get('soilMoisture', 0),
        "phLevel": data.get('phLevel', 0),
        "salinity": data.get('salinity', 0),
        "lightIntensity": data.get('lightIntensity', 0)
    }

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
        print(f"💾 SAVED to Database at {now}")
        return jsonify({"status": "saved", "message": "Data saved to DB"}), 201
    
    else:
        print(f"⚡ RAM Update Only (Next save in {5 - (now - last_save_time).seconds//60} mins)")
        return jsonify({"status": "live", "message": "Updated Live View only"}), 200

# --- 3. HISTORY ROUTE (MOVED TO LEFT MARGIN) ---
# This MUST be aligned with the other @app.route definitions
@app.route('/api/sensors/history', methods=['GET'])
def get_sensor_history():
    time_range = request.args.get('range', '24h')
    
    if time_range == '7d':
        cutoff_date = datetime.now() - timedelta(days=7)
    elif time_range == '30d':
        cutoff_date = datetime.now() - timedelta(days=30)
    else: 
        cutoff_date = datetime.now() - timedelta(days=1)
    
    cutoff_str = cutoff_date.strftime("%Y-%m-%d %H:%M:%S")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM sensor_readings 
        WHERE timestamp >= ? 
        ORDER BY timestamp ASC
    ''', (cutoff_str,))
    
    rows = cursor.fetchall()
    conn.close()
    
    history_data = []
    for row in rows:
        history_data.append({
            "timestamp": row[1],
            "temperature": row[2],
            "humidity": row[3],
            "soilMoisture": row[4],
            "phLevel": row[5],
            "salinity": row[6],
            "lightIntensity": row[7]
        })
        
    return jsonify(history_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)