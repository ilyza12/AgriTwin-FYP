const API_URL = 'http://127.0.0.1:5000/api'

export default {
  // 1. Fetch latest data from Flask
  async getLatestReadings() {
    try {
      const response = await fetch(`${API_URL}/sensors/latest`)
      if (!response.ok) {
        throw new Error('Network response was not ok')
      }
      return await response.json()
    } catch (error) {
      console.error('API Error:', error)
      return null
    }
  },

  // 2. (Optional) For testing: Send fake data to Flask
  async sendFakeData(data) {
    try {
      const response = await fetch(`${API_URL}/sensors/update`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      })
      return await response.json()
    } catch (error) {
      console.error('API Post Error:', error)
    }
  },

  // NEW: Fetch historical data
  async getHistory(timeRange) {
    try {
      // e.g. /api/sensors/history?range=7d
      const response = await fetch(`${API_URL}/sensors/history?range=${timeRange}`)
      return await response.json()
    } catch (error) {
      console.error('History API Error:', error)
      return []
    }
  },
}
