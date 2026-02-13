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
import { ref, computed, onMounted, watch } from 'vue'
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
import api from '@/services/api' // Import the API

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
const selectedRange = ref('24h') // Default to 24h

// Reactive storage for DB data
const dbData = ref([])

// 1. FETCH DATA FUNCTION
const loadHistory = async () => {
  const data = await api.getHistory(selectedRange.value)
  dbData.value = data
}

// 2. Load on startup & when range changes
onMounted(loadHistory)
watch(selectedRange, loadHistory)

// 3. TRANSFORM DATA FOR CHART
const chartData = computed(() => {
  // If no data, return empty structure
  if (!dbData.value.length) return { labels: [], datasets: [] }

  // A. Create Labels (X-Axis)
  // Format timestamp: "14:00" (for 24h) or "Feb 10" (for 7d)
  const labels = dbData.value.map((row) => {
    const date = new Date(row.timestamp + 'Z')
    if (selectedRange.value === '24h') {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    } else {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' })
    }
  })

  // B. Create Datasets (Y-Axis)
  return {
    labels: labels,
    datasets: [
      {
        label: 'Temperature (°C)',
        data: dbData.value.map((d) => d.temperature),
        borderColor: '#f39c12',
        backgroundColor: 'rgba(243, 156, 18, 0.1)',
        fill: true,
        tension: 0.4,
        hidden: selectedMetric.value !== 'All' && selectedMetric.value !== 'Temperature',
      },
      {
        label: 'Moisture (%)',
        data: dbData.value.map((d) => d.soilMoisture), // Note: matches DB column name
        borderColor: '#3498db',
        backgroundColor: 'rgba(52, 152, 219, 0.1)',
        fill: true,
        tension: 0.4,
        hidden: selectedMetric.value !== 'All' && selectedMetric.value !== 'Moisture',
      },
      {
        label: 'pH Level',
        data: dbData.value.map((d) => d.phLevel),
        borderColor: '#9b59b6',
        backgroundColor: 'rgba(155, 89, 182, 0.1)',
        fill: true,
        tension: 0.4,
        hidden: selectedMetric.value !== 'All' && selectedMetric.value !== 'pH',
      },
      {
        label: 'Humidity (%)',
        data: dbData.value.map((d) => d.humidity),
        borderColor: '#ff42ae',
        backgroundColor: 'rgba(243, 167, 206, 0.1)',
        fill: true,
        tension: 0.4,
        hidden: selectedMetric.value !== 'All' && selectedMetric.value !== 'Humidity',
      },
      {
        label: 'Salinity (dS/m)',
        data: dbData.value.map((d) => d.salinity),
        borderColor: '#006806',
        backgroundColor: 'rgba(184, 218, 135, 0.1)',
        fill: true,
        tension: 0.4,
        hidden: selectedMetric.value !== 'All' && selectedMetric.value !== 'Salinity',
      },
      {
        label: 'Light Intensity (%)',
        data: dbData.value.map((d) => d.lightIntensity),
        borderColor: '#c9ba00',
        backgroundColor: 'rgba(255, 243, 70, 0.1)',
        fill: true,
        tension: 0.4,
        hidden: selectedMetric.value !== 'All' && selectedMetric.value !== 'Light Intensity',
      },
    ],
  }
})

// Keep chart options same
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { position: 'bottom' } },
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
