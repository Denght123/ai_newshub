<template>
  <div class="page">
    <header class="page-header">
      <div>
        <h1 class="page-title">选题详情</h1>
        <p class="page-subtitle">检查写作角度、推荐标题、价值评分和计划发布时间。</p>
      </div>
      <el-button :icon="Back" @click="router.back()">返回</el-button>
    </header>

    <LoadingState v-if="loading" />
    <el-alert v-else-if="errorMessage" type="error" show-icon title="选题详情加载失败" :description="errorMessage" />
    <section v-else-if="topic" class="section">
      <div class="section-body detail-stack">
        <div>
          <el-tag>{{ topicStatusText[topic.status] }}</el-tag>
          <h2>{{ topic.title }}</h2>
          <p class="muted">{{ topic.recommended_title || '未填写推荐公众号标题' }}</p>
        </div>

        <div class="detail-grid">
          <div class="detail-item">
            <div class="detail-label">关联资讯</div>
            <RouterLink v-if="topic.news" class="text-link" :to="`/news/${topic.news.id}`">{{ topic.news.title }}</RouterLink>
            <span v-else>-</span>
          </div>
          <div class="detail-item">
            <div class="detail-label">分类</div>
            <div class="detail-value">{{ topic.category?.name || '-' }}</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">计划发布时间</div>
            <div class="detail-value">{{ formatDate(topic.deadline) }}</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">创建时间</div>
            <div class="detail-value">{{ formatDate(topic.created_at) }}</div>
          </div>
        </div>

        <div class="detail-grid">
          <div class="detail-item">
            <div class="detail-label">选题价值</div>
            <ScoreDots :value="topic.value_score" />
          </div>
          <div class="detail-item">
            <div class="detail-label">写作难度</div>
            <ScoreDots :value="topic.difficulty_score" />
          </div>
          <div class="detail-item">
            <div class="detail-label">传播潜力</div>
            <ScoreDots :value="topic.traffic_score" />
          </div>
        </div>

        <div class="detail-item">
          <div class="detail-label">写作角度</div>
          <div class="detail-value">{{ topic.angle || '未填写写作角度' }}</div>
        </div>
        <div class="detail-item">
          <div class="detail-label">选题理由</div>
          <div class="detail-value">{{ topic.reason || '未填写选题理由' }}</div>
        </div>
        <div class="detail-item">
          <div class="detail-label">目标读者</div>
          <div class="detail-value">{{ topic.target_reader || '未填写目标读者' }}</div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Back } from '@element-plus/icons-vue'
import LoadingState from '@/components/LoadingState.vue'
import ScoreDots from '@/components/ScoreDots.vue'
import { getTopicDetail } from '@/api/topics'
import type { TopicItem } from '@/types/topic'
import { formatDate, topicStatusText } from '@/utils/display'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const errorMessage = ref('')
const topic = ref<TopicItem>()

async function fetchDetail() {
  const topicId = Number(route.params.id)
  if (!Number.isInteger(topicId) || topicId <= 0) {
    errorMessage.value = '选题 ID 不正确，请从选题列表重新进入'
    return
  }

  loading.value = true
  errorMessage.value = ''
  try {
    topic.value = await getTopicDetail(topicId)
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '请稍后重试'
  } finally {
    loading.value = false
  }
}

onMounted(fetchDetail)
</script>

<style scoped>
.detail-stack {
  display: grid;
  gap: 16px;
}

h2 {
  margin: 12px 0 6px;
  font-size: 28px;
  letter-spacing: 0;
}
</style>
