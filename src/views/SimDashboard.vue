<template>
  <div class="dashboard-container">
    <NavBar />

    <main class="scrollable-content">
      <div class="tabs-container">
        <div class="tab" @click="$router.push('/')">⚡ Live Dashboard</div>
        <div class="tab active">🎛 Simulation</div>
      </div>

      <div class="sim-grid">
        <div class="col-visual">
          <div ref="threeContainer" style="width: 100%; height: 600px; border-radius: 12px; overflow: hidden; background: #ecf0f1; box-shadow: 0 4px 6px rgba(0,0,0,0.02);"></div>
        </div>
        <div class="col-controls">
          <ControlPanel v-model="simParams" @reset="resetSimulation" />
        </div>
      </div>

      <section class="section-block ai-section">
        <div class="section-header">
          <h3>🧠 AI Forecast and Recommendations</h3>
        </div>

        <div class="ai-card">
          <div v-if="isSimulating" style="text-align: center; color: #7f8c8d; padding: 20px;">
            🤖 Simulating parameters...
          </div>

          <div v-else-if="simResult">
            
            <div class="yield-banner">
              <div style="display: flex; flex-direction: column;">
                <span class="label">📈 Simulated Yield Prediction</span>
                <span style="font-size: 0.9rem; color: #7f8c8d;">
                <!-- ~{{ simResult.yield.predicted_fruit_count }} chilies ({{ simResult.yield.predicted_total_weight_g }}g) -->
                </span>
              </div>
              <span class="prediction" :style="{ color: simResult.yield.yield_class === 'Low' ? '#c0392b' : '#f57f17' }">
                {{ simResult.yield.yield_class }}
              </span>
            </div>

            <div :style="{ background: `${healthScoreInsight.color}20`, padding: '12px 20px', borderRadius: '8px', margin: '20px 0', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderLeft: `4px solid ${healthScoreInsight.color}` }">
              <strong>Simulated Plant Health Score {{ healthScoreInsight.emoji }}</strong>
              <div style="text-align: right;">
                <strong :style="{ color: healthScoreInsight.color, fontSize: '1.2rem', display: 'block' }">{{ simResult.analysis.health.overall_score }}/100</strong>
                <span style="font-size: 0.8rem; color: #7f8c8d;">{{ healthScoreInsight.status }}: {{ healthScoreInsight.description }}</span>
              </div>
            </div>



            <div class="rec-list" v-if="hasRecommendations">
              <div class="rec-label">Targeted Interventions</div>
              
              <div class="rec-item" v-for="(rec, index) in expertRecommendations" :key="index" style="background: #f8f9fa;">
                <span class="tag high" :style="{ backgroundColor: rec.color }">{{ rec.tag }}</span>
                <div class="rec-content" style="width: 100%;">
                  <strong style="font-size: 1.05rem; display: block; margin-bottom: 5px;">{{ rec.action }}</strong>
                  <p style="margin-bottom: 8px;">{{ rec.reason }}</p>
                  
                  <div style="display: flex; gap: 15px; font-size: 0.75rem; color: #95a5a6; border-top: 1px solid #eee; padding-top: 8px;">
                    <span v-if="rec.cost">💰 {{ rec.cost }} Cost</span>
                  </div>
                </div>
              </div>
            </div>
          </div> </div> </section>

      <section class="section-block alerts-section">
        <div class="section-header row">
          <h3>🔔 System Alerts</h3>
          <span class="badge-count" :style="{ backgroundColor: dynamicAlerts[0]?.type === 'success' ? '#27ae60' : '#e74c3c' }">
            {{ dynamicAlerts.length }} Active
          </span>
        </div>

        <div class="alerts-list">
          <SystemAlert 
            v-for="(alert, index) in dynamicAlerts" 
            :key="index"
            :type="alert.type" 
            :title="alert.title" 
            :message="alert.message" 
            :time="alert.time" 
            :actionLabel="alert.actionLabel" 
          />
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import NavBar from '../components/common/NavBar.vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
// import TwinVisual from '../components/simulation/TwinVisual.vue'
import ControlPanel from '../components/simulation/ControlPanel.vue'
import SystemAlert from '../components/common/SystemAlert.vue'
import { useTwinStore } from '../stores/twinStore'
import { storeToRefs } from 'pinia'

// Access the Store
const twinStore = useTwinStore()
const { simParams } = storeToRefs(twinStore)
const { resetSimulation } = twinStore

// --- AI INTEGRATION STATE ---
const simResult = ref(null)
const isSimulating = ref(false)

// --- 3D DIGITAL TWIN STATE ---
const threeContainer = ref(null)
let scene, camera, renderer, plantMixer
let animationActions = []
let leafMeshes = []
let chiliMeshes = []
let stemMesh = null
let totalAnimationTime = 0

function initThreeJS() {
  scene = new THREE.Scene()
  // Matches your dashboard background
  scene.background = new THREE.Color(0xecf0f1) 

  // Setup Camera
  camera = new THREE.PerspectiveCamera(45, threeContainer.value.clientWidth / threeContainer.value.clientHeight, 0.1, 100)
  camera.position.set(0, 2, 6) // You may need to adjust these numbers depending on how big the .glb is!
  // Tilt the camera to look directly at the center of the plant
  camera.lookAt(0, 1, 0)

  // Setup Renderer
  renderer = new THREE.WebGLRenderer({ antialias: true })
  renderer.setSize(threeContainer.value.clientWidth, threeContainer.value.clientHeight)

  // Web browsers naturally wash out 3D colors. 
  // We explicitly enabled SRGBColorSpace and ACESFilmicToneMapping 
  // to perfectly mimic the cinematic camera lens used in Blender. 
  // This ensures the visual data representation of the chili plant remains scientifically accurate.

// 🎯 1. THE COLOR FIX: Turn on proper color management and tone mapping
  renderer.outputColorSpace = THREE.SRGBColorSpace; // Ensures texture colors aren't washed out
  renderer.toneMapping = THREE.ACESFilmicToneMapping; // Mimics Blender's cinematic camera lens
  renderer.toneMappingExposure = 1.2; // Tweaks overall brightness

  threeContainer.value.appendChild(renderer.domElement)

  // Add Lights
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.3)
  scene.add(ambientLight)

  // Add a Hemisphere light (Simulates sky color from above, dirt color from below)
  const hemiLight = new THREE.HemisphereLight(0xe0f7fa, 0x8d6e63, 0.8)
  hemiLight.position.set(0, 10, 0)
  scene.add(hemiLight)

  // Create a strong, warm directional light to act as the "Sun"
  const directionalLight = new THREE.DirectionalLight(0xfffaed, 1.5)
  directionalLight.position.set(5, 8, 5)
  scene.add(directionalLight)

  const controls = new OrbitControls(camera, renderer.domElement)
  controls.target.set(0, 1, 0) // Keeps the rotation centered on the plant

  loadPlantModel()
  animate()
}

