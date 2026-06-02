<template>
  <div class="page">
    <header class="page-header">
      <div>
        <h1 class="page-title">仪表盘</h1>
        <p class="page-subtitle">快速看清资讯池、选题池和最近需要跟进的内容。</p>
      </div>
      <el-button :icon="Refresh" :loading="loading" @click="fetchOverview">刷新</el-button>
    </header>

    <LoadingState v-if="loading" />

    <template v-else-if="overview">
      <section class="stats-grid">
        <article v-for="item in stats" :key="item.label" class="stat-card">
          <small>{{ item.label }}</small>
          <strong>{{ item.value }}</strong>
        </article>
      </section>

      <section class="dashboard-grid">
        <div class="section">
          <div class="section-body">
            <h2>最近资讯</h2>
            <EmptyState v-if="overview.recent_news.length === 0" title="暂无资讯" description="新增资讯后会显示在这里。" />
            <el-timeline v-else>
              <el-timeline-item v-for="news in overview.recent_news" :key="news.id" :timestamp="formatDate(news.created_at)">
                <RouterLink class="text-link" :to="`/news/${news.id}`">{{ news.title }}</RouterLink>
                <el-tag size="small" class="item-tag">{{ newsStatusText[news.status] }}</el-tag>
              </el-timeline-item>
            </el-timeline>
          </div>
        </div>

        <div class="section">
          <div class="section-body">
            <h2>最近选题</h2>
            <EmptyState v-if="overview.recent_topics.length === 0" title="暂无选题" description="从资讯创建选题或手动新建后会显示在这里。" />
            <el-timeline v-else>
              <el-timeline-item v-for="topic in overview.recent_topics" :key="topic.id" :timestamp="formatDate(topic.created_at)">
                <RouterLink class="text-link" :to="`/topics/${topic.id}`">{{ topic.title }}</RouterLink>
                <el-tag size="small" class="item-tag">{{ topicStatusText[topic.status] }}</el-tag>
              </el-timeline-item>
            </el-timeline>
          </div>
        </div>
      </section>
    </template>

    <el-alert v-else type="error" show-icon title="仪表盘加载失败" :description="errorMessage" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import EmptyState from '@/components/EmptyState.vue'
import LoadingState from '@/components/LoadingState.vue'
import { getDashboardOverview } from '@/api/dashboard'
import type { DashboardOverview } from '@/types/dashboard'
import { formatDate, newsStatusText, topicStatusText } from '@/utils/display'

const overview = ref<DashboardOverview>()
const loading = ref(false)
const errorMessage = ref('')

const stats = computed(() => {
  if (!overview.value) return []
  return [
    { label: '资讯总数', value: overview.value.news_total },
    { label: '未读资讯', value: overview.value.unread_news_total },
    { label: '收藏资讯', value: overview.value.favorite_news_total },
    { label: '选题总数', value: overview.value.topic_total },
    { label: '待评估选题', value: overview.value.pending_topic_total },
    { label: '写作中选题', value: overview.value.writing_topic_total },
    { label: '已发布选题', value: overview.value.published_topic_total },
  ]
})

async function fetchOverview() {
  loading.value = true
  errorMessage.value = ''
  try {
    overview.value = await getDashboardOverview()
  } catch (error) {
    overview.value = undefined
    errorMessage.value = error instanceof Error ? error.message : '请稍后重试'
  } finally {
    loading.value = false
  }
}

onMounted(fetchOverview)
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(116px, 1fr));
  gap: 12px;
}

.stat-card {
  position: relative;
  min-height: 118px;
  padding: 18px;
  overflow: hidden;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.92), rgba(248, 251, 255, 0.78));
  border: 1px solid var(--nh-border);
  border-radius: var(--nh-radius);
  box-shadow: var(--nh-shadow);
  transition:
    border-color var(--nh-transition),
    box-shadow var(--nh-transition),
    transform var(--nh-transition);
}

.stat-card::before {
  position: absolute;
  top: 0;
  right: 14px;
  left: 14px;
  height: 3px;
  content: "";
  background: linear-gradient(90deg, var(--nh-primary), var(--nh-accent));
  border-radius: 999px;
  opacity: 0.68;
}

.stat-card:hover {
  border-color: var(--nh-border-strong);
  box-shadow: var(--nh-shadow-hover);
  transform: translateY(-2px);
}

.stat-card small {
  color: var(--nh-muted);
  font-weight: 650;
}

.stat-card strong {
  display: block;
  margin-top: 10px;
  font-size: 30px;
  line-height: 1;
  letter-spacing: 0;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

h2 {
  margin: 0 0 16px;
  font-size: 18px;
  line-height: 1.3;
}

.item-tag {
  margin-left: 8px;
}

:deep(.el-timeline) {
  padding-left: 2px;
}

:deep(.el-timeline-item__timestamp) {
  color: var(--nh-muted);
}

@media (max-width: 1180px) {
  .stats-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 860px) {
  .stats-grid,
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}
</style>
