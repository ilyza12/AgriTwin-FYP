<template>
  <div class="sensor-card" :class="{ critical: isCritical }">
    <div class="card-header">
      <span class="icon">{{ icon }}</span>
      <span class="status-dot"></span>
    </div>

    <div class="card-body">
      <h3>{{ title }}</h3>
      <div class="value-box">
        <span class="value">{{ value }}</span>
        <span class="unit">{{ unit }}</span>
      </div>
    </div>

    <div class="card-footer">
      <div class="range-info">
        <span>Optimal: {{ range }}</span>
        <span class="status-text">{{ isCritical ? 'Critical' : 'Optimal' }}</span>
      </div>
      <div class="progress-bar">
        <div class="fill" :style="{ width: percentage + '%' }"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: String,
  value: [Number, String],
  unit: String,
  icon: String,
  range: String,
  isCritical: Boolean,
  percentage: Number,
})
</script>

<style scoped>
.sensor-card {
  background: white;
  border-radius: 12px;
  padding: 1.2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
  border: 1px solid #eee;
  transition: transform 0.2s;
}

.sensor-card.critical {
  border-left: 4px solid #e74c3c;
  background: #fff5f5;
}
.sensor-card:not(.critical) {
  border-left: 4px solid #27ae60;
  background: #f0fdf4;
}

.card-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}
.icon {
  font-size: 1.2rem;
}
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #27ae60;
}
.critical .status-dot {
  background: #e74c3c;
}

.value-box {
  display: flex;
  align-items: baseline;
  gap: 5px;
}
.value {
  font-size: 2rem;
  font-weight: 700;
  color: #2c3e50;
}
.critical .value {
  color: #c0392b;
}
.unit {
  color: #7f8c8d;
  font-weight: 500;
}

.card-footer {
  margin-top: 15px;
}
.range-info {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: #7f8c8d;
  margin-bottom: 5px;
}
.critical .status-text {
  color: #c0392b;
  font-weight: bold;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: #e0e0e0;
  border-radius: 3px;
  overflow: hidden;
}
.fill {
  height: 100%;
  background: #27ae60;
  border-radius: 3px;
}
.critical .fill {
  background: #e74c3c;
}
</style>
