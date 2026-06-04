<template>
  <div class="rag-chat-workspace">
    <aside class="chat-rail" aria-label="聊天历史">
      <div class="rail-heading">
        <div>
          <strong>AI 问答</strong>
          <span>历史会话</span>
        </div>
      </div>

      <button class="new-chat-button" type="button" @click="startNewChat">
        <el-icon><Plus /></el-icon>
        <span>新对话</span>
      </button>

      <el-input
        v-model="historyKeyword"
        class="history-search"
        clearable
        placeholder="搜索历史"
        :prefix-icon="Search"
      />

      <div class="session-list">
        <p v-if="loadingSessions" class="rail-empty">正在加载历史会话...</p>
        <p v-else-if="!filteredSessions.length" class="rail-empty">暂无会话</p>

        <div
          v-for="session in filteredSessions"
          :key="session.id"
          class="session-row"
          :class="{ 'is-active': session.id === activeSessionId }"
        >
          <button class="session-button" type="button" @click="selectSession(session.id)">
            <el-icon><ChatLineRound /></el-icon>
            <span>{{ session.title }}</span>
            <small>{{ formatSessionTime(session.updated_at) }}</small>
          </button>

          <button class="session-delete" type="button" aria-label="删除会话" @click.stop="handleDeleteSession(session)">
            <el-icon><Delete /></el-icon>
          </button>
        </div>
      </div>
    </aside>

    <section class="chat-stage">
      <header class="chat-stage-header">
        <div>
          <span class="stage-kicker">AI NewsHub RAG</span>
          <h1>{{ activeTitle }}</h1>
        </div>

        <el-popover trigger="click" placement="bottom-end" width="286px">
          <template #reference>
            <button class="scope-button" type="button">
              <el-icon><Setting /></el-icon>
              <span>检索范围</span>
            </button>
          </template>

          <div class="scope-popover">
            <label>
              <span>开始日期</span>
              <el-date-picker v-model="form.date_from" type="date" value-format="YYYY-MM-DD" placeholder="开始日期" />
            </label>
            <label>
              <span>结束日期</span>
              <el-date-picker v-model="form.date_to" type="date" value-format="YYYY-MM-DD" placeholder="结束日期" />
            </label>
            <label>
              <span>命中片段数</span>
              <el-input-number v-model="form.top_k" :min="1" :max="20" />
            </label>
            <el-switch v-model="useStream" active-text="流式输出" inactive-text="普通回答" />
          </div>
        </el-popover>
      </header>

      <main ref="messageScrollRef" class="message-scroll">
        <section v-if="!messages.length" class="welcome-state">
          <span>AI NewsHub RAG</span>
          <h2>想了解哪一天的 AI 消息？</h2>
          <p>选择一个问题开始，我会基于已入库的资讯回答。</p>

          <div class="quick-prompts">
            <button v-for="prompt in quickPrompts" :key="prompt" type="button" @click="askQuickPrompt(prompt)">
              {{ prompt }}
            </button>
          </div>
        </section>

        <template v-else>
          <article
            v-for="(message, index) in messages"
            :key="message.id || `${message.role}-${index}`"
            class="chat-message"
            :class="message.role === 'user' ? 'is-user' : 'is-assistant'"
          >
            <div class="message-avatar">{{ message.role === 'user' ? '你' : 'AI' }}</div>

            <div class="message-bubble">
              <p>{{ message.content || '正在生成回答...' }}</p>

              <details v-if="message.role !== 'user' && getMessageCitations(message).length" class="source-details">
                <summary>引用来源</summary>
                <div class="source-list">
                  <a
                    v-for="item in getMessageCitations(message)"
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
            </div>
          </article>
        </template>
      </main>

      <form class="chat-composer" @submit.prevent="handleAsk">
        <el-input
          v-model="form.question"
          class="composer-input"
          type="textarea"
          :autosize="{ minRows: 1, maxRows: 5 }"
          maxlength="1000"
          placeholder="问问今天、某一天，或某条 AI 资讯发生了什么"
          @keydown.enter.exact.prevent="handleAsk"
        />

        <div class="composer-actions">
          <button class="composer-ghost" type="button" @click="startNewChat">
            <el-icon><Plus /></el-icon>
            <span>新对话</span>
          </button>

          <el-button class="send-button" type="primary" native-type="submit" :icon="ChatLineRound" :loading="loading">
            发送
          </el-button>
        </div>
      </form>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ChatLineRound, Delete, Plus, Search, Setting } from '@element-plus/icons-vue'