function loadPlantModel() {
  const loader = new GLTFLoader()
  loader.load('/chili_plant.glb', (gltf) => { 
    const plantModel = gltf.scene

   // 1. GRAB ALL ANIMATIONS
   // We extract the animation clips from the .glb file, pause them, and save them. This allows us to manually "scrub" the timeline later based on physical stress data. 
    if (gltf.animations && gltf.animations.length > 0) {
      plantMixer = new THREE.AnimationMixer(plantModel)
      
      gltf.animations.forEach((clip) => {
        totalAnimationTime = Math.max(totalAnimationTime, clip.duration) 
        const action = plantMixer.clipAction(clip)
        action.setEffectiveWeight(1) // THE FIX: Force the animation strength to 100%
        action.play()
        action.paused = true
        
        // THE FIX: Save the action to our new array so we can control it directly
        animationActions.push(action)
      })
    }

    // 2. SETUP LEAVES & STEM
    plantModel.traverse((child) => {
      if (child.isMesh) {
        const partName = child.name.toLowerCase()
        
        if (partName.includes('leaf')) {
          child.material = child.material.clone() 
          // THE FIX: Give every leaf a random number between 0.0 and 1.0
          child.material.map = null
          child.userData.colorOffset = Math.random()

          // 🚀 NEW: Randomly select ~50% of all leaves to be vulnerable to Low pH!
          child.userData.phVulnerable = Math.random() > 0.5;
          
          // ==========================================
          // 🚀 GPU SHADER: Mildew Spots & Tip Burn
          // ==========================================

          // 🗣️ DEFENSE NOTE: This is a custom WebGL fragment shader. Instead of swapping images, it calculates procedural math on the GPU to dynamically paint mildew, tip burn, and pH chlorosis pixel-by-pixel.
          child.material.onBeforeCompile = (shader) => {
            // I didn't just swap out static 2D images of sick plants. 
            // I wrote a custom WebGL fragment shader. Then take the environmental data 
            // (like Humidity) and pass it directly into the user's GPU as 'uniforms'.

            // Create the uniforms to talk to Vue
            shader.uniforms.uMildew = { value: 0.0 };
            shader.uniforms.uTipBurn = { value: 0.0 };
            shader.uniforms.uHeatScorch = { value: 0.0 };
            shader.uniforms.uPhTipYellow = { value: 0.0 };
            child.userData.shader = shader; 

            // 1. Pass UV coordinates
            shader.vertexShader = `
              varying vec2 vMyUv;
              ${shader.vertexShader}
            `.replace(
              '#include <uv_vertex>',
              '#include <uv_vertex>\n vMyUv = uv;'
            );

            // The graphics card then runs procedural math 
            // (like pseudo-random noise algorithms) to dynamically paint disease vectors 
            // directly onto the 3D geometry in real-time without lagging the browser.

            // 2. Procedural GPU Math
            shader.fragmentShader = `
              varying vec2 vMyUv;
              uniform float uMildew;
              uniform float uTipBurn;
              uniform float uHeatScorch;
              uniform float uPhTipYellow;

              // Pseudo-random noise generator
              float randomSpot(vec2 n) {
                  return fract(sin(dot(n, vec2(12.9898, 4.1414))) * 43758.5453);
              }

              ${shader.fragmentShader}
            `.replace(
              '#include <color_fragment>',
              `#include <color_fragment>
              
              // --- A. POWDERY MILDEW (High Humidity) ---
              // Break the leaf into a microscopic grid
              vec2 grid = floor(vMyUv * 40.0);
              vec2 local = fract(vMyUv * 40.0);
              float r = randomSpot(grid);
              
              // 2. Clamp the maximum probability to hit your exact 20-50 spot target!
              // 50 spots / 1,600 cells = 0.03125 max probability
              float maxProbability = 0.03125; 
              float probability = uMildew * maxProbability;
              
              // Only spawn spots if the random number hits our microscopic probability window
              float spotMask = step(1.0 - probability, r);
              
              // 3. Draw the spot 
              float softCircle = smoothstep(0.5, 0.2, length(local - vec2(0.5)));
              
              // 4. Fade the spots in gently as humidity rises
              float finalMildew = spotMask * softCircle * uMildew; 
              
              vec3 mildewColor = vec3(0.88, 0.91, 0.89); // Chalky white fungal color

              // --- B. EDGE DAMAGE (Tip Burn & Heat Scorch) ---
              float dist = distance(vMyUv, vec2(0.5)); // 0.0 is center, larger is edges
              
              float tipNoise = randomSpot(vMyUv * 10.0) * 0.1; 
              float burnThreshold = 0.7 - (uTipBurn * 0.4);
              float finalBurn = smoothstep(burnThreshold, burnThreshold + 0.15, dist + tipNoise) * uTipBurn;
              vec3 burnColor = vec3(0.76, 0.77, 0.52); 

              float scorchNoise = randomSpot(vMyUv * 15.0) * 0.15; 
              float scorchThreshold = 0.75 - (uHeatScorch * 0.4);
              float finalScorch = smoothstep(scorchThreshold, scorchThreshold + 0.15, dist + scorchNoise) * uHeatScorch;
              vec3 scorchColor = vec3(0.65, 0.35, 0.15); 

              // --- C. pH NUTRIENT LOCKOUT (Tip Yellowing) ---
              // Pulls soft organic yellow inward from the edges, but stops before the center
              float phNoise = randomSpot(vMyUv * 5.0) * 0.1;
              float phThreshold = 0.8 - (uPhTipYellow * 0.6); 
              float finalPhYellow = smoothstep(phThreshold, phThreshold + 0.3, dist + phNoise) * min(uPhTipYellow * 2.0, 1.0);
              vec3 phColor = vec3(0.83, 0.77, 0.36); // Chlorosis yellow

              // --- D. APPLY THE PAINT ---
              diffuseColor.rgb = mix(diffuseColor.rgb, phColor, finalPhYellow); // Paint pH first
              diffuseColor.rgb = mix(diffuseColor.rgb, burnColor, finalBurn);
              diffuseColor.rgb = mix(diffuseColor.rgb, scorchColor, finalScorch);
              diffuseColor.rgb = mix(diffuseColor.rgb, mildewColor, finalMildew);
              `
            );
          };

          leafMeshes.push(child) 
        }
        // B. THE CHILIES
        else if (partName.includes('chili') || partName.includes('chilli') || partName.includes('fruit')) {
          child.material = child.material.clone()
          
          child.material.map = null // Rips off the ghost texture!
          child.material.roughness = 0.3 

          chiliMeshes.push(child)
        }
        // C. THE WOODEN STICK
        else if (partName.includes('support')) {
          child.material = child.material.clone()

          // THE FIX: Rip off the broken texture and paint it manually!
          child.material.map = null 
          child.material.color.set('#d4c4a8') // Natural cream/bamboo color
          
          child.material.roughness = 0.9 
        }
        else if (!partName.includes('pot') && !partName.includes('soil')) {
          child.material = child.material.clone()
          child.material.map = null 
          child.material.color.set('#5C4033')
          child.material.roughness = 0.9

          stemMesh = child // <-- ADD THIS LINE to save the mesh!
        }
      }
    })

    plantModel.position.set(0, -0.5, 0)
    scene.add(plantModel)
    updatePlantVisuals()
  })
}

