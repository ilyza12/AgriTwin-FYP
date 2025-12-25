<template>
  <div class="dashboard-container">
    <NavBar />

    <main class="scrollable-content">
      <div class="tabs-container">
        <div class="tab" @click="$router.push('/')">⚡ Live Dashboard</div>
        <div class="tab active">🎛 Simulation</div>
      </div>

      <div class="sim-grid">
        <div class="col-visual">
          <TwinVisual
            :temperature="simParams.temperature"
            :moisture="simParams.soilMoisture"
            :light="simParams.lightIntensity"
          />
        </div>
        <div class="col-controls">
          <ControlPanel v-model="simParams" @reset="resetSimulation" @preset="applyPreset" />
        </div>
      </div>

      <section class="section-block ai-section">
        <div class="section-header">
          <h3>🧠 AI Forecast and Recommendations</h3>
        </div>

        <div class="ai-card">
          <div class="yield-banner">
            <span class="label">📈 Yield Prediction</span>
            <span class="prediction">{{ predictedYield }}</span>
          </div>

          <div class="insight-label">AI-Generated Insights</div>
          <div class="alert-banner" :class="yieldPredictionClass">
            <span class="icon">⚠️</span>
            <div class="text">
              <strong>{{ insightTitle }}</strong>
              <p>{{ insightMessage }}</p>
            </div>
          </div>

          <div class="rec-list">
            <div class="rec-label">System Recommendations</div>
            <div class="rec-item" v-for="(rec, i) in recommendations" :key="i">
              <span class="tag high">High</span>
              <div class="rec-content">
                <strong>{{ rec.action }}</strong>
                <p>{{ rec.reason }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="section-block alerts-section">
        <div class="section-header row">
          <h3>🔔 System Alerts</h3>
          <span class="badge-count">{{ activeAlerts.length }} Critical</span>
        </div>

        <div class="alerts-list">
          <SystemAlert
            v-for="(alert, index) in activeAlerts"
            :key="index"
            :type="alert.type"
            :title="alert.title"
            :message="alert.message"
            :time="alert.time"
            :actionLabel="alert.actionLabel"
          />
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import NavBar from '../components/common/NavBar.vue'
import TwinVisual from '../components/simulation/TwinVisual.vue'
import ControlPanel from '../components/simulation/ControlPanel.vue'
import SystemAlert from '../components/common/SystemAlert.vue'
import { useTwinStore } from '../stores/twinStore'
import { storeToRefs } from 'pinia'

// Access the Store
const twinStore = useTwinStore()
const { simParams, predictedYield } = storeToRefs(twinStore)
const { resetSimulation, applyPreset } = twinStore

// --- LOGIC FOR AI SECTION ---
const yieldPredictionClass = computed(() =>
  predictedYield.value === 'Low' ? 'critical' : 'warning',
)

const insightTitle = computed(() => {
  if (predictedYield.value === 'Low') return 'Immediate Action Required'
  if (predictedYield.value === 'Medium') return 'Attention Needed'
  return 'Conditions Optimal'
})

const insightMessage = computed(() => {
  if (predictedYield.value === 'Low')
    return 'Critical conditions detected for Rice. Immediate intervention required to prevent crop damage.'
  return 'Current parameters may lead to reduced yield. Monitor soil moisture levels closely.'
})

// Mock Recommendations based on slider values
const recommendations = computed(() => {
  const recs = []
  if (simParams.value.soilMoisture < 80) {
    recs.push({
      action: 'Increase irrigation frequency',
      reason: `Soil moisture at ${simParams.value.soilMoisture}% (optimal for Rice: 80-95%)`,
    })
  }
  if (simParams.value.salinity > 0.5) {
    recs.push({
      action: 'Increase leaching to reduce salinity',
      reason: `Salinity at ${simParams.value.salinity} dS/m (optimal max 0.5)`,
    })
  }
  if (recs.length === 0) {
    recs.push({
      action: 'Maintain current schedule',
      reason: 'All parameters within optimal range.',
    })
  }
  return recs
})

// --- LOGIC FOR SYSTEM ALERTS (Bottom Section) ---
// This would typically come from a store, but here is the mock data matching your image
const activeAlerts = computed(() => [
  {
    type: 'critical',
    title: 'Soil Moisture Critically Low',
    message: 'Rice requires moisture level of 80-95%. Current: 25%. Immediate irrigation required.',
    time: '2 min ago',
    actionLabel: 'Take Action',
  },
  {
    type: 'warning',
    title: 'High Temperature Alert',
    message: 'Temperature exceeding optimal range for Rice. Monitor crop stress levels.',
    time: '15 min ago',
    actionLabel: 'Take Action',
  },
  {
    type: 'info',
    title: 'Irrigation Completed',
    message: 'Field B irrigation cycle completed successfully for Rice crop.',
    time: '1 hour ago',
  },
  {
    type: 'warning',
    title: 'pH Imbalance Detected',
    message: 'pH level outside optimal range (5.5-6.5). Consider corrective measures.',
    time: '2 hours ago',
    actionLabel: 'Take Action',
  },
  {
    type: 'success',
    title: 'Optimal Conditions',
    message: 'All parameters for Rice within optimal range.',
    time: '3 hours ago',
  },
])
</script>

<style scoped>
/* Reuse the Layout from LiveDashboard for consistency */
.dashboard-container {
  min-height: 100vh;
  width: 100%;
  background-color: #f8f9fa;
  font-family: 'Segoe UI', sans-serif;
  display: flex;
  flex-direction: column;
}
.scrollable-content {
  padding-top: 100px;
  padding-bottom: 50px;
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
  padding-left: 20px;
  padding-right: 20px;
  box-sizing: border-box;
}

/* TABS */
.tabs-container {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
}
.tab {
  background: white;
  padding: 10px 25px;
  border-radius: 25px;
  font-weight: 600;
  color: #7f8c8d;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s;
}
.tab.active {
  background: white;
  color: #2c3e50;
  border-color: #2c3e50;
}
.tab:hover:not(.active) {
  background: #e9ecef;
}

/* GRID LAYOUT FOR TOP SECTION */
.sim-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 25px;
  margin-bottom: 40px;
  min-height: 600px;
}
@media (max-width: 1000px) {
  .sim-grid {
    grid-template-columns: 1fr;
  }
}

