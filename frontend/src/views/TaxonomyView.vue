<template>
  <div class="page">
    <header class="page-header">
      <div>
        <h1 class="page-title">分类与标签</h1>
        <p class="page-subtitle">维护资讯和选题的基础归类，方便后续筛选与统计。</p>
      </div>
      <el-button :icon="Refresh" :loading="loading" @click="fetchAll">刷新</el-button>
    </header>

    <section class="taxonomy-grid">
      <div class="section">
        <div class="toolbar">
          <strong>分类</strong>
          <el-button type="primary" :icon="Plus" @click="openCategoryDialog()">新增分类</el-button>
        </div>
        <LoadingState v-if="loading" />
        <EmptyState v-else-if="categories.length === 0" title="暂无分类" description="管理员新增分类后，可以用于资讯和选题筛选。" />
        <el-table v-else :data="categories">
          <el-table-column prop="name" label="名称" min-width="130" />
          <el-table-column prop="description" label="描述" min-width="180" />
          <el-table-column prop="sort_order" label="排序" width="90" />
          <el-table-column label="启用" width="90">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '停用' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150">
            <template #default="{ row }">
              <el-button text type="primary" :icon="Edit" @click="openCategoryDialog(row)">编辑</el-button>
              <el-button text type="danger" :icon="Delete" @click="handleDeleteCategory(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="section">
        <div class="toolbar">
          <strong>标签</strong>
          <el-button type="primary" :icon="Plus" @click="openTagDialog()">新增标签</el-button>
        </div>
        <LoadingState v-if="loading" />
        <EmptyState v-else-if="tags.length === 0" title="暂无标签" description="标签适合记录 OpenAI、DeepSeek、开源、降价等更细粒度信息。" />
        <div v-else class="tag-board">
          <div v-for="tag in tags" :key="tag.id" class="tag-card">
            <span>{{ tag.name }}</span>
            <div>
              <el-button text :icon="Edit" @click="openTagDialog(tag)" />
              <el-button text type="danger" :icon="Delete" @click="handleDeleteTag(tag)" />
            </div>
          </div>
        </div>
      </div>
    </section>

    <el-dialog v-model="categoryDialogVisible" :title="editingCategoryId ? '编辑分类' : '新增分类'" width="520px">
      <el-form ref="categoryFormRef" :model="categoryForm" :rules="categoryRules" label-position="top">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model.trim="categoryForm.name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="categoryForm.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="categoryForm.sort_order" :min="0" />
        </el-form-item>
        <el-form-item label="是否启用">
          <el-switch v-model="categoryForm.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="categoryDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmitCategory">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="tagDialogVisible" :title="editingTagId ? '编辑标签' : '新增标签'" width="420px">
      <el-form ref="tagFormRef" :model="tagForm" :rules="tagRules" label-position="top">
        <el-form-item label="标签名称" prop="name">
          <el-input v-model.trim="tagForm.name" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="tagDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmitTag">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Delete, Edit, Plus, Refresh } from '@element-plus/icons-vue'
import EmptyState from '@/components/EmptyState.vue'
import LoadingState from '@/components/LoadingState.vue'
import {
  createCategory,
  createTag,
  deleteCategory,
  deleteTag,
  getCategories,
  getTags,
  updateCategory,
  updateTag,
} from '@/api/taxonomy'
import type { CategoryItem, CategoryPayload, TagItem, TagPayload } from '@/types/taxonomy'

const loading = ref(false)
const submitting = ref(false)
const categories = ref<CategoryItem[]>([])
const tags = ref<TagItem[]>([])

const categoryDialogVisible = ref(false)
const tagDialogVisible = ref(false)
const editingCategoryId = ref<number>()
const editingTagId = ref<number>()
const categoryFormRef = ref<FormInstance>()
const tagFormRef = ref<FormInstance>()

const categoryForm = reactive<CategoryPayload>({
  name: '',
  description: '',
  sort_order: 0,
  is_active: true,
})

const tagForm = reactive<TagPayload>({
  name: '',
})

const categoryRules: FormRules = {
  name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }],
}

const tagRules: FormRules = {
  name: [{ required: true, message: '请输入标签名称', trigger: 'blur' }],
}

async function fetchAll() {
  loading.value = true
  try {
    const [categoryResult, tagResult] = await Promise.all([getCategories(false), getTags()])
    categories.value = categoryResult
    tags.value = tagResult
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '分类标签加载失败')
  } finally {
    loading.value = false
  }
}

function openCategoryDialog(row?: CategoryItem) {
  editingCategoryId.value = row?.id
  Object.assign(categoryForm, {
    name: row?.name || '',
    description: row?.description || '',
    sort_order: row?.sort_order || 0,
    is_active: row?.is_active ?? true,
  })
  categoryDialogVisible.value = true
}

function openTagDialog(row?: TagItem) {
  editingTagId.value = row?.id
  tagForm.name = row?.name || ''
  tagDialogVisible.value = true
}

async function handleSubmitCategory() {
  const valid = await categoryFormRef.value?.validate()
  if (!valid) return

  submitting.value = true
  try {
    if (editingCategoryId.value) {
      await updateCategory(editingCategoryId.value, categoryForm)
      ElMessage.success('分类已更新')
    } else {
      await createCategory(categoryForm)
      ElMessage.success('分类已新增')
    }
    categoryDialogVisible.value = false
    fetchAll()
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '保存失败')
  } finally {
    submitting.value = false
  }
}

async function handleSubmitTag() {
  const valid = await tagFormRef.value?.validate()
  if (!valid) return

  submitting.value = true
  try {
    if (editingTagId.value) {
      await updateTag(editingTagId.value, tagForm)
      ElMessage.success('标签已更新')
    } else {
      await createTag(tagForm)
      ElMessage.success('标签已新增')
    }
    tagDialogVisible.value = false
    fetchAll()
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '保存失败')
  } finally {
    submitting.value = false
  }
}

async function handleDeleteCategory(row: CategoryItem) {
  try {
    await ElMessageBox.confirm(`确认删除分类「${row.name}」吗？`, '删除分类', { type: 'warning' })
    await deleteCategory(row.id)
    ElMessage.success('删除成功')
    fetchAll()
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      ElMessage.error(error instanceof Error ? error.message : '删除失败')
    }
  }
}

async function handleDeleteTag(row: TagItem) {
  try {
    await ElMessageBox.confirm(`确认删除标签「${row.name}」吗？`, '删除标签', { type: 'warning' })
    await deleteTag(row.id)
    ElMessage.success('删除成功')
    fetchAll()
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      ElMessage.error(error instanceof Error ? error.message : '删除失败')
    }
  }
}

onMounted(fetchAll)
</script>

<style scoped>
.taxonomy-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.3fr) minmax(320px, 0.7fr);
  gap: 18px;
}

.toolbar {
  justify-content: space-between;
}

.tag-board {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 18px;
}

.tag-card {
  display: inline-flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  min-height: 44px;
  padding: 8px 8px 8px 14px;
  background: #fbfcfa;
  border: 1px solid var(--nh-border);
  border-radius: 8px;
}

@media (max-width: 980px) {
  .taxonomy-grid {
    grid-template-columns: 1fr;
  }
}
</style>
