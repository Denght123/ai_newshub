<template>
  <el-container class="app-layout">
    <el-aside class="sidebar" width="248px">
      <AppLogo />
      <el-menu :default-active="route.path" router class="nav-menu">
        <el-menu-item index="/dashboard">
          <el-icon><DataBoard /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/news">
          <el-icon><Reading /></el-icon>
          <span>资讯管理</span>
        </el-menu-item>
        <el-menu-item index="/topics">
          <el-icon><Collection /></el-icon>
          <span>选题池</span>
        </el-menu-item>
        <el-menu-item index="/taxonomy">
          <el-icon><PriceTag /></el-icon>
          <span>分类与标签</span>
        </el-menu-item>
        <el-menu-item index="/ai-digest">
          <el-icon><MagicStick /></el-icon>
          <span>AI 自动抓取</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="topbar">
        <div>
          <span class="topbar-title">{{ route.meta.title || 'AI NewsHub' }}</span>
          <small>把资讯沉淀成可跟进的内容选题</small>
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
import { Collection, DataBoard, MagicStick, PriceTag, Reading, User } from '@element-plus/icons-vue'
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
  min-height: 100vh;
}

.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  padding: 24px 14px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(248, 251, 255, 0.9)),
    var(--nh-surface);
  border-right: 1px solid var(--nh-border);
  box-shadow: 12px 0 34px rgba(16, 24, 40, 0.04);
  backdrop-filter: blur(18px);
}

.nav-menu {
  margin-top: 30px;
  background: transparent;
  border-right: 0;
}

.nav-menu :deep(.el-menu-item) {
  height: 44px;
  margin: 7px 0;
  padding: 0 14px !important;
  color: #4d5a6c;
  border-radius: var(--nh-radius);
  transition:
    background-color var(--nh-transition),
    color var(--nh-transition),
    transform var(--nh-transition);
}

.nav-menu :deep(.el-menu-item:hover) {
  color: var(--nh-primary-dark);
  background: rgba(45, 108, 223, 0.08);
}

.nav-menu :deep(.el-menu-item .el-icon) {
  margin-right: 10px;
  font-size: 18px;
}

.nav-menu :deep(.is-active) {
  color: var(--nh-primary-dark);
  background: linear-gradient(135deg, var(--nh-soft), rgba(232, 251, 247, 0.88));
  box-shadow: inset 3px 0 0 var(--nh-primary);
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
  background: rgba(246, 248, 251, 0.78);
  border-bottom: 1px solid var(--nh-border);
  backdrop-filter: blur(18px);
}

.topbar-title {
  display: block;
  font-size: 18px;
  font-weight: 760;
  line-height: 1.3;
}

.topbar small {
  color: var(--nh-muted);
  line-height: 1.6;
}

.topbar :deep(.el-button) {
  min-width: 104px;
  background: rgba(255, 255, 255, 0.72);
}

.main-content {
  padding: 30px;
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
