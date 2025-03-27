<template>
  <div class="logo-container">
    <img src="../assets/logo-transparent.png" alt="Logo" class="logo-image" />
  </div>
</template>

<script setup>
// 无需额外的脚本逻辑
</script>

<style scoped>
.logo-container {
  padding: 16px;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 80px; /* 增加Logo容器高度 */
}

.logo-image {
  height: 200%;
  width: auto;
  object-fit: contain;
}
</style> 