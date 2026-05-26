<template>
  <span class="score-row" :aria-label="`${label}${value}分`">
    <span v-for="index in 5" :key="index" class="score-dot" :class="{ 'is-on': index <= value }" />
  </span>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    value?: number
    label?: string
  }>(),
  {
    value: 0,
    label: '评分',
  },
)
</script>