import {
  askRagChat,
  deleteRagChatSession,
  getRagChatSessionDetail,
  getRagChatSessions,
  streamRagChat,
} from '@/api/rag'
import type {
  MatchedChunk,
  RagChatMessage,
  RagChatPayload,
  RagChatResult,
  RagChatSession,
  RagCitation,
  RagMessageMetadata,
} from '@/types/rag'
import type { StreamDonePayload } from '@/api/rag'
import { getLocalDateString } from '@/utils/date'

interface ChatMessageView {
  id?: number
  role: 'user' | 'assistant' | string
  content: string
  metadata?: RagMessageMetadata | null
  created_at?: string
}

const quickPrompts = [
  '今天有哪些重要 AI 消息？',
  '最近的大模型更新有哪些？',
  '帮我总结今天最值得关注的一条资讯',
]

const loading = ref(false)
const loadingSessions = ref(false)
const loadingDetail = ref(false)
const useStream = ref(true)
const historyKeyword = ref('')
const activeSessionId = ref<number | null>(null)
const activeSessionTitle = ref('')
const sessions = ref<RagChatSession[]>([])
const messages = ref<ChatMessageView[]>([])
const messageScrollRef = ref<HTMLElement | null>(null)

const form = reactive<RagChatPayload>({
  session_id: null,
  question: '',
  date_from: getLocalDateString(),
  date_to: getLocalDateString(),
  top_k: 5,
})

const activeTitle = computed(() => activeSessionTitle.value || '和知识库聊聊 AI 资讯')

const filteredSessions = computed(() => {
  const keyword = historyKeyword.value.trim().toLowerCase()
  if (!keyword) return sessions.value
  return sessions.value.filter((session) => session.title.toLowerCase().includes(keyword))
})

onMounted(() => {
  void loadSessions()
})

// 加载当前用户的所有聊天会话，用于左侧历史栏。
async function loadSessions() {
  loadingSessions.value = true
  try {
    sessions.value = await getRagChatSessions()
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '聊天历史加载失败')
  } finally {
    loadingSessions.value = false
  }
}

// 点击左侧历史会话时，读取该会话下的所有历史消息。
async function selectSession(sessionId: number) {
  if (loading.value || loadingDetail.value) return

  loadingDetail.value = true
  try {
    const detail = await getRagChatSessionDetail(sessionId)
    activeSessionId.value = detail.id
    activeSessionTitle.value = detail.title
    form.session_id = detail.id
    messages.value = detail.messages.map((message) => normalizeMessage(message))
    await scrollToBottom()
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '会话详情加载失败')
  } finally {
    loadingDetail.value = false
  }
}

// 新对话只清空当前页面状态，不会删除数据库里的历史会话。
function startNewChat() {
  activeSessionId.value = null
  activeSessionTitle.value = ''
  form.session_id = null
  form.question = ''
  messages.value = []
}

// 删除当前用户的一条聊天会话；后端是软删除，前端从列表里移除。
async function handleDeleteSession(session: RagChatSession) {
  try {
    await ElMessageBox.confirm(`确定删除“${session.title}”吗？`, '删除会话', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })

    await deleteRagChatSession(session.id)
    sessions.value = sessions.value.filter((item) => item.id !== session.id)
    if (activeSessionId.value === session.id) startNewChat()
    ElMessage.success('会话已删除')
  } catch (error) {
    if (error === 'cancel' || error === 'close') return
    ElMessage.error(error instanceof Error ? error.message : '删除会话失败')
  }
}

// 点击快捷问题时，直接使用该问题发起一次问答。
function askQuickPrompt(prompt: string) {
  if (loading.value) return
  form.question = prompt
  void handleAsk()
}

