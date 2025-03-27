<template>
  <div 
    class="sidebar-button" 
    :class="{ active: isActive }"
    @click="$emit('click')"
  >
    <i v-if="icon" :class="icon" class="button-icon"></i>
    <span class="button-text">{{ text }}</span>
  </div>
</template>

<script setup>
defineProps({
  text: {
    type: String,
    required: true
  },
  icon: {
    type: String,
    default: ''
  },
  isActive: {
    type: Boolean,
    default: false
  }
});

defineEmits(['click']);
</script>

<style scoped>
.sidebar-button {
  padding: 12px 20px;
  margin: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  color: #fff;
  transition: background-color 0.3s;
  display: flex;
  align-items: center;
}

.sidebar-button:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.sidebar-button.active {
  background-color: rgba(255, 255, 255, 0.2);
}

.button-icon {
  margin-right: 10px;
}

.button-text {
  font-size: 14px;
}
</style> 