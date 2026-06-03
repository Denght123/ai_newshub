<template>
  <div class="gemini-chat-page" :class="{ 'has-answer': hasConversation }">
    <div class="chat-shell">
      <section v-if="!hasConversation" class="welcome-panel">
        <span class="eyebrow">AI NewsHub RAG</span>
        <h1>今天想了解哪些 AI 资讯？</h1>
        <p>直接提问即可，我会从你的知识库里找依据回答。</p>

        <div class="prompt-list">
          <button v-for="prompt in quickPrompts" :key="prompt" type="button" @click="usePrompt(prompt)">
            {{ prompt }}
          </button>
        </div>
      </section>

      <section v-else class="conversation-panel">
        <article class="message user-message">
          <p>{{ currentQuestion }}</p>
        </article>

        <article class="message assistant-message">
          <span class="assistant-name">AI NewsHub</span>
          <p>{{ answer || '正在检索知识库...' }}</p>

          <details v-if="citations.length || matchedChunks.length" class="source-details">
            <summary>查看依据</summary>
            <div class="source-list">
              <a
                v-for="item in citations"
                :key="`${item.document_id}-${item.title}`"
                class="source-item"
                :href="item.source_url || undefined"
                target="_blank"
                rel="noreferrer"
              >
                <strong>{{ item.title }}</strong>
                <span>{{ item.digest_date || '未知日期' }} · {{ item.source_name || '未知来源' }}</span>
              </a>
            </div>
          </details>
        </article>
      </section>

      <form class="composer" @submit.prevent="handleAsk">
        <button class="icon-button" type="button" title="新对话" @click="resetChat">
          <el-icon><Refresh /></el-icon>
        </button>

        <el-input
          v-model.trim="form.question"
          class="composer-input"
          type="textarea"
          :autosize="{ minRows: 1, maxRows: 5 }"
          maxlength="1000"
          placeholder="问问今天、某一天，或某条 AI 资讯发生了什么"
          @keydown.enter.exact.prevent="handleAsk"
        />

        <el-popover trigger="click" placement="top" width="280px">
          <template #reference>
            <button class="plain-pill" type="button">
              范围
              <el-icon><Setting /></el-icon>
            </button>
          </template>
          <div class="scope-popover">
            <el-date-picker v-model="form.date_from" type="date" value-format="YYYY-MM-DD" placeholder="开始日期" />
            <el-date-picker v-model="form.date_to" type="date" value-format="YYYY-MM-DD" placeholder="结束日期" />
            <el-input-number v-model="form.top_k" :min="1" :max="20" />
            <el-switch v-model="useStream" active-text="流式输出" inactive-text="普通回答" />
          </div>
        </el-popover>

        <el-button class="send-button" type="primary" native-type="submit" :icon="ChatLineRound" :loading="loading">
          发送
        </el-button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { ChatLineRound, Refresh, Setting } from '@element-plus/icons-vue'
import { askRagChat, streamRagChat } from '@/api/rag'
import type { MatchedChunk, RagChatPayload, RagCitation } from '@/types/rag'
import { getLocalDateString } from '@/utils/date'

const quickPrompts = [
  '今天有哪些重要 AI 消息？',
  '最近的大模型更新有哪些？',
  '帮我总结今天最值得关注的一条资讯',
]

const loading = ref(false)
const useStream = ref(true)
const answer = ref('')
const currentQuestion = ref('')
const citations = ref<RagCitation[]>([])
const matchedChunks = ref<MatchedChunk[]>([])
const hasConversation = computed(() => Boolean(currentQuestion.value || answer.value || loading.value))

const form = reactive<RagChatPayload>({
  question: '',
  date_from: getLocalDateString(),
  date_to: getLocalDateString(),
  top_k: 5,
})

function usePrompt(prompt: string) {
  form.question = prompt
}

function resetChat() {
  answer.value = ''
  currentQuestion.value = ''
  citations.value = []
  matchedChunks.value = []
  form.question = ''
}

