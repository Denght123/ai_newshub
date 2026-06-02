<template>
  <div class="page">
    <header class="page-header">
      <div>
        <h1 class="page-title">AI 自动抓取</h1>
        <p class="page-subtitle">调用 AI 资讯工作流抓取近 24 小时信息，并按现有分类预处理成可入库资讯。</p>
      </div>
      <el-button :icon="Refresh" :loading="optionsLoading" @click="fetchOptions">刷新分类</el-button>
    </header>

    <section class="digest-overview">
      <div class="digest-panel">
        <div class="panel-icon">
          <el-icon><MagicStick /></el-icon>
        </div>
        <div>
          <strong>工作流来源</strong>
          <span>ai-news-blogger-digest</span>
        </div>
      </div>
      <div class="digest-panel">
        <div class="panel-icon">
          <el-icon><Connection /></el-icon>
        </div>
        <div>
          <strong>模型接口</strong>
          <span>OpenAI-compatible API</span>
        </div>
      </div>
      <div class="digest-panel">
        <div class="panel-icon">
          <el-icon><FolderChecked /></el-icon>
        </div>
        <div>
          <strong>分类策略</strong>
          <span>优先匹配现有分类</span>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="toolbar">
        <strong>抓取任务配置</strong>
        <span class="muted">密钥不会保存在前端，只随本次请求发送到后端接口。</span>
      </div>

      <div class="section-body">
        <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="digest-form">
          <div class="form-block">
            <h2>模型配置</h2>
            <div class="form-grid">
              <el-form-item label="服务商" prop="llm_provider">
                <el-select v-model="form.llm_provider">
                  <el-option label="OpenAI Compatible" value="openai_compatible" />
                  <el-option label="OpenAI" value="openai" />
                  <el-option label="DeepSeek Compatible" value="deepseek_compatible" />
                  <el-option label="通义 / 百炼兼容" value="dashscope_compatible" />
                </el-select>
              </el-form-item>
              <el-form-item label="Base URL" prop="api_base_url">
                <el-input v-model.trim="form.api_base_url" placeholder="https://api.example.com/v1" />
              </el-form-item>
              <el-form-item label="模型名" prop="model">
                <el-input v-model.trim="form.model" placeholder="gpt-4.1-mini / deepseek-chat / qwen-plus" />
              </el-form-item>
              <el-form-item label="API Key（可选）" prop="api_key">
                <el-input v-model="form.api_key" type="password" show-password placeholder="后端未配置环境变量时可临时填写" autocomplete="off" />
              </el-form-item>
            </div>
          </div>

          <div class="form-block">
            <h2>抓取与入库策略</h2>
            <div class="form-grid">
              <el-form-item label="时间窗口">
                <el-input-number v-model="form.time_window_hours" :min="1" :max="168" />
              </el-form-item>
              <el-form-item label="最多候选条数">
                <el-input-number v-model="form.max_items" :min="5" :max="100" />
              </el-form-item>
              <el-form-item label="来源覆盖">
                <el-select v-model="form.source_profile">
                  <el-option label="均衡覆盖" value="balanced" />
                  <el-option label="最小可用" value="minimal" />
                  <el-option label="官方优先" value="official_first" />
                  <el-option label="社区热点" value="community_hot" />
                </el-select>
              </el-form-item>
              <el-form-item label="分类方式">
                <el-select v-model="form.category_strategy">
                  <el-option label="自动匹配现有分类" value="match_existing" />
                  <el-option label="固定写入所选分类" value="fixed" />
                  <el-option label="暂不设置分类" value="none" />
                </el-select>
              </el-form-item>
            </div>

            <el-form-item label="可匹配分类">
              <el-alert
                v-if="categories.length === 0"
                type="warning"
                show-icon
                title="当前没有可用分类，建议先在分类与标签中创建基础分类。"
              />
              <el-checkbox-group v-else v-model="form.category_ids" class="category-picker">
                <el-checkbox v-for="category in categories" :key="category.id" :label="category.id">
                  {{ category.name }}
                </el-checkbox>
              </el-checkbox-group>
            </el-form-item>

            <div class="switch-grid">
              <label>
                <span>允许创建缺失分类</span>
                <el-switch v-model="form.auto_create_missing_categories" />
              </label>
              <label>
                <span>同时生成选题建议</span>
                <el-switch v-model="form.create_topics" />
              </label>
              <label>
                <span>仅预览不入库</span>
                <el-switch v-model="form.dry_run" />
              </label>
            </div>

            <el-form-item label="给抓取工作流的补充要求">
              <el-input
                v-model="form.prompt_note"
                type="textarea"
                :rows="4"
                placeholder="例如：更关注国产大模型、开源 Agent、API 降价，不要收录纯融资八卦。"
              />
            </el-form-item>
          </div>

          <div class="form-actions">
            <el-button type="primary" :icon="DocumentAdd" :loading="submitting" @click="handleSubmit">
              一键抓取
            </el-button>
            <el-button @click="resetForm">恢复默认</el-button>
          </div>
        </el-form>
      </div>
    </section>

    <section v-if="result" class="section">
      <div class="toolbar">
        <strong>任务返回</strong>
        <el-tag>{{ statusText[result.status] || result.status }}</el-tag>
      </div>
      <div class="section-body result-body">
        <div class="result-summary">
          <div>
            <span>候选</span>
            <strong>{{ result.received_items }}</strong>
          </div>
          <div>
            <span>资讯入库</span>
            <strong>{{ result.created_news_count }}</strong>
          </div>
          <div>
            <span>选题生成</span>
            <strong>{{ result.created_topic_count }}</strong>
          </div>
          <div>
            <span>跳过</span>
            <strong>{{ result.skipped_count }}</strong>
          </div>
        </div>

        <el-alert type="info" show-icon :title="result.message" />

        <div v-if="result.preview_items.length" class="preview-list">
          <article v-for="item in result.preview_items" :key="item.title" class="preview-item">
            <strong>{{ item.title }}</strong>
            <p>{{ item.one_line_summary || '暂无摘要' }}</p>
            <div class="preview-meta">
              <span>{{ item.source_name || '未知来源' }}</span>
              <span>{{ item.matched_category?.name || '未匹配分类' }}</span>
            </div>
          </article>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Connection, DocumentAdd, FolderChecked, MagicStick, Refresh } from '@element-plus/icons-vue'
