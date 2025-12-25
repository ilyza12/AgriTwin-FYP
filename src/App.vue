<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
  <RouterView />
</template>

<style>
/* GLOBAL STYLES - Resets standard margins */
html,
body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f8f9fa; /* Matches your dashboard background */
}

#app {
  width: 100%;
  min-height: 100vh;
}
</style>
