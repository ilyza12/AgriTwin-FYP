<template>
  <section class="section-block col-camera">
    <div class="section-header row">
      <h3>📹 Live Camera Feed</h3>
      <span class="recording-badge">🔴 Streaming</span>
    </div>
    
    <div class="camera-box">
      <img 
        src="http://192.168.154.175:81/stream" 
        alt="Chili Plant Live Feed" 
        crossorigin="anonymous"
        class="live-stream-img"
      />
      
      <div class="video-overlay">
        <span>{{ currentTime }}</span>
        <button>CAM</button>
      </div>
    </div>
  </section>
</template>

<script setup>
// Accept the current time from the main dashboard to keep things synced
defineProps({
  currentTime: {
    type: String,
    required: true
  }
})
</script>

<style scoped>
/* Inherit standard section styles from parent */
.section-block {
  display: flex;
  flex-direction: column;
}
.section-header {
  margin-bottom: 20px;
  padding-left: 5px;
}
.section-header.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.section-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.25rem;
}

/* Specific Camera Styles */
.camera-box {
  flex-grow: 1; 
  min-height: 400px; 
  background: #000;
  border-radius: 12px;
  position: relative;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden; /* Keeps the rounded corners over the image */
  display: flex;
  justify-content: center;
  align-items: center;
}

.live-stream-img {
  width: 100%;
  height: 100%;
  object-fit: cover; /* Ensures the video fills the box perfectly */
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

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}
</style>