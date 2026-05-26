<template>
  <div class="page">
    <header class="page-header">
      <div>
        <h1 class="page-title">选题池</h1>
        <p class="page-subtitle">把值得跟进的资讯变成写作任务，并推进状态流转。</p>
      </div>
      <el-button type="primary" :icon="Plus" @click="openCreateDialog">新建选题</el-button>
    </header>

    <section class="section">
      <div class="toolbar">
        <el-input v-model.trim="filters.keyword" clearable placeholder="搜索标题、角度、推荐标题" :prefix-icon="Search" @keyup.enter="handleSearch" />
        <el-select v-model="filters.category_id" clearable placeholder="分类">
          <el-option v-for="category in categories" :key="category.id" :label="category.name" :value="category.id" />
        </el-select>
        <el-select v-model="filters.status" clearable placeholder="状态">
          <el-option v-for="item in topicStatusOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
        <el-select v-model="filters.order_by" placeholder="排序">
          <el-option label="创建时间" value="created_at" />
          <el-option label="截止时间" value="deadline" />
          <el-option label="选题价值" value="value_score" />
          <el-option label="传播潜力" value="traffic_score" />
          <el-option label="写作难度" value="difficulty_score" />
        </el-select>
        <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
        <el-button :icon="Refresh" @click="handleReset">重置</el-button>
      </div>

      <LoadingState v-if="loading" />
      <EmptyState v-else-if="pageData.items.length === 0" title="暂无选题" description="可以从资讯详情加入选题池，或手动新建一个选题。" />
      <el-table v-else :data="pageData.items" class="data-table">
        <el-table-column label="选题" min-width="260">
          <template #default="{ row }">
            <RouterLink class="text-link" :to="`/topics/${row.id}`">{{ row.title }}</RouterLink>
            <div class="muted">{{ row.recommended_title || '未填写推荐标题' }}</div>
          </template>
        </el-table-column>
        <el-table-column label="分类" width="120">
          <template #default="{ row }">{{ row.category?.name || '-' }}</template>
        </el-table-column>
        <el-table-column label="状态" width="132">
          <template #default="{ row }">
            <el-select :model-value="row.status" size="small" @change="(value: unknown) => handleStatusChange(row, value)">
              <el-option v-for="item in topicStatusOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="评分" width="170">
          <template #default="{ row }">
            <div>价值 <ScoreDots :value="row.value_score" /></div>
            <div>传播 <ScoreDots :value="row.traffic_score" /></div>
          </template>
        </el-table-column>
        <el-table-column label="计划发布时间" width="170">
          <template #default="{ row }">{{ formatDate(row.deadline) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" :icon="Edit" @click="openEditDialog(row)">编辑</el-button>
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

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑选题' : '新建选题'" width="720px">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="选题标题" prop="title">
          <el-input v-model.trim="form.title" />
        </el-form-item>
        <el-form-item label="推荐公众号标题">
          <el-input v-model.trim="form.recommended_title" />
        </el-form-item>
        <el-form-item label="写作角度">
          <el-input v-model="form.angle" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="选题理由">
          <el-input v-model="form.reason" type="textarea" :rows="3" />
        </el-form-item>
        <div class="form-grid">
          <el-form-item label="分类">
            <el-select v-model="form.category_id" clearable>
              <el-option v-for="category in categories" :key="category.id" :label="category.name" :value="category.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="form.status">
              <el-option v-for="item in topicStatusOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>
          <el-form-item label="目标读者">
            <el-input v-model.trim="form.target_reader" />
          </el-form-item>
          <el-form-item label="计划发布时间">
            <el-date-picker v-model="deadlineInput" type="datetime" value-format="YYYY-MM-DDTHH:mm" />
          </el-form-item>
          <el-form-item label="选题价值">
            <el-input-number v-model="form.value_score" :min="1" :max="5" />
          </el-form-item>
          <el-form-item label="写作难度">
            <el-input-number v-model="form.difficulty_score" :min="1" :max="5" />
          </el-form-item>
          <el-form-item label="传播潜力">
            <el-input-number v-model="form.traffic_score" :min="1" :max="5" />
          </el-form-item>
        </div>
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
import { Delete, Edit, Plus, Refresh, Search } from '@element-plus/icons-vue'
import EmptyState from '@/components/EmptyState.vue'
import LoadingState from '@/components/LoadingState.vue'
import ScoreDots from '@/components/ScoreDots.vue'
import { createTopic, deleteTopic, getTopicList, updateTopic, updateTopicStatus } from '@/api/topics'
import { getCategories } from '@/api/taxonomy'
import type { PageResult } from '@/types/common'
import type { CategoryItem } from '@/types/taxonomy'
import type { TopicItem, TopicListParams, TopicPayload, TopicStatus } from '@/types/topic'
import { formatDate, toApiDateTime, toDateTimeInputValue, topicStatusText } from '@/utils/display'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const editingId = ref<number>()
const deadlineInput = ref('')
const formRef = ref<FormInstance>()
const categories = ref<CategoryItem[]>([])

