<template>
  <div class="page">
    <header class="page-header">
      <div>
        <h1 class="page-title">资讯管理</h1>
        <p class="page-subtitle">录入、筛选、收藏资讯，并把有价值的素材转成公众号选题。</p>
      </div>
      <el-button type="primary" :icon="Plus" @click="openCreateDialog">新增资讯</el-button>
    </header>

    <section class="section">
      <div class="toolbar">
        <el-input v-model.trim="filters.keyword" clearable placeholder="搜索标题、摘要、来源" :prefix-icon="Search" @keyup.enter="handleSearch" />
        <el-select v-model="filters.category_id" clearable placeholder="分类">
          <el-option v-for="category in categories" :key="category.id" :label="category.name" :value="category.id" />
        </el-select>
        <el-select v-model="filters.status" clearable placeholder="状态">
          <el-option v-for="item in newsStatusOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
        <el-select v-model="filters.is_favorite" clearable placeholder="收藏">
          <el-option label="仅收藏" :value="true" />
          <el-option label="未收藏" :value="false" />
        </el-select>
        <el-select v-model="filters.order_by" placeholder="排序">
          <el-option label="创建时间" value="created_at" />
          <el-option label="发布时间" value="publish_time" />
          <el-option label="热度" value="heat_score" />
          <el-option label="重要度" value="importance_score" />
        </el-select>
        <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
        <el-button :icon="Refresh" @click="handleReset">重置</el-button>
      </div>

      <LoadingState v-if="loading" />
      <EmptyState v-else-if="pageData.items.length === 0" title="暂无资讯" description="可以先新增一条 AI 新闻或产品动态。" />
      <el-table v-else :data="pageData.items" class="data-table">
        <el-table-column prop="title" label="标题" min-width="240">
          <template #default="{ row }">
            <RouterLink class="text-link" :to="`/news/${row.id}`">{{ row.title }}</RouterLink>
            <div class="muted">{{ row.source_name || '未填写来源' }}</div>
          </template>
        </el-table-column>
        <el-table-column label="分类" width="120">
          <template #default="{ row }">{{ row.category?.name || '-' }}</template>
        </el-table-column>
        <el-table-column label="标签" min-width="150">
          <template #default="{ row }">
            <div class="tag-list">
              <el-tag v-for="tag in row.tags" :key="tag.id" size="small" type="success">{{ tag.name }}</el-tag>
              <span v-if="!row.tags?.length" class="muted">-</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <el-tag>{{ getNewsStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="评分" width="150">
          <template #default="{ row }">
            <div>热度 <ScoreDots :value="row.heat_score" /></div>
            <div>重要 <ScoreDots :value="row.importance_score" /></div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" :icon="Edit" @click="openEditDialog(row)">编辑</el-button>
            <el-button text :icon="Star" @click="handleFavorite(row)">
              {{ row.is_favorite ? '取消收藏' : '收藏' }}
            </el-button>
            <el-button text type="danger" :icon="Delete" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-bar">
        <el-pagination
          background
          layout="prev, pager, next, total"
          :current-page="filters.page"
          :page-size="filters.page_size"
          :total="pageData.total"
          @current-change="handlePageChange"
        />
      </div>
    </section>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑资讯' : '新增资讯'" width="720px" append-to-body>
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="标题" prop="title">
          <el-input v-model.trim="form.title" />
        </el-form-item>
        <div class="form-grid">
          <el-form-item label="来源名称">
            <el-input v-model.trim="form.source_name" />
          </el-form-item>
          <el-form-item label="原文链接">
            <el-input v-model.trim="form.source_url" />
          </el-form-item>
          <el-form-item label="分类">
            <el-select v-model="form.category_id" clearable>
              <el-option v-for="category in categories" :key="category.id" :label="category.name" :value="category.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="form.status">
              <el-option v-for="item in newsStatusOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>
          <el-form-item label="重要度">
            <el-input-number v-model="form.importance_score" :min="1" :max="5" />
          </el-form-item>
          <el-form-item label="热度">
            <el-input-number v-model="form.heat_score" :min="1" :max="5" />
          </el-form-item>
        </div>
        <el-form-item label="标签">
          <el-select v-model="form.tag_ids" multiple clearable class="full-width">
            <el-option v-for="tag in tags" :key="tag.id" :label="tag.name" :value="tag.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="发布时间">
          <el-date-picker v-model="publishTimeInput" type="datetime" value-format="YYYY-MM-DDTHH:mm" />
        </el-form-item>
        <el-form-item label="摘要">
          <el-input v-model="form.summary" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="内容笔记">
          <el-input v-model="form.content" type="textarea" :rows="5" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Delete, Edit, Plus, Refresh, Search, Star } from '@element-plus/icons-vue'
import EmptyState from '@/components/EmptyState.vue'
import LoadingState from '@/components/LoadingState.vue'
import ScoreDots from '@/components/ScoreDots.vue'
import { createNews, deleteNews, getNewsList, updateNews, updateNewsFavorite } from '@/api/news'
import { getCategories, getTags } from '@/api/taxonomy'
import type { PageResult } from '@/types/common'
import type { NewsItem, NewsListParams, NewsPayload, NewsStatus } from '@/types/news'
import type { CategoryItem, TagItem } from '@/types/taxonomy'
import { newsStatusText, toApiDateTime, toDateTimeInputValue } from '@/utils/display'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const editingId = ref<number>()
const formRef = ref<FormInstance>()
const publishTimeInput = ref('')
const categories = ref<CategoryItem[]>([])
const tags = ref<TagItem[]>([])

const pageData = reactive<PageResult<NewsItem>>({
  items: [],
  total: 0,
  page: 1,
  page_size: 10,
  pages: 0,
})

const filters = reactive<NewsListParams>({
  page: 1,
  page_size: 10,
  order_by: 'created_at',
  order: 'desc',
})

const form = reactive<NewsPayload>({
  title: '',
  source_name: '',
  source_url: '',
  summary: '',
  content: '',
  category_id: null,
  tag_ids: [],
  status: 'unread',
  importance_score: 3,
  heat_score: 3,
})

const rules: FormRules = {
  title: [{ required: true, message: '请输入资讯标题', trigger: 'blur' }],
}

const newsStatusOptions = Object.entries(newsStatusText).map(([value, label]) => ({ value: value as NewsStatus, label }))

function getNewsStatusLabel(status: string) {
  return newsStatusText[status as NewsStatus] || status
}

async function fetchPage() {
  loading.value = true
  try {
    const result = await getNewsList(filters)
    Object.assign(pageData, result)
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '资讯列表加载失败')
  } finally {
    loading.value = false
  }
}

