<template>
  <div class="role-badge" :class="roleClass">
    {{ roleName }}
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  roleName: {
    type: String,
    required: true
  }
});

const roleClass = computed(() => {
  switch (props.roleName) {
    case '管理员':
      return 'admin';
    case '员工':
      return 'staff';
    case '客户':
      return 'customer';
    default:
      return '';
  }
});
</script>

<style scoped>
.role-badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.role-badge:hover {
  transform: translateY(-1px);
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
}

.admin {
  background: linear-gradient(135deg, #ffd700, #ffaa00);
  color: #5c4500;
  border: 1px solid rgba(255, 215, 0, 0.3);
}

.staff {
  background: linear-gradient(135deg, #87ceeb, #4a9bd1);
  color: #1a4766;
  border: 1px solid rgba(135, 206, 235, 0.3);
}

.customer {
  background: linear-gradient(135deg, #98fb98, #56c656);
  color: #1e5e1e;
  border: 1px solid rgba(152, 251, 152, 0.3);
}
</style> 