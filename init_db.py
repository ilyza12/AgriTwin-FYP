import sqlite3

def initialize_database():
    # This creates the farm_data.db file if it doesn't exist
    conn = sqlite3.connect('farm_data.db')
    cursor = conn.cursor()

    # Create the table using your exact schema
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
    print("✅ Successfully initialized an empty farm_data.db database with the sensor_readings table!")

if __name__ == '__main__':
    initialize_database()