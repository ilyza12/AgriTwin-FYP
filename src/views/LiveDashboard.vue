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
    <p>🌶️ Capsicum annuum - Optimal temp 17-30°C, highly sensitive to water stress</p>
  </div>
  
  <div class="sensor-grid">
    
    <SensorCard 
      title="Temperature" 
      :value="liveSensorData.temperature" 
      unit="°C" 
      icon="🌡️" 
      range="17-30°C" 
      :percentage="(liveSensorData.temperature / 50) * 100" 
      :status="(liveSensorData.temperature < 8 || liveSensorData.temperature > 35) ? 'critical' : ((liveSensorData.temperature < 17 || liveSensorData.temperature > 30) ? 'suboptimal' : 'optimal')" 
    />
    
    <SensorCard 
      title="Humidity" 
      :value="liveSensorData.humidity" 
      unit="%" 
      icon="💧" 
      range="65-85%" 
      :percentage="liveSensorData.humidity" 
      :status="(liveSensorData.humidity < 40 || liveSensorData.humidity > 95) ? 'critical' : ((liveSensorData.humidity < 65 || liveSensorData.humidity > 85) ? 'suboptimal' : 'optimal')" 
    />
    
    <SensorCard 
      title="Soil Moisture" 
      :value="liveSensorData.moisture" 
      unit="%" 
      icon="🌱" 
      range="23-27%" 
      :percentage="liveSensorData.moisture" 
      :status="(liveSensorData.moisture < 13.1 || liveSensorData.moisture > 32) ? 'critical' : ((liveSensorData.moisture < 23 || liveSensorData.moisture > 27) ? 'suboptimal' : 'optimal')" 
    />
    
    <SensorCard 
      title="Salinity" 
      :value="liveSensorData.salinity" 
      unit="dS/m" 
      icon="⚡" 
      range="1.0-1.5 dS/m" 
      :percentage="(liveSensorData.salinity / 5) * 100" 
      :status="(liveSensorData.salinity < 0.3 || liveSensorData.salinity > 3.0) ? 'critical' : ((liveSensorData.salinity < 1.0 || liveSensorData.salinity > 1.5) ? 'suboptimal' : 'optimal')" 
    />
    
    <SensorCard 
      title="Light Intensity" 
      :value="liveSensorData.light_percent" 
      unit="%" 
      icon="☀️" 
      :range="`${liveSensorData.light} µmol | Opt: 600-1224`" 
      :percentage="liveSensorData.light_percent" 
      :status="(liveSensorData.light < 17.3 || liveSensorData.light > 1500) ? 'critical' : ((liveSensorData.light < 600 || liveSensorData.light > 1224) ? 'suboptimal' : 'optimal')" 
    />
    
  </div>
</section>

      <div class="split-section">
        
        <CameraFeed :currentTime="currentTime" />

        <section class="section-block col-ai">
          <div class="section-header">
            <h3>🧠 AI Insights & Yield</h3>
          </div>
          
          <div v-if="isLoadingAI" class="ai-card center-content">
            <p>🤖 AI is analyzing current conditions...</p>
          </div>

          <div v-else class="ai-card">
            <div class="yield-banner" v-if="yieldData.status === 'success'">
              <div class="yield-text">
                <span class="label">Plant Health (7-Day)</span>
              </div>
              <span class="prediction">{{ yieldData.yield_class }}</span>
            </div>
            <div class="yield-banner" v-else>
              <span class="label">Yield Prediction</span>
              <span class="prediction text-sm">Gathering Data...</span>
            </div>

            <!-- <div class="health-score-box">
              <strong>Plant Health Score</strong>
              <strong class="score-text">{{ liveAnalysis.health?.overall_score || 0 }}/100</strong>
            </div> -->

            <!-- <div v-if="liveAnalysis.recommendations?.irrigation?.action === 'irrigate'" class="alert-item" style="background: #fff3e0; color: #e65100; border-color: #ff9800;">
              💧 Action Required: Irrigate ~{{ liveAnalysis.recommendations.irrigation.amount_liters }}L of water.
            </div> -->

            <div v-if="liveAnalysis.anomaly_detection?.is_anomaly" class="alert-item critical-alert">
              🤖 AI STATISTICAL ANOMALY: Multi-variable stress detected.
            </div>

            <div v-if="!liveAnalysis.anomaly_detection?.is_anomaly" class="alert-item good">
              ✅ Optimal conditions. No critical stress detected.
            </div>
          </div>
        </section>

        <section class="section-block col-twin">
          <div class="section-header">
            <h3>🌱 Digital Twin View</h3>
          </div>
          <div class="twin-card" ref="twinContainer" id="live-twin-container">
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
import { ref, onMounted, onUnmounted } from 'vue'
import NavBar from '../components/common/NavBar.vue'
import SensorCard from '../components/live/SensorCard.vue'
import CameraFeed from '../components/live/CameraFeed.vue'
import HistoryTrends from '../components/live/HistoryTrends.vue'
import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'