async function handleAsk() {
  if (loading.value) return
  if (!form.question) {
    ElMessage.warning('请先输入问题')
    return
  }

  loading.value = true
  currentQuestion.value = form.question
  answer.value = ''
  citations.value = []
  matchedChunks.value = []

  try {
    const payload = {
      ...form,
      date_from: form.date_from || undefined,
      date_to: form.date_to || undefined,
      top_k: Number(form.top_k) || 5,
    }

    if (useStream.value) {
      await streamRagChat(
        payload,
        (content) => {
          answer.value += content
        },
        (doneData) => {
          citations.value = doneData?.citations || []
          matchedChunks.value = doneData?.matched_chunks || []
        },
      )
    } else {
      const result = await askRagChat(payload)
      answer.value = result.answer
      citations.value = result.citations
      matchedChunks.value = result.matched_chunks
    }
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '问答请求失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.gemini-chat-page {
  display: grid;
  min-height: calc(100dvh - 134px);
  place-items: center;
  padding: 18px;
}

.chat-shell {
  display: grid;
  width: min(780px, 100%);
  gap: 28px;
}

.gemini-chat-page.has-answer {
  align-items: start;
}

.gemini-chat-page.has-answer .chat-shell {
  min-height: calc(100dvh - 170px);
  grid-template-rows: 1fr auto;
}

.welcome-panel {
  display: grid;
  gap: 14px;
  text-align: center;
  animation: nh-fade-up 320ms var(--nh-transition) both;
}

.eyebrow {
  color: var(--nh-primary-dark);
  font-size: 13px;
  font-weight: 750;
}

.welcome-panel h1 {
  margin: 0;
  color: #26323d;
  font-family: var(--nh-font-body);
  font-size: clamp(30px, 4vw, 42px);
  font-weight: 540;
  letter-spacing: 0;
  line-height: 1.2;
}

.welcome-panel p {
  margin: 0;
  color: var(--nh-muted);
  line-height: 1.7;
}

.prompt-list {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
  margin-top: 10px;
}

.prompt-list button {
  min-height: 38px;
  padding: 0 14px;
  color: #41515d;
  cursor: pointer;
  background: rgba(255, 253, 248, 0.72);
  border: 1px solid var(--nh-border);
  border-radius: 999px;
  transition:
    border-color var(--nh-transition-fast),
    box-shadow var(--nh-transition-fast),
    transform var(--nh-transition-fast);
}

.prompt-list button:hover {
  border-color: var(--nh-border-strong);
  box-shadow: 0 10px 20px rgba(84, 60, 28, 0.08);
  transform: translateY(-1px);
}

.conversation-panel {
  display: grid;
  align-content: start;
  gap: 22px;
  padding-top: 18px;
}

.message {
  max-width: 82%;
  padding: 16px 18px;
  border-radius: 20px;
  animation: nh-fade-up 260ms var(--nh-transition) both;
}

.message p {
  margin: 0;
  line-height: 1.78;
  white-space: pre-wrap;
  word-break: break-word;
}

.user-message {
  justify-self: end;
  color: #29323a;
  background: rgba(255, 253, 248, 0.92);
  border: 1px solid var(--nh-border);
}

.assistant-message {
  justify-self: start;
  color: #25313b;
  background: transparent;
}

.assistant-name {
  display: block;
  margin-bottom: 8px;
  color: var(--nh-primary-dark);
  font-size: 13px;
  font-weight: 760;
}

.source-details {
  margin-top: 16px;
  color: var(--nh-muted);
}

.source-details summary {
  width: fit-content;
  cursor: pointer;
  font-size: 13px;
  font-weight: 700;
}

.source-list {
  display: grid;
  gap: 8px;
  margin-top: 10px;
}

.source-item {
  display: grid;
  gap: 4px;
  padding: 11px 12px;
  color: var(--nh-ink);
  background: rgba(255, 253, 248, 0.7);
  border: 1px solid var(--nh-border);
  border-radius: var(--nh-radius);
}

.source-item span {
  color: var(--nh-muted);
  font-size: 13px;
}

.composer {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(213, 225, 236, 0.9);
  border-radius: 28px;
  box-shadow:
    0 18px 44px rgba(70, 94, 116, 0.14),
    0 0 0 8px rgba(220, 237, 250, 0.22);
}

.composer-input {
  flex: 1;
}

.composer-input :deep(.el-textarea__inner) {
  min-height: 42px !important;
  padding: 11px 4px;
  resize: none;
  background: transparent;
  border: 0;
  box-shadow: none;
}

.composer-input :deep(.el-input__count) {
  display: none;
}

.icon-button,
.plain-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 42px;
  height: 42px;
  color: #40515f;
  cursor: pointer;
  background: transparent;
  border: 0;
  border-radius: 999px;
  transition:
    background-color var(--nh-transition-fast),
    color var(--nh-transition-fast);
}

.plain-pill {
  gap: 5px;
  min-width: auto;
  padding: 0 10px;
  font-size: 13px;
  font-weight: 700;
}

.icon-button:hover,
.plain-pill:hover {
  color: var(--nh-primary-dark);
  background: rgba(53, 97, 90, 0.08);
}

.send-button {
  height: 42px;
  border-radius: 999px;
}

.scope-popover {
  display: grid;
  gap: 12px;
}

.scope-popover :deep(.el-date-editor),
.scope-popover :deep(.el-input-number) {
  width: 100%;
}

@media (max-width: 720px) {
  .gemini-chat-page {
    min-height: auto;
    padding: 10px 0 0;
  }

  .message {
    max-width: 100%;
  }

  .composer {
    flex-wrap: wrap;
    border-radius: 20px;
  }

  .composer-input {
    order: -1;
    flex-basis: 100%;
  }
}
</style>
