import type { LoginPayload, LoginResult, RegisterPayload, UserInfo } from '@/types/auth'
import type { DashboardOverview } from '@/types/dashboard'
import type { NewsItem, NewsPayload } from '@/types/news'
import type { TopicItem, TopicPayload, TopicStatus } from '@/types/topic'
import type { CategoryItem, TagItem } from '@/types/taxonomy'
import type { PageResult } from '@/types/common'
import type { AIDigestRunPayload, AIDigestRunResult } from '@/types/aiDigest'
import type {
  DailyDigestRunPayload as RagDailyDigestRunPayload,
  DailyDigestRunResult as RagDailyDigestRunResult,
  KnowledgeDocumentDetail,
  RagChatMessage,
  RagChatPayload,
  RagChatResult,
  RagChatSession,
  RagChatSessionDetail,
} from '@/types/rag'

const mockUser: UserInfo = {
  id: 1,
  username: 'demo',
  email: 'demo@ai-newshub.local',
  nickname: '演示用户',
  role: 'admin',
  is_active: true,
  created_at: '2026-04-28T10:00:00',
}

const categories: CategoryItem[] = [
  { id: 1, name: '大模型', description: '模型发布、能力更新和评测', sort_order: 1, is_active: true },
  { id: 2, name: 'AI 绘画', description: '图像、视频和设计工具', sort_order: 2, is_active: true },
  { id: 3, name: 'Agent', description: '智能体、自动化和编程助手', sort_order: 3, is_active: true },
  { id: 4, name: '开源项目', description: 'GitHub 与社区项目动态', sort_order: 4, is_active: true },
]

const tags: TagItem[] = [
  { id: 1, name: 'OpenAI' },
  { id: 2, name: 'DeepSeek' },
  { id: 3, name: '多模态' },
  { id: 4, name: '开源' },
  { id: 5, name: 'API 降价' },
]

let newsList: NewsItem[] = [
  {
    id: 1,
    title: 'DeepSeek 发布新一代推理模型，成本与性能再次成为焦点',
    source_name: 'DeepSeek 官方',
    source_url: 'https://example.com/deepseek',
    summary: '新模型在推理能力、接口价格和中文场景表现上都有明显提升，适合持续跟进。',
    content: '{\n  "note": "可以从国产 AI、成本下降、开发者生态三个角度分析",\n  "risk": "注意核对官方 benchmark"\n}',
    category: { id: 1, name: '大模型' },
    tags: [tags[1], tags[2], tags[4]],
    status: 'unread',
    importance_score: 5,
    heat_score: 5,
    is_favorite: true,
    publish_time: '2026-04-28T09:30:00',
    created_at: '2026-04-28T12:00:00',
  },
  {
    id: 2,
    title: '某开源 Agent 框架新增浏览器自动化能力',
    source_name: 'GitHub Trending',
    source_url: 'https://example.com/agent',
    summary: '项目新增网页操作、任务规划和工具调用示例，适合做开发者向选题。',
    content: '这类内容可以整理成“如何判断一个 Agent 框架是否值得使用”的实用文章。',
    category: { id: 3, name: 'Agent' },
    tags: [tags[3]],
    status: 'read',
    importance_score: 4,
    heat_score: 4,
    is_favorite: false,
    publish_time: '2026-04-27T18:20:00',
    created_at: '2026-04-28T11:00:00',
  },
  {
    id: 3,
    title: 'AI 视频工具更新角色一致性功能',
    source_name: 'Product Blog',
    summary: '角色一致性、镜头控制和批量生成能力增强，面向内容创作者很有传播潜力。',
    content: '可以对比传统剪辑流程，突出创作者工作流变化。',
    category: { id: 2, name: 'AI 绘画' },
    tags: [tags[2]],
    status: 'added_to_topic',
    importance_score: 3,
    heat_score: 5,
    is_favorite: false,
    publish_time: '2026-04-26T15:00:00',
    created_at: '2026-04-27T10:30:00',
  },
]