// 发起 RAG 问答：先把用户消息显示出来，再把后端返回的助手消息落到页面上。
async function handleAsk() {
  if (loading.value) return

  const question = form.question.trim()
  if (!question) {
    ElMessage.warning('请先输入问题')
    return
  }

  const payload: RagChatPayload = {
    session_id: activeSessionId.value,
    question,
    date_from: form.date_from || undefined,
    date_to: form.date_to || undefined,
    top_k: Number(form.top_k) || 5,
  }

  const userMessage: ChatMessageView = {
    role: 'user',
    content: question,
    created_at: new Date().toISOString(),
  }
  const assistantMessage: ChatMessageView = {
    role: 'assistant',
    content: '',
    metadata: null,
    created_at: new Date().toISOString(),
  }

  messages.value.push(userMessage, assistantMessage)
  form.question = ''
  loading.value = true
  await scrollToBottom()

  try {
    if (useStream.value) {
      await streamRagChat(
        payload,
        async (content) => {
          assistantMessage.content += content
          await scrollToBottom()
        },
        (doneData) => {
          syncSessionFromDone(doneData)
          assistantMessage.metadata = {
            citations: doneData?.citations || [],
            matched_chunks: doneData?.matched_chunks || [],
          }
        },
      )
    } else {
      const result = await askRagChat(payload)
      syncSessionFromResult(result)
      assistantMessage.content = result.answer
      assistantMessage.metadata = {
        citations: result.citations,
        matched_chunks: result.matched_chunks,
      }
    }

    await loadSessions()
    await scrollToBottom()
  } catch (error) {
    assistantMessage.content = error instanceof Error ? `问答失败：${error.message}` : '问答请求失败'
    ElMessage.error(error instanceof Error ? error.message : '问答请求失败')
  } finally {
    loading.value = false
  }
}

// 把后端消息对象转成页面可直接渲染的消息对象。
function normalizeMessage(message: RagChatMessage): ChatMessageView {
  return {
    id: message.id,
    role: message.role,
    content: message.content,
    metadata: message.metadata || null,
    created_at: message.created_at,
  }
}

// 普通问答结束后，同步后端返回的会话 id 和标题。
function syncSessionFromResult(result: RagChatResult) {
  if (!result.session_id) return
  activeSessionId.value = result.session_id
  activeSessionTitle.value = result.session_title || activeSessionTitle.value
  form.session_id = result.session_id
}

// 流式问答结束后，同步后端 done 事件里的会话信息。
function syncSessionFromDone(doneData?: StreamDonePayload) {
  if (!doneData?.session_id) return
  activeSessionId.value = doneData.session_id
  activeSessionTitle.value = doneData.session_title || activeSessionTitle.value
  form.session_id = doneData.session_id
}

// 从助手消息 metadata 里取出引用来源。
function getMessageCitations(message: ChatMessageView): RagCitation[] {
  return message.metadata?.citations || []
}

// 格式化左侧历史会话的更新时间。
function formatSessionTime(value: string) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''

  const today = getLocalDateString()
  if (value.slice(0, 10) === today) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }

  return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
}

// 消息新增或流式输出时，把滚动条保持在最新回答附近。
async function scrollToBottom() {
  await nextTick()
  const element = messageScrollRef.value
  if (!element) return
  element.scrollTop = element.scrollHeight
}
</script>

<style scoped>
.rag-chat-workspace {
  display: grid;
  grid-template-columns: 286px minmax(0, 1fr);
  gap: 18px;
  min-height: calc(100dvh - 134px);
}

.chat-rail,
.chat-stage {
  min-width: 0;
  background:
    linear-gradient(180deg, rgba(255, 253, 248, 0.95), rgba(255, 250, 240, 0.88)),
    var(--nh-paper);
  border: 1px solid var(--nh-border);
  border-radius: var(--nh-radius);
  box-shadow: var(--nh-shadow);
}

.chat-rail {
  display: grid;
  grid-template-rows: auto auto auto 1fr;
  gap: 12px;
  min-height: 0;
  padding: 16px;
}

.rail-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.rail-heading strong,
.rail-heading span {
  display: block;
}

.rail-heading strong {
  color: var(--nh-ink);
  font-size: 18px;
  line-height: 1.3;
}

.rail-heading span {
  margin-top: 3px;
  color: var(--nh-muted);
  font-size: 12px;
}

.new-chat-button,
.scope-button,
.composer-ghost,
.session-delete {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 40px;
  color: #41515d;
  cursor: pointer;
  background: rgba(255, 253, 248, 0.78);
  border: 1px solid var(--nh-border);
  border-radius: var(--nh-radius);
  transition:
    background-color var(--nh-transition-fast),
    border-color var(--nh-transition-fast),
    color var(--nh-transition-fast),
    box-shadow var(--nh-transition-fast),
    transform var(--nh-transition-fast);
}

