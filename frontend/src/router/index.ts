import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppLayout from '@/layouts/AppLayout.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/dashboard',
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
          path: 'dashboard',
          name: 'dashboard',
          component: () => import('@/views/DashboardView.vue'),
          meta: { title: '仪表盘' },
        },
        {
          path: 'news',
          name: 'news',
          component: () => import('@/views/NewsListView.vue'),
          meta: { title: '资讯管理' },
        },
        {
          path: 'news/:id',
          name: 'news-detail',
          component: () => import('@/views/NewsDetailView.vue'),
          meta: { title: '资讯详情' },
        },
        {
          path: 'topics',
          name: 'topics',
          component: () => import('@/views/TopicListView.vue'),
          meta: { title: '选题池' },
        },
        {
          path: 'topics/:id',
          name: 'topic-detail',
          component: () => import('@/views/TopicDetailView.vue'),
          meta: { title: '选题详情' },
        },
        {
          path: 'taxonomy',
          name: 'taxonomy',
          component: () => import('@/views/TaxonomyView.vue'),
          meta: { title: '分类与标签' },
        },
        {
          path: 'ai-digest',
          name: 'ai-digest',
          component: () => import('@/views/AIDigestView.vue'),
          meta: { title: 'AI 自动抓取' },
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
    return { name: 'dashboard' }
  }

  document.title = to.meta.title ? `${String(to.meta.title)} - AI NewsHub` : 'AI NewsHub'
})

export default router