function updatePlantVisuals() {
  const p = simParams.value;

  // The UI sliders use percentages (0-100%) for user experience, 
  // but biological models require precise Photosynthetic Photon Flux Density (PPFD). 
  // This line bridges UI with biology by dynamically translating the percentage 
  // back into scientific µmol/m²/s before applying physical stress to the 3D armature.

  // 1. Secret Translation for Light
  const ppfd = (p.lightIntensity / 100) * 2000;

  // ==========================================
  // PART 1: PHYSICAL COLLAPSE (Droop & Shrivel)
  // ==========================================

  // We map multi-variable environmental extremes (heat, drought, salt) into a single 0-1 "droop" metric to drive the physical collapse of the 3D armature.
  let droopStress = 0; 

  // Water Stress: Drought (<23%) or Waterlogged (>27%)
  if (p.soilMoisture < 23) droopStress = Math.max(droopStress, (23 - p.soilMoisture) / 9.9);
  if (p.soilMoisture > 27) droopStress = Math.max(droopStress, (p.soilMoisture - 27) / 18.0);

  // Heat Stress: (>30°C)
  if (p.temperature > 30) droopStress = Math.max(droopStress, (p.temperature - 30) / 15);

  // Dry Air: (<65%) - Causes rapid transpiration wilting
  if (p.humidity < 65) droopStress = Math.max(droopStress, (65 - p.humidity) / 45.0);

  // Salinity: (>3.0) - Osmotic shock prevents water absorption, mimicking drought
  if (p.salinity > 3.0) droopStress = Math.max(droopStress, (p.salinity - 3.0) / 5);

  // ADD THIS: High light causes leaf curling/shriveling
  if (p.lightIntensity > 65) droopStress = Math.max(droopStress, (p.lightIntensity - 65) / 35);

  // Heat Stress: Critical High (>32°C) - Shriveled and scorched
  if (p.temperature > 32) droopStress = Math.max(droopStress, (p.temperature - 32) / 20.0);
  
  // Cold Stress: Critical Low (<15°C) - Wilts
  if (p.temperature < 15) droopStress = Math.max(droopStress, (15 - p.temperature) / 10.0);

  droopStress = Math.min(Math.max(droopStress, 0), 1); 

  // Apply to Stem (Armature)
  if (animationActions && animationActions.length > 0) {
    const targetTime = droopStress * totalAnimationTime;
    animationActions.forEach(action => action.time = targetTime);
    plantMixer.update(0); 
  }

  // ==========================================
  // PART 1.5: LOW LIGHT STUNTING & DROP
  // ==========================================
  let thinScale = 1.0;
  let visibleLeafPercent = 1.0;
  let visibleChiliPercent = 1.0;

  if (p.lightIntensity < 40) {
    // SMOOTH DROP: As the slider moves from 40 down to 0, 
    // this ratio smoothly scales from 1.0 down to 0.0
    const lightRatio = p.lightIntensity / 40; 

    // Leaves thin out gradually, stopping at 15% so it's never a completely bare stick
    visibleLeafPercent = Math.max(0.15, lightRatio); 
    
    // Chilies drop gradually, going all the way to 0 at the bottom
    visibleChiliPercent = Math.max(0.2, lightRatio); 
    
    // Stem shrinks smoothly down to 40% of its normal thickness
    thinScale = Math.max(0.4, 0.4 + (0.6 * lightRatio)); 
  }

  // Cold Stress (<15) - Drops chilies smoothly alongside the wilt, leaving at least 30%
  if (p.temperature < 15) {
    const coldSeverity = (15 - p.temperature) / 15.0; // Divisor 15.0 stretches the drag
    const coldRatio = Math.max(0.3, 1.0 - coldSeverity); // Floor set at 0.3 (30%)
    visibleChiliPercent = Math.min(visibleChiliPercent, coldRatio);
  }

  // Apply thickness directly to the mesh
  if (stemMesh) {
    stemMesh.scale.set(thinScale, 1.0, thinScale); 
  }

  // ==========================================
  // PART 2: PATHOLOGY COLOR GRADIENTS
  // ==========================================

  // Color Lerping. We linearly interpolate (blend) the base healthy hex colors with disease hex colors depending on the calculated necrosis/cold/light stress severity.
  if (leafMeshes.length > 0) {
    // 1. The Organic Base Colors (Your Custom Hex Codes)
    const healthyA = new THREE.Color('#425b32'); 
    const healthyB = new THREE.Color('#386628'); 
    
    // 2. The Disease Colors
    const deadBrownA = new THREE.Color('#554b26'); // Heat/Drought/Salt
    const deadBrownB = new THREE.Color('#8a8d53');
    const chlorosisYellow = new THREE.Color('#d4c45d'); // pH Nutrient Lockout
    const coldPurple = new THREE.Color('#2c3e50');     // Frost Damage
    const bleachedPale = new THREE.Color('#a8b89e');   // Light Photoinhibition

    // Calculate individual color stress factors (0.0 to 1.0) based on your THRESHOLDS
    let necrosisFactor = Math.max(
      // NEW: Turns brown from BOTH severe drought (<13.1) and waterlogging (>32)
      p.soilMoisture < 23 ? (23 - p.soilMoisture)/9.9 : (p.soilMoisture > 27 ? (p.soilMoisture - 27)/5.0 : 0),
      p.temperature > 30 ? (p.temperature - 30)/15 : 0,
      p.salinity > 3.0 ? (p.salinity - 3.0)/5 : 0
    );
    let coldFactor = p.temperature < 17 ? (17 - p.temperature)/10 : 0;
    let lightFactor = ppfd > 1224 ? (ppfd - 1224)/776 : (ppfd < 600 ? (600 - ppfd)/600 : 0);
 
    // Temp variables for the loop to save browser memory
    const myHealthy = new THREE.Color();
    const myDeadBrown = new THREE.Color();
    const finalDiseaseColor = new THREE.Color();

    leafMeshes.forEach((mesh, index) => {
      // ADD THIS LINE: Drops the leaves based on the percentage
      mesh.visible = (index / leafMeshes.length) < visibleLeafPercent;
      const offset = mesh.userData.colorOffset || 0;

      // Calculate this specific leaf's organic healthy and brown shades
      myHealthy.lerpColors(healthyA, healthyB, offset);
      myDeadBrown.lerpColors(deadBrownA, deadBrownB, offset);

      // ---------------------------------------------------
      // 🚀 3A. THE GPU pH LOGIC
      // ---------------------------------------------------
      let phTipSeverity = 0;

      if (p.phLevel < 7.0) {
        // Suboptimal Low (< 5.5): Targets our randomly selected "vulnerable" leaves 
        if (mesh.userData.phVulnerable) {
          phTipSeverity = Math.min((7.0 - p.phLevel) / 2.0, 1.0);
        }
      } else if (p.phLevel > 6.0) {
        // Suboptimal High (> 6.8): Targets new leaves first
        if (offset > 0.5) {
          phTipSeverity = Math.min((p.phLevel - 6.0) / 2.0, 1.0);
        } else {
          // Critical High (> 8.3): Old leaves start catching up!
          if (p.phLevel > 7.5) {
            phTipSeverity = Math.min((p.phLevel - 7.5) / 2.0, 1.0);
          }
        }
      }

      // ---------------------------------------------------
      // 🚀 3B. THE GPU HUMIDITY & HEAT LOGIC
      // ---------------------------------------------------
      let mildewSeverity = 0;
      let tipBurnSeverity = 0;
      let heatScorchSeverity = 0;

      if (p.humidity > 85) mildewSeverity = Math.min((p.humidity - 85) / 10.0, 1.0); 
      if (p.humidity < 65) tipBurnSeverity = Math.min((65 - p.humidity) / 15.0, 1.0); 
      if (p.temperature > 32) heatScorchSeverity = Math.min((p.temperature - 32) / 20.0, 1.0);

      // Ship ALL the data into the graphics card!
      if (mesh.userData.shader) {
        mesh.userData.shader.uniforms.uMildew.value = mildewSeverity;
        mesh.userData.shader.uniforms.uTipBurn.value = tipBurnSeverity;
        mesh.userData.shader.uniforms.uHeatScorch.value = heatScorchSeverity; 
        mesh.userData.shader.uniforms.uPhTipYellow.value = phTipSeverity; // SHIP pH!
      }

      // ---------------------------------------------------
      // 4. THE JAVASCRIPT MIXER
      // ---------------------------------------------------
      const otherColorStress = necrosisFactor + coldFactor + lightFactor;
      const maxOtherSickness = Math.min(Math.max(necrosisFactor, coldFactor, lightFactor), 1);

      if (otherColorStress <= 0) {
        mesh.material.color.copy(myHealthy);
      } else {
        const nW = necrosisFactor / otherColorStress;
        const coW = coldFactor / otherColorStress;
        const lW = lightFactor / otherColorStress;

        finalDiseaseColor.r = (myDeadBrown.r * nW) + (coldPurple.r * coW) + (bleachedPale.r * lW);
        finalDiseaseColor.g = (myDeadBrown.g * nW) + (coldPurple.g * coW) + (bleachedPale.g * lW);
        finalDiseaseColor.b = (myDeadBrown.b * nW) + (coldPurple.b * coW) + (bleachedPale.b * lW);

        mesh.material.color.lerpColors(myHealthy, finalDiseaseColor, maxOtherSickness);
      }
      
      if (mesh.morphTargetInfluences) {
        mesh.morphTargetInfluences[0] = droopStress;
      }
    });
  }

  // ==========================================
  // PART 2.5: FRUIT STUNTING (Salinity, Drought & Heat)
  // ==========================================
  let saltScale = 1.0; 
  if (p.salinity > 4.0) saltScale = Math.max(0.5, 1.0 - (0.5 * ((p.salinity - 4.0) / 4.64)));

  let droughtScale = 1.0;
  if (p.soilMoisture < 23) droughtScale = Math.max(0.6, 1.0 - (0.4 * ((23 - p.soilMoisture) / 9.9)));

  // Suboptimal High Temp (>28) - Shrinks to 60%
  let heatScale = 1.0;
  if (p.temperature > 28) {
    const heatSeverity = (p.temperature - 28) / 12.0; 
    heatScale = Math.max(0.6, 1.0 - (0.4 * heatSeverity));
  }

  // Apply the worst-case shrink to the final scale
  const chiliScale = Math.min(saltScale, droughtScale, heatScale);
  
  // ==========================================
  // PART 3: CHILI YIELD VISIBILITY
  // ==========================================
  if (typeof chiliMeshes !== 'undefined') {
    chiliMeshes.forEach((chili, index) => {
      chili.visible = (index / chiliMeshes.length) < visibleChiliPercent;

      // 2. NEW: Shrinks the chilies (from the Salinity logic)
      chili.scale.set(chiliScale, chiliScale, chiliScale);
    });
  }
}

