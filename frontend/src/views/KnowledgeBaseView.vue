<template>
  <div class="page">
    <header class="page-header">
      <div>
        <h1 class="page-title">知识库</h1>
        <p class="page-subtitle">按日期查看已经沉淀的 AI 资讯，后续 RAG 问答会从这里检索。</p>
      </div>
    </header>

    <section class="section">
      <div class="toolbar">
        <el-date-picker v-model="filters.digest_date" type="date" value-format="YYYY-MM-DD" placeholder="归档日期" />
        <el-input v-model.trim="filters.keyword" clearable :prefix-icon="Search" placeholder="搜索标题、摘要、来源" @keyup.enter="fetchDocuments" />
        <el-button type="primary" :icon="Search" :loading="loading" @click="fetchDocuments">查询</el-button>
        <el-button :icon="Refresh" @click="resetFilters">重置</el-button>
      </div>

      <div class="knowledge-layout">
        <div class="document-list">
          <LoadingState v-if="loading" />
          <EmptyState v-else-if="documents.length === 0" title="暂无知识文档" description="完成一次每日采集后，入库内容会显示在这里。" />
          <template v-else>
            <button
              v-for="document in documents"
              :key="document.id"
              class="document-item"
              :class="{ 'is-active': selected?.id === document.id }"
              @click="selectDocument(document.id)"
            >
              <strong>{{ document.title }}</strong>
              <p>{{ document.summary || '暂无摘要' }}</p>
              <span>{{ document.digest_date }} · {{ document.source_name || '未知来源' }}</span>
            </button>
          </template>
        </div>

        <aside class="detail-panel">
          <EmptyState v-if="!selected" title="选择一条文档" description="右侧会展示正文、来源和 RAG chunk。" />
          <template v-else>
            <el-tag>{{ selected.credibility }}</el-tag>
            <h2>{{ selected.title }}</h2>
            <p class="muted">{{ selected.summary || '暂无摘要' }}</p>
            <a v-if="selected.source_url" class="text-link" :href="selected.source_url" target="_blank" rel="noreferrer">查看原文</a>

            <div class="detail-item">
              <div class="detail-label">正文</div>
              <div class="detail-value">{{ selected.content || '等待后端写入正文内容' }}</div>
            </div>

            <div class="chunk-list">
              <strong>RAG Chunks</strong>
              <div v-for="chunk in selected.chunks" :key="chunk.id" class="chunk-item">
                <span>#{{ chunk.chunk_index }}</span>
                <p>{{ chunk.chunk_text }}</p>
              </div>
            </div>
          </template>
        </aside>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Search } from '@element-plus/icons-vue'
import EmptyState from '@/components/EmptyState.vue'
import LoadingState from '@/components/LoadingState.vue'
import { getKnowledgeDocumentDetail, getKnowledgeDocuments } from '@/api/rag'
import type { KnowledgeDocumentDetail, KnowledgeDocumentItem } from '@/types/rag'
import { getLocalDateString } from '@/utils/date'

const loading = ref(false)
const documents = ref<KnowledgeDocumentItem[]>([])
const selected = ref<KnowledgeDocumentDetail>()

const filters = reactive({
  digest_date: getLocalDateString(),
  keyword: '',
  page: 1,
  page_size: 10,
})

async function fetchDocuments() {
  loading.value = true
  try {
    const result = await getKnowledgeDocuments({
      digest_date: filters.digest_date || undefined,
      keyword: filters.keyword || undefined,
      page: filters.page,
      page_size: filters.page_size,
    })
    documents.value = result.items
    if (documents.value.length > 0) {
      await selectDocument(documents.value[0].id)
    } else {
      selected.value = undefined
    }
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '知识库加载失败')
  } finally {
    loading.value = false
  }
}

async function selectDocument(documentId: number) {
  try {
    selected.value = await getKnowledgeDocumentDetail(documentId)
  } catch (error) {
    selected.value = undefined
    ElMessage.error(error instanceof Error ? error.message : '知识文档详情加载失败')
  }
}

function resetFilters() {
  filters.digest_date = getLocalDateString()
  filters.keyword = ''
  fetchDocuments()
}

onMounted(fetchDocuments)
</script>

<style scoped>
.knowledge-layout {
  display: grid;
  grid-template-columns: minmax(320px, 0.82fr) minmax(0, 1.18fr);
  gap: 0;
}

.document-list {
  display: grid;
  gap: 10px;
  align-content: start;
  padding: 18px;
  border-right: 1px solid var(--nh-border);
}

.document-item {
  display: grid;
  gap: 7px;
  width: 100%;
  padding: 14px;
  color: var(--nh-ink);
  text-align: left;
  cursor: pointer;
  background: rgba(255, 253, 248, 0.74);
  border: 1px solid var(--nh-border);
  border-radius: var(--nh-radius);
  transition:
    border-color var(--nh-transition),
    box-shadow var(--nh-transition),
    transform var(--nh-transition);
}

.document-item:hover,
.document-item.is-active {
  border-color: var(--nh-border-strong);
  box-shadow: 0 12px 26px rgba(84, 60, 28, 0.1);
  transform: translateY(-1px);
}

.document-item p {
  margin: 0;
  color: var(--nh-muted);
  line-height: 1.65;
}

.document-item span {
  color: var(--nh-muted);
  font-size: 13px;
}

.detail-panel {
  display: grid;
  gap: 16px;
  align-content: start;
  padding: 22px;
}

.detail-panel h2 {
  margin: 0;
  font-family: var(--nh-font-heading);
  font-size: 28px;
  line-height: 1.25;
}

.chunk-list {
  display: grid;
  gap: 10px;
}

.chunk-item {
  padding: 12px;
  background: rgba(255, 253, 248, 0.76);
  border: 1px solid var(--nh-border);
  border-radius: var(--nh-radius);
}

.chunk-item span {
  color: var(--nh-muted);
  font-size: 13px;
}

.chunk-item p {
  margin: 6px 0 0;
  line-height: 1.7;
}

@media (max-width: 980px) {
  .knowledge-layout {
    grid-template-columns: 1fr;
  }

  .document-list {
    border-right: 0;
    border-bottom: 1px solid var(--nh-border);
  }
}
</style>