let topicList: TopicItem[] = [
  {
    id: 1,
    news: { id: 1, title: newsList[0].title },
    title: 'DeepSeek 新模型为什么值得普通人关注？',
    recommended_title: 'DeepSeek 这次，把 AI 使用成本又往下压了一截',
    angle: '从成本下降、国产 AI 生态和普通用户可感知变化三个角度写。',
    reason: '既有技术热度，也能落到普通用户和内容创作者的使用场景。',
    target_reader: 'AI 工具用户、大学生、科技公众号读者',
    category: { id: 1, name: '大模型' },
    status: 'pending',
    value_score: 5,
    difficulty_score: 3,
    traffic_score: 5,
    deadline: '2026-05-01T20:00:00',
    created_at: '2026-04-28T12:30:00',
  },
  {
    id: 2,
    title: 'Agent 框架进入浏览器：自动化真的更近了吗？',
    recommended_title: '让 AI 自己点网页，离普通人还有多远？',
    angle: '解释浏览器自动化能做什么、不能做什么，以及真实落地阻碍。',
    reason: '适合做一篇兼具科普和工具判断的方法论文章。',
    target_reader: '开发者、AI 产品经理、效率工具用户',
    category: { id: 3, name: 'Agent' },
    status: 'writing',
    value_score: 4,
    difficulty_score: 4,
    traffic_score: 4,
    deadline: '2026-05-03T20:00:00',
    created_at: '2026-04-28T13:20:00',
  },
]

const knowledgeDocuments: KnowledgeDocumentDetail[] = [
  {
    id: 1,
    title: 'OpenAI 兼容接口生态继续扩张',
    summary: '越来越多第三方模型服务采用 OpenAI-compatible API，方便开发者复用同一套调用逻辑。',
    source_name: 'Reserved Source',
    source_url: 'https://example.com/openai-compatible',
    published_at: '2026-06-03T09:30:00',
    digest_date: '2026-06-03',
    credibility: 'medium',
    content: '这条示例文档用于演示 RAG 知识库列表和详情页。真实后端完成后，正文会来自固定抓取 skill 的结果。',
    chunks: [
      {
        id: 1,
        chunk_index: 0,
        chunk_text: 'OpenAI-compatible API 让不同模型供应商可以共用相近的请求格式。',
      },
      {
        id: 2,
        chunk_index: 1,
        chunk_text: '对本项目来说，这意味着用户填入 Base URL、API Key 和模型名后，就能切换第三方大模型。',
      },
    ],
  },
  {
    id: 2,
    title: 'RAG 成为资讯沉淀的常见方案',
    summary: '抓取后的资讯不再只作为列表展示，而是被切分为 chunk，供后续问答和选题推荐检索。',
    source_name: 'AI NewsHub Demo',
    published_at: '2026-06-03T11:00:00',
    digest_date: '2026-06-03',
    credibility: 'high',
    content: 'RAG 的核心是先检索可信资料，再让模型基于资料回答，降低凭空编造的风险。',
    chunks: [
      {
        id: 3,
        chunk_index: 0,
        chunk_text: 'RAG 问答应返回引用来源，让用户知道答案来自哪一天、哪条资讯。',
      },
    ],
  },
]

let ragChatSessions: RagChatSession[] = [
  {
    id: 1,
    title: '今天有哪些重要 AI 消息？',
    created_at: '2026-06-03T11:30:00',
    updated_at: '2026-06-03T11:34:00',
  },
]

type MockRagChatMessage = RagChatMessage & { session_id: number }

let ragChatMessages: MockRagChatMessage[] = [
  {
    id: 1,
    session_id: 1,
    role: 'user',
    content: '今天有哪些重要 AI 消息？',
    created_at: '2026-06-03T11:30:00',
  },
  {
    id: 2,
    session_id: 1,
    role: 'assistant',
    content: '演示回答：今天可以重点关注 OpenAI-compatible 接口生态和 RAG 资讯沉淀方案。',
    metadata: {
      citations: [
        {
          document_id: 1,
          title: knowledgeDocuments[0].title,
          source_name: knowledgeDocuments[0].source_name,
          source_url: knowledgeDocuments[0].source_url,
          digest_date: knowledgeDocuments[0].digest_date,
        },
      ],
      matched_chunks: knowledgeDocuments[0].chunks.map((chunk) => ({
        chunk_id: chunk.id,
        document_id: knowledgeDocuments[0].id,
        chunk_text: chunk.chunk_text,
        score: 0.82,
      })),
    },
    created_at: '2026-06-03T11:34:00',
  },
]