function animate() {
  requestAnimationFrame(animate)
  renderer.render(scene, camera)
}

onBeforeUnmount(() => {
  if (renderer) renderer.dispose()
})

// === ENHANCED AGRONOMY RULES ENGINE ===
const THRESHOLDS = {
  temperature: {
    critical_low:  8,    // base temp from FAO/GAEZ
    stress_low:    17,   // optimal min
    optimal_low:   18,
    optimal_high:  27,   // optimal max
    stress_high:   30,
    critical_high: 35,   // max temp
  },
  humidity: {
    critical_low:  40,   // severe dry air
    stress_low:    65,   // low humidity threshold from paper
    optimal_low:   65,
    optimal_high:  85,   // high humidity threshold from paper
    stress_high:   85,
    critical_high: 95,
  },
  soilMoisture: {
    critical_low:  13.1, // wilting point (WP) from paper
    stress_low:    23,   // lower bound of optimal ±2
    optimal_low:   23,
    optimal_high:  27,   // upper bound of optimal ±2
    stress_high:   27,
    critical_high: 32,   // waterlogged
  },
  phLevel: {
    critical_low:  4.3,  // min pH from FAO/GAEZ
    stress_low:    5.5,  // optimal min
    optimal_low:   5.5,
    optimal_high:  6.8,  // optimal max
    stress_high:   6.8,
    critical_high: 8.3,  // max pH
  },
  salinity: {
    // 🔻 THE DEPLETION ZONE (Triggers 1-Liter Precision Fertigation)
    critical_low:  0.3,  // Plant is starving, growth halted completely
    stress_low:    1.0,  // The "Fuel Light" - Trigger the fertilize message!
    optimal_low:   1.0,  
    // 🟢 THE SWEET SPOT (Perfectly fed, zero osmotic stress)
    optimal_high:  1.5,  // Maas-Hoffman Limit - The absolute safe ceiling
    stress_high:   3.0,  // yield loss ~21% at this point
    critical_high: 6.0,
    severe_high:   8.64, // lethal limit (Yr = 0 from formula)
  },
  lightIntensity: {
    // values in µmol/m²/s (simDashboard translates % → µmol internally)
    critical_low:  17.3,  // LCP (light compensation point) from paper
    stress_low:    600,   // lower bound of productive range
    optimal_low:   600,
    optimal_high:  1224,  // LSP (light saturation point) from paper
    stress_high:   1224,
    critical_high: 1500,  // photoinhibition territory
  },
}

