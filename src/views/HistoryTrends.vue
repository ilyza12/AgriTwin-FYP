<template>
  <div class="dashboard-container">
    <NavBar />

    <main class="scrollable-content">
      <div class="page-header">
        <h2>📉 Historical Trends</h2>

        <div class="controls-row">
          <div class="metric-toggles">
            <button
              v-for="m in metrics"
              :key="m"
              :class="{ active: selectedMetric === m }"
              @click="selectedMetric = m"
            >
              {{ m }}
            </button>
          </div>

          <div class="time-filters">
            <button
              v-for="range in ['24h', '7d', '30d']"
              :key="range"
              :class="{ active: selectedRange === range }"
              @click="selectedRange = range"
            >
              {{ range }}
            </button>
          </div>
        </div>
      </div>

      <div class="chart-card">
        <Line :data="chartData" :options="chartOptions" class="chart-canvas" />
      </div>

      <div class="stats-grid">
        <div class="stat-card temp">
          <span class="label">Avg Temperature</span>
          <span class="value">24.2°C</span>
          <span class="trend up">▲ 1.2%</span>
        </div>
        <div class="stat-card moisture">
          <span class="label">Avg Soil Moisture</span>
          <span class="value">70.1%</span>
          <span class="trend down">▼ 0.5%</span>
        </div>
        <div class="stat-card ph">
          <span class="label">Avg pH Level</span>
          <span class="value">6.66</span>
          <span class="trend stable">− 0.0%</span>
        </div>
        <div class="stat-card salinity">
          <span class="label">Avg Salinity</span>
          <span class="value">1.08 dS/m</span>
          <span class="trend up">▲ 2.1%</span>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import NavBar from '../components/common/NavBar.vue'

// Import Chart.js components
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Line } from 'vue-chartjs'

// Register Chart.js modules so they work in Vue
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend)

// --- STATE ---
const selectedRange = ref('7d')
const selectedMetric = ref('All Metrics')
const metrics = ['All Metrics', 'Temperature', 'Soil Moisture', 'pH Level', 'Salinity']

// --- CHART DATA CONFIGURATION ---
const chartData = computed(() => {
  return {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        label: 'Temperature (°C)',
        backgroundColor: '#f39c12',
        borderColor: '#f39c12',
        data: [24, 25, 24.5, 23, 24, 25, 26],
        tension: 0.4, // Makes the line curved
        hidden: selectedMetric.value !== 'All Metrics' && selectedMetric.value !== 'Temperature',
      },
      {
        label: 'Soil Moisture (%)',
        backgroundColor: '#3498db',
        borderColor: '#3498db',
        data: [68, 70, 72, 71, 69, 68, 70],
        tension: 0.4,
        hidden: selectedMetric.value !== 'All Metrics' && selectedMetric.value !== 'Soil Moisture',
      },
      {
        label: 'pH Level',
        backgroundColor: '#9b59b6',
        borderColor: '#9b59b6',
        data: [6.5, 6.6, 6.5, 6.7, 6.6, 6.5, 6.6],
        tension: 0.4,
        hidden: selectedMetric.value !== 'All Metrics' && selectedMetric.value !== 'pH Level',
      },
      {
        label: 'Salinity (dS/m)',
        backgroundColor: '#e74c3c',
        borderColor: '#e74c3c',
        data: [1.0, 1.1, 1.0, 0.9, 1.0, 1.1, 1.2],
        tension: 0.4,
        hidden: selectedMetric.value !== 'All Metrics' && selectedMetric.value !== 'Salinity',
      },
    ],
  }
})

// --- CHART OPTIONS ---
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: 'index',
    intersect: false,
  },
  scales: {
    y: {
      beginAtZero: true,
      grid: { color: '#f0f0f0' },
    },
    x: {
      grid: { display: false },
    },
  },
  plugins: {
    legend: { position: 'bottom' },
  },
}
</script>

<style scoped>
.dashboard-container {
  min-height: 100vh;
  background-color: #f8f9fa;
  font-family: 'Segoe UI', sans-serif;
}
.scrollable-content {
  padding-top: 100px;
  padding-bottom: 50px;
  max-width: 1400px;
  margin: 0 auto;
  padding-left: 2rem;
  padding-right: 2rem;
}

/* Header & Controls */
.page-header {
  margin-bottom: 30px;
}
.page-header h2 {
  color: #2c3e50;
  margin-bottom: 20px;
}

.controls-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
}

.metric-toggles button,
.time-filters button {
  background: white;
  border: 1px solid #eee;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  color: #7f8c8d;
  margin-right: 8px;
  transition: all 0.2s;
}

.metric-toggles button:hover,
.time-filters button:hover {
  background: #f8f9fa;
}
.metric-toggles button.active {
  background: #2c3e50;
  color: white;
  border-color: #2c3e50;
}
.time-filters button.active {
  background: #27ae60;
  color: white;
  border-color: #27ae60;
}

/* Chart Area */
.chart-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  height: 400px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
  margin-bottom: 30px;
  position: relative;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  border-left: 5px solid #ddd;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
}

.stat-card.temp {
  border-color: #f39c12;
}
.stat-card.moisture {
  border-color: #3498db;
}
.stat-card.ph {
  border-color: #9b59b6;
}
.stat-card.salinity {
  border-color: #e74c3c;
}

.stat-card .label {
  display: block;
  font-size: 0.85rem;
  color: #7f8c8d;
  margin-bottom: 5px;
}
.stat-card .value {
  display: block;
  font-size: 1.5rem;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 5px;
}
.stat-card .trend {
  font-size: 0.8rem;
  font-weight: 600;
}
.trend.up {
  color: #e74c3c;
} /* Usually bad in agriculture depending on metric, or good for yield */
.trend.down {
  color: #c0392b;
}
.trend.stable {
  color: #7f8c8d;
}
</style>
