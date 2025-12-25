<template>
  <header class="fixed-header">
    <div class="header-content">
      <div class="brand-section">
        <div class="logo-box">
          <span class="logo-icon">🌱</span>
        </div>
        <div class="title-box">
          <h1>AgriTwin AI</h1>
          <p>Digital Twin Platform</p>
        </div>
        <div class="dashboard-info">
          <h2>Agriculture Digital Twin Dashboard</h2>
          <p class="current-date">{{ currentDate }}</p>
        </div>
      </div>

      <div class="crop-selector">
        <label>Selected Crop</label>
        <select v-model="selectedCrop">
          <option value="Rice">🌾 Rice</option>
          <option value="Wheat">🌾 Wheat</option>
          <option value="Corn">🌽 Corn</option>
        </select>
      </div>

      <div class="status-section">
        <div class="status-badge active"><span class="dot"></span> Live Data Stream Active</div>
        <button class="icon-btn">↻</button>
        <button class="icon-btn notification">🔔 <span class="badge">5</span></button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const selectedCrop = ref('Rice')
const currentDate = ref('')

// Function to format date like "Wednesday, December 24, 2025 at 11:23 PM"
const updateTime = () => {
  const now = new Date()
  const options = {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }
  currentDate.value = now.toLocaleDateString('en-US', options)
}

onMounted(() => {
  updateTime()
  setInterval(updateTime, 60000) // Update every minute
})
</script>

<style scoped>
.fixed-header {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 80px;
  background-color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  z-index: 1000;
  padding: 0 2rem;
  display: flex;
  align-items: center;
}

.header-content {
  width: 100%;
  max-width: 1400px; /* Keep content centered on huge screens */
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.brand-section {
  display: flex;
  align-items: center;
  gap: 15px;
}

.logo-icon {
  font-size: 2rem;
}

.title-box h1 {
  font-size: 1.2rem;
  color: #2c3e50;
  margin: 0;
}
.title-box p {
  font-size: 0.8rem;
  color: #7f8c8d;
  margin: 0;
}

.dashboard-info {
  border-left: 1px solid #ddd;
  padding-left: 15px;
  margin-left: 15px;
}
.dashboard-info h2 {
  font-size: 1rem;
  margin: 0;
}
.current-date {
  font-size: 0.8rem;
  color: #7f8c8d;
}

.crop-selector {
  background: #f8f9fa;
  padding: 5px 15px;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  min-width: 200px;
}
.crop-selector label {
  display: block;
  font-size: 0.7rem;
  color: #27ae60;
  font-weight: bold;
}
.crop-selector select {
  border: none;
  background: transparent;
  font-weight: bold;
  font-size: 1rem;
  outline: none;
  width: 100%;
  cursor: pointer;
}

.status-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-badge {
  background: #e8f5e9;
  color: #27ae60;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}
.dot {
  width: 8px;
  height: 8px;
  background: #27ae60;
  border-radius: 50%;
  display: block;
}

.icon-btn {
  background: white;
  border: 1px solid #ddd;
  width: 35px;
  height: 35px;
  border-radius: 8px;
  cursor: pointer;
  position: relative;
}
.badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background: #e74c3c;
  color: white;
  font-size: 0.7rem;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