const getSeverity = (value, param) => {
  // A universal severity classifier that checks any sensor value against its specific threshold object and returns optimal, suboptimal, or critical.
  const t = THRESHOLDS[param]
  if (!t) return 'unknown'

  // Because we added an 8.64 lethal limit just for salinity, we catch it first
  if (param === 'salinity' && value >= t.severe_high) return 'severe'

  // Now everything else (including salinity) smoothly uses the two-sided bands!
  if (value < t.critical_low || value > t.critical_high) return 'critical'
  if (value < t.stress_low   || value > t.stress_high)   return 'suboptimal'
  return 'optimal'
}

// This computed property acts as an Expert System. It evaluates all parameters and builds an array of alerts, sorting them by priority so lethal compound threats (like Heat+Drought) always show first.
const combinedIssues = computed(() => {
  const issues = []
  const p = simParams.value
  
  // It listens for the True flag from Python and creates the banner locally.
  if (simResult.value?.analysis?.anomaly_detection?.is_anomaly) {
    issues.push({ 
      parameter: 'ai_anomaly',
      message: `🤖 AI STATISTICAL ANOMALY: Machine Learning model detected an unusual data cluster.`, 
      severity: 'critical', 
      impact: 'Complex multi-variable stress detected by Isolation Forest.',
      timeframe: 'Investigate dashboard parameters immediately',
      priority: 1 
    })
  }
  
  const tempSeverity = getSeverity(p.temperature, 'temperature')
  if (tempSeverity !== 'optimal') {
    if (p.temperature < THRESHOLDS.temperature.critical_low) {
      issues.push({ parameter: 'temperature', message: `🥶 SEVERE COLD STRESS (${p.temperature}°C): Plant metabolism has nearly stopped. Cellular damage is occurring.`, severity: 'critical', priority: 1, impact: 'Growth cessation, permanent tissue damage, possible plant death', timeframe: 'Critical - Act within 1 hour' })
    } else if (p.temperature < THRESHOLDS.temperature.stress_low) {
      issues.push({ parameter: 'temperature', message: `❄️ Cold Stress (${p.temperature}°C): Enzyme activity reduced by ~40%. Photosynthesis slowing.`, severity: 'warning', priority: 2, impact: 'Stunted growth, delayed flowering, reduced fruit set', timeframe: 'Address within 6 hours' })
    } else if (p.temperature > THRESHOLDS.temperature.critical_high) {
      issues.push({ parameter: 'temperature', message: `🔥 EXTREME HEAT STRESS (${p.temperature}°C): Protein denaturation occurring. Blossom drop imminent.`, severity: 'critical', priority: 1, impact: 'Flower abortion, fruit drop, permanent leaf damage', timeframe: 'URGENT - Act immediately' })
    } else if (p.temperature > THRESHOLDS.temperature.stress_high) {
      issues.push({ parameter: 'temperature', message: `🌡️ Heat Stress (${p.temperature}°C): Transpiration exceeding water uptake. Pollen viability dropping.`, severity: 'warning', priority: 2, impact: 'Reduced fruit set, smaller peppers, accelerated flowering', timeframe: 'Address within 3 hours' })
    }
  }
  
  const humSeverity = getSeverity(p.humidity, 'humidity')
  if (humSeverity !== 'optimal') {
    if (p.humidity < THRESHOLDS.humidity.critical_low) {
      issues.push({ parameter: 'humidity', message: `🏜️ SEVERE DRY AIR (${p.humidity}%): Stomata forced closed. Photosynthesis halted to prevent water loss.`, severity: 'critical', priority: 1, impact: 'Wilting, leaf curling, growth stops completely', timeframe: 'Critical - Act within 2 hours' })
    } else if (p.humidity < THRESHOLDS.humidity.stress_low) {
      issues.push({ parameter: 'humidity', message: `💨 Low Humidity (${p.humidity}%): Excessive transpiration (~3x normal). VPD too high.`, severity: 'warning', priority: 2, impact: 'Water stress, nutrient transport impaired, tip burn', timeframe: 'Address within 6 hours' })
    } else if (p.humidity > THRESHOLDS.humidity.critical_high) {
      issues.push({ parameter: 'humidity', message: `💧 SATURATED AIR (${p.humidity}%): Transpiration nearly zero. Fungal spore germination accelerating.`, severity: 'critical', priority: 1, impact: 'Botrytis, powdery mildew, bacterial spot risk extremely high', timeframe: 'URGENT - Ventilate immediately' })
    } else if (p.humidity > THRESHOLDS.humidity.stress_high) {
      issues.push({ parameter: 'humidity', message: `💦 High Humidity (${p.humidity}%): Disease pressure elevated. Calcium transport reduced.`, severity: 'warning', priority: 2, impact: 'Increased disease susceptibility, blossom end rot', timeframe: 'Address within 12 hours' })
    }
  }
  
  const moistSeverity = getSeverity(p.soilMoisture, 'soilMoisture')
  if (moistSeverity !== 'optimal') {
    if (p.soilMoisture < THRESHOLDS.soilMoisture.critical_low) {
      issues.push({ parameter: 'soilMoisture', message: `🌵 SEVERE DROUGHT (${p.soilMoisture}%): Approaching permanent wilting point. Xylem cavitation risk.`, severity: 'critical', priority: 1, impact: 'Irreversible wilting, leaf death, plant collapse', timeframe: 'EMERGENCY - Irrigate NOW' })
    } else if (p.soilMoisture < THRESHOLDS.soilMoisture.stress_low) {
      issues.push({ parameter: 'soilMoisture', message: `💧 Water Deficit (${p.soilMoisture}%): Soil tension high. Roots struggling to extract water.`, severity: 'warning', priority: 2, impact: 'Reduced turgor, fruit size decrease, blossom drop', timeframe: 'Irrigate within 6 hours' })
    } else if (p.soilMoisture > THRESHOLDS.soilMoisture.critical_high) {
      issues.push({ parameter: 'soilMoisture', message: `🌊 WATERLOGGED (${p.soilMoisture}%): Anaerobic conditions. Root oxygen deprivation causing cellular death.`, severity: 'critical', priority: 1, impact: 'Root rot, plant death', timeframe: 'URGENT - Stop irrigation, improve drainage' })
    } else if (p.soilMoisture > THRESHOLDS.soilMoisture.stress_high) {
      issues.push({ parameter: 'soilMoisture', message: `💦 Overwatered (${p.soilMoisture}%): Soil pores saturated. Oxygen levels dropping.`, severity: 'warning', priority: 2, impact: 'Weak root development, nutrient leaching, disease risk', timeframe: 'Skip next irrigation, monitor closely' })
    }
  }
  
  const phSeverity = getSeverity(p.phLevel, 'phLevel')
  if (phSeverity !== 'optimal') {
    if (p.phLevel < THRESHOLDS.phLevel.critical_low) {
      issues.push({ parameter: 'phLevel', message: `🔴 EXTREME ACIDITY (pH ${p.phLevel}): Aluminum/manganese toxicity. Phosphorus locked out.`, severity: 'critical', priority: 1, impact: 'Nutrient lockout, root damage, yellowing, stunted growth', timeframe: 'Critical - Lime application required' })
    } else if (p.phLevel < THRESHOLDS.phLevel.stress_low) {
      issues.push({ parameter: 'phLevel', message: `🍋 Acidic Soil (pH ${p.phLevel}): Nitrogen availability reduced by ~30%. Calcium uptake impaired.`, severity: 'warning', priority: 2, impact: 'Slow growth, yellowing leaves, blossom end rot risk', timeframe: 'Address within 1 week' })
    } else if (p.phLevel > THRESHOLDS.phLevel.critical_high) {
      issues.push({ parameter: 'phLevel', message: `🔵 EXTREME ALKALINITY (pH ${p.phLevel}): Iron/zinc chelation failed. Micronutrient crisis.`, severity: 'critical', priority: 1, impact: 'Interveinal chlorosis, iron deficiency, growth cessation', timeframe: 'Critical - Acidify immediately' })
    } else if (p.phLevel > THRESHOLDS.phLevel.stress_high) {
      issues.push({ parameter: 'phLevel', message: `⚗️ Alkaline Soil (pH ${p.phLevel}): Iron availability dropping. Chlorosis developing.`, severity: 'warning', priority: 2, impact: 'Yellowing new growth, reduced yields', timeframe: 'Address within 1 week' })
    }
  }
  
  const salSeverity = getSeverity(p.salinity, 'salinity')
  if (salSeverity !== 'optimal') {
    if (p.salinity > THRESHOLDS.salinity.severe_high) {
      issues.push({ parameter: 'salinity', message: `⚠️ SALT TOXICITY (${p.salinity} dS/m): Osmotic stress extreme. Plant cannot absorb water despite availability.`, severity: 'severe', priority: 1, impact: 'Yield loss >70%, leaf burn, possible plant death', timeframe: 'EMERGENCY - Flush soil immediately' })
    } else if (p.salinity > THRESHOLDS.salinity.critical_high) {
      issues.push({ parameter: 'salinity', message: `🧂 HIGH SALT (${p.salinity} dS/m): Yield reduction ~${Math.round((p.salinity - 1.5) * 14)}%. Ion toxicity building.`, severity: 'critical', priority: 1, impact: `Estimated ${Math.round((p.salinity - 1.5) * 14)}% yield loss, leaf tip necrosis`, timeframe: 'Leach within 48 hours' })
    } else if (p.salinity > THRESHOLDS.salinity.optimal_high) {
      issues.push({ parameter: 'salinity', message: `🧂 Elevated Salt (${p.salinity} dS/m): Threshold exceeded. Yield reduction beginning (~${Math.round((p.salinity - 1.5) * 14)}%).`, severity: 'warning', priority: 2, impact: 'Reduced growth, smaller fruits, leaf edge browning', timeframe: 'Leach soon' })
    } else if (p.salinity < THRESHOLDS.salinity.critical_low) {
      // 🚀 NEW: Plant is starving
      issues.push({ parameter: 'salinity', message: `📉 SEVERE STARVATION (${p.salinity} dS/m): Soil completely depleted of NPK.`, severity: 'critical', priority: 1, impact: 'Growth halted, severe nutrient deficiency', timeframe: 'Fertilize immediately' })
    } else if (p.salinity < THRESHOLDS.salinity.stress_low) {
      // 🚀 NEW: The Fuel Light is on!
      issues.push({ parameter: 'salinity', message: `⛽ Low Nutrients (${p.salinity} dS/m): Soil depleting. Top off required to maintain optimal growth.`, severity: 'warning', priority: 3, impact: 'Suboptimal growth', timeframe: 'Fertilize within 48 hours' })
    }
  }
  
  // 1. Secret Translation for the Frontend Alerts
  const actualPPFD = (p.lightIntensity / 100) * 2000;
  
  // 2. Evaluate the translated actualPPFD, NOT the percentage
  const lightSeverity = getSeverity(actualPPFD, 'lightIntensity')
  
  if (lightSeverity !== 'optimal') {
    if (actualPPFD < THRESHOLDS.lightIntensity.critical_low) {
      issues.push({ parameter: 'lightIntensity', message: `🌑 SEVERE LIGHT STARVATION (${Math.round(actualPPFD)} µmol/m²/s): Below compensation point. Using stored energy to survive.`, severity: 'critical', priority: 1, impact: 'Etiolation, flower abortion, stem elongation, leaf drop', timeframe: 'URGENT - Supplement light immediately' })
    } else if (actualPPFD < THRESHOLDS.lightIntensity.stress_low) {
      issues.push({ parameter: 'lightIntensity', message: `🌥️ Insufficient Light (${Math.round(actualPPFD)} µmol/m²/s): Photosynthesis ~40% of optimal. Energy deficit.`, severity: 'warning', priority: 2, impact: 'Leggy growth, poor fruiting, low yields', timeframe: 'Increase light within 24 hours' })
    } else if (actualPPFD > THRESHOLDS.lightIntensity.critical_high) {
      issues.push({ parameter: 'lightIntensity', message: `☀️ PHOTOINHIBITION (${Math.round(actualPPFD)} µmol/m²/s): Chloroplast damage. Reactive oxygen species accumulating.`, severity: 'critical', priority: 1, impact: 'Bleached leaves, sunburn, photosystem II damage', timeframe: 'URGENT - Shade immediately' })
    } else if (actualPPFD > THRESHOLDS.lightIntensity.stress_high) {
      issues.push({ parameter: 'lightIntensity', message: `☀️ Excessive Light (${Math.round(actualPPFD)} µmol/m²/s): Approaching saturation. Leaf temperature rising.`, severity: 'warning', priority: 2, impact: 'Leaf curling, increased transpiration, heat stress', timeframe: 'Consider shade cloth' })
    }
  }
  
  if (p.temperature > 30 && p.soilMoisture < 23) {
    issues.push({ parameter: 'combined', message: `⚠️ COMPOUNDED CRISIS: Heat + Drought detected. LETHAL for peppers.`, severity: 'severe', priority: 1, impact: 'Rapid wilting, irreversible damage within hours', timeframe: 'EMERGENCY - Cool AND water immediately' })
  }
  if (p.humidity > 85 && p.soilMoisture > 27) {
    issues.push({ parameter: 'combined', message: `🍄 DISEASE BOMB: High humidity + waterlogged soil = fungal incubator.`, severity: 'severe', priority: 1, impact: 'Pythium, fusarium, bacterial wilt risk extreme', timeframe: 'EMERGENCY - Ventilate AND drain NOW' })
  }
  if (p.salinity > 2.5 && p.soilMoisture < 23) {
    issues.push({ parameter: 'combined', message: `🧪 SALT + DROUGHT SYNERGY: Concentrated salts + low water = osmotic shock.`, severity: 'severe', priority: 1, impact: 'Plant cannot absorb water despite need', timeframe: 'Must leach AND irrigate carefully' })
  }
  
  return issues.sort((a, b) => a.priority - b.priority)
})