const pageData = reactive<PageResult<TopicItem>>({
  items: [],
  total: 0,
  page: 1,
  page_size: 10,
  pages: 0,
})

const filters = reactive<TopicListParams>({
  page: 1,
  page_size: 10,
  order_by: 'created_at',
  order: 'desc',
})

const form = reactive<TopicPayload>({
  title: '',
  angle: '',
  recommended_title: '',
  reason: '',
  target_reader: '',
  category_id: null,
  status: 'pending',
  value_score: 3,
  difficulty_score: 3,
  traffic_score: 3,
})

const rules: FormRules = {
  title: [{ required: true, message: '请输入选题标题', trigger: 'blur' }],
}

const topicStatusOptions = Object.entries(topicStatusText).map(([value, label]) => ({ value: value as TopicStatus, label }))

async function fetchPage() {
  loading.value = true
  try {
    const result = await getTopicList(filters)
    Object.assign(pageData, result)
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '选题列表加载失败')
  } finally {
    loading.value = false
  }
}

function resetForm() {
  editingId.value = undefined
  deadlineInput.value = ''
  Object.assign(form, {
    title: '',
    angle: '',
    recommended_title: '',
    reason: '',
    target_reader: '',
    category_id: null,
    status: 'pending',
    value_score: 3,
    difficulty_score: 3,
    traffic_score: 3,
    deadline: undefined,
  })
}

function openCreateDialog() {
  resetForm()
  dialogVisible.value = true
}

function openEditDialog(row: TopicItem) {
  editingId.value = row.id
  deadlineInput.value = toDateTimeInputValue(row.deadline)
  Object.assign(form, {
    title: row.title,
    angle: row.angle || '',
    recommended_title: row.recommended_title || '',
    reason: row.reason || '',
    target_reader: row.target_reader || '',
    category_id: row.category?.id || null,
    status: row.status,
    value_score: row.value_score,
    difficulty_score: row.difficulty_score,
    traffic_score: row.traffic_score,
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  const valid = await formRef.value?.validate()
  if (!valid) return

  submitting.value = true
  try {
    const payload = { ...form, deadline: toApiDateTime(deadlineInput.value) }
    if (editingId.value) {
      await updateTopic(editingId.value, payload)
      ElMessage.success('选题已更新')
    } else {
      await createTopic(payload)
      ElMessage.success('选题已创建')
    }
    dialogVisible.value = false
    fetchPage()
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '保存失败')
  } finally {
    submitting.value = false
  }
}

async function handleStatusChange(row: TopicItem, value: unknown) {
  await updateTopicStatus(row.id, value as TopicStatus)
  ElMessage.success('状态已更新')
  fetchPage()
}

async function handleDelete(row: TopicItem) {
  try {
    await ElMessageBox.confirm(`确认删除「${row.title}」吗？`, '删除选题', { type: 'warning' })
    await deleteTopic(row.id)
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
  Object.assign(filters, { page: 1, page_size: 10, keyword: undefined, category_id: undefined, status: undefined, order_by: 'created_at', order: 'desc' })
  fetchPage()
}

function handlePageChange(page: number) {
  filters.page = page
  fetchPage()
}

onMounted(() => {
  getCategories(true).then((result) => (categories.value = result))
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
  padding: 16px;
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
