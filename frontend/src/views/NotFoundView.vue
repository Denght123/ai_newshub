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
  position: relative;
  display: grid;
  min-height: 100vh;
  place-items: center;
  padding: 24px;
  overflow: hidden;
}

.not-found-page::before {
  position: absolute;
  inset: 0;
  z-index: -1;
  content: "";
  background:
    linear-gradient(120deg, rgba(45, 108, 223, 0.12), transparent 42%),
    linear-gradient(300deg, rgba(22, 163, 148, 0.13), transparent 48%);
}

.not-found-panel {
  display: grid;
  width: min(440px, 100%);
  gap: 18px;
  padding: 36px;
  background: rgba(255, 255, 255, 0.88);
  border: 1px solid var(--nh-border);
  border-radius: var(--nh-radius);
  box-shadow: var(--nh-shadow);
  backdrop-filter: blur(18px);
  animation: nh-fade-up 360ms ease both;
}

h1 {
  margin: 0;
  font-size: 32px;
  letter-spacing: 0;
  line-height: 1.18;
}

p {
  margin: 0;
  color: var(--nh-muted);
  line-height: 1.7;
}
</style>