// A decision-tree algorithm that maps specific environmental issues to actionable, real-world agronomic interventions (e.g., applying shade cloth vs. watering).
const expertRecommendations = computed(() => {
  const recs = []
  const p = simParams.value  
  const issues = combinedIssues.value
  
  issues.forEach(issue => {
    const severity = issue.severity
    const color = severity === 'critical' || severity === 'severe' ? '#e74c3c' : severity === 'warning' ? '#e67e22' : '#f39c12'
    
    switch(issue.parameter) {
      case 'temperature':
        if (p.temperature > THRESHOLDS.temperature.stress_high) { recs.push({ tag: 'URGENT: Cooling', color: '#e74c3c', action: p.temperature > 33 ? 'Emergency shade + misting' : 'Deploy 50% shade cloth', reason: issue.impact, priority: issue.priority, cost: 'Moderate', effectiveness: '95%', implementation: '1-2 hours' }) }
        else if (p.temperature < THRESHOLDS.temperature.stress_low) { recs.push({ tag: 'URGENT: Heating', color: '#e74c3c', action: p.temperature < 12 ? 'Emergency heating + insulation' : 'Move to warmer location or heat', reason: issue.impact, priority: issue.priority, cost: 'Low-Moderate', effectiveness: '90%', implementation: '1-3 hours' }) }
        break
      case 'humidity':
        if (p.humidity > THRESHOLDS.humidity.stress_high) { recs.push({ tag: 'Ventilation', color: '#3498db', action: p.humidity > 90 ? 'Max ventilation + dehumidifier' : 'Increase air circulation (fans)', reason: issue.impact, priority: issue.priority, cost: 'Low', effectiveness: '85%', implementation: 'Immediate' }) }
        else if (p.humidity < THRESHOLDS.humidity.stress_low) { recs.push({ tag: 'Humidification', color: '#3498db', action: p.humidity < 45 ? 'Misting system + water trays' : 'Increase humidity (misting)', reason: issue.impact, priority: issue.priority, cost: 'Low', effectiveness: '80%', implementation: '30 minutes' }) }
        break
      case 'soilMoisture':
        if (p.soilMoisture > THRESHOLDS.soilMoisture.stress_high) { recs.push({ tag: 'STOP Watering', color: '#e74c3c', action: p.soilMoisture > 30 ? 'Halt irrigation + drill drainage holes' : 'Skip irrigation + improve drainage', reason: issue.impact, priority: issue.priority, cost: 'Very Low', effectiveness: '100%', implementation: 'Immediate' }) }
        else if (p.soilMoisture < THRESHOLDS.soilMoisture.stress_low) {
          const aiAmount = simResult.value?.analysis?.recommendations?.irrigation?.amount_liters
          recs.push({ tag: 'Irrigate NOW', color: '#3498db', action: aiAmount ? `Water ${aiAmount}L immediately` : `Water ${((26.1 - p.soilMoisture) * 0.0197).toFixed(3)}L now`, reason: issue.impact, priority: issue.priority, cost: 'Very Low', effectiveness: '100%', implementation: '15 minutes' })
        }
        break
      case 'phLevel':
        if (p.phLevel < THRESHOLDS.phLevel.stress_low) { recs.push({ tag: 'pH Correction', color: '#9b59b6', action: `Apply powdered dolomite lime to neutralize soil acidity and safely raise pH`, reason: issue.impact, priority: issue.priority, cost: 'Low', effectiveness: '90%' }) }
        else if (p.phLevel > THRESHOLDS.phLevel.stress_high) { recs.push({ tag: 'pH Correction', color: '#9b59b6', action: `Apply iron sulfate to reduce soil alkalinity and safely lower pH`, reason: issue.impact, priority: issue.priority, cost: 'Low', effectiveness: '85%' }) }
        break
      case 'salinity':
        if (p.salinity > THRESHOLDS.salinity.optimal_high) { 
          recs.push({ tag: 'Leach Salts', color: '#e67e22', action: `Flush with ${p.salinity > 4.0 ? '3x' : '2x'} pot volume of clean water`, reason: `Current salinity is causing osmotic stress and yield loss.`, priority: issue.priority, cost: 'Very Low', effectiveness: '95%', implementation: 'Immediate' }) 
        }
        else if (p.salinity < THRESHOLDS.salinity.optimal_low) { 
          // Safety Check: Never fertilize during a pH lockout
          if (p.phLevel < 5.8 || p.phLevel > 6.8) {
             recs.push({ tag: '⚠️ NUTRIENT LOCKOUT', color: '#e74c3c', action: 'DO NOT FERTILIZE. Fix pH first.', reason: 'Roots cannot absorb nutrients at current pH.', priority: 1, cost: 'Low', effectiveness: 'Critical', implementation: 'Immediate' })
          } else {
             // --- EXPLICIT MATH VARIABLES ---
             const targetEC = 1.4;
             const waterVolume = 1.0; // <-- Change this to 2.0, 5.0, etc., in the future!
             
             // The full dimensional analysis formula: (Deficit * 640 * Volume) / 1000
             const grams = (((targetEC - p.salinity) * 640 * waterVolume) / 1000).toFixed(2);
             
             recs.push({ 
               tag: 'Precision Fertigation', 
               color: '#27ae60', 
               action: `Mix ${grams}g of NPK into your ${waterVolume}L watering bottle`, 
               reason: `Safely replenishes soil to ${targetEC} dS/m without crossing the 1.5 Maas-Hoffman threshold.`, 
               priority: issue.priority, 
               cost: 'Low', 
               effectiveness: '100%',   
               implementation: 'Next Watering' 
             }) 
          }
        }
        break
      // --- START REPLACEMENT 2 ---
      case 'lightIntensity':
        // Translate here as well
        const actualPPFD_rec = (p.lightIntensity / 100) * 2000;
        
        if (actualPPFD_rec < THRESHOLDS.lightIntensity.stress_low) { 
          recs.push({ tag: 'Supplemental Light', color: '#f1c40f', action: `Add grow lights (need +${Math.round(600 - actualPPFD_rec)} µmol)`, reason: issue.impact, priority: issue.priority, cost: 'Moderate', effectiveness: '100%', implementation: '24 hours' }) 
        }
        else if (actualPPFD_rec > THRESHOLDS.lightIntensity.stress_high) { 
          recs.push({ tag: 'Shading', color: '#34495e', action: actualPPFD_rec > 1300 ? 'Apply 50% shade cloth' : 'Apply 30% shade cloth', reason: issue.impact, priority: issue.priority, cost: 'Low', effectiveness: '100%', implementation: '30 minutes' }) 
        }
        break
      // --- END REPLACEMENT 2 ---
      case 'combined':
        recs.push({ tag: '⚠️ MULTI-STRESS', color: '#c0392b', action: 'Address ALL flagged issues simultaneously', reason: issue.impact, priority: 1, cost: 'Variable', effectiveness: 'Critical', implementation: 'Immediate' })
        break
    }
  })
  
  return recs.filter((rec, index, self) => index === self.findIndex(r => r.tag === rec.tag && r.action === rec.action)).sort((a, b) => a.priority - b.priority)
})

