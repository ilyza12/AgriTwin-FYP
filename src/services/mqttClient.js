import mqtt from 'mqtt'
import { reactive, ref } from 'vue'

// 1. Create a reactive object to hold the live data
export const liveSensorData = reactive({
  temperature: 0,
  humidity: 0,
  moisture: 0,
  light_percent: 0,
  light: 0,
  ph: 0,
  salinity: 0,
})

// 2. Track connection status
export const isMqttConnected = ref(false)

let client = null

// 3. Function to start the connection
export function startMqttClient() {
  if (client) return // Prevent multiple connections

  // Connect to HiveMQ using WebSockets (wss:// on port 8884)
  const brokerUrl = 'wss://broker.hivemq.com:8884/mqtt'
  client = mqtt.connect(brokerUrl)

  client.on('connect', () => {
    isMqttConnected.value = true
    console.log('✅ Vue connected to HiveMQ!')
    client.subscribe('agritwin/sensors/live') // Must match your ESP32 topic
  })

  client.on('message', (topic, message) => {
    try {
      const incomingData = JSON.parse(message.toString())

      // Update our reactive object with the new data
      // (This will instantly update any Vue component using it)
      Object.assign(liveSensorData, incomingData)
    } catch (error) {
      console.error('Error parsing MQTT data:', error)
    }
  })

  client.on('error', (err) => {
    console.error('MQTT Error:', err)
    client.end()
  })
}

// 4. Function to cleanly disconnect
export function stopMqttClient() {
  if (client) {
    client.end()
    client = null
    isMqttConnected.value = false
  }
}
