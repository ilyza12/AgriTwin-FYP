<template>
  <div class="sensor-card" :class="status">
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
        
        <span class="status-label" style="text-transform: capitalize;">
          {{ status }}
        </span>
        
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
  status: String,
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

/* 🚀 1. ROOT CARD COLORS (Background & Border) */
.sensor-card.optimal {
  border-left: 4px solid #27ae60;
  background: #f0fdf4;
}
.sensor-card.suboptimal {
  border-left: 4px solid #f39c12;
  background: #fff9e6; /* Soft amber background */
}
.sensor-card.critical {
  border-left: 4px solid #e74c3c;
  background: #fff5f5;
}

.card-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}
.icon {
  font-size: 1.2rem;
}

/* 🚀 2. STATUS DOT COLORS */
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.optimal .status-dot { background: #27ae60; }
.suboptimal .status-dot { background: #f39c12; }
.critical .status-dot { background: #e74c3c; }

.value-box {
  display: flex;
  align-items: baseline;
  gap: 5px;
}

/* 🚀 3. MAIN NUMBER (VALUE) COLORS */
.value {
  font-size: 2rem;
  font-weight: 700;
  color: #2c3e50; /* Default dark gray for optimal */
}
.suboptimal .value { color: #d68910; } /* Darker amber for readability */
.critical .value { color: #c0392b; }

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

/* 🚀 4. STATUS TEXT LABEL COLORS */
.status-label {
  font-weight: bold;
}
.optimal .status-label { color: #27ae60; }
.suboptimal .status-label { color: #f39c12; }
.critical .status-label { color: #c0392b; }

.progress-bar {
  width: 100%;
  height: 6px;
  background: #e0e0e0;
  border-radius: 3px;
  overflow: hidden;
}

/* 🚀 5. PROGRESS BAR FILL COLORS */
.fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}
.optimal .fill { background: #27ae60; }
.suboptimal .fill { background: #f39c12; }
.critical .fill { background: #e74c3c; }
</style>