// MQTT imports
import {
  liveSensorData,
  isMqttConnected,
  startMqttClient,
  stopMqttClient,
} from '@/services/mqttClient.js'   // Decoupled MQTT client runs in background

import { useTwinStore } from '../stores/twinStore'

const twinStore = useTwinStore()

// --- NEW AI STATE VARIABLES ---
const isLoadingAI = ref(true)
const yieldData = ref({})
const liveAnalysis = ref({})
const currentTime = ref(new Date().toLocaleTimeString())
let aiPollingInterval = null
let timeInterval = null

// --- FETCH YIELD (Runs Once) ---

// 🗣️ DEFENSE NOTE: Yield prediction only needs to be fetched once on load because a plant's 7-day harvest forecast doesn't fluctuate second-by-second. This saves significant processing power on the Flask backend.
const fetchYieldPrediction = async () => {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/ml/live-yield')   // Fetch 7-day forecast only once on load
    const data = await response.json()
    yieldData.value = data
  } catch (error) {
    console.error("Error fetching yield prediction:", error)
  }
}

// --- FETCH LIVE ANALYSIS (Runs every 5 seconds) ---

// 🗣️ DEFENSE NOTE: Unlike the yield, the anomaly detection and health scoring are polled dynamically. I architected this as an asynchronous fetch rather than a continuous websocket to prevent network congestion while still maintaining near-real-time AI oversight.
const fetchLiveAnalysis = async () => {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/ml/live-analysis')    // Async fetch prevents websocket network congestion
    if (response.ok) {
      const data = await response.json()
      liveAnalysis.value = data
      isLoadingAI.value = false // Hide loader once we have first data
    }
  } catch (error) {
    console.error("Error fetching live AI analysis:", error)
  }
}

// --- NEW DIGITAL TWIN 3D STATE ---
const twinContainer = ref(null)
let scene, camera, renderer, controls, animationId

const initLiveTwin = () => {
  if (!twinContainer.value) return;

  // 1. Setup Scene & Get Dimensions
  const width = twinContainer.value.clientWidth;
  const height = twinContainer.value.clientHeight;
  
  scene = new THREE.Scene();
  scene.background = new THREE.Color('#ffffff'); // Matches the white card

  // 2. Camera setup
  camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
  camera.position.set(0, 2.0, 6);

  // 3. Renderer setup
  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(width, height);
  renderer.setPixelRatio(window.devicePixelRatio);
  twinContainer.value.appendChild(renderer.domElement);

  // 4. Lighting
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
  scene.add(ambientLight);
  const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
  dirLight.position.set(5, 10, 5);
  scene.add(dirLight);

  // 5. Controls (Allows user to rotate the plant)
  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.enablePan = false;
  controls.minDistance = 2; // Can't zoom in too close
  controls.maxDistance = 8; // Can't zoom out too far
  controls.target.set(0, 1.2, 0);

  // 6. Load your No-Fruit Model!
  const loader = new GLTFLoader();
  loader.load('/chili_plant_nofruit.glb', (gltf) => {
    const livePlant = gltf.scene;

    // 🚀 THE FIX: Traverse the model and paint the white branches!
    livePlant.traverse((child) => {
      if (child.isMesh) {
        const partName = child.name.toLowerCase();
        
        // If it's NOT a leaf, pot, soil, or the support stick... it's the stem!
        if (!partName.includes('leaf') && 
            !partName.includes('pot') && 
            !partName.includes('soil') && 
            !partName.includes('support')) {
              
          child.material = child.material.clone();
          child.material.map = null; // Remove any broken textures
          child.material.color.set('#5C4033'); // Bark brown
          child.material.roughness = 0.9; // Make it look like rough wood
        }
      }
    });

    // ==========================================
    // 🚀 THE FIX: Snap the bones into the "Healthy" pose
    // ==========================================
    if (gltf.animations && gltf.animations.length > 0) {
      const liveMixer = new THREE.AnimationMixer(livePlant);
      
      gltf.animations.forEach((clip) => {
        const action = liveMixer.clipAction(clip);
        action.setEffectiveWeight(1);
        action.play();
        action.paused = true; // Freeze the animation immediately
        action.time = 0;      // 0 = The perfectly upright, healthy frame
      });
      

      liveMixer.update(0); // Force Three.js to calculate the bone attachments!
    }

    livePlant.position.set(0, -0.5, 0);
    scene.add(livePlant);
  });

  // 7. Animation Loop
  const animate = () => {
    animationId = requestAnimationFrame(animate);
    controls.update(); // Required for damping
    renderer.render(scene, camera);
  };
  animate();

  // 8. Handle Window Resizing seamlessly
  window.addEventListener('resize', handleResize);
}

