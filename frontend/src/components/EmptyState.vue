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
  gap: 9px;
  padding: 28px;
  color: var(--nh-muted);
  text-align: center;
}

.empty-state :deep(.el-icon) {
  display: grid;
  width: 54px;
  height: 54px;
  place-items: center;
  color: var(--nh-primary);
  background: var(--nh-soft);
  border: 1px solid var(--nh-border);
  border-radius: var(--nh-radius);
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