export function isMockMode() {
  return localStorage.getItem('ai_newshub_mock') === '1'
}

export async function mockRequest<T>(method: string, url: string, data?: unknown, params?: Record<string, unknown>): Promise<T> {
  await new Promise((resolve) => window.setTimeout(resolve, 180))

  if (url === '/auth/login' && method === 'POST') return mockLogin(data as LoginPayload) as T
  if (url === '/auth/register' && method === 'POST') return mockRegister(data as RegisterPayload) as T
  if (url === '/auth/me' && method === 'GET') return mockUser as T
  if (url === '/categories' && method === 'GET') return categories as T
  if (url === '/tags' && method === 'GET') return tags as T
  if (url === '/dashboard/overview' && method === 'GET') return mockDashboard() as T
  if (url === '/news' && method === 'GET') return pageResult(filterNews(params), params) as T
  if (url === '/news' && method === 'POST') return addNews(data as NewsPayload) as T
  if (url === '/topics' && method === 'GET') return pageResult(filterTopics(params), params) as T
  if (url === '/topics' && method === 'POST') return addTopic(data as TopicPayload) as T
  if (url === '/ai-digest/runs' && method === 'POST') return mockAIDigestRun(data as AIDigestRunPayload) as T
  if (url === '/daily-digest/runs' && method === 'POST') return mockDailyDigestRun(data as RagDailyDigestRunPayload) as T
  if (url === '/knowledge/documents' && method === 'GET') return pageResult(filterKnowledgeDocuments(params), params) as T
  if (url === '/rag-chat/sessions' && method === 'GET') return getMockRagChatSessions() as T
  if (url === '/rag-chat/ask' && method === 'POST') return mockRagChatAnswer(data as RagChatPayload) as T

  const newsDetailMatch = url.match(/^\/news\/(\d+)$/)
  if (newsDetailMatch && method === 'GET') return findNews(Number(newsDetailMatch[1])) as T
  if (newsDetailMatch && method === 'PUT') return updateMockNews(Number(newsDetailMatch[1]), data as NewsPayload) as T
  if (newsDetailMatch && method === 'DELETE') {
    newsList = newsList.filter((item) => item.id !== Number(newsDetailMatch[1]))
    return null as T
  }

  const favoriteMatch = url.match(/^\/news\/(\d+)\/favorite$/)
  if (favoriteMatch && method === 'PATCH') return updateFavorite(Number(favoriteMatch[1]), data as { is_favorite: boolean }) as T

  const toTopicMatch = url.match(/^\/news\/(\d+)\/to-topic$/)
  if (toTopicMatch && method === 'POST') return addTopic({ ...(data as TopicPayload), news_id: Number(toTopicMatch[1]) }) as T

  const topicDetailMatch = url.match(/^\/topics\/(\d+)$/)
  if (topicDetailMatch && method === 'GET') return findTopic(Number(topicDetailMatch[1])) as T
  if (topicDetailMatch && method === 'PUT') return updateMockTopic(Number(topicDetailMatch[1]), data as TopicPayload) as T
  if (topicDetailMatch && method === 'DELETE') {
    topicList = topicList.filter((item) => item.id !== Number(topicDetailMatch[1]))
    return null as T
  }

  const topicStatusMatch = url.match(/^\/topics\/(\d+)\/status$/)
  if (topicStatusMatch && method === 'PATCH') return updateMockTopicStatus(Number(topicStatusMatch[1]), data as { status: TopicStatus }) as T

  const knowledgeDetailMatch = url.match(/^\/knowledge\/documents\/(\d+)$/)
  if (knowledgeDetailMatch && method === 'GET') return findKnowledgeDocument(Number(knowledgeDetailMatch[1])) as T

  const ragSessionMatch = url.match(/^\/rag-chat\/sessions\/(\d+)$/)
  if (ragSessionMatch && method === 'GET') return getMockRagChatSessionDetail(Number(ragSessionMatch[1])) as T
  if (ragSessionMatch && method === 'DELETE') {
    deleteMockRagChatSession(Number(ragSessionMatch[1]))
    return null as T
  }

  throw new Error(`演示模式暂未覆盖接口：${method} ${url}`)
}

