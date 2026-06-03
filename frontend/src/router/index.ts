import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppLayout from '@/layouts/AppLayout.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/daily',
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { guestOnly: true },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/RegisterView.vue'),
      meta: { guestOnly: true },
    },
    {
      path: '/',
      component: AppLayout,
      meta: { requiresAuth: true },
      children: [
        {
          path: 'daily',
          name: 'daily-digest',
          component: () => import('@/views/DailyDigestView.vue'),
          meta: { title: '每日采集' },
        },
        {
          path: 'knowledge',
          name: 'knowledge-base',
          component: () => import('@/views/KnowledgeBaseView.vue'),
          meta: { title: '知识库' },
        },
        {
          path: 'ask',
          name: 'rag-chat',
          component: () => import('@/views/RagChatView.vue'),
          meta: { title: 'AI 问答' },
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/views/NotFoundView.vue'),
    },
  ],
})

router.beforeEach(async (to) => {
  const authStore = useAuthStore()
  const needsAuth = to.matched.some((record) => record.meta.requiresAuth)

  if (needsAuth && !authStore.isLoggedIn) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  if (needsAuth && authStore.isLoggedIn && !authStore.user) {
    try {
      await authStore.fetchCurrentUser()
    } catch {
      authStore.logout()
      return { name: 'login', query: { redirect: to.fullPath } }
    }
  }

  if (to.meta.guestOnly && authStore.isLoggedIn) {
    return { name: 'daily-digest' }
  }

  document.title = to.meta.title ? `${String(to.meta.title)} - AI NewsHub` : 'AI NewsHub'
})

export default router
