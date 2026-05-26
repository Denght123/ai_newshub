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
  gap: 8px;
  padding: 28px;
  color: #718078;
  text-align: center;
}

strong {
  color: #26352f;
  font-size: 17px;
}

p {
  max-width: 360px;
  margin: 0;
  line-height: 1.7;
}
</style>
