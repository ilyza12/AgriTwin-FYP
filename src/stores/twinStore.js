import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useTwinStore = defineStore('twin', () => {
  // =========================================
  // 1. STATE (The Data We Track)
  // =========================================

  // A. Live Sensor Readings (From ESP32 via MQTT)
  const liveSensors = ref({
    temperature: 24.5,
    humidity: 66.1,
    soilMoisture: 68.9,
    phLevel: 6.48,
    salinity: 0.84,
    lightIntensity: 75.3,
  })

  // B. Simulation Settings (For "What-If" Scenarios)
  const simParams = ref({
    temperature: 24, // Optimal for Rice: 20-35
    humidity: 70, // Optimal: 70-90
    soilMoisture: 85, // Optimal: 80-95
    phLevel: 6.0, // Optimal: 5.5-6.5
  })

  // =========================================
  // 2. GETTERS (Calculated Values)
  // =========================================

  // Calculate Crop Health based on SIMULATION sliders
  const visualHealth = computed(() => {
    const s = simParams.value
    // Logic: If conditions are extreme, plant wilts
    if (s.temperature > 38 || s.soilMoisture < 40 || s.phLevel < 4 || s.phLevel > 8) {
      return 'Wilted'
    }
    return 'Healthy'
  })

  // Calculate Yield Prediction (High/Medium/Low)
  const predictedYield = computed(() => {
    const s = simParams.value

    // Perfect conditions = High Yield
    if (
      s.temperature >= 22 &&
      s.temperature <= 32 &&
      s.soilMoisture >= 80 &&
      s.phLevel >= 5.5 &&
      s.phLevel <= 7
    ) {
      return 'High'
    }

    // Extreme conditions = Low Yield
    if (s.temperature > 38 || s.soilMoisture < 40) {
      return 'Low'
    }

    // Everything else = Medium
    return 'Medium'
  })

  // Check if LIVE sensors are critical (For Alerts)
  const liveAlerts = computed(() => {
    const alerts = []
    const l = liveSensors.value

    if (l.soilMoisture < 50) {
      alerts.push({
        type: 'critical',
        title: 'Soil Moisture Critically Low',
        message: 'Rice requires moisture level of 80-95%. Immediate irrigation required.',
      })
    }
    if (l.temperature > 35) {
      alerts.push({
        type: 'warning',
        title: 'High Temperature Alert',
        message: 'Temperature exceeding optimal range. Monitor crop stress levels.',
      })
    }
    return alerts
  })

  // =========================================
  // 3. ACTIONS (Functions to Change Data)
  // =========================================

  // Updates real sensor data (We will call this from MQTT later)
  function updateLiveReadings(payload) {
    liveSensors.value = { ...liveSensors.value, ...payload }
  }

  // Updates a single simulation slider
  function updateSimParam(key, value) {
    if (simParams.value.hasOwnProperty(key)) {
      simParams.value[key] = value
    }
  }

  // Reset simulation to "Perfect" defaults
  function resetSimulation() {
    simParams.value = {
      temperature: 24,
      humidity: 70,
      soilMoisture: 85,
      phLevel: 6.0,
    }
  }

  // Preset scenarios (Matches your ControlPanel.vue buttons)
  function applyPreset(scenario) {
    if (scenario === 'drought') {
      simParams.value = { temperature: 38, humidity: 30, soilMoisture: 20, phLevel: 6.0 }
    } else if (scenario === 'heatwave') {
      simParams.value = { temperature: 42, humidity: 40, soilMoisture: 50, phLevel: 6.0 }
    } else if (scenario === 'flood') {
      simParams.value = { temperature: 22, humidity: 95, soilMoisture: 100, phLevel: 6.0 }
    }
  }

  return {
    liveSensors,
    simParams,
    visualHealth,
    predictedYield,
    liveAlerts,
    updateLiveReadings,
    updateSimParam,
    resetSimulation,
    applyPreset,
  }
})
