<template>
  <div class="page">
    <header class="page-header">
      <div>
        <h1 class="page-title">资讯详情</h1>
        <p class="page-subtitle">查看素材信息，并把它沉淀成一个可执行选题。</p>
      </div>
      <div class="header-actions">
        <el-button :icon="Back" @click="router.back()">返回</el-button>
        <el-button v-if="news" :icon="Star" @click="handleFavorite">{{ news.is_favorite ? '取消收藏' : '收藏' }}</el-button>
        <el-button v-if="news" type="primary" :icon="Plus" @click="openTopicDialog">加入选题池</el-button>
      </div>
    </header>

    <LoadingState v-if="loading" />
    <el-alert v-else-if="errorMessage" type="error" show-icon title="资讯详情加载失败" :description="errorMessage" />
    <section v-else-if="news" class="section">
      <div class="section-body detail-stack">
        <div>
          <el-tag>{{ newsStatusText[news.status] }}</el-tag>
          <h2>{{ news.title }}</h2>
          <p class="muted">
            {{ news.source_name || '未填写来源' }} · {{ formatDate(news.publish_time || news.created_at) }}
          </p>
        </div>

        <div class="detail-grid">
          <div class="detail-item">
            <div class="detail-label">分类</div>
            <div class="detail-value">{{ news.category?.name || '-' }}</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">标签</div>
            <div class="tag-list">
              <el-tag v-for="tag in news.tags" :key="tag.id" type="success">{{ tag.name }}</el-tag>
              <span v-if="!news.tags?.length">-</span>
            </div>
          </div>
          <div class="detail-item">
            <div class="detail-label">热度</div>
            <ScoreDots :value="news.heat_score" />
          </div>
          <div class="detail-item">
            <div class="detail-label">重要度</div>
            <ScoreDots :value="news.importance_score" />
          </div>
        </div>

        <div class="detail-item" v-if="news.source_url">
          <div class="detail-label">原文链接</div>
          <a class="text-link" :href="news.source_url" target="_blank" rel="noreferrer">{{ news.source_url }}</a>
        </div>
        <div class="detail-item">
          <div class="detail-label">摘要</div>
          <div class="detail-value">{{ news.summary || '未填写摘要' }}</div>
        </div>
        <div class="detail-item">
          <div class="detail-label">内容笔记</div>
          <CodeBlock v-if="looksLikeCode(news.content)" :code="news.content || ''" language="json" />
          <div v-else class="detail-value">{{ news.content || '未填写内容笔记' }}</div>
        </div>
      </div>
    </section>

    <el-dialog v-model="topicDialogVisible" title="从资讯创建选题" width="720px">
      <el-form ref="topicFormRef" :model="topicForm" :rules="topicRules" label-position="top">
        <el-form-item label="选题标题" prop="title">
          <el-input v-model.trim="topicForm.title" />
        </el-form-item>
        <el-form-item label="推荐公众号标题">
          <el-input v-model.trim="topicForm.recommended_title" />
        </el-form-item>
        <el-form-item label="写作角度">
          <el-input v-model="topicForm.angle" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="选题理由">
          <el-input v-model="topicForm.reason" type="textarea" :rows="3" />
        </el-form-item>
        <div class="form-grid">
          <el-form-item label="目标读者">
            <el-input v-model.trim="topicForm.target_reader" />
          </el-form-item>
          <el-form-item label="计划发布时间">
            <el-date-picker v-model="deadlineInput" type="datetime" value-format="YYYY-MM-DDTHH:mm" />
          </el-form-item>
          <el-form-item label="选题价值">
            <el-input-number v-model="topicForm.value_score" :min="1" :max="5" />
          </el-form-item>
          <el-form-item label="写作难度">
            <el-input-number v-model="topicForm.difficulty_score" :min="1" :max="5" />
          </el-form-item>
          <el-form-item label="传播潜力">
            <el-input-number v-model="topicForm.traffic_score" :min="1" :max="5" />
          </el-form-item>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="topicDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleCreateTopic">创建选题</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Back, Plus, Star } from '@element-plus/icons-vue'
import CodeBlock from '@/components/CodeBlock.vue'
import LoadingState from '@/components/LoadingState.vue'
import ScoreDots from '@/components/ScoreDots.vue'
import { createTopicFromNews, getNewsDetail, updateNewsFavorite } from '@/api/news'
import type { NewsItem } from '@/types/news'
import type { TopicPayload } from '@/types/topic'
import { formatDate, newsStatusText, toApiDateTime } from '@/utils/display'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const submitting = ref(false)
const errorMessage = ref('')
const news = ref<NewsItem>()
const topicDialogVisible = ref(false)
const topicFormRef = ref<FormInstance>()
const deadlineInput = ref('')

const topicForm = reactive<TopicPayload>({
  title: '',
  angle: '',
  recommended_title: '',
  reason: '',
  target_reader: '',
  category_id: null,
  value_score: 3,
  difficulty_score: 3,
  traffic_score: 3,
})

const topicRules: FormRules = {
  title: [{ required: true, message: '请输入选题标题', trigger: 'blur' }],
}

async function fetchDetail() {
  const newsId = Number(route.params.id)
  if (!Number.isInteger(newsId) || newsId <= 0) {
    errorMessage.value = '资讯 ID 不正确，请从资讯列表重新进入'
    return
  }

  loading.value = true
  errorMessage.value = ''
  try {
    news.value = await getNewsDetail(newsId)
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '请稍后重试'
  } finally {
    loading.value = false
  }
}

async function handleFavorite() {
  if (!news.value) return
  await updateNewsFavorite(news.value.id, { is_favorite: !news.value.is_favorite })
  ElMessage.success(news.value.is_favorite ? '已取消收藏' : '已收藏')
  fetchDetail()
}

function openTopicDialog() {
  if (!news.value) return
  Object.assign(topicForm, {
    title: news.value.title,
    recommended_title: news.value.title,
    angle: '',
    reason: news.value.summary || '',
    target_reader: 'AI 资讯关注者、内容创作者',
    category_id: news.value.category?.id || null,
    value_score: news.value.importance_score || 3,
    difficulty_score: 3,
    traffic_score: news.value.heat_score || 3,
  })
  topicDialogVisible.value = true
}

async function handleCreateTopic() {
  if (!news.value) return
  const valid = await topicFormRef.value?.validate()
  if (!valid) return

  submitting.value = true
  try {
    const created = await createTopicFromNews(news.value.id, {
      ...topicForm,
      deadline: toApiDateTime(deadlineInput.value),
    })
    ElMessage.success('选题创建成功')
    router.push(`/topics/${created.id}`)
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '创建选题失败')
  } finally {
    submitting.value = false
  }
}

function looksLikeCode(value?: string | null) {
  if (!value) return false
  const trimmed = value.trim()
  return trimmed.startsWith('{') || trimmed.startsWith('[') || trimmed.includes('```')
}

onMounted(fetchDetail)
</script>

<style scoped>
.header-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.detail-stack {
  display: grid;
  gap: 16px;
}

h2 {
  margin: 12px 0 6px;
  font-size: 28px;
  letter-spacing: 0;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

@media (max-width: 720px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
