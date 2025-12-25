<template>
  <div class="visual-card">
    <div class="visual-header">
      <div class="title-row">
        <span class="icon">🧊</span>
        <h4>Crop Health Model</h4>
      </div>
      <div class="view-toggles">
        <span class="badge status" :class="healthStatus.toLowerCase()">{{ healthStatus }}</span>
        <div class="toggle-group">
          <button class="active">2D</button>
          <button>3D</button>
        </div>
      </div>
    </div>

    <div class="sim-window">
      <div class="stats-overlay">
        <div class="stat-tag sun">☀️ {{ light }}%</div>
        <div class="stat-tag water">💧 {{ moisture }}%</div>
        <div class="stat-tag temp">🌡️ {{ temperature }}°C</div>
      </div>

      <div class="scene">
        <div class="sky"></div>
        <div class="soil"></div>

        <div class="plant-container" :class="healthStatus.toLowerCase()">
          <div class="stem"></div>
          <div class="leaf leaf-1"></div>
          <div class="leaf leaf-2"></div>
          <div class="leaf leaf-3"></div>
          <div class="head">🌾</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  temperature: Number,
  moisture: Number,
  light: Number,
})

// Simple logic to determine if plant looks "Healthy" or "Wilted"
const healthStatus = computed(() => {
  if (props.temperature > 38 || props.moisture < 30) return 'Critical'
  return 'Healthy'
})
</script>

<style scoped>
.visual-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
  height: 100%;
  display: flex;
  flex-direction: column;
}

.visual-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.title-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.title-row h4 {
  margin: 0;
  color: #2c3e50;
}

.view-toggles {
  display: flex;
  gap: 10px;
  align-items: center;
}
.badge {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
  color: white;
}
.badge.healthy {
  background: #2c3e50;
}
.badge.critical {
  background: #c0392b;
}

.toggle-group {
  background: #f1f2f6;
  border-radius: 6px;
  padding: 2px;
  display: flex;
}
.toggle-group button {
  border: none;
  background: none;
  padding: 4px 10px;
  font-size: 0.8rem;
  cursor: pointer;
  border-radius: 4px;
  color: #7f8c8d;
}
.toggle-group button.active {
  background: white;
  color: #2c3e50;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* SCENE */
.sim-window {
  flex: 1;
  border-radius: 12px;
  overflow: hidden;
  position: relative;
  display: flex;
  flex-direction: column;
  min-height: 400px;
}

.stats-overlay {
  position: absolute;
  top: 15px;
  left: 15px;
  right: 15px;
  display: flex;
  justify-content: space-between;
  z-index: 10;
}
.stat-tag {
  background: rgba(255, 255, 255, 0.9);
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  color: #555;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.scene {
  width: 100%;
  height: 100%;
  position: relative;
}
.sky {
  height: 70%;
  background: linear-gradient(to bottom, #e0f7fa, #b2ebf2);
}
.soil {
  height: 30%;
  background: #d7ccc8;
  border-top: 4px solid #a1887f;
}

/* PLANT ANIMATION */
.plant-container {
  position: absolute;
  bottom: 25%; /* Sits on soil */
  left: 50%;
  transform: translateX(-50%);
  transition: all 1s ease;
}

.stem {
  width: 8px;
  height: 120px;
  background: #4caf50;
  margin: 0 auto;
  border-radius: 4px;
}
.leaf {
  position: absolute;
  width: 40px;
  height: 40px;
  background: #66bb6a;
  border-radius: 0 50% 50% 50%;
}
.leaf-1 {
  bottom: 30px;
  left: -30px;
  transform: rotate(-45deg);
}
.leaf-2 {
  bottom: 60px;
  right: -30px;
  transform: rotate(135deg) scaleX(-1);
}
.leaf-3 {
  bottom: 90px;
  left: -20px;
  transform: rotate(-30deg) scale(0.8);
}
.head {
  position: absolute;
  top: -30px;
  left: -10px;
  font-size: 2rem;
}

/* CRITICAL STATE CSS */
.plant-container.critical .stem {
  background: #d35400;
  transform: translateX(-50%) rotate(5deg);
}
.plant-container.critical .leaf {
  background: #e67e22;
  transform-origin: bottom left;
}
.plant-container.critical .leaf-1 {
  transform: rotate(10deg) translateY(20px);
}
.plant-container.critical .leaf-2 {
  transform: rotate(170deg) translateY(20px);
}
.plant-container.critical .head {
  opacity: 0.5;
}
</style>
