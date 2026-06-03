<template>
  <div class="page">
    <header class="page-header">
      <div>
        <h1 class="page-title">每日采集</h1>
        <p class="page-subtitle">选择日期后触发固定 AI 资讯 skill 流程，结果将进入 RAG 知识库。</p>
      </div>
    </header>

    <section class="focus-grid">
      <div class="section">
        <div class="toolbar">
          <strong>采集任务</strong>
          <span class="muted">后端逻辑预留完成，你可以从这里开始接入真实抓取。</span>
        </div>
        <div class="section-body">
          <el-form label-position="top" class="digest-form">
            <div class="form-grid">
              <el-form-item label="采集日期">
                <el-date-picker v-model="form.digest_date" type="date" value-format="YYYY-MM-DD" />
              </el-form-item>
              <el-form-item label="最多候选条数">
                <el-input-number v-model="form.max_items" :min="1" :max="100" />
              </el-form-item>
              <el-form-item label="运行方式">
                <el-switch v-model="form.dry_run" active-text="只预览" inactive-text="写入知识库" />
              </el-form-item>
            </div>

            <el-collapse class="model-collapse">
              <el-collapse-item title="模型设置" name="model">
                <div class="form-grid">
                  <el-form-item label="Base URL">
                    <el-input v-model.trim="form.llm_config.api_base_url" placeholder="留空则使用后端 .env" />
                  </el-form-item>
                  <el-form-item label="模型名">
                    <el-input v-model.trim="form.llm_config.model" placeholder="留空则使用 OPENAI_MODEL" />
                  </el-form-item>
                  <el-form-item label="API Key">
                    <el-input v-model="form.llm_config.api_key" type="password" show-password autocomplete="off" />
                  </el-form-item>
                </div>
              </el-collapse-item>
            </el-collapse>

            <div class="form-actions">
              <el-button type="primary" :icon="MagicStick" :loading="submitting" @click="handleRun">
                开始采集
              </el-button>
              <el-button :icon="Refresh" @click="resetForm">重置</el-button>
            </div>
          </el-form>
        </div>
      </div>

      <div class="section">
        <div class="toolbar">
          <strong>本次结果</strong>
        </div>
        <div class="section-body result-panel">
          <EmptyState
            v-if="!result"
            title="还没有采集结果"
            description="点击开始采集后，这里会显示任务状态、入库数量和预览内容。"
          />
          <template v-else>
            <div class="run-summary">
              <div>
                <span>状态</span>
                <strong>{{ result.status }}</strong>
              </div>
              <div>
                <span>文档</span>
                <strong>{{ result.document_count }}</strong>
              </div>
              <div>
                <span>Chunk</span>
                <strong>{{ result.chunk_count }}</strong>
              </div>
            </div>

            <el-alert :title="result.message" type="info" show-icon />

            <article v-for="item in result.preview_items" :key="item.title" class="preview-item">
              <strong>{{ item.title }}</strong>
              <p>{{ item.summary || '暂无摘要' }}</p>
              <div class="preview-meta">
                <span>{{ item.source_name || '未知来源' }}</span>
                <span>{{ item.credibility }}</span>
              </div>
            </article>
          </template>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { MagicStick, Refresh } from '@element-plus/icons-vue'
import EmptyState from '@/components/EmptyState.vue'
import { createDailyDigestRun } from '@/api/rag'
import type { DailyDigestRunPayload, DailyDigestRunResult } from '@/types/rag'
import { getLocalDateString } from '@/utils/date'

const submitting = ref(false)
const result = ref<DailyDigestRunResult>()

const defaultForm: DailyDigestRunPayload = {
  digest_date: getLocalDateString(),
  max_items: 30,
  dry_run: true,
  llm_config: {
    api_base_url: '',
    api_key: '',
    model: '',
  },
}

const form = reactive<DailyDigestRunPayload>({
  ...defaultForm,
  llm_config: { ...defaultForm.llm_config },
})

async function handleRun() {
  submitting.value = true
  try {
    result.value = await createDailyDigestRun({
      ...form,
      digest_date: form.digest_date || undefined,
      max_items: Number(form.max_items) || defaultForm.max_items,
      llm_config: { ...form.llm_config },
    })
    ElMessage.success('采集任务已提交')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '采集任务提交失败')
  } finally {
    submitting.value = false
  }
}

function resetForm() {
  Object.assign(form, {
    ...defaultForm,
    llm_config: { ...defaultForm.llm_config },
  })
  result.value = undefined
}
</script>

<style scoped>
.focus-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(340px, 0.78fr);
  gap: 20px;
}

.digest-form,
.result-panel {
  display: grid;
  gap: 18px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.model-collapse {
  border-top: 1px solid var(--nh-border);
  border-bottom: 1px solid var(--nh-border);
}

.form-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.run-summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.run-summary div,
.preview-item {
  padding: 14px;
  background: rgba(255, 253, 248, 0.78);
  border: 1px solid var(--nh-border);
  border-radius: var(--nh-radius);
}

.run-summary span,
.preview-meta {
  color: var(--nh-muted);
}

.run-summary strong {
  display: block;
  margin-top: 7px;
  font-family: var(--nh-font-heading);
  font-size: 25px;
}

.preview-item p {
  margin: 8px 0;
  color: var(--nh-muted);
  line-height: 1.7;
}

.preview-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  font-size: 13px;
}

@media (max-width: 980px) {
  .focus-grid,
  .form-grid,
  .run-summary {
    grid-template-columns: 1fr;
  }
}
</style>
