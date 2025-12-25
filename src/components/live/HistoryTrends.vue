<template>
  <div class="chart-widget">
    <div class="chart-header">
      <div class="toggles">
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
          v-for="t in timeRanges"
          :key="t"
          :class="{ active: selectedRange === t }"
          @click="selectedRange = t"
        >
          {{ t }}
        </button>
      </div>
    </div>

    <div class="canvas-wrapper">
      <Line :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'
import { Line } from 'vue-chartjs'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
)

// State
const metrics = ['All', 'Temperature', 'Moisture', 'pH', 'Humidity', 'Salinity', 'Light Intensity']
const timeRanges = ['24h', '7d', '30d']
const selectedMetric = ref('All')
const selectedRange = ref('7d')

// Mock Data (Static for now, can be connected to Store later)
const chartData = computed(() => {
  return {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        label: 'Temperature (°C)',
        data: [24, 25, 24.5, 23, 24, 25, 26],
        borderColor: '#f39c12',
        backgroundColor: 'rgba(243, 156, 18, 0.1)',
        fill: true,
        tension: 0.4,
        hidden: selectedMetric.value !== 'All' && selectedMetric.value !== 'Temperature',
      },
      {
        label: 'Moisture (%)',
        data: [68, 70, 72, 71, 69, 68, 70],
        borderColor: '#3498db',
        backgroundColor: 'rgba(52, 152, 219, 0.1)',
        fill: true,
        tension: 0.4,
        hidden: selectedMetric.value !== 'All' && selectedMetric.value !== 'Moisture',
      },
      {
        label: 'pH Level',
        data: [6.5, 6.6, 6.5, 6.7, 6.6, 6.5, 6.6],
        borderColor: '#9b59b6',
        backgroundColor: 'rgba(155, 89, 182, 0.1)',
        fill: true,
        tension: 0.4,
        hidden: selectedMetric.value !== 'All' && selectedMetric.value !== 'pH',
      },
      {
        label: 'Humidity Level (%)',
        data: [95.4, 88.3, 66.1, 72.9, 89.1, 60.4, 75.3],
        borderColor: '#ff42ae',
        backgroundColor: 'rgba(243, 167, 206, 0.1)',
        fill: true,
        tension: 0.4,
        hidden: selectedMetric.value !== 'All' && selectedMetric.value !== 'Humidity',
      },
      {
        label: 'Salinity Level (dS/m)',
        data: [0.12, 0.27, 0.54, 0.33, 0.84, 0.73, 0.41],
        borderColor: '#006806',
        backgroundColor: 'rgba(184, 218, 135, 0.1)',
        fill: true,
        tension: 0.4,
        hidden: selectedMetric.value !== 'All' && selectedMetric.value !== 'Salinity',
      },
      {
        label: 'Light Intensity Level (%)',
        data: [75.3, 79.7, 64.6, 50.3, 42.3, 69.7, 79.0],
        borderColor: '#c9ba00',
        backgroundColor: 'rgba(255, 243, 70, 0.1)',
        fill: true,
        tension: 0.4,
        hidden: selectedMetric.value !== 'All' && selectedMetric.value !== 'Light Intensity',
      },
    ],
  }
})

// Chart Configuration
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'bottom' },
  },
  scales: {
    y: { beginAtZero: true },
    x: { grid: { display: false } },
  },
}
</script>

<style scoped>
.chart-widget {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
  height: 100%;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

button {
  border: 1px solid #eee;
  background: white;
  padding: 6px 14px;
  border-radius: 6px;
  cursor: pointer;
  color: #7f8c8d;
  margin-right: 5px;
  font-size: 0.9rem;
  transition: all 0.2s;
}

button:hover {
  background: #f8f9fa;
}

button.active {
  background: #2c3e50;
  color: white;
  border-color: #2c3e50;
}

.time-filters button.active {
  background: #27ae60;
  border-color: #27ae60;
}

.canvas-wrapper {
  height: 350px;
  width: 100%;
}
</style>