.new-chat-button {
  gap: 8px;
  width: 100%;
  font-weight: 760;
}

.new-chat-button:hover,
.scope-button:hover,
.composer-ghost:hover,
.session-delete:hover {
  color: var(--nh-primary-dark);
  background: rgba(232, 240, 235, 0.76);
  border-color: var(--nh-border-strong);
  box-shadow: 0 10px 22px rgba(84, 60, 28, 0.08);
  transform: translateY(-1px);
}

.history-search :deep(.el-input__wrapper) {
  min-height: 40px;
}

.session-list {
  display: grid;
  align-content: start;
  gap: 8px;
  min-height: 0;
  padding-right: 2px;
  overflow: auto;
}

.rail-empty {
  margin: 10px 0 0;
  color: var(--nh-muted);
  font-size: 13px;
  line-height: 1.6;
}

.session-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 36px;
  gap: 6px;
  align-items: center;
}

.session-button {
  display: grid;
  grid-template-columns: 20px minmax(0, 1fr);
  gap: 8px;
  align-items: center;
  min-height: 54px;
  padding: 9px 10px;
  color: #4b5660;
  text-align: left;
  cursor: pointer;
  background: transparent;
  border: 1px solid transparent;
  border-radius: var(--nh-radius);
}

.session-button span,
.session-button small {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.session-button span {
  font-size: 14px;
  font-weight: 700;
}

.session-button small {
  grid-column: 2;
  color: var(--nh-muted);
  font-size: 12px;
}

.session-row.is-active .session-button,
.session-button:hover {
  color: var(--nh-primary-dark);
  background: rgba(255, 253, 248, 0.84);
  border-color: var(--nh-border);
}

.session-delete {
  width: 36px;
  min-width: 36px;
  min-height: 36px;
  color: var(--nh-muted);
  opacity: 0;
}

.session-row:hover .session-delete,
.session-row.is-active .session-delete {
  opacity: 1;
}

.chat-stage {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr) auto;
  min-height: calc(100dvh - 134px);
  overflow: hidden;
}

.chat-stage-header {
  display: flex;
  gap: 16px;
  align-items: center;
  justify-content: space-between;
  min-height: 76px;
  padding: 16px 20px;
  border-bottom: 1px solid var(--nh-border);
}

.stage-kicker {
  display: block;
  margin-bottom: 5px;
  color: var(--nh-primary-dark);
  font-size: 12px;
  font-weight: 760;
}