async function fetchOptions() {
  const [categoryResult, tagResult] = await Promise.all([getCategories(true), getTags()])
  categories.value = categoryResult
  tags.value = tagResult
}

function resetForm() {
  editingId.value = undefined
  publishTimeInput.value = ''
  Object.assign(form, {
    title: '',
    source_name: '',
    source_url: '',
    summary: '',
    content: '',
    category_id: null,
    tag_ids: [],
    status: 'unread',
    importance_score: 3,
    heat_score: 3,
    publish_time: undefined,
  })
}

function openCreateDialog() {
  resetForm()
  dialogVisible.value = true
}

function openEditDialog(row: NewsItem) {
  editingId.value = row.id
  publishTimeInput.value = toDateTimeInputValue(row.publish_time)
  Object.assign(form, {
    title: row.title,
    source_name: row.source_name || '',
    source_url: row.source_url || '',
    summary: row.summary || '',
    content: row.content || '',
    category_id: row.category?.id || null,
    tag_ids: row.tags?.map((tag) => tag.id) || [],
    status: row.status,
    importance_score: row.importance_score,
    heat_score: row.heat_score,
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  const valid = await formRef.value?.validate()
  if (!valid) return

  submitting.value = true
  try {
    const payload = { ...form, publish_time: toApiDateTime(publishTimeInput.value) }
    if (editingId.value) {
      await updateNews(editingId.value, payload)
      ElMessage.success('资讯已更新')
    } else {
      await createNews(payload)
      ElMessage.success('资讯已新增')
    }
    dialogVisible.value = false
    fetchPage()
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '保存失败')
  } finally {
    submitting.value = false
  }
}

async function handleFavorite(row: NewsItem) {
  try {
    await updateNewsFavorite(row.id, { is_favorite: !row.is_favorite })
    ElMessage.success(row.is_favorite ? '已取消收藏' : '已收藏')
    fetchPage()
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '操作失败')
  }
}

async function handleDelete(row: NewsItem) {
  try {
    await ElMessageBox.confirm(`确认删除「${row.title}」吗？`, '删除资讯', { type: 'warning' })
    await deleteNews(row.id)
    ElMessage.success('删除成功')
    fetchPage()
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      ElMessage.error(error instanceof Error ? error.message : '删除失败')
    }
  }
}

function handleSearch() {
  filters.page = 1
  fetchPage()
}

function handleReset() {
  Object.assign(filters, { page: 1, page_size: 10, keyword: undefined, category_id: undefined, status: undefined, is_favorite: undefined, order_by: 'created_at', order: 'desc' })
  fetchPage()
}

function handlePageChange(page: number) {
  filters.page = page
  fetchPage()
}

onMounted(() => {
  fetchOptions().catch(() => ElMessage.warning('分类或标签加载失败，可稍后刷新'))
  fetchPage()
})
</script>

<style scoped>
.data-table {
  width: 100%;
}

.pagination-bar {
  display: flex;
  justify-content: flex-end;
  padding: 16px 18px 18px;
  border-top: 1px solid var(--nh-border);
  background: rgba(255, 250, 240, 0.72);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px 14px;
}

.full-width {
  width: 100%;
}

:deep(.el-table .el-button.is-text) {
  padding-inline: 7px;
}

@media (max-width: 720px) {
  .form-grid {
    grid-template-columns: 1fr;
  }

  .pagination-bar {
    justify-content: center;
  }
}
</style>
