<template>
  <div class="empty-state">
    <el-icon :size="34"><Document /></el-icon>
    <strong>{{ title }}</strong>
    <p>{{ description }}</p>
  </div>
</template>

<script setup lang="ts">
import { Document } from '@element-plus/icons-vue'

defineProps<{
  title?: string
  description?: string
}>()
</script>

<style scoped>
.empty-state {
  display: grid;
  min-height: 180px;
  place-items: center;
  gap: 10px;
  padding: 28px;
  color: var(--nh-muted);
  text-align: center;
  animation: nh-fade-up 260ms var(--nh-transition) both;
}

.empty-state :deep(.el-icon) {
  display: grid;
  width: 54px;
  height: 54px;
  place-items: center;
  color: var(--nh-primary-dark);
  background: rgba(255, 253, 248, 0.82);
  border: 1px solid var(--nh-border);
  border-radius: var(--nh-radius);
  box-shadow: 0 10px 22px rgba(84, 60, 28, 0.08);
}

strong {
  color: var(--nh-ink);
  font-size: 17px;
}

p {
  max-width: 360px;
  margin: 0;
  line-height: 1.7;
}
</style>
