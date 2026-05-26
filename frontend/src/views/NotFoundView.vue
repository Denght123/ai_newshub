<template>
  <main class="not-found-page">
    <section class="not-found-panel">
      <AppLogo />
      <h1>页面不存在</h1>
      <p>这个地址没有对应的页面，可以回到仪表盘继续整理资讯。</p>
      <el-button type="primary" @click="router.push('/dashboard')">回到仪表盘</el-button>
    </section>
  </main>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import AppLogo from '@/components/AppLogo.vue'

const router = useRouter()
</script>

<style scoped>
.not-found-page {
  display: grid;
  min-height: 100vh;
  place-items: center;
  padding: 24px;
}

.not-found-panel {
  display: grid;
  width: min(440px, 100%);
  gap: 18px;
  padding: 34px;
  background: rgba(255, 255, 255, 0.86);
  border: 1px solid var(--nh-border);
  border-radius: 8px;
  box-shadow: var(--nh-shadow);
}

h1 {
  margin: 0;
  font-size: 30px;
  letter-spacing: 0;
}

p {
  margin: 0;
  color: var(--nh-muted);
  line-height: 1.7;
}
</style>
