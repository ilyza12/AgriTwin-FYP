<template>
  <div class="visual-container">
    <div class="visual-header">
      <div class="title">
        <span class="icon">🧊</span>
        <h3>Crop Health Model</h3>
      </div>
      <div class="controls">
        <div class="toggle">
          <button class="active">2D</button>
          <button class="disabled">3D</button>
        </div>
      </div>
    </div>

    <div class="scene-area">
      <div class="sensor-badges">
        <span class="badge">☀️ {{ light }}%</span>
        <span class="badge">💧 {{ moisture }}%</span>
        <span class="badge">🌡️ {{ temperature }}°C</span>
      </div>

      <div class="construction-zone">
        <span class="emoji">🚧</span>
        <h2>Visualisation Under Construction</h2>
      </div>

      <div class="sky"></div>
      <div class="ground"></div>
    </div>
  </div>
</template>

<script setup>
// We MUST keep the props so SimDashboard.vue doesn't crash when it passes data here!
defineProps({
  temperature: Number,
  moisture: Number,
  light: Number
})
</script>

<style scoped>
.visual-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 500px;
  overflow: hidden;
}

.visual-header {
  padding: 15px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eee;
}

.title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.title h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #2c3e50;
}

.toggle {
  display: flex;
  background: #f1f3f5;
  border-radius: 6px;
  overflow: hidden;
}

.toggle button {
  border: none;
  padding: 5px 12px;
  cursor: pointer;
  background: transparent;
  color: #7f8c8d;
  font-weight: 600;
  font-size: 0.85rem;
}

.toggle button.active {
  background: white;
  color: #2c3e50;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.toggle button.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* SCENE AREA */
.scene-area {
  flex-grow: 1;
  position: relative;
  display: flex;
  flex-direction: column;
}

.sensor-badges {
  position: absolute;
  top: 20px;
  width: 100%;
  display: flex;
  justify-content: space-around;
  z-index: 10;
}

.sensor-badges .badge {
  background: white;
  padding: 6px 15px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: bold;
  color: #2c3e50;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* THE NEW CONSTRUCTION ZONE */
.construction-zone {
  position: absolute;
  top: 45%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  z-index: 20;
  background: rgba(255, 255, 255, 0.85);
  padding: 20px 40px;
  border-radius: 12px;
  border: 2px dashed #f39c12;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  backdrop-filter: blur(4px);
}

.construction-zone .emoji {
  font-size: 3rem;
  display: block;
  margin-bottom: 10px;
}

.construction-zone h2 {
  margin: 0 0 5px 0;
  color: #2c3e50;
  font-size: 1.4rem;
}

.construction-zone p {
  margin: 0;
  color: #7f8c8d;
  font-size: 0.95rem;
  font-weight: 500;
}

/* BACKGROUNDS */
.sky {
  background: linear-gradient(180deg, #e0f7fa 0%, #b2ebf2 100%);
  height: 70%;
  width: 100%;
}

.ground {
  background: linear-gradient(180deg, #d7ccc8 0%, #a1887f 100%);
  height: 30%;
  width: 100%;
  border-top: 2px solid #8d6e63;
}
</style>