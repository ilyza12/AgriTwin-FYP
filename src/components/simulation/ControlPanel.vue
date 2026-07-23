<template>
  <div class="control-panel">
    <div class="panel-header">
      <div class="title">
        <span class="icon">🎛️</span>
        <h3>Scenario Simulation Panel</h3>
      </div>
      <button class="reset-btn" @click="$emit('reset')">↺ Reset to Optimal</button>
    </div>

    <div class="sliders-container">
      <div class="slider-item" v-for="(config, key) in sliders" :key="key">
        <div class="slider-top">
          <label>{{ config.label }}</label>
          <span class="badge" :class="getStatus(key, modelValue[key])">
            {{ getStatusText(key, modelValue[key]) }}
          </span>
        </div>

        <input
          type="range"
          :min="config.min"
          :max="config.max"
          :step="config.step"
          :value="modelValue[key]"
          @input="$emit('update:modelValue', { ...modelValue, [key]: Number($event.target.value) })"
        />

        <div class="slider-bottom">
          <span class="min">{{ config.min }}{{ config.unit }}</span>
          
          <span class="optimal-text">Optimal: {{ config.optimal }}</span>
          
          <span class="max" v-if="key === 'lightIntensity'">
            {{ modelValue[key] }}% (~{{ Math.round((modelValue[key] / 100) * 2000) }} µmol)
          </span>
          <span class="max" v-else>
            {{ modelValue[key] }} {{ config.unit }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps(['modelValue'])
defineEmits(['update:modelValue', 'reset', 'preset'])

// 1. UPDATED RANGES: Perfectly tuned for Capsicum annuum!

// 🎯 DEFENSE: Encapsulated Configuration. Storing all agronomic parameters (min, max, steps, and optimal thresholds) in one JSON object
const sliders = {
  temperature: {
    label: 'Temperature',
    min: 0,
    max: 50,
    step: 0.5,
    unit: '°C',
    optimal: '17-30°C',
    optMin: 17,
    optMax: 30,
    subMin: 8,    // base temp — below this is critical
    subMax: 35,   // max temp — above this is critical
  },
  humidity: {
    label: 'Humidity',
    min: 0,
    max: 100,
    step: 1,
    unit: '%',
    optimal: '65-85%',
    optMin: 65,
    optMax: 85,
    subMin: 40,   // below this is critical
    subMax: 95,   // above this is critical
  },
  soilMoisture: {
    label: 'Soil Moisture',
    min: 0,
    max: 50, // Reduced from 100 to 50 so users can easily select the 26.1% mark
    step: 0.1, // Added decimal precision for the 13.1 and 26.1 bounds
    unit: '%',
    optimal: '23-27%',
    optMin: 23,
    optMax: 27,
    subMin: 13.1, // wilting point — below this is critical
    subMax: 32,   // above this is critical
  },
  phLevel: {
    label: 'pH Level',
    min: 0,
    max: 14,
    step: 0.1,
    unit: '',
    optimal: '5.5-6.8',
    optMin: 5.5,
    optMax: 6.8,
    subMin: 4.3,  // min pH — below this is critical
    subMax: 8.3,  // max pH — above this is critical
  },
  salinity: {
    label: 'Salinity',
    min: 0,
    max: 10, 
    step: 0.1,
    unit: 'dS/m',
    optimal: '1.0-1.5',   // 🚀 FIXED: Shows correct sweet spot text
    optMin: 1.0,          // 🚀 FIXED: The "Fuel Light" warning boundary
    optMax: 1.5,
    subMin: 0.3,          // 🚀 ADDED: The starvation critical boundary
    subMax: 3.0,          
    critMax: 8.64 
  },
  lightIntensity: {
    label: 'Light Intensity',
    min: 0,
    max: 100, // True percentage!
    step: 1,
    unit: '%',
    optimal: '30–61% (600–1224 µmol)',
    optMin: 30,   // 600 µmol / 2000 * 100
    optMax: 61,   // 1224 µmol / 2000 * 100 (LSP)
    subMin: 1,    // 17.3 µmol / 2000 * 100 ≈ 0.87% → round to 1% (LCP)
    subMax: 75,   // 1500 µmol / 2000 * 100
    // below subMin (LCP) = critical; above subMax = critical
  },
}

// 3-tier: 'optimal' | 'suboptimal' | 'critical'

// 🎯 DEFENSE: Client-Side Evaluation. This function calculates the Optimal/Suboptimal/Critical UI status locally in the browser.
const getStatus = (key, val) => {
  const s = sliders[key]
  if (!s) return 'optimal'

  // 🚀 DELETED the special "salinity" override block here!
  // Now salinity behaves exactly like pH and Temperature.

  // all other params: critical outer band, suboptimal middle, optimal core
  if (val < s.subMin || val > s.subMax) return 'critical'
  if (val < s.optMin || val > s.optMax) return 'suboptimal'
  return 'optimal'
}

const getStatusText = (key, val) => {
  const s = getStatus(key, val)
  if (s === 'optimal')    return 'Optimal'
  if (s === 'suboptimal') return 'Suboptimal'
  return 'Critical'
}

// use this to drive badge color in your template:
// 'optimal' → green, 'suboptimal' → amber, 'critical' → red
const getStatusClass = (key, val) => {
  const s = getStatus(key, val)
  return {
    'status-optimal':    s === 'optimal',
    'status-suboptimal': s === 'suboptimal',
    'status-critical':   s === 'critical',
  }
}
</script>

<style scoped>
/* Keep your existing styles exactly as they were */
.control-panel {
  background: white;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
  height: 100%;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}
.title {
  display: flex;
  gap: 10px;
  align-items: center;
}
.title h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #2c3e50;
}
.reset-btn {
  border: 1px solid #ddd;
  background: white;
  padding: 8px 15px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  color: #2c3e50;
}
.reset-btn:hover {
  background: #f8f9fa;
}

.section-label {
  font-size: 0.9rem;
  color: #7f8c8d;
  margin-bottom: 10px;
}

.scenario-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 15px;
  margin-bottom: 30px;
}
.scenario-card {
  border: 1px solid #eee;
  background: white;
  padding: 15px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}
.scenario-card:hover {
  border-color: #3498db;
  background: #f0f8ff;
}
.emoji {
  font-size: 1.5rem;
}

/* SLIDERS */
.slider-item {
  margin-bottom: 20px;
}
.slider-top {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}
.slider-top label {
  font-weight: 600;
  color: #34495e;
  font-size: 0.9rem;
}

.badge {
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 0.7rem;
  color: white;
  font-weight: bold;
}
.badge.optimal {
  background: #27ae60;
}
.badge.critical {
  background: #e74c3c;
}
.badge.suboptimal {
  background: #f39c12;
}
input[type='range'] {
  width: 100%;
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  outline: none;
  appearance: none;
}
input[type='range']::-webkit-slider-thumb {
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: white;
  border: 2px solid #2c3e50;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.slider-bottom {
  display: flex;
  justify-content: space-between;
  margin-top: 5px;
  font-size: 0.75rem;
  color: #95a5a6;
}
.max {
  font-weight: bold;
  color: #2c3e50;
}
</style>