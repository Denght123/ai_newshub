<template>
  <div class="loading-state">
    <el-skeleton :rows="rows" animated />
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    rows?: number
  }>(),
  {
    rows: 5,
  },
)
</script>

<style scoped>
.loading-state {
  padding: 18px;
}
</style>
