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
import { Collection, DataBoard, PriceTag, Reading, User } from '@element-plus/icons-vue'
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
  padding: 22px 16px;
  background: rgba(255, 255, 255, 0.86);
  border-right: 1px solid var(--nh-border);
}

.nav-menu {
  margin-top: 28px;
  background: transparent;
  border-right: 0;
}

.nav-menu :deep(.el-menu-item) {
  height: 46px;
  margin: 6px 0;
  border-radius: 8px;
}

.nav-menu :deep(.is-active) {
  color: var(--nh-primary-dark);
  background: var(--nh-soft);
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 72px;
  padding: 0 28px;
  background: rgba(246, 248, 244, 0.82);
  border-bottom: 1px solid var(--nh-border);
  backdrop-filter: blur(12px);
}

.topbar-title {
  display: block;
  font-size: 18px;
  font-weight: 760;
}

.topbar small {
  color: var(--nh-muted);
}

.main-content {
  padding: 28px;
}

@media (max-width: 860px) {
  .app-layout {
    display: block;
  }

  .sidebar {
    position: static;
    width: 100% !important;
    height: auto;
  }

  .topbar {
    padding: 0 16px;
  }

  .main-content {
    padding: 18px;
  }
}
</style>
