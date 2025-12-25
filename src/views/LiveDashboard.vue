<template>
  <div class="dashboard-container">
    <NavBar />

    <main class="scrollable-content">
      <div class="tabs-container">
        <div class="tab active">⚡ Live Dashboard</div>
        <div class="tab" @click="$router.push('/simulation')">🎛 Simulation</div>
      </div>

      <section class="section-block">
        <div class="section-header">
          <h3>Real-Time Sensor Analytics</h3>
          <p>🌾 Rice - Water-intensive cereal crop, requires flooded conditions</p>
        </div>
        <div class="sensor-grid">
          <SensorCard
            title="Temperature"
            :value="liveSensors.temperature"
            unit="°C"
            icon="🌡️"
            range="20-35°C"
            :percentage="(liveSensors.temperature / 50) * 100"
            :isCritical="liveSensors.temperature > 35"
          />
          <SensorCard
            title="Humidity"
            :value="liveSensors.humidity"
            unit="%"
            icon="💧"
            range="70-90%"
            :percentage="liveSensors.humidity"
            :isCritical="liveSensors.humidity < 70"
          />
          <SensorCard
            title="Soil Moisture"
            :value="liveSensors.soilMoisture"
            unit="%"
            icon="🌱"
            range="80-95%"
            :percentage="liveSensors.soilMoisture"
            :isCritical="liveSensors.soilMoisture < 80"
          />
          <SensorCard
            title="pH Level"
            :value="liveSensors.phLevel"
            unit=""
            icon="⚗️"
            range="5.5-6.5"
            :percentage="(liveSensors.phLevel / 14) * 100"
            :isCritical="liveSensors.phLevel < 5.5 || liveSensors.phLevel > 7"
          />
          <SensorCard
            title="Salinity"
            :value="liveSensors.salinity"
            unit="dS/m"
            icon="⚡"
            range="0.0-0.5 dS/m"
            :percentage="(liveSensors.salinity / 2) * 100"
            :isCritical="liveSensors.salinity > 0.5"
          />
          <SensorCard
            title="Light Intensity"
            :value="liveSensors.lightIntensity"
            unit="%"
            icon="☀️"
            range="60-80%"
            :percentage="liveSensors.lightIntensity"
            :isCritical="false"
          />
        </div>
      </section>

      <div class="split-section">
        <section class="section-block half">
          <div class="section-header row">
            <h3>📹 Live Camera Feed</h3>
            <span class="recording-badge">🔴 Recording</span>
          </div>
          <div class="camera-box">
            <div class="video-overlay"><span>11:24:22 PM</span><button>REC</button></div>
          </div>
        </section>

        <section class="section-block half">
          <div class="section-header">
            <h3>🧠 AI Insights</h3>
          </div>
          <div class="ai-card">
            <div class="yield-banner">
              <span class="label">Yield Prediction</span>
              <span class="prediction">Medium</span>
            </div>
            <div v-for="(alert, index) in liveAlerts" :key="index" class="alert-item">
              ⚠️ {{ alert.message }}
            </div>
            <div v-if="liveAlerts.length === 0" class="alert-item good">
              ✅ No critical issues detected.
            </div>
          </div>
        </section>
      </div>

      <section class="section-block">
        <div class="section-header">
          <h3>📉 Historical Trends</h3>
        </div>
        <HistoryTrends />
      </section>
    </main>
  </div>
</template>

<script setup>
import NavBar from '../components/common/NavBar.vue'
import SensorCard from '../components/live/SensorCard.vue'
// Import the component we just created
import HistoryTrends from '../components/live/HistoryTrends.vue'

import { useTwinStore } from '../stores/twinStore'
import { storeToRefs } from 'pinia'

const twinStore = useTwinStore()
const { liveSensors, liveAlerts } = storeToRefs(twinStore)
</script>