function mockLogin(_payload: LoginPayload): LoginResult {
  return {
    access_token: 'demo-token',
    token_type: 'bearer',
    user: mockUser,
  }
}

function mockRegister(payload: RegisterPayload): UserInfo {
  return {
    ...mockUser,
    username: payload.username,
    email: payload.email,
  }
}

function mockDashboard(): DashboardOverview {
  return {
    news_total: newsList.length,
    unread_news_total: newsList.filter((item) => item.status === 'unread').length,
    favorite_news_total: newsList.filter((item) => item.is_favorite).length,
    topic_total: topicList.length,
    pending_topic_total: topicList.filter((item) => item.status === 'pending').length,
    writing_topic_total: topicList.filter((item) => item.status === 'writing').length,
    published_topic_total: topicList.filter((item) => item.status === 'published').length,
    recent_news: newsList.slice(0, 5).map((item) => ({
      id: item.id,
      title: item.title,
      status: item.status,
      created_at: item.created_at || '',
    })),
    recent_topics: topicList.slice(0, 5).map((item) => ({
      id: item.id,
      title: item.title,
      status: item.status,
      created_at: item.created_at || '',
    })),
  }
}

function mockAIDigestRun(payload: AIDigestRunPayload): AIDigestRunResult {
  const selectedCategories = categories.filter((category) => payload.category_ids.includes(category.id))
  const firstCategory = selectedCategories[0] || categories[0]

  return {
    run_id: `demo-${Date.now()}`,
    status: 'reserved',
    message: '演示模式已收到抓取配置，真实抓取逻辑等待后端实现',
    received_items: 3,
    created_news_count: payload.dry_run ? 0 : 3,
    created_topic_count: payload.create_topics && !payload.dry_run ? 2 : 0,
    skipped_count: 0,
    failed_sources: [],
    preview_items: [
      {
        title: 'OpenAI 兼容模型接口更新带来新的内容自动化机会',
        source_name: '官方/媒体候选',
        source_url: 'https://example.com/openai-compatible-news',
        matched_category: firstCategory ? { id: firstCategory.id, name: firstCategory.name } : null,
        importance_score: 4,
        heat_score: 4,
        one_line_summary: '后端实现后，这类候选会由抓取工作流自动去重、评分并匹配分类。',
      },
      {
        title: 'GitHub 热门 AI Agent 项目持续活跃',
        source_name: 'GitHub Trending',
        matched_category: selectedCategories.find((category) => category.name.includes('Agent')) || firstCategory || null,
        importance_score: 4,
        heat_score: 5,
        one_line_summary: '适合转成开发者向选题，前端会展示后端返回的预览与入库统计。',
      },
      {
        title: '国内大模型产品更新进入内容创作视野',
        source_name: '可靠中文源候选',
        matched_category: firstCategory ? { id: firstCategory.id, name: firstCategory.name } : null,
        importance_score: 5,
        heat_score: 4,
        one_line_summary: '可由后端根据现有分类、标签和评分规则自动生成资讯记录。',
      },
    ],
  }
}

function mockDailyDigestRun(payload: RagDailyDigestRunPayload): RagDailyDigestRunResult {
  const digestDate = payload.digest_date || new Date().toISOString().slice(0, 10)

  return {
    run_id: `demo-rag-${Date.now()}`,
    status: 'reserved',
    digest_date: digestDate,
    message: payload.dry_run ? '演示模式：本次只预览，不写入知识库' : '演示模式：模拟写入知识库完成',
    collected_count: 2,
    document_count: payload.dry_run ? 0 : 2,
    chunk_count: payload.dry_run ? 0 : 3,
    failed_sources: [],
    preview_items: knowledgeDocuments.slice(0, 2).map((item) => ({
      title: item.title,
      summary: item.summary,
      source_name: item.source_name,
      source_url: item.source_url,
      published_at: item.published_at,
      credibility: item.credibility,
    })),
  }
}

