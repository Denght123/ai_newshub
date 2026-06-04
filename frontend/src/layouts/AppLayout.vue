<template>
  <el-container class="app-layout">
    <el-aside class="sidebar" width="280px">
      <AppLogo />
      <el-menu :default-active="route.path" router class="nav-menu">
        <el-menu-item index="/daily">
          <el-icon><MagicStick /></el-icon>
          <span>每日采集</span>
        </el-menu-item>
        <el-menu-item index="/knowledge">
          <el-icon><Files /></el-icon>
          <span>知识库</span>
        </el-menu-item>
        <el-menu-item index="/ask">
          <el-icon><ChatLineRound /></el-icon>
          <span>AI 问答</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="topbar">
        <div class="topbar-copy">
          <span class="topbar-title">{{ route.meta.title || 'AI NewsHub' }}</span>
          <small>把每日 AI 资讯沉淀为可检索、可追溯的 RAG 知识库</small>
        </div>
        <el-dropdown>
          <el-button>
            <el-icon><User /></el-icon>
            {{ authStore.user?.nickname || authStore.user?.username || '用户' }}
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item disabled>{{ authStore.user?.email }}</el-dropdown-item>
              <el-dropdown-item v-if="isMockModeEnabled" disabled>当前为演示模式</el-dropdown-item>
              <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-header>

      <el-main class="main-content">
        <RouterView />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { ChatLineRound, Files, MagicStick, User } from '@element-plus/icons-vue'
import AppLogo from '@/components/AppLogo.vue'
import { useAuthStore } from '@/stores/auth'
import { isMockMode } from '@/api/mock'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const isMockModeEnabled = isMockMode()

function handleLogout() {
  authStore.logout()
  localStorage.removeItem('ai_newshub_mock')
  router.push('/login')
}
</script>

<style scoped>
.app-layout {
  min-height: 100dvh;
}

.sidebar {
  position: sticky;
  top: 0;
  height: 100dvh;
  padding: 24px 14px 18px;
  background:
    linear-gradient(180deg, rgba(255, 250, 240, 0.98), rgba(239, 225, 201, 0.9)),
    repeating-linear-gradient(
      0deg,
      transparent 0,
      transparent 31px,
      rgba(145, 108, 62, 0.08) 32px,
      transparent 33px
    ),
    var(--nh-paper);
  border-right: 1px solid var(--nh-border);
  box-shadow: 14px 0 34px rgba(84, 60, 28, 0.08);
}

.nav-menu {
  margin-top: 28px;
  background: transparent;
  border-right: 0;
}

.nav-menu :deep(.el-menu-item) {
  height: 46px;
  margin: 7px 0;
  padding: 0 14px !important;
  color: #5f5548;
  border-radius: var(--nh-radius);
  transition:
    background-color var(--nh-transition),
    color var(--nh-transition),
    box-shadow var(--nh-transition),
    transform var(--nh-transition);
}

.nav-menu :deep(.el-menu-item span) {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.nav-menu :deep(.el-menu-item:hover) {
  color: var(--nh-primary-dark);
  background: rgba(255, 253, 248, 0.72);
  box-shadow: inset 0 0 0 1px var(--nh-border);
  transform: translateX(2px);
}

.nav-menu :deep(.el-menu-item .el-icon) {
  margin-right: 10px;
  font-size: 18px;
}

.nav-menu :deep(.is-active) {
  color: var(--nh-primary-dark);
  background: linear-gradient(135deg, rgba(255, 253, 248, 0.96), rgba(232, 240, 235, 0.84));
  box-shadow:
    inset 3px 0 0 var(--nh-primary),
    0 10px 24px rgba(83, 60, 30, 0.08);
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 74px;
  padding: 0 30px;
  background:
    linear-gradient(180deg, rgba(255, 250, 240, 0.9), rgba(247, 240, 227, 0.76));
  border-bottom: 1px solid var(--nh-border);
  backdrop-filter: blur(14px);
}

.topbar-copy {
  min-width: 0;
}

.topbar-title {
  display: block;
  font-family: var(--nh-font-heading);
  font-size: 20px;
  font-weight: 760;
  letter-spacing: 0;
  line-height: 1.3;
}

.topbar small {
  color: var(--nh-muted);
  line-height: 1.6;
}

.topbar :deep(.el-button) {
  min-width: 104px;
  background: rgba(255, 253, 248, 0.78);
}

.main-content {
  width: min(100%, 1500px);
  padding: 30px;
  margin: 0 auto;
}

@media (max-width: 860px) {
  .app-layout {
    display: block;
  }

  .sidebar {
    position: static;
    width: 100% !important;
    height: auto;
    padding: 18px;
    border-right: 0;
    border-bottom: 1px solid var(--nh-border);
  }

  .nav-menu {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px;
    margin-top: 18px;
  }

  .nav-menu :deep(.el-menu-item) {
    margin: 0;
  }

  .topbar {
    height: auto;
    min-height: 72px;
    gap: 14px;
    padding: 14px 18px;
  }

  .main-content {
    padding: 18px;
  }
}

@media (max-width: 560px) {
  .nav-menu {
    grid-template-columns: 1fr;
  }

  .topbar {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