<style scoped>
/* --- 1. GLOBAL CONTAINER SETUP --- */
.dashboard-container {
  min-height: 100vh;
  width: 100%; /* Force full width */
  background-color: #f8f9fa;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  display: flex; /* Fixes alignment issues */
  flex-direction: column;
}

/* --- 2. SCROLLABLE AREA --- */
.scrollable-content {
  /* Pushes content down so it's not hidden behind the Fixed Header */
  padding-top: 100px;
  padding-bottom: 50px;

  /* Width Control */
  width: 100%;
  max-width: 1600px; /* Increased width for big screens */
  margin: 0 auto; /* Centers the content block */

  /* Spacing */
  padding-left: 20px;
  padding-right: 20px;
  box-sizing: border-box; /* Ensures padding doesn't break width */
}

/* --- 3. TABS --- */
.tabs-container {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
  padding-left: 5px; /* Aligns tabs with the cards */
}

.tab {
  background: white;
  padding: 10px 25px;
  border-radius: 25px;
  font-weight: 600;
  color: #7f8c8d;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: all 0.2s;
  border: 2px solid transparent; /* Prevents jumping when active */
}

.tab.active {
  background: white;
  color: #2c3e50;
  border-color: #2c3e50;
}

.tab:hover:not(.active) {
  background: #e9ecef;
}

/* --- 4. SECTIONS & GRID --- */
.section-block {
  margin-bottom: 40px;
  width: 100%; /* Ensures sections fill the container */
}

.section-header {
  margin-bottom: 20px;
  padding-left: 5px;
}

.section-header h3 {
  margin: 0 0 5px 0;
  color: #2c3e50;
  font-size: 1.25rem;
}

.section-header p {
  margin: 0;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.section-header.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* SENSOR GRID - RESPONSIVE */
.sensor-grid {
  display: grid;
  /* Auto-fit: Creates as many columns as fit on the screen */
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  width: 100%;
}

/* --- 5. SPLIT SECTION (Camera + AI) --- */
.split-section {
  display: flex;
  gap: 25px;
  flex-wrap: wrap; /* Wraps on small screens */
  margin-bottom: 40px;
  width: 100%;
}

.half {
  flex: 1; /* Both sides take equal space */
  min-width: 350px; /* But don't shrink below 350px */
}

/* CAMERA BOX */
.camera-box {
  height: 400px; /* Taller camera view */
  background: black;
  border-radius: 12px;
  position: relative;
  background-image: url('https://images.unsplash.com/photo-1586771107445-d3ca888129ff?q=80&w=2072&auto=format&fit=crop');
  background-size: cover;
  background-position: center;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.recording-badge {
  color: #e74c3c;
  font-weight: bold;
  font-size: 0.8rem;
  animation: pulse 2s infinite;
}

.video-overlay {
  position: absolute;
  bottom: 15px;
  left: 15px;
  color: white;
  display: flex;
  gap: 10px;
  align-items: center;
  font-family: monospace;
  background: rgba(0, 0, 0, 0.6);
  padding: 5px 10px;
  border-radius: 4px;
}

.video-overlay button {
  background: #e74c3c;
  border: none;
  color: white;
  font-weight: bold;
  padding: 2px 8px;
  border-radius: 3px;
  cursor: pointer;
}

/* AI INSIGHTS CARD */
.ai-card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
  height: 100%; /* Matches height of camera box */
  display: flex;
  flex-direction: column;
}

.yield-banner {
  background: #fff9c4;
  padding: 15px 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.prediction {
  font-size: 1.5rem;
  font-weight: bold;
  color: #f57f17;
}

.alert-item {
  background: #ffebee;
  color: #c0392b;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 10px;
  font-weight: 500;
  border-left: 4px solid #c0392b;
  font-size: 0.9rem;
}

.alert-item.good {
  background: #e8f5e9;
  color: #27ae60;
  border-color: #27ae60;
}

@keyframes pulse {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
  100% {
    opacity: 1;
  }
}
</style>