function filterKnowledgeDocuments(params?: Record<string, unknown>) {
  const keyword = String(params?.keyword || '').toLowerCase()
  return knowledgeDocuments.filter((item) => {
    const matchDate = !params?.digest_date || item.digest_date === params.digest_date
    const matchKeyword =
      !keyword ||
      [item.title, item.summary, item.source_name, item.content]
        .some((value) => value?.toLowerCase().includes(keyword))
    return matchDate && matchKeyword
  })
}

function findKnowledgeDocument(id: number) {
  const item = knowledgeDocuments.find((document) => document.id === id)
  if (!item) throw new Error('演示知识文档不存在')
  return item
}

function getMockRagChatSessions() {
  return [...ragChatSessions].sort((left, right) => right.updated_at.localeCompare(left.updated_at))
}

function getMockRagChatSessionDetail(sessionId: number): RagChatSessionDetail {
  const session = ragChatSessions.find((item) => item.id === sessionId)
  if (!session) throw new Error('演示聊天会话不存在')

  const messages = ragChatMessages
    .filter((message) => message.session_id === sessionId)
    .map((message) => {
      const { session_id: _sessionId, ...publicMessage } = message
      return publicMessage
    })

  return {
    ...session,
    messages,
  }
}

function deleteMockRagChatSession(sessionId: number) {
  const exists = ragChatSessions.some((item) => item.id === sessionId)
  if (!exists) throw new Error('演示聊天会话不存在')

  ragChatSessions = ragChatSessions.filter((item) => item.id !== sessionId)
}

function buildMockSessionTitle(question: string) {
  const title = question.replace(/\s+/g, ' ').trim()
  return title.length > 28 ? `${title.slice(0, 28)}...` : title || '新的 AI 问答'
}

function getOrCreateMockRagSession(payload: RagChatPayload) {
  const sessionId = payload.session_id || undefined
  const oldSession = sessionId ? ragChatSessions.find((item) => item.id === sessionId) : undefined
  if (oldSession) return oldSession

  const now = new Date().toISOString()
  const session: RagChatSession = {
    id: Date.now(),
    title: buildMockSessionTitle(payload.question),
    created_at: now,
    updated_at: now,
  }
  ragChatSessions.unshift(session)
  return session
}

function mockRagChatAnswer(payload: RagChatPayload): RagChatResult {
  const firstDocument = knowledgeDocuments[0]
  const session = getOrCreateMockRagSession(payload)
  const now = new Date().toISOString()
  const citations = [
    {
      document_id: firstDocument.id,
      title: firstDocument.title,
      source_name: firstDocument.source_name,
      source_url: firstDocument.source_url,
      digest_date: firstDocument.digest_date,
    },
  ]
  const matchedChunks = firstDocument.chunks.map((chunk) => ({
    chunk_id: chunk.id,
    document_id: firstDocument.id,
    chunk_text: chunk.chunk_text,
    score: 0.82,
  }))
  const answer = `演示回答：你问的是“${payload.question}”。真实后端会先按日期范围检索 RAG chunk，再把命中的资料交给大模型回答。`

  ragChatMessages.push(
    {
      id: Date.now(),
      session_id: session.id,
      role: 'user',
      content: payload.question,
      created_at: now,
    },
    {
      id: Date.now() + 1,
      session_id: session.id,
      role: 'assistant',
      content: answer,
      metadata: {
        citations,
        matched_chunks: matchedChunks,
      },
      created_at: now,
    },
  )
  session.updated_at = now

  return {
    session_id: session.id,
    session_title: session.title,
    answer,
    citations,
    matched_chunks: matchedChunks,
  }
}

function pageResult<T>(items: T[], params?: Record<string, unknown>): PageResult<T> {
  const page = Number(params?.page || 1)
  const pageSize = Number(params?.page_size || 10)
  const start = (page - 1) * pageSize
  return {
    items: items.slice(start, start + pageSize),
    total: items.length,
    page,
    page_size: pageSize,
    pages: Math.max(1, Math.ceil(items.length / pageSize)),
  }
}