const hasRecommendations = computed(() => expertRecommendations.value.length > 0)

const dynamicAlerts = computed(() => {
  const alerts = []
  const issues = combinedIssues.value
  
  if (issues.length === 0) {
    alerts.push({ type: 'success', title: '🎯 Perfect Growing Conditions', message: 'All environmental parameters are within optimal range for Capsicum annuum.', time: 'Current Status' })
  } else {
    const critical = issues.filter(i => i.severity === 'critical' || i.severity === 'severe')
    const warnings = issues.filter(i => i.severity === 'warning')
    const cautions = issues.filter(i => i.severity === 'caution')
    
    // ✅ Let all severity levels push to the alerts array independently
    if (critical.length > 0) { 
      critical.forEach(issue => { 
        alerts.push({ type: 'critical', title: '🚨 CRITICAL ALERT', message: issue.message, detail: `Impact: ${issue.impact} | Timeframe: ${issue.timeframe}`, time: 'Immediate Action Required' }) 
      }) 
    }
    if (warnings.length > 0) { 
      warnings.forEach(issue => { 
        alerts.push({ type: 'warning', title: '⚠️ Warning', message: issue.message, detail: `Impact: ${issue.impact}`, time: 'Action Needed' }) 
      }) 
    }
    if (cautions.length > 0) { 
      cautions.forEach(issue => { 
        alerts.push({ type: 'info', title: 'ℹ️ Suboptimal', message: issue.message, time: 'Monitor Closely' }) 
      }) 
    }
  }

  return alerts
})

