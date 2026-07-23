# synthetic_training_data.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from capsicum_annuum_model import CapsicumAnnuumParametricModel

class SyntheticDataGenerator:
    """
    Generate 100% synthetic training data for Capsicum annuum
    """
    
    def __init__(self):
        # 🎯 DEFENSE: Synthetic Bootstrapping. Allows us to train robust Machine Learning models on thousands of extreme edge cases (like lethal salt toxicity) without needing to physically kill hundreds of real chili plants during the FYP timeframe.
        # Initialize the biological model
        self.model = CapsicumAnnuumParametricModel()
        
        self.optimal_values = {
            'temperature': {'mean': 23.5, 'std': 3.0, 'min': 17, 'max': 30},
            'humidity': {'mean': 75.0, 'std': 5.0, 'min': 65, 'max': 85},
            'soil_moisture': {'mean': 25.0, 'std': 1.0, 'min': 23, 'max': 27},
            'ph': {'mean': 6.15, 'std': 0.3, 'min': 5.5, 'max': 6.8},
            'salinity': {'mean': 0.75, 'std': 0.3, 'min': 0.0, 'max': 1.5},
            'light_intensity': {'mean': 600.0, 'std': 200.0, 'min': 17.3, 'max': 1224.0}
        }
    
    def generate_normal_conditions(self, num_samples=300):
        data = []
        print(f"📊 Generating {num_samples} normal condition samples...")
        
        for i in range(num_samples):
            # 🎯 DEFENSE: Gaussian Distribution. Uses normal statistical distribution to simulate natural, real-world sensor fluctuations rather than hardcoding static flatlines.
            temp = np.clip(np.random.normal(self.optimal_values['temperature']['mean'], self.optimal_values['temperature']['std']), 17, 30)
            humidity = np.clip(np.random.normal(self.optimal_values['humidity']['mean'], self.optimal_values['humidity']['std']), 65, 85)
            moisture = np.clip(np.random.normal(self.optimal_values['soil_moisture']['mean'], self.optimal_values['soil_moisture']['std']), 23, 27)
            ph = np.clip(np.random.normal(self.optimal_values['ph']['mean'], self.optimal_values['ph']['std']), 5.5, 6.8)
            salinity = np.clip(np.random.normal(self.optimal_values['salinity']['mean'], self.optimal_values['salinity']['std']), 0.0, 1.5)
            light = np.clip(np.random.normal(self.optimal_values['light_intensity']['mean'], self.optimal_values['light_intensity']['std']), 17.3, 1224)
            
            # Use the Parametric Model to calculate health!
            health = self.model.calculate_overall_health(temp, humidity, moisture, ph, salinity, light)
            
            data.append({
                'timestamp': datetime.now() + timedelta(hours=i),
                'temperature': round(temp, 2),
                'humidity': round(humidity, 2),
                'soil_moisture': round(moisture, 2),
                'ph_level': round(ph, 2),
                'salinity': round(salinity, 2),
                'light_intensity': round(light, 2),
                'health_score': round(health['health_score'], 2),
                'anomaly': 0,
                'label': 'normal'
            })
        return pd.DataFrame(data)
    
    def generate_anomaly_scenarios(self, num_samples=150):
        anomalies = []
        print(f"⚠️  Generating {num_samples} anomaly scenarios...")
        
        # 🎯 DEFENSE: Targeted Edge-Case Generation. Explicitly forces extreme multi-variable crises (e.g., heat + drought) so the Isolation Forest ML model learns to recognize compounding lethal stressors.
        anomaly_types = [
            ('high_temp', 20), ('low_temp', 15), ('drought', 25), 
            ('overwater', 20), ('high_salinity', 20), ('ph_acidic', 15), 
            ('ph_alkaline', 15), ('low_light', 10), ('combined_stress', 10)
        ]
        
        total_freq = sum(freq for _, freq in anomaly_types)
        samples_per_type = [(atype, int(freq / total_freq * num_samples)) for atype, freq in anomaly_types]
        
        for anomaly_type, count in samples_per_type:
            for _ in range(count):
                temp, humidity, moisture, ph, salinity, light = (
                    self.optimal_values['temperature']['mean'], self.optimal_values['humidity']['mean'],
                    self.optimal_values['soil_moisture']['mean'], self.optimal_values['ph']['mean'],
                    self.optimal_values['salinity']['mean'], self.optimal_values['light_intensity']['mean']
                )
                
                if anomaly_type == 'high_temp': temp = np.random.uniform(32, 38); humidity = np.random.uniform(40, 60)
                elif anomaly_type == 'low_temp': temp = np.random.uniform(8, 16)
                elif anomaly_type == 'drought': moisture = np.random.uniform(10, 18); salinity = np.random.uniform(1.6, 3.5)
                elif anomaly_type == 'overwater': moisture = np.random.uniform(28, 35)
                elif anomaly_type == 'high_salinity': salinity = np.random.uniform(1.6, 8.6)
                elif anomaly_type == 'ph_acidic': ph = np.random.uniform(4.0, 5.2)
                elif anomaly_type == 'ph_alkaline': ph = np.random.uniform(7.0, 8.5)
                elif anomaly_type == 'low_light': light = np.random.uniform(0, 15)
                elif anomaly_type == 'combined_stress':
                    temp = np.random.uniform(31, 35); moisture = np.random.uniform(10, 18); salinity = np.random.uniform(2.0, 4.0)
                
                health = self.model.calculate_overall_health(temp, humidity, moisture, ph, salinity, light)
                
                anomalies.append({
                    'timestamp': datetime.now() + timedelta(hours=random.randint(0, 1000)),
                    'temperature': round(temp, 2),
                    'humidity': round(humidity, 2),
                    'soil_moisture': round(moisture, 2),
                    'ph_level': round(ph, 2),
                    'salinity': round(salinity, 2),
                    'light_intensity': round(light, 2),
                    'health_score': round(health['health_score'], 2),
                    'anomaly': 1,
                    'label': anomaly_type
                })
        return pd.DataFrame(anomalies)
    
    def generate_yield_training_data(self, num_samples=500):
        print(f"🌱 Generating {num_samples} yield training samples...")
        yield_data = []
        
        for _ in range(num_samples):
            days_observed = np.random.randint(30, 120)
            base_health = np.random.uniform(40, 100)
            
            # 🎯 DEFENSE: Feature Correlation. Artificially grouping the data ensures the Machine Learning models (Random Forest) correctly map bad environmental histories to low fruit counts.
            if base_health > 80:
                avg_temp = np.random.normal(25, 2)
                avg_humidity = np.random.normal(72, 4)
                avg_moisture = np.random.normal(25, 1.5)
                avg_ph = np.random.normal(6.2, 0.25)
                avg_salinity = np.random.normal(0.8, 0.3)
                avg_light = np.random.normal(800, 100)
            elif base_health > 60:
                avg_temp = np.random.normal(28, 3)
                avg_humidity = np.random.normal(65, 8)
                avg_moisture = np.random.normal(20, 3)
                avg_ph = np.random.normal(5.8, 0.5)
                avg_salinity = np.random.normal(1.3, 0.4)
                avg_light = np.random.normal(400, 150)
            else:
                avg_temp = np.random.normal(32, 4)
                avg_humidity = np.random.normal(55, 12)
                avg_moisture = np.random.normal(15, 5)
                avg_ph = np.random.normal(5.0, 0.8)
                avg_salinity = np.random.normal(2.5, 1.0)
                avg_light = np.random.normal(100, 50)
            
            health = self.model.calculate_overall_health(avg_temp, avg_humidity, avg_moisture, avg_ph, avg_salinity, avg_light)
            yield_pred = self.model.predict_yield(health['health_score'], days_observed)
            
            yield_data.append({
                'avg_temperature': round(avg_temp, 2),
                'avg_humidity': round(avg_humidity, 2),
                'avg_soil_moisture': round(avg_moisture, 2),
                'avg_ph_level': round(avg_ph, 2),
                'avg_salinity': round(avg_salinity, 2),
                'avg_light_intensity': round(max(0, avg_light), 2),
                'avg_health_score': round(health['health_score'], 2),
                'fruit_count': yield_pred['fruit_count'],           # <-- ADDED THIS
                'total_weight_g': yield_pred['total_weight_g'],     # <-- ADDED THIS
                'yield_class': yield_pred['yield_class']  # Target column for ML
            })
            
        return pd.DataFrame(yield_data)
    
    def generate_complete_dataset(self):
        print("="*70)
        print("GENERATING COMPLETE SYNTHETIC TRAINING DATASET")
        print("="*70)
        
        # 🎯 DEFENSE: Realistic Class Imbalance. Generating 9,500 normal points and only 500 anomaly points mimics a real-world IoT deployment, ensuring the AI doesn't over-predict failures.
        normal_data = self.generate_normal_conditions(num_samples=9500)
        anomaly_data = self.generate_anomaly_scenarios(num_samples=500)
        sensor_data = pd.concat([normal_data, anomaly_data], ignore_index=True).sample(frac=1, random_state=42).reset_index(drop=True)
        yield_data = self.generate_yield_training_data(num_samples=2000)
        
        return {'sensor_data': sensor_data, 'yield_data': yield_data}

if __name__ == "__main__":
    generator = SyntheticDataGenerator()
    datasets = generator.generate_complete_dataset()
    
    print("\n💾 Saving datasets...")
    datasets['sensor_data'].to_csv('training_data_anomaly_detection.csv', index=False)
    datasets['yield_data'].to_csv('training_data_yield_prediction.csv', index=False)
    print("✅ Files saved successfully!")