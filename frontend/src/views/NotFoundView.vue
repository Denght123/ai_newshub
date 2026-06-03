<template>
  <main class="not-found-page">
    <section class="not-found-panel">
      <AppLogo />
      <h1>页面不存在</h1>
      <p>这个地址没有对应的页面，可以回到每日采集继续整理资讯。</p>
      <el-button type="primary" @click="router.push('/daily')">回到每日采集</el-button>
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
  min-height: 100dvh;
  place-items: center;
  padding: 24px;
  overflow: hidden;
  background:
    linear-gradient(180deg, rgba(255, 250, 240, 0.82), rgba(239, 225, 201, 0.72)),
    repeating-linear-gradient(
      0deg,
      transparent 0,
      transparent 31px,
      var(--nh-line) 32px,
      transparent 33px
    );
}

.not-found-page::before {
  position: absolute;
  inset: 18px;
  z-index: -1;
  content: "";
  border: 1px solid rgba(205, 179, 139, 0.36);
  border-radius: var(--nh-radius);
  pointer-events: none;
}

.not-found-panel {
  position: relative;
  display: grid;
  width: min(440px, 100%);
  gap: 18px;
  padding: 36px;
  overflow: hidden;
  background:
    linear-gradient(180deg, rgba(255, 253, 248, 0.98), rgba(255, 250, 240, 0.92)),
    var(--nh-paper);
  border: 1px solid var(--nh-border);
  border-radius: var(--nh-radius);
  box-shadow: var(--nh-shadow);
  animation: nh-fade-up 340ms var(--nh-transition) both;
}

h1 {
  margin: 0;
  font-family: var(--nh-font-heading);
  font-size: 32px;
  font-weight: 750;
  letter-spacing: 0;
  line-height: 1.18;
}

p {
  margin: 0;
  color: var(--nh-muted);
  line-height: 1.7;
}
</style>