const healthScoreInsight = computed(() => {
  const health = simResult.value?.analysis?.health?.overall_score || 0
  if (health >= 90) return { emoji: '🌟', status: 'Excellent', description: 'Plant is thriving in near-perfect conditions', color: '#27ae60' }
  if (health >= 75) return { emoji: '✅', status: 'Good', description: 'Plant is healthy with minor stress factors', color: '#2ecc71' }
  if (health >= 60) return { emoji: '⚠️', status: 'Fair', description: 'Plant is coping but stress is accumulating', color: '#f39c12' }
  if (health >= 40) return { emoji: '❌', status: 'Poor', description: 'Plant is struggling, intervention needed', color: '#e67e22' }
  return { emoji: '🆘', status: 'Critical', description: 'Plant survival at risk, emergency measures required', color: '#e74c3c' }
})

// === KEEP YOUR EXISTING `runSimulation`, `watch`, and `onMounted` FUNCTIONS BELOW THIS LINE ===

// --- THE FETCH FUNCTION ---

// The HTTP POST request to the Python Flask backend. We send the translated scientific data to the Isolation Forest / Predictive model to get our final AI forecast.
const runSimulation = async () => {
  isSimulating.value = true
  try {
    // 1. Secret Translation: Convert UI percentage to Scientific PPFD
    const calculatedPPFD = (simParams.value.lightIntensity / 100) * 2000;

    const response = await fetch('http://127.0.0.1:5000/api/ml/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        temperature: simParams.value.temperature, // Reverted to original key
        humidity: simParams.value.humidity,
        soilMoisture: simParams.value.soilMoisture, // Reverted to original key
        phLevel: simParams.value.phLevel, // Reverted to original key
        salinity: simParams.value.salinity,
        lightIntensity: calculatedPPFD // Send the calculated µmol to the original key
      })
    })
    
    if (response.ok) {
      const data = await response.json()
      simResult.value = data
    }
  } catch (error) {
    console.error("Failed to run simulation:", error)
  } finally {
    isSimulating.value = false
  }
}

// --- VUE WATCHER (The Magic Trick) ---

// 1. Create the timer variable just above your watcher
let debounceTimer = null;

// This watches the simParams object. Anytime a slider moves, it re-runs the AI!
watch(simParams, () => {

  // The moment a slider moves, it instantly fires a new 
  // asynchronous payload to our Flask ML backend and simultaneously triggers 
  // the Three.js engine to morph the plant visually.
  
  updatePlantVisuals()

  // First, clear the previous timer if the user is still dragging.
  clearTimeout(debounceTimer)

  // Then, set a new timer. It will wait 300ms after the slider stops before fetching.
  debounceTimer = setTimeout(() => {
    runSimulation()
  }, 300)

}, { deep: true })


// Run an initial simulation as soon as the page loads
onMounted(() => {
  initThreeJS()
  runSimulation()
})
</script>

<style scoped>
/* Reuse the Layout from LiveDashboard for consistency */
.dashboard-container {
  min-height: 100vh;
  width: 100%;
  background-color: #f8f9fa;
  font-family: 'Segoe UI', sans-serif;
  display: flex;
  flex-direction: column;
}
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

/* TABS */
.tabs-container {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
}
.tab {
  background: white;
  padding: 10px 25px;
  border-radius: 25px;
  font-weight: 600;
  color: #7f8c8d;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s;
}
.tab.active {
  background: white;
  color: #2c3e50;
  border-color: #2c3e50;
}
.tab:hover:not(.active) {
  background: #e9ecef;
}

/* GRID LAYOUT FOR TOP SECTION */
.sim-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 25px;
  margin-bottom: 40px;
  min-height: 600px;
}
@media (max-width: 1000px) {
  .sim-grid {
    grid-template-columns: 1fr;
  }
}

/* AI SECTION STYLES */
.ai-section {
  margin-bottom: 40px;
}
.ai-card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
}
.yield-banner {
  background: #fff9c4;
  padding: 15px 20px;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}
.prediction {
  font-size: 2rem;
  font-weight: bold;
  color: #f57f17;
}

.insight-label,
.rec-label {
  font-size: 0.9rem;
  color: #7f8c8d;
  margin-bottom: 10px;
  display: block;
}
.alert-banner {
  padding: 15px;
  border-radius: 6px;
  display: flex;
  gap: 15px;
  align-items: flex-start;
  margin-bottom: 25px;
}
.alert-banner.critical {
  background: #ffebee;
  border-left: 4px solid #c0392b;
  color: #c0392b;
}
.alert-banner.warning {
  background: #fff3e0;
  border-left: 4px solid #f39c12;
  color: #e67e22;
}

.rec-item {
  border: 1px solid #eee;
  padding: 15px;
  border-radius: 8px;
  display: flex;
  gap: 15px;
  margin-bottom: 10px;
  align-items: center;
}
.tag.high {
  background: #e74c3c;
  color: white;
  padding: 4px 10px;
  border-radius: 4px;
  font-weight: bold;
  font-size: 0.75rem;
  height: fit-content;
}
.rec-content p {
  margin: 0;
  font-size: 0.85rem;
  color: #7f8c8d;
}

/* ALERTS SECTION */
.section-header.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.badge-count {
  background: #e74c3c;
  color: white;
  padding: 5px 10px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: bold;
}
.alerts-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
} 
</style>