function filterNews(params?: Record<string, unknown>) {
  const keyword = String(params?.keyword || '').toLowerCase()
  return newsList.filter((item) => {
    const matchKeyword = !keyword || [item.title, item.summary, item.source_name].some((value) => value?.toLowerCase().includes(keyword))
    const matchCategory = !params?.category_id || item.category?.id === Number(params.category_id)
    const matchStatus = !params?.status || item.status === params.status
    const matchFavorite = params?.is_favorite === undefined || item.is_favorite === params.is_favorite
    return matchKeyword && matchCategory && matchStatus && matchFavorite
  })
}

function filterTopics(params?: Record<string, unknown>) {
  const keyword = String(params?.keyword || '').toLowerCase()
  return topicList.filter((item) => {
    const matchKeyword = !keyword || [item.title, item.angle, item.recommended_title].some((value) => value?.toLowerCase().includes(keyword))
    const matchCategory = !params?.category_id || item.category?.id === Number(params.category_id)
    const matchStatus = !params?.status || item.status === params.status
    return matchKeyword && matchCategory && matchStatus
  })
}

function findNews(id: number) {
  const item = newsList.find((news) => news.id === id)
  if (!item) throw new Error('演示资讯不存在')
  return item
}

function findTopic(id: number) {
  const item = topicList.find((topic) => topic.id === id)
  if (!item) throw new Error('演示选题不存在')
  return item
}

function addNews(payload: NewsPayload) {
  const category = categories.find((item) => item.id === payload.category_id)
  const item: NewsItem = {
    id: Date.now(),
    title: payload.title,
    source_name: payload.source_name,
    source_url: payload.source_url,
    summary: payload.summary,
    content: payload.content,
    category: category ? { id: category.id, name: category.name } : null,
    tags: tags.filter((tag) => payload.tag_ids?.includes(tag.id)),
    status: payload.status || 'unread',
    importance_score: payload.importance_score || 3,
    heat_score: payload.heat_score || 3,
    is_favorite: false,
    publish_time: payload.publish_time,
    created_at: new Date().toISOString(),
  }
  newsList.unshift(item)
  return item
}

function updateMockNews(id: number, payload: NewsPayload) {
  const oldItem = findNews(id)
  const category = categories.find((item) => item.id === payload.category_id)
  Object.assign(oldItem, {
    ...payload,
    category: category ? { id: category.id, name: category.name } : null,
    tags: tags.filter((tag) => payload.tag_ids?.includes(tag.id)),
    updated_at: new Date().toISOString(),
  })
  return oldItem
}

function updateFavorite(id: number, payload: { is_favorite: boolean }) {
  const item = findNews(id)
  item.is_favorite = payload.is_favorite
  return { id, is_favorite: item.is_favorite }
}

function addTopic(payload: TopicPayload) {
  const news = payload.news_id ? findNews(payload.news_id) : undefined
  const category = categories.find((item) => item.id === payload.category_id)
  const item: TopicItem = {
    id: Date.now(),
    news: news ? { id: news.id, title: news.title } : null,
    title: payload.title,
    angle: payload.angle,
    recommended_title: payload.recommended_title,
    reason: payload.reason,
    target_reader: payload.target_reader,
    category: category ? { id: category.id, name: category.name } : null,
    status: payload.status || 'pending',
    value_score: payload.value_score || 3,
    difficulty_score: payload.difficulty_score || 3,
    traffic_score: payload.traffic_score || 3,
    deadline: payload.deadline,
    created_at: new Date().toISOString(),
  }
  topicList.unshift(item)
  if (news) news.status = 'added_to_topic'
  return item
}

function updateMockTopic(id: number, payload: TopicPayload) {
  const item = findTopic(id)
  const category = categories.find((categoryItem) => categoryItem.id === payload.category_id)
  Object.assign(item, {
    ...payload,
    category: category ? { id: category.id, name: category.name } : null,
    updated_at: new Date().toISOString(),
  })
  return item
}

function updateMockTopicStatus(id: number, payload: { status: TopicStatus }) {
  const item = findTopic(id)
  item.status = payload.status
  return { id, status: item.status }
}