.chat-stage-header h1 {
  max-width: min(720px, 68vw);
  margin: 0;
  overflow: hidden;
  color: #25313b;
  font-family: var(--nh-font-body);
  font-size: 20px;
  font-weight: 760;
  letter-spacing: 0;
  line-height: 1.35;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.scope-button {
  gap: 7px;
  padding: 0 13px;
  font-weight: 700;
}

.scope-popover {
  display: grid;
  gap: 12px;
}

.scope-popover label {
  display: grid;
  gap: 6px;
  color: var(--nh-muted);
  font-size: 13px;
  font-weight: 700;
}

.scope-popover :deep(.el-date-editor),
.scope-popover :deep(.el-input-number) {
  width: 100%;
}

.message-scroll {
  display: grid;
  align-content: start;
  gap: 20px;
  min-height: 0;
  padding: 28px clamp(18px, 5vw, 70px);
  overflow-y: auto;
}

.welcome-state {
  display: grid;
  gap: 14px;
  width: min(740px, 100%);
  margin: min(12vh, 96px) auto 0;
  text-align: center;
}

.welcome-state span {
  color: var(--nh-primary-dark);
  font-size: 13px;
  font-weight: 800;
}

.welcome-state h2 {
  margin: 0;
  color: #24313a;
  font-family: var(--nh-font-body);
  font-size: clamp(30px, 4vw, 44px);
  font-weight: 560;
  letter-spacing: 0;
  line-height: 1.18;
}

.welcome-state p {
  margin: 0;
  color: var(--nh-muted);
  line-height: 1.7;
}

.quick-prompts {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
  margin-top: 8px;
}

.quick-prompts button {
  min-height: 40px;
  padding: 0 14px;
  color: #40515f;
  cursor: pointer;
  background: rgba(255, 253, 248, 0.72);
  border: 1px solid var(--nh-border);
  border-radius: 999px;
  transition:
    border-color var(--nh-transition-fast),
    box-shadow var(--nh-transition-fast),
    transform var(--nh-transition-fast);
}

.quick-prompts button:hover {
  border-color: var(--nh-border-strong);
  box-shadow: 0 10px 20px rgba(84, 60, 28, 0.08);
  transform: translateY(-1px);
}

.chat-message {
  display: grid;
  grid-template-columns: 36px minmax(0, 1fr);
  gap: 12px;
  width: min(820px, 100%);
}

.chat-message.is-user {
  justify-self: end;
  width: min(720px, 100%);
}

.message-avatar {
  display: grid;
  width: 36px;
  height: 36px;
  color: var(--nh-primary-dark);
  font-size: 13px;
  font-weight: 800;
  place-items: center;
  background: rgba(232, 240, 235, 0.82);
  border: 1px solid var(--nh-border);
  border-radius: 50%;
}

.is-user .message-avatar {
  color: #5f5548;
  background: rgba(255, 253, 248, 0.9);
}

.message-bubble {
  min-width: 0;
  padding: 14px 16px;
  color: #25313b;
  background: rgba(255, 253, 248, 0.68);
  border: 1px solid transparent;
  border-radius: 16px;
}

.is-user .message-bubble {
  background: rgba(255, 253, 248, 0.94);
  border-color: var(--nh-border);
}

.message-bubble p {
  margin: 0;
  line-height: 1.78;
  white-space: pre-wrap;
  word-break: break-word;
}

.source-details {
  margin-top: 14px;
  color: var(--nh-muted);
}

.source-details summary {
  width: fit-content;
  cursor: pointer;
  font-size: 13px;
  font-weight: 760;
}

.source-list {
  display: grid;
  gap: 8px;
  margin-top: 10px;
}

.source-item {
  display: grid;
  gap: 4px;
  padding: 10px 12px;
  color: var(--nh-ink);
  background: rgba(255, 253, 248, 0.78);
  border: 1px solid var(--nh-border);
  border-radius: var(--nh-radius);
}

.source-item strong {
  line-height: 1.5;
}

.source-item span {
  color: var(--nh-muted);
  font-size: 13px;
}

.chat-composer {
  display: grid;
  gap: 10px;
  padding: 14px clamp(18px, 5vw, 70px) 18px;
  background: linear-gradient(180deg, rgba(255, 250, 240, 0.22), rgba(255, 250, 240, 0.86));
  border-top: 1px solid var(--nh-border);
}

.composer-input :deep(.el-textarea__inner) {
  min-height: 52px !important;
  padding: 14px 16px;
  color: #24313a;
  resize: none;
  background: rgba(255, 253, 248, 0.96);
  border: 1px solid var(--nh-border);
  border-radius: 18px;
  box-shadow:
    0 14px 32px rgba(84, 60, 28, 0.08),
    0 0 0 0 rgba(53, 97, 90, 0);
}

.composer-input :deep(.el-textarea__inner:focus) {
  border-color: var(--nh-primary);
  box-shadow:
    0 14px 32px rgba(84, 60, 28, 0.1),
    var(--nh-ring);
}

.composer-input :deep(.el-input__count) {
  display: none;
}

.composer-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.composer-ghost {
  gap: 7px;
  min-height: 38px;
  padding: 0 12px;
  font-weight: 720;
}

.send-button {
  min-width: 92px;
  min-height: 40px;
  border-radius: 999px;
}

@media (max-width: 1100px) {
  .rag-chat-workspace {
    grid-template-columns: 250px minmax(0, 1fr);
  }
}

@media (max-width: 900px) {
  .rag-chat-workspace {
    grid-template-columns: 1fr;
    min-height: auto;
  }

  .chat-rail {
    min-height: auto;
    max-height: 260px;
  }

  .chat-stage {
    min-height: calc(100dvh - 280px);
  }
}

@media (max-width: 620px) {
  .chat-stage-header,
  .composer-actions {
    align-items: flex-start;
    flex-direction: column;
  }

  .chat-stage-header h1 {
    max-width: 100%;
    white-space: normal;
  }

  .scope-button,
  .send-button,
  .composer-ghost {
    width: 100%;
  }

  .chat-message,
  .chat-message.is-user {
    grid-template-columns: 32px minmax(0, 1fr);
    width: 100%;
  }

  .message-avatar {
    width: 32px;
    height: 32px;
  }
}
</style>