import { runAIDigestImport } from '@/api/aiDigest'
import { getCategories } from '@/api/taxonomy'
import type { AIDigestRunPayload, AIDigestRunResult, AIDigestRunStatus } from '@/types/aiDigest'
import type { CategoryItem } from '@/types/taxonomy'

const formRef = ref<FormInstance>()
const submitting = ref(false)
const optionsLoading = ref(false)
const categories = ref<CategoryItem[]>([])
const result = ref<AIDigestRunResult>()

const defaultForm: AIDigestRunPayload = {
  skill_name: 'ai-news-blogger-digest',
  llm_provider: 'openai_compatible',
  api_base_url: 'https://api.openai.com/v1',
  api_key: '',
  model: 'gpt-4.1-mini',
  time_window_hours: 24,
  max_items: 30,
  source_profile: 'balanced',
  category_strategy: 'match_existing',
  category_ids: [],
  auto_create_missing_categories: false,
  create_topics: true,
  dry_run: true,
  prompt_note: '',
}

const form = reactive<AIDigestRunPayload>({ ...defaultForm })

const rules: FormRules = {
  api_base_url: [{ required: true, message: '请输入兼容 OpenAI 的 Base URL', trigger: 'blur' }],
  model: [{ required: true, message: '请输入模型名', trigger: 'blur' }],
}

const statusText: Record<AIDigestRunStatus, string> = {
  reserved: '接口已预留',
  queued: '排队中',
  running: '运行中',
  completed: '已完成',
  failed: '失败',
}

async function fetchOptions() {
  optionsLoading.value = true
  try {
    categories.value = await getCategories(true)
    if (form.category_ids.length === 0) {
      form.category_ids = categories.value.map((category) => category.id)
    }
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '分类加载失败')
  } finally {
    optionsLoading.value = false
  }
}

async function handleSubmit() {
  const valid = await formRef.value?.validate()
  if (!valid) return

  submitting.value = true
  try {
    result.value = await runAIDigestImport({ ...form })
    ElMessage.success(result.value.message || '抓取任务已提交')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '抓取任务提交失败')
  } finally {
    submitting.value = false
  }
}

function resetForm() {
  Object.assign(form, { ...defaultForm, category_ids: categories.value.map((category) => category.id) })
  result.value = undefined
}

onMounted(fetchOptions)
</script>

<style scoped>
.digest-overview {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.digest-panel {
  display: flex;
  min-height: 94px;
  align-items: center;
  gap: 14px;
  padding: 18px;
  background: var(--nh-surface-raised);
  border: 1px solid var(--nh-border);
  border-radius: var(--nh-radius);
  box-shadow: var(--nh-shadow);
}

.panel-icon {
  display: grid;
  width: 44px;
  height: 44px;
  flex: 0 0 auto;
  place-items: center;
  color: var(--nh-primary-dark);
  background: linear-gradient(135deg, var(--nh-soft), var(--nh-accent-soft));
  border: 1px solid var(--nh-border);
  border-radius: var(--nh-radius);
}

.digest-panel strong,
.digest-panel span {
  display: block;
}

.digest-panel strong {
  font-size: 16px;
}

.digest-panel span {
  margin-top: 4px;
  color: var(--nh-muted);
}

.digest-form {
  display: grid;
  gap: 24px;
}

.form-block {
  display: grid;
  gap: 14px;
}

.form-block h2 {
  margin: 0;
  font-size: 18px;
  line-height: 1.3;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px 14px;
}

.category-picker {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 14px;
}

.switch-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.switch-grid label {
  display: flex;
  min-height: 48px;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 11px 13px;
  color: var(--nh-ink);
  background: rgba(249, 251, 254, 0.78);
  border: 1px solid var(--nh-border);
  border-radius: var(--nh-radius);
}

.form-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.result-body {
  display: grid;
  gap: 16px;
}

.result-summary {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.result-summary div {
  padding: 14px;
  background: rgba(249, 251, 254, 0.78);
  border: 1px solid var(--nh-border);
  border-radius: var(--nh-radius);
}

.result-summary span,
.preview-meta {
  color: var(--nh-muted);
}

.result-summary strong {
  display: block;
  margin-top: 6px;
  font-size: 24px;
  line-height: 1;
}

.preview-list {
  display: grid;
  gap: 10px;
}

.preview-item {
  padding: 14px;
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid var(--nh-border);
  border-radius: var(--nh-radius);
}

.preview-item p {
  margin: 8px 0;
  color: var(--nh-muted);
  line-height: 1.65;
}

.preview-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  font-size: 13px;
}

@media (max-width: 980px) {
  .digest-overview,
  .switch-grid,
  .result-summary {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
