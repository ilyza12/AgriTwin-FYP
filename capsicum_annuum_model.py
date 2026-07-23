# capsicum_annuum_model.py

import numpy as np

class CapsicumAnnuumParametricModel:
    """
    Parametric model for Capsicum annuum (Long Red Chili)
    All parameters based on documented research (FAO, GAEZ, Published Studies)
    """
    
    def __init__(self):
        # ========== TEMPERATURE PARAMETERS ==========
        self.base_temp = 8          # °C - Below this, no growth
        self.optimal_temp_min = 17  # °C - Lower optimal bound
        self.optimal_temp_max = 30  # °C - Upper optimal bound
        self.max_temp = 35          # °C - Above this, damage occurs
        
        # ========== HUMIDITY PARAMETERS ==========
        self.optimal_humidity_min = 65  # %
        self.optimal_humidity_max = 85  # %
        self.critical_humidity_min = 40 # % - Critical below this
        self.critical_humidity_max = 95 # % - Critical above this
        
        # ========== SOIL MOISTURE PARAMETERS ==========
        self.field_capacity = 26.1      # % volumetric
        self.wilting_point = 13.1       # % volumetric
        self.optimal_moisture_min = 23  # % - Lower bound (25% - 2)
        self.optimal_moisture_max = 27  # % - Upper bound (25% + 2)
        self.waterlogged = 32           # % - Critical high (anaerobic conditions)
        self.critical_depletion = 0.35  # 35% depletion threshold for irrigation trigger
        self.kc_fruiting = 1.05         # Crop coefficient (FAO-56)
        
        # ========== pH PARAMETERS ==========
        self.optimal_ph_min = 5.5
        self.optimal_ph_max = 6.8
        self.min_ph = 4.3
        self.max_ph = 8.3
        
        # ========== SALINITY PARAMETERS ==========
        self.salinity_critical_low = 0.3  # dS/m - Starvation
        self.salinity_optimal_min = 1.0   # dS/m - Lower optimal bound (The "Fuel Light")
        self.salinity_threshold = 1.5     # dS/m - No yield loss below (Maas-Hoffman limit)
        self.salinity_suboptimal = 3.0    # dS/m - Serious stress above this (critical)
        self.salinity_slope = 14          # % yield loss per dS/m above threshold
        self.max_salinity = 8.64          # dS/m - Lethal limit (Yr=0 from Maas-Hoffman) 
        
        # ========== LIGHT PARAMETERS ==========
        self.light_compensation = 17.3  # µmol/m²/s - Min for growth
        self.light_optimal_min = 600    # µmol/m²/s - Lower productive bound
        self.light_saturation = 1224    # µmol/m²/s - LSP, max useful light
        self.light_critical_high = 1500 # µmol/m²/s - Photoinhibition territory
        
        # ========== GROWTH & YIELD PARAMETERS ==========
        self.fruit_weight_avg = 15      # grams per fruit
        self.fruit_weight_std = 3       # Standard deviation
        self.base_fruits = 30           # Baseline fruit count (502.64g / 15g)
        self.days_green_to_red = 45     # Days for fruit to ripen
        self.max_fruits_per_plant = 50  # Maximum potential fruits

    def calc_temperature_stress(self, temp):
        """
        Critical:   temp <= 8°C  or  temp >= 35°C  → 0.0
        Suboptimal: 8 < temp < 17  or  30 < temp < 35 → 0.6
        Optimal:    17 <= temp <= 30  → 1.0
        """
        if temp <= self.base_temp or temp >= self.max_temp:
            return 0.0
        elif self.optimal_temp_min <= temp <= self.optimal_temp_max:
            return 1.0
        else:
            return 0.6  # suboptimal band (8–17°C or 30–35°C)

    def calc_humidity_stress(self, humidity):
        """
        Critical:   humidity < 40%  or  humidity > 95%  → 0.2
        Suboptimal: 40–65%  or  85–95%  → 0.7
        Optimal:    65–85%  → 1.0
        """
        if humidity < self.critical_humidity_min or humidity > self.critical_humidity_max:
            return 0.2
        elif self.optimal_humidity_min <= humidity <= self.optimal_humidity_max:
            return 1.0
        else:
            return 0.7  # suboptimal band

    def calc_soil_moisture_stress(self, moisture):
        # 🎯 DEFENSE: Distinguishes between physics (Field Capacity) and biology (Agronomic Optimal). Prevents the AI from accidentally drowning the plant by targeting the wrong metric.
        """
        Critical:   moisture <= 13.1% (wilting point)  → 0.0
                    moisture >= 32%   (waterlogged)     → 0.0
        Suboptimal: 13.1–23%  or  27–32%  → 0.5
        Optimal:    23–27%  → 1.0

        NOTE: Field Capacity (26.1%) is a soil physics reference point.
        It sits INSIDE the optimal range and must NOT be used as a ceiling.
        The agronomic optimal range from the paper is 25% ± 2 = 23–27%.
        """
        if moisture <= self.wilting_point:          # <= 13.1% — permanent wilting
            return 0.0
        elif moisture >= self.waterlogged:          # >= 32% — anaerobic, root death
            return 0.0
        elif self.optimal_moisture_min <= moisture <= self.optimal_moisture_max:  # 23–27%
            return 1.0
        else:
            return 0.5  # suboptimal band (13.1–23% or 27–32%)

    def calc_ph_stress(self, ph):
        """
        Critical:   ph <= 4.3  or  ph >= 8.3  → 0.0
        Suboptimal: 4.3–5.5  or  6.8–8.3  → 0.6
        Optimal:    5.5–6.8  → 1.0
        """
        if ph <= self.min_ph or ph >= self.max_ph:
            return 0.0
        elif self.optimal_ph_min <= ph <= self.optimal_ph_max:
            return 1.0
        else:
            return 0.6  # suboptimal band

    def calc_salinity_stress(self, salinity):
        """
        Critical Low:  salinity <= 0.3 dS/m → 0.4 (Severe starvation, stunts yield)
        Suboptimal:    0.3 < salinity < 1.0 → 0.7 (Fuel light on, slowing growth)
        Optimal:       1.0 <= salinity <= 1.5 → 1.0 (Sweet spot, perfect feeding)
        Suboptimal:    1.5 < salinity < 8.64 → gradual reduction via Maas-Hoffman
        Lethal:        >= 8.64 dS/m → 0.0 (Yr = 0)
        """
        if salinity <= self.salinity_critical_low:         # <= 0.3 dS/m
            return 0.4  # Heavy penalty for starvation
            
        elif salinity < self.salinity_optimal_min:         # 0.3 to 1.0 dS/m
            return 0.7  # Mild penalty for depleting nutrients
            
        elif self.salinity_optimal_min <= salinity <= self.salinity_threshold:  # 1.0 to 1.5 dS/m
            return 1.0  # Perfect health sweet spot
            
        elif salinity >= self.max_salinity:                # >= 8.64 dS/m
            return 0.0  # Lethal toxicity
            
        else:
            # Maas-Hoffman equation: 14% yield loss per dS/m above 1.5 threshold
            reduction = (self.salinity_slope / 100) * (salinity - self.salinity_threshold)
            return max(0.0, 1.0 - reduction)

    def calc_light_stress(self, light_intensity):
        """
        Critical low:  light <= 17.3 µmol (below LCP — plant consuming reserves)  → 0.0
        Suboptimal:    17.3–600 µmol  → 0.4 (insufficient photosynthesis)
        Optimal:       600–1224 µmol  → 1.0 (between productive min and LSP)
        Suboptimal:    1224–1500 µmol → 0.7 (above LSP, diminishing returns)
        Critical high: > 1500 µmol   → 0.2 (photoinhibition, chloroplast damage)
        """
        if light_intensity <= self.light_compensation:      # <= 17.3
            return 0.0
        elif light_intensity >= self.light_critical_high:   # >= 1500
            return 0.2
        elif self.light_optimal_min <= light_intensity <= self.light_saturation:  # 600–1224
            return 1.0
        elif light_intensity < self.light_optimal_min:      # 17.3–600
            return 0.4
        else:                                               # 1224–1500
            return 0.7

    def calculate_overall_health(self, temp, humidity, moisture, ph, salinity, light):
        # 🎯 DEFENSE: Liebig's Law of the Minimum. By multiplying (instead of averaging), the system understands that if water is at 0, the plant is dead (0% health), even if light and temperature are perfect. An average would incorrectly rate a dead plant at 80% health.
        """
        Multiplicative Stress Model (Liebig's Law of the Minimum).
        One zero factor collapses the entire score to zero.
        This correctly reflects that no perfect parameter can compensate
        for a completely absent one (e.g. zero water = dead plant).
        """
        temp_stress     = self.calc_temperature_stress(temp)
        humidity_stress = self.calc_humidity_stress(humidity)
        moisture_stress = self.calc_soil_moisture_stress(moisture)
        ph_stress       = self.calc_ph_stress(ph)
        salinity_stress = self.calc_salinity_stress(salinity)
        light_stress    = self.calc_light_stress(light)
        
        combined_stress = (
            temp_stress *
            humidity_stress *
            moisture_stress *
            ph_stress *
            salinity_stress *
            light_stress
        )
        
        return {
            'health_score':     round(combined_stress * 100, 2),
            'temp_stress':      round(temp_stress, 2),
            'humidity_stress':  round(humidity_stress, 2),
            'moisture_stress':  round(moisture_stress, 2),
            'ph_stress':        round(ph_stress, 2),
            'salinity_stress':  round(salinity_stress, 2),
            'light_stress':     round(light_stress, 2),
            'combined_stress':  round(combined_stress, 2)
        }

    def predict_yield(self, avg_health_score, days_observed):
        """
        Baseline: 30 fruits per plant (502.64g / 15g avg fruit weight, Kulai 907 variety)
        Yield class thresholds based on health-adjusted fruit count.
        """
        health_factor = avg_health_score / 100
        time_factor = min(days_observed / 90, 1.0)
        
        fruit_count = int(self.base_fruits * health_factor * time_factor)
        weights = np.random.normal(self.fruit_weight_avg, self.fruit_weight_std, max(fruit_count, 1))
        total_weight_g = max(0, np.sum(weights))
        
        if fruit_count > 20:    yield_class = 'High'
        elif fruit_count > 10:  yield_class = 'Medium'
        else:                   yield_class = 'Low'
        
        return {
            'fruit_count':    max(0, fruit_count),
            'total_weight_g': round(total_weight_g, 1),
            'quality_score':  round(avg_health_score * 0.9, 1),
            'yield_class':    yield_class
        }

    def recommend_irrigation(self, soil_moisture, temp, humidity):
        """
        Irrigation trigger based on FAO-56 critical depletion threshold (35%).
        Target is field capacity (26.1%) as the refill point.
        """
        available_water = self.field_capacity - self.wilting_point  # 26.1 - 13.1 = 13%
        critical_threshold = self.field_capacity - (available_water * self.critical_depletion)
        # = 26.1 - (13 * 0.35) = 26.1 - 4.55 = 21.55%

        # 🎯 DEFENSE: Precision Resource Management. AI calculates the exact volumetric deficit needed to hit Field Capacity without wasting water or leaching fertilizer out the bottom of the pot.
        if soil_moisture < critical_threshold:
            deficit = self.field_capacity - soil_moisture  # irrigate back to FC
            return {
                'action': 'irrigate',
                'amount_liters': round(deficit * 0.1970, 2),  # based on pot volume 1.97L
                'urgency': 'high'
            }
        elif soil_moisture > self.waterlogged:              # > 32%
            return {'action': 'drain', 'amount_liters': 0, 'urgency': 'high'}
        elif soil_moisture > self.optimal_moisture_max:     # 27–32%
            return {'action': 'reduce', 'amount_liters': 0, 'urgency': 'low'}
        else:
            return {'action': 'maintain', 'amount_liters': 0, 'urgency': 'none'}

    def recommend_fertilization(self, current_ph, current_salinity, days_since_last_fert=0):
        """
        Calculates precision fertigation using agronomic dimensional analysis.
        Formula: M = ((Target EC - Current EC) * 640 * Volume) / 1000
        """

        # 🎯 DEFENSE: Biological Safeguard. AI refuses to fertilize if pH is locked out, preventing toxic salt buildup in the soil when the plant physically cannot absorb it.

        # 1. Safety Check: Nutrient Lockout
        if current_ph < 5.8 or current_ph > 6.8:
            return {'action': 'lockout', 'message': 'Fix pH before fertilizing', 'amount_g': 0}
            
        # 2. Maas-Hoffman Toxicity Danger
        if current_salinity > self.salinity_threshold:
            return {'action': 'flush', 'message': 'Leach soil with pure water', 'amount_g': 0}
            
        # 3. Precision Deficit Feeding
        if current_salinity < self.salinity_optimal_min:
            target_ec = 1.4
            water_volume_l = 1.0  # Your standard 1-liter bottle
            
            # 🎯 DEFENSE: Dimensional Analysis applied to precision agriculture. Converts electrical conductivity back to physical gram weight.
            grams_needed = ((target_ec - current_salinity) * 640 * water_volume_l) / 1000
            
            return {
                'action': 'fertilize', 
                'npk_ratio': '5-10-15', 
                'amount_g': round(grams_needed, 2),
                'message': f"Mix {round(grams_needed, 2)}g into 1L watering bottle"
            }
            
        return {'action': 'maintain', 'message': 'Nutrients optimal', 'amount_g': 0}