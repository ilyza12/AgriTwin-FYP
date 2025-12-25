<template>
  <div class="control-panel">
    <div class="panel-header">
      <div class="title">
        <span class="icon">🎛️</span>
        <h3>Scenario Simulation Panel</h3>
      </div>
      <button class="reset-btn" @click="$emit('reset')">↺ Reset to Optimal</button>
    </div>

    <div class="section-label">Quick Scenarios</div>
    <div class="scenario-grid">
      <button class="scenario-card" @click="$emit('preset', 'drought')">
        <span class="emoji">🔥</span>
        <span>Drought</span>
      </button>
      <button class="scenario-card" @click="$emit('preset', 'heatwave')">
        <span class="emoji">♨️</span>
        <span>Heatwave</span>
      </button>
      <button class="scenario-card" @click="$emit('preset', 'flood')">
        <span class="emoji">💧</span>
        <span>Flood</span>
      </button>
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
          <span class="max">{{ modelValue[key] }} {{ config.unit }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps(['modelValue'])
defineEmits(['update:modelValue', 'reset', 'preset'])

// 1. I added 'optMin' and 'optMax' to every slider so the code knows the limits
const sliders = {
  temperature: {
    label: 'Temperature',
    min: 0,
    max: 50,
    step: 1,
    unit: '°C',
    optimal: '20-35°C',
    optMin: 20,
    optMax: 35,
  },
  humidity: {
    label: 'Humidity',
    min: 0,
    max: 100,
    step: 1,
    unit: '%',
    optimal: '70-90%',
    optMin: 70,
    optMax: 90,
  },
  soilMoisture: {
    label: 'Soil Moisture',
    min: 0,
    max: 100,
    step: 1,
    unit: '%',
    optimal: '80-95%',
    optMin: 80,
    optMax: 95,
  },
  phLevel: {
    label: 'pH Level',
    min: 0,
    max: 14,
    step: 0.1,
    unit: '',
    optimal: '5.5-6.5',
    optMin: 5.5,
    optMax: 6.5,
  },
  salinity: {
    label: 'Salinity',
    min: 0,
    max: 5,
    step: 0.1,
    unit: 'dS/m',
    optimal: '0.0-0.5',
    optMin: 0,
    optMax: 0.5,
  },
  lightIntensity: {
    label: 'Light Intensity',
    min: 0,
    max: 100,
    step: 1,
    unit: '%',
    optimal: '60-80%',
    optMin: 60,
    optMax: 80,
  },
}

// 2. Updated Logic: Checks if value is lower than Min OR higher than Max
const getStatus = (key, val) => {
  const { optMin, optMax } = sliders[key]
  if (val < optMin || val > optMax) return 'critical' // Returns Red class
  return 'optimal' // Returns Green class
}

const getStatusText = (key, val) => {
  const { optMin, optMax } = sliders[key]
  if (val < optMin || val > optMax) return 'Out of Range'
  return 'Optimal'
}
</script>

<style scoped>
/* (Your styles remain exactly the same) */
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