/* AI SECTION STYLES */
.ai-section {
  margin-bottom: 40px;
}
.ai-card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
}
.yield-banner {
  background: #fff9c4;
  padding: 15px 20px;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}
.prediction {
  font-size: 2rem;
  font-weight: bold;
  color: #f57f17;
}

.insight-label,
.rec-label {
  font-size: 0.9rem;
  color: #7f8c8d;
  margin-bottom: 10px;
  display: block;
}
.alert-banner {
  padding: 15px;
  border-radius: 6px;
  display: flex;
  gap: 15px;
  align-items: flex-start;
  margin-bottom: 25px;
}
.alert-banner.critical {
  background: #ffebee;
  border-left: 4px solid #c0392b;
  color: #c0392b;
}
.alert-banner.warning {
  background: #fff3e0;
  border-left: 4px solid #f39c12;
  color: #e67e22;
}

.rec-item {
  border: 1px solid #eee;
  padding: 15px;
  border-radius: 8px;
  display: flex;
  gap: 15px;
  margin-bottom: 10px;
  align-items: center;
}
.tag.high {
  background: #e74c3c;
  color: white;
  padding: 4px 10px;
  border-radius: 4px;
  font-weight: bold;
  font-size: 0.75rem;
  height: fit-content;
}
.rec-content p {
  margin: 0;
  font-size: 0.85rem;
  color: #7f8c8d;
}

/* ALERTS SECTION */
.section-header.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.badge-count {
  background: #e74c3c;
  color: white;
  padding: 5px 10px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: bold;
}
.alerts-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
</style>
