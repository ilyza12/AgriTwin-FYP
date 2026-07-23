# ml_inference.py

"""
ML Inference System for Live & Simulation Dashboards
Loads trained models and provides real-time predictions
"""

import joblib
import numpy as np
import sqlite3
from datetime import datetime, timedelta
from capsicum_annuum_model import CapsicumAnnuumParametricModel

class LiveMLInference:
    """Real-time ML predictions for Vue.js dashboards"""
    
    def __init__(self, db_path='farm_data.db'):
        """Initialize and load all trained models"""
        self.db_path = db_path
        print("📦 Loading ML models...")
        
        try:
            # 🎯 DEFENSE: Pre-loading. Models (.pkl) are loaded into RAM once on startup. Prevents massive disk I/O bottlenecks during live Vue API requests.
            self.anomaly_model = joblib.load('models/anomaly_detector.pkl')
            self.yield_classifier = joblib.load('models/yield_classifier.pkl')
            self.yield_count_model = joblib.load('models/yield_predictor_count.pkl')
            self.yield_weight_model = joblib.load('models/yield_predictor_weight.pkl')
            print("✅ Models loaded successfully!")
        except FileNotFoundError as e: 
            print(f"❌ Error: Could not find model files!")
            raise e
        
        # Load parametric model for recommendations
        self.param_model = CapsicumAnnuumParametricModel()
        print("✅ ML Inference System ready!\n")
    
    # ========== ANOMALY DETECTION ==========
    def detect_anomaly(self, temp, humidity, soil_moisture, ph, salinity, light):
        # Features must strictly match: [temperature, humidity, soil_moisture, ph_level, salinity, light_intensity]
        features = np.array([[temp, humidity, soil_moisture, ph, salinity, light]])
        
        # 🎯 DEFENSE: Hybrid AI. Uses unsupervised ML (-1) to catch invisible multi-variable patterns, paired with explicit hardcoded thresholds as a biological safety net.
        prediction = self.anomaly_model.predict(features)[0]
        anomaly_score = self.anomaly_model.score_samples(features)[0]
        is_anomaly = bool(prediction == -1)
        
        issues = []
        
        # 1. TEMPERATURE
        if temp <= 8.0 or temp >= 35.0:
            issues.append(f"CRITICAL: Temp ({temp:.1f}°C) breached survival limits (8-35°C)") 
        elif temp < 17.0 or temp > 30.0:
            issues.append(f"WARNING: Temp ({temp:.1f}°C) is sub-optimal")

        # 2. HUMIDITY
        if humidity < 65 or humidity > 85: 
            issues.append(f"WARNING: Humidity ({humidity:.1f}%) causing stress/disease risk")

        # 3. SOIL MOISTURE
        if soil_moisture > 32:
            issues.append(f"CRITICAL: Soil moisture at ({soil_moisture:.1f}%) Soil waterlogged — anaerobic conditions")
        elif soil_moisture > 27:
            issues.append(f"WARNING: Soil moisture ({soil_moisture:.1f}%) above optimal range")
        elif soil_moisture < 13.1:
            issues.append(f"CRITICAL: Soil moisture ({soil_moisture:.1f}%) at wilting point")
        elif soil_moisture < 23:
            issues.append(f"WARNING: Soil moisture ({soil_moisture:.1f}%) below optimal range")

        # 4. pH LEVEL
        if ph <= 4.3 or ph >= 8.3:
            issues.append(f"CRITICAL: pH ({ph:.2f}) limits breached, risking nutrient lockout")
        elif ph < 5.5 or ph > 6.8:
            issues.append(f"WARNING: pH ({ph:.2f}) is outside optimal nutrient uptake range")

        # 5. SALINITY
        if salinity > 1.5: 
            issues.append(f"WARNING: Salinity ({salinity:.2f} dS/m) above threshold")

        # 6. LIGHT INTENSITY (PPFD)
        if light <= 17.3:
            issues.append(f"CRITICAL: Light ({light:.1f} µmol) below Compensation Point ")
        elif light >= 1224.0:
            issues.append(f"CRITICAL: Light ({light:.1f} µmol) exceeds Saturation Point ")
        
        if is_anomaly:
            alert_level = 'critical' if len(issues) >= 3 else 'warning' if len(issues) >= 2 else 'caution'
            message = "⚠️ ANOMALY DETECTED: " + " | ".join(issues)
        else:
            alert_level = 'normal'
            message = "✓ All parameters within normal range" 
        
        return {
            'is_anomaly': is_anomaly,
            'anomaly_score': round(anomaly_score, 3),
            'alert_level': alert_level,
            'issues': issues,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
    
    # ========== LIVE DASHBOARD YIELD (From Database) ==========
    def predict_yield_live(self, days_observed=7):
        """Predict yield based on historical sensor data from SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 🎯 DEFENSE: Time-Series Smoothing. Averaging 7 days of data filters out momentary hardware glitches to provide a stable, biologically accurate trend line.
        query = f'''
            SELECT 
                COUNT(*) as count,
                AVG(temperature) as avg_temp,
                AVG(humidity) as avg_humidity,
                AVG(soil_moisture) as avg_moisture,
                AVG(ph_level) as avg_ph,
                AVG(salinity) as avg_salinity,
                AVG(light_intensity) as avg_light
            FROM sensor_readings
            WHERE timestamp >= datetime('now', '-{days_observed} days')
        '''
        cursor.execute(query)
        row = cursor.fetchone()
        conn.close()
        
        if not row or row[0] < 10:
            return {'status': 'insufficient_data', 'message': 'Need at least 10 historical readings.'}
        
        count, avg_temp, avg_humidity, avg_moisture, avg_ph, avg_salinity, avg_light = row
        
        # Calculate health using parametric model
        health = self.param_model.calculate_overall_health(avg_temp, avg_humidity, avg_moisture, avg_ph, avg_salinity, avg_light)
        
        # Use our new simulation method to do the actual prediction
        prediction = self.predict_yield_simulation(avg_temp, avg_humidity, avg_moisture, avg_ph, avg_salinity, avg_light)
        prediction['based_on_readings'] = count
        return prediction

    # ========== SIMULATION DASHBOARD YIELD (From Sliders) ==========
    def predict_yield_simulation(self, temp, humidity, moisture, ph, salinity, light):
        """Predict yield instantly based on hypothetical slider inputs"""
        
        # 1. Calculate the hypothetical health score
        health = self.param_model.calculate_overall_health(temp, humidity, moisture, ph, salinity, light)
        avg_health = health['health_score']
        
        # 2. Prepare exact 7 features for Random Forest models
        features = np.array([[temp, humidity, moisture, ph, salinity, light, avg_health]])
        
        # 3. Get AI Predictions
        yield_class = self.yield_classifier.predict(features)[0]
        fruit_count = int(self.yield_count_model.predict(features)[0])
        total_weight = self.yield_weight_model.predict(features)[0]
        
        return {
            'status': 'success',
            'yield_class': yield_class, # High, Medium, or Low
            'predicted_fruit_count': max(0, fruit_count),
            'predicted_total_weight_g': round(max(0, total_weight), 1),
            'hypothetical_health_score': round(avg_health, 1)
        }

    # ========== OPTIMAL IRRIGATION MATH ==========
    def calculate_optimal_irrigation(self, current_vwc, pot_volume_liters=1.97):
        """
        Calculates the exact liters of water needed to return the soil to Field Capacity
        without causing runoff or wasting resources.
        """
        # FAO Standard Field Capacity for Loam is ~26.1%
        TARGET_VWC = 26.1 
        
        # If the soil is already wetter than optimal, we need 0 liters
        if current_vwc >= TARGET_VWC:
            return 0.0
            
        # Calculate the percentage of empty pore space that needs water
        vwc_deficit_percent = TARGET_VWC - current_vwc
        
        # Convert percentage to a decimal, multiply by total dirt volume
        liters_needed = (vwc_deficit_percent / 100.0) * pot_volume_liters
        
        return round(liters_needed, 3) # Rounding to 3 decimals gives exact milliliters
    
    # ========== COMPLETE LIVE ANALYSIS ROUTE ==========
    def analyze_current_state(self, temp, humidity, soil_moisture, ph, salinity, light):
        anomaly_result = self.detect_anomaly(temp, humidity, soil_moisture, ph, salinity, light)
        health_data = self.param_model.calculate_overall_health(temp, humidity, soil_moisture, ph, salinity, light)
        fertilization = self.param_model.recommend_fertilization(ph, salinity, days_since_last_fert=15)
        
        # --- NEW OPTIMAL IRRIGATION LOGIC ---
        liters_needed = self.calculate_optimal_irrigation(soil_moisture)
        
        # Format the dictionary exactly how your Vue dashboard expects it
        irrigation = {
            'action': 'irrigate' if liters_needed > 0 else 'wait',
            'amount_liters': liters_needed,
            'message': f"Apply exactly {liters_needed}L to reach 26.1% Field Capacity." if liters_needed > 0 else "Soil is at optimal hydration."
        }
        
        # 🎯 DEFENSE: Unified Payload. Aggregating all AI predictions and parametric math into one JSON dictionary minimizes HTTP requests, reducing network latency.
        return {
            'timestamp': datetime.now().isoformat(),
            'current_readings': {'temperature': temp, 'humidity': humidity, 'soil_moisture': soil_moisture, 'ph': ph, 'salinity': salinity, 'light_intensity': light},
            'anomaly_detection': anomaly_result,
            'health': {'overall_score': health_data['health_score']},
            'recommendations': {'irrigation': irrigation, 'fertilization': fertilization}
        }