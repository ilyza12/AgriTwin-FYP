<template>
  <div class="alert-container" v-if="visible">
    <div class="alert-card" :class="type">
      <div class="icon-box">
        <span v-if="type === 'critical'">⚠️</span>
        <span v-else-if="type === 'warning'">⚡</span>
        <span v-else-if="type === 'success'">✅</span>
        <span v-else>ℹ️</span>
      </div>

      <div class="content-box">
        <div class="header-row">
          <h4>{{ title }}</h4>
          <span class="time">{{ time }}</span>
        </div>
        <p>{{ message }}</p>
      </div>

      <div class="action-box">
        <button v-if="actionLabel" @click="$emit('action')" class="action-btn">
          {{ actionLabel }}
        </button>
        <button @click="visible = false" class="close-btn">×</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  title: String,
  message: String,
  type: {
    type: String,
    default: 'info', // Options: 'critical', 'warning', 'success', 'info'
    validator: (value) => ['critical', 'warning', 'success', 'info'].includes(value),
  },
  time: {
    type: String,
    default: 'Just now',
  },
  actionLabel: String,
})

defineEmits(['action'])

const visible = ref(true)
</script>

<style scoped>
.alert-container {
  margin-bottom: 15px;
  animation: slideIn 0.3s ease-out;
}

.alert-card {
  display: flex;
  align-items: flex-start;
  padding: 15px;
  border-radius: 8px;
  background: white;
  border-left: 5px solid #ccc;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

/* --- COLOR THEMES (Matches your Report Figure A.6) --- */

/* Critical (Red) */
.alert-card.critical {
  background-color: #ffebee;
  border-left-color: #e74c3c;
}
.alert-card.critical h4 {
  color: #c0392b;
}
.alert-card.critical .action-btn {
  background: #e74c3c;
  color: white;
}

/* Warning (Yellow) */
.alert-card.warning {
  background-color: #fffde7;
  border-left-color: #f1c40f;
}
.alert-card.warning h4 {
  color: #f39c12;
}
.alert-card.warning .action-btn {
  background: #f1c40f;
  color: black;
}

/* Success (Green) */
.alert-card.success {
  background-color: #e8f5e9;
  border-left-color: #27ae60;
}
.alert-card.success h4 {
  color: #27ae60;
}
.alert-card.success .action-btn {
  background: #27ae60;
  color: white;
}

/* Info (Blue) */
.alert-card.info {
  background-color: #e3f2fd;
  border-left-color: #3498db;
}
.alert-card.info h4 {
  color: #2980b9;
}

/* --- LAYOUT STYLES --- */
.icon-box {
  font-size: 1.5rem;
  margin-right: 15px;
  padding-top: 2px;
}

.content-box {
  flex: 1;
}

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
}

h4 {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
}

.time {
  font-size: 0.75rem;
  color: #7f8c8d;
  margin-right: 10px;
}

p {
  margin: 0;
  font-size: 0.9rem;
  color: #34495e;
  line-height: 1.4;
}

.action-box {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10px;
  margin-left: 15px;
}

.action-btn {
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: opacity 0.2s;
}
.action-btn:hover {
  opacity: 0.9;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  color: #95a5a6;
  cursor: pointer;
  line-height: 1;
}
.close-btn:hover {
  color: #7f8c8d;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