const handleResize = () => {
  if (!twinContainer.value || !camera || !renderer) return;
  const width = twinContainer.value.clientWidth;
  const height = twinContainer.value.clientHeight;
  
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  renderer.setSize(width, height);
}

onMounted(() => {
  // 1. Connect to HiveMQ for instant sensor updates
  startMqttClient()

  // 2. Fetch History for the charts
  twinStore.fetchBackendData()

  // 3. Initial AI Fetches
  fetchYieldPrediction()
  fetchLiveAnalysis()

  initLiveTwin()

  timeInterval = setInterval(() => {
    currentTime.value = new Date().toLocaleTimeString()
  }, 1000)

  aiPollingInterval = setInterval(() => {
    fetchLiveAnalysis()
  }, 5000)    // 5-second polling balances real-time AI with minimal server load
})

onUnmounted(() => {
  stopMqttClient()
  clearInterval(aiPollingInterval)
  clearInterval(timeInterval)
  
  // 🚀 CLEANUP 3D MEMORY

  // 🗣️ DEFENSE NOTE: WebGL can easily cause memory leaks in Single Page Applications (SPAs). This explicit cleanup block destroys the renderer, clears the animation frame, and removes event listeners so the browser memory stays clean when navigating between routes.
  window.removeEventListener('resize', handleResize)
  if (animationId) cancelAnimationFrame(animationId)    // Kill render loop
  if (renderer) renderer.dispose()    // Destroy WebGL context from GPU memory
})

onUnmounted(() => {
  stopMqttClient()
  clearInterval(aiPollingInterval)
  clearInterval(timeInterval)
})
</script>

<style scoped>
/* --- 1. GLOBAL CONTAINER SETUP --- */
.dashboard-container {
  min-height: 100vh;
  width: 100%;
  background-color: #f8f9fa;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  display: flex; 
  flex-direction: column;
}

/* --- 2. SCROLLABLE AREA --- */
.scrollable-content {
  padding-top: 100px;
  padding-bottom: 50px;
  width: 100%;
  max-width: 1600px; 
  margin: 0 auto; 
  padding-left: 20px;
  padding-right: 20px;
  box-sizing: border-box; 
}

/* --- 3. TABS --- */
.tabs-container {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
  padding-left: 5px; 
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
  border: 2px solid transparent; 
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
  width: 100%; 
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
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  width: 100%;
}

/* --- 5. SPLIT SECTION (Camera + AI + Twin) --- */
.split-section {
  display: grid;
  /* 50% Camera, 25% AI, 25% Digital Twin */
  grid-template-columns: 2fr 1fr 1fr;
  gap: 25px;
  margin-bottom: 40px;
  width: 100%;
}

/* Ensure columns stretch to match height */
.col-ai, .col-twin {
  display: flex;
  flex-direction: column;
}



/* AI INSIGHTS CARD */
.ai-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
  flex-grow: 1; 
  display: flex;
  flex-direction: column;
}

.center-content {
  justify-content: center;
  align-items: center;
}

/* 3D TWIN CARD */
.twin-card {
  background: white;
  border-radius: 12px;
  padding: 0; 
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
  border: 1px solid #eee;
  flex-grow: 1; 
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden; 
}

/* REFINED AI CARD INTERNALS */
.yield-banner {
  background: #fff9c4;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 15px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 5px;
}

.yield-text {
  display: flex;
  flex-direction: column;
}

.prediction {
  font-size: 1.4rem;
  font-weight: bold;
  color: #f57f17;
}

.health-score-box {
  background: #e3f2fd; 
  padding: 15px; 
  border-radius: 8px; 
  margin-bottom: 15px; 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  border-left: 4px solid #2196f3;
}

.score-text {
  color: #1976d2; 
  font-size: 1.2rem;
  font-weight: bold;
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



/* RESPONSIVE LAYOUT BREAKPOINTS */
@media (max-width: 1200px) {
  .split-section {
    grid-template-columns: 1fr 1fr; 
  }
  .col-twin {
    grid-column: span 2; 
  }
}

@media (max-width: 768px) {
  .split-section {
    grid-template-columns: 1fr; 
  }
  .col-twin {
    grid-column: span 1;
  }
}
</style>