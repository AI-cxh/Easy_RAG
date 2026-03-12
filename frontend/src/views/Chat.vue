<template>
  <div class="chat-layout">
    <!-- 左侧固定导航栏 -->
    <nav class="nav-rail">
      <button class="nav-rail-btn" @click="toggleSidebar" title="历史记录">
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/>
        </svg>
      </button>
      <router-link to="/knowledge" class="nav-rail-btn" title="知识库管理">
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path d="M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-1 9H9V9h10v2zm-4 4H9v-2h6v2zm4-8H9V5h10v2z"/>
        </svg>
      </router-link>
      <router-link to="/settings" class="nav-rail-btn" title="设置">
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path d="M19.14 12.94c.04-.31.06-.63.06-.94 0-.31-.02-.63-.06-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.04.31-.06.63-.06.94s.02.63.06.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/>
        </svg>
      </router-link>
    </nav>

    <!-- 移动端侧边栏遮罩 -->
    <div
      v-if="sidebarOpen"
      class="sidebar-overlay"
      @click="sidebarOpen = false"
    />

    <!-- 左侧会话列表 -->
    <aside class="chat-sidebar" :class="{ open: sidebarOpen, collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <button class="btn btn-primary new-chat-btn" @click="newChat">
          <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
          </svg>
          <span class="btn-text">新对话</span>
        </button>
      </div>

      <div class="sidebar-content">
        <div v-if="loadingSessions" class="loading-state">
          <span class="spinner"></span>
        </div>

        <div v-else-if="sessions.length === 0" class="empty-sessions">
          <p>暂无对话记录</p>
        </div>

        <div v-else class="session-list">
          <div
            v-for="session in sessions"
            :key="session.id"
            :class="['session-item', { active: currentSessionId === session.id }]"
            @click="handleSelectSession(session.id)"
          >
            <div class="session-content">
              <span class="session-title">{{ session.title }}</span>
              <span class="session-time">{{ formatTime(session.created_at) }}</span>
            </div>
            <div class="session-actions" @click.stop>
              <button class="btn-icon btn-icon-sm" @click="startRename(session)" title="重命名">
                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
                </svg>
              </button>
              <button class="btn-icon btn-icon-sm delete-btn" @click="deleteSession(session.id)" title="删除">
                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </aside>

    <!-- 右侧对话区域 -->
    <main class="chat-main">
      <!-- 顶部工具栏 -->
      <header class="chat-header">
        <h1 class="header-title">Easy RAG</h1>
      </header>

      <!-- 消息区域 -->
      <div class="chat-messages" ref="messagesRef">
        <div v-if="!hasUserInteracted" class="welcome-screen">
          <div class="welcome-icon">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
            </svg>
          </div>
          <h2 class="welcome-title">欢迎使用 Easy RAG</h2>
          <p class="welcome-desc">基于知识库的智能问答助手</p>
          <div class="welcome-tips">
            <div class="tip-item">
              <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-1 9H9V9h10v2zm-4 4H9v-2h6v2zm4-8H9V5h10v2z"/>
              </svg>
              <span>上传文档构建知识库</span>
            </div>
            <div class="tip-item">
              <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
              </svg>
              <span>选择知识库进行问答</span>
            </div>
            <div class="tip-item">
              <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
              </svg>
              <span>开启网络搜索获取更多信息</span>
            </div>
          </div>
        </div>

        <div v-else class="messages-container">
          <div
            v-for="(msg, index) in messages"
            :key="index"
            :class="['message', msg.role]"
          >
            <div class="message-avatar">
              <span v-if="msg.role === 'user'">U</span>
              <svg v-else viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
              </svg>
            </div>
            <div class="message-content">
              <div class="message-text" :class="{ 'markdown': msg.role === 'assistant' }">
                <template v-if="msg.role === 'assistant'">
                  <div v-html="renderMarkdown(msg.content)"></div>
                  <span v-if="!msg.content && isSending" class="typing-indicator">
                    <span></span><span></span><span></span>
                  </span>
                </template>
                <template v-else>{{ msg.content }}</template>
              </div>
              <!-- 来源信息 -->
              <div v-if="msg.sources?.length" class="message-sources">
                <span class="sources-label">参考来源:</span>
                <span v-for="(source, i) in msg.sources" :key="i" class="source-tag">{{ source }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="chat-input-area">
        <div class="input-wrapper">
          <!-- 知识库选择 -->
          <div class="kb-selector">
            <button
              v-for="kb in knowledgeBases"
              :key="kb.id"
              :class="['kb-tag', { active: selectedKbIds.includes(kb.id) }]"
              @click="toggleKb(kb.id)"
            >
              {{ kb.name }}
            </button>
          </div>

          <!-- 输入框 -->
          <div class="input-box">
            <textarea
              v-model="inputMessage"
              class="input textarea"
              placeholder="输入消息..."
              rows="1"
              @keydown.enter.exact.prevent="handleSend"
              @input="autoResize"
              ref="inputRef"
            ></textarea>
            <div class="input-actions">
              <button
                :class="['action-btn', { active: useWebSearch }]"
                @click="useWebSearch = !useWebSearch"
                title="网络搜索"
              >
                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                </svg>
              </button>
              <button
                class="send-btn"
                :disabled="!inputMessage.trim() || isSending"
                @click="handleSend"
              >
                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { chatAPI, knowledgeAPI } from '../api/client'
import { marked } from 'marked'

// 类型定义
interface Message {
  role: 'user' | 'assistant'
  content: string
  sources?: string[]
  search_results?: Array<{ title: string; url: string; snippet?: string }>
}

interface ChatSession {
  id: number
  title: string
  created_at: string
}

// 状态
const messages = ref<Message[]>([])
const currentSessionId = ref<number>()
const sessions = ref<ChatSession[]>([])
const loadingSessions = ref(false)
const isSending = ref(false)
const hasUserInteracted = ref(false)
const sidebarOpen = ref(false)
const sidebarCollapsed = ref(false)
const messagesRef = ref<HTMLElement>()
const inputRef = ref<HTMLTextAreaElement>()

const selectedKbIds = ref<number[]>([])
const useWebSearch = ref(false)
const knowledgeBases = ref<any[]>([])
const inputMessage = ref('')

// Markdown 渲染
const renderMarkdown = (content: string) => {
  if (!content) return ''
  return marked(content)
}

// 时间格式化
const formatTime = (dateStr: string) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

// 切换侧边栏
const toggleSidebar = () => {
  // 移动端使用 sidebarOpen，桌面端使用 sidebarCollapsed
  if (window.innerWidth <= 768) {
    sidebarOpen.value = !sidebarOpen.value
  } else {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }
}

// 自动调整输入框高度
const autoResize = () => {
  if (inputRef.value) {
    inputRef.value.style.height = 'auto'
    inputRef.value.style.height = Math.min(inputRef.value.scrollHeight, 150) + 'px'
  }
}

// 本地存储
const loadSavedState = () => {
  const saved = localStorage.getItem('chatState')
  if (saved) {
    const state = JSON.parse(saved)
    messages.value = state.messages || []
    currentSessionId.value = state.sessionId
    selectedKbIds.value = state.selectedKbIds || []
    useWebSearch.value = state.useWebSearch || false
    hasUserInteracted.value = state.hasUserInteracted || false
  }
}

const saveState = () => {
  localStorage.setItem('chatState', JSON.stringify({
    messages: messages.value,
    sessionId: currentSessionId.value,
    selectedKbIds: selectedKbIds.value,
    useWebSearch: useWebSearch.value,
    hasUserInteracted: hasUserInteracted.value
  }))
}

// 加载数据
const loadSessions = async () => {
  loadingSessions.value = true
  try {
    const result = await chatAPI.getSessions()
    sessions.value = result.sessions || result || []
  } catch (error) {
    console.error('Failed to load sessions:', error)
  } finally {
    loadingSessions.value = false
  }
}

const loadKnowledgeBases = async () => {
  try {
    knowledgeBases.value = await knowledgeAPI.getAll()
  } catch (error) {
    console.error('Failed to load knowledge bases:', error)
  }
}

// 会话操作
const handleSelectSession = async (sessionId: number) => {
  await loadSession(sessionId)
  sidebarOpen.value = false
}

const loadSession = async (sessionId: number) => {
  try {
    const result = await chatAPI.getSession(sessionId)
    currentSessionId.value = sessionId
    messages.value = result.messages || []
    hasUserInteracted.value = messages.value.length > 0
    saveState()
  } catch (error) {
    console.error('Failed to load session:', error)
  }
}

const deleteSession = async (sessionId: number) => {
  if (!confirm('确定要删除该对话吗？')) return

  try {
    await chatAPI.deleteSession(sessionId)
    if (currentSessionId.value === sessionId) {
      currentSessionId.value = undefined
      messages.value = []
      hasUserInteracted.value = false
    }
    await loadSessions()
    saveState()
  } catch (error) {
    console.error('Failed to delete session:', error)
  }
}

const startRename = (session: ChatSession) => {
  const newTitle = prompt('重命名对话', session.title)
  if (newTitle && newTitle.trim()) {
    renameSession(session.id, newTitle.trim())
  }
}

const renameSession = async (sessionId: number, title: string) => {
  try {
    await chatAPI.renameSession(sessionId, title)
    await loadSessions()
  } catch (error) {
    console.error('Failed to rename session:', error)
  }
}

const newChat = () => {
  currentSessionId.value = undefined
  messages.value = []
  hasUserInteracted.value = false
  sidebarOpen.value = false
  saveState()
}

// 知识库操作
const toggleKb = (kbId: number) => {
  if (selectedKbIds.value.includes(kbId)) {
    selectedKbIds.value = selectedKbIds.value.filter(id => id !== kbId)
  } else {
    selectedKbIds.value.push(kbId)
  }
  saveState()
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

// 发送消息
const handleSend = async () => {
  const message = inputMessage.value.trim()
  if (!message || isSending.value) return

  inputMessage.value = ''
  autoResize()
  hasUserInteracted.value = true

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: message
  })
  saveState()
  scrollToBottom()

  isSending.value = true

  try {
    // 添加空的助手消息用于流式更新
    const assistantIndex = messages.value.length
    messages.value.push({
      role: 'assistant',
      content: '',
      sources: undefined,
      search_results: undefined
    })
    scrollToBottom()

    const result = await chatAPI.sendMessageStream(
      {
        message,
        session_id: currentSessionId.value,
        kb_ids: selectedKbIds.value,
        use_web_search: useWebSearch.value
      },
      (chunk) => {
        if (chunk.type === 'chunk' && chunk.content) {
          messages.value[assistantIndex].content += chunk.content
          scrollToBottom()
        } else if (chunk.type === 'error') {
          console.error('Stream error:', chunk.message)
          messages.value[assistantIndex].content = '抱歉，发生了错误，请稍后重试。'
        }
      }
    )

    currentSessionId.value = result.sessionId
    messages.value[assistantIndex].sources = result.sources
    messages.value[assistantIndex].search_results = result.searchResults
    saveState()

    await loadSessions()
  } catch (error) {
    console.error('Chat error:', error)
    messages.value.push({
      role: 'assistant',
      content: '抱歉，发生了错误，请稍后重试。'
    })
  } finally {
    isSending.value = false
  }
}

// 初始化
onMounted(() => {
  loadSavedState()
  loadSessions()
  loadKnowledgeBases()
})
</script>

<style scoped>
.chat-layout {
  display: flex;
  height: 100vh;
  background: var(--bg-primary);
}

/* 左侧固定导航栏 */
.nav-rail {
  width: 56px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-3) 0;
  gap: var(--space-2);
  flex-shrink: 0;
}

.nav-rail-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--duration-fast);
  text-decoration: none;
  position: relative;
}

.nav-rail-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.nav-rail-btn.router-link-active {
  color: var(--color-primary);
  background: var(--color-primary-light);
}

.nav-rail-btn svg {
  width: 22px;
  height: 22px;
  fill: currentColor;
}

/* 侧边栏 */
.chat-sidebar {
  width: 280px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  transition: width var(--duration-normal) var(--ease-out);
}

.chat-sidebar.collapsed {
  width: 0;
  border-right: none;
  overflow: hidden;
}

.sidebar-header {
  padding: var(--space-4);
}

.new-chat-btn {
  width: 100%;
  justify-content: center;
  gap: var(--space-2);
}

.new-chat-btn svg {
  width: 18px;
  height: 18px;
  fill: currentColor;
  flex-shrink: 0;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 0 var(--space-2);
}

.loading-state {
  display: flex;
  justify-content: center;
  padding: var(--space-8);
}

.empty-sessions {
  text-align: center;
  padding: var(--space-8);
  color: var(--text-muted);
  font-size: var(--text-sm);
}

.session-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.session-item {
  display: flex;
  align-items: center;
  padding: var(--space-3);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--duration-fast);
}

.session-item:hover {
  background: var(--bg-hover);
}

.session-item.active {
  background: var(--color-primary-light);
}

.session-content {
  flex: 1;
  min-width: 0;
}

.session-title {
  display: block;
  font-size: var(--text-sm);
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.session-time {
  font-size: var(--text-xs);
  color: var(--text-muted);
}

.session-actions {
  display: flex;
  gap: var(--space-1);
  opacity: 0;
  transition: opacity var(--duration-fast);
}

.session-item:hover .session-actions {
  opacity: 1;
}

.delete-btn:hover {
  color: var(--color-danger);
}

/* 主内容区 */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.chat-header {
  height: 56px;
  padding: 0 var(--space-4);
  display: flex;
  align-items: center;
  border-bottom: 1px solid var(--border-subtle);
  background: var(--bg-secondary);
}

.header-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0;
}

.header-spacer {
  width: 32px;
}

/* 消息区域 */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-6);
}

.welcome-screen {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  padding: var(--space-8);
}

.welcome-icon {
  width: 64px;
  height: 64px;
  background: var(--color-primary-light);
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--space-5);
}

.welcome-icon svg {
  width: 32px;
  height: 32px;
  fill: var(--color-primary);
}

.welcome-title {
  font-size: var(--text-2xl);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-2);
}

.welcome-desc {
  font-size: var(--text-base);
  color: var(--text-secondary);
  margin: 0 0 var(--space-8);
}

.welcome-tips {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.tip-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.tip-item svg {
  width: 20px;
  height: 20px;
  fill: var(--color-primary);
  flex-shrink: 0;
}

.messages-container {
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
}

.message {
  display: flex;
  gap: var(--space-3);
  margin-bottom: var(--space-6);
}

.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
}

.message.user .message-avatar {
  background: var(--color-primary);
  color: white;
}

.message.assistant .message-avatar {
  background: var(--bg-tertiary);
}

.message.assistant .message-avatar svg {
  width: 18px;
  height: 18px;
  fill: var(--text-secondary);
}

.message-content {
  flex: 1;
  min-width: 0;
}

.message-text {
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-lg);
  font-size: var(--text-sm);
  line-height: 1.6;
}

.message.user .message-text {
  background: var(--color-primary);
  color: white;
}

.message.assistant .message-text {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.message-sources {
  margin-top: var(--space-2);
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  align-items: center;
}

.sources-label {
  font-size: var(--text-xs);
  color: var(--text-muted);
}

.source-tag {
  font-size: var(--text-xs);
  padding: var(--space-1) var(--space-2);
  background: var(--bg-tertiary);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
}

/* 打字指示器 */
.typing-indicator {
  display: inline-flex;
  gap: 4px;
  padding: var(--space-1);
}

.typing-indicator span {
  width: 6px;
  height: 6px;
  background: var(--text-muted);
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

/* 输入区域 */
.chat-input-area {
  padding: var(--space-4) var(--space-6) var(--space-6);
}

.input-wrapper {
  max-width: 800px;
  margin: 0 auto;
}

.kb-selector {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  margin-bottom: var(--space-3);
}

.kb-tag {
  padding: var(--space-1) var(--space-3);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  background: var(--bg-tertiary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-full);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--duration-fast);
}

.kb-tag:hover {
  border-color: var(--border-strong);
  color: var(--text-primary);
}

.kb-tag.active {
  background: var(--color-primary-light);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.input-box {
  display: flex;
  align-items: flex-end;
  gap: var(--space-2);
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-xl);
  padding: var(--space-2) var(--space-3);
  transition: border-color var(--duration-fast);
}

.input-box:focus-within {
  border-color: var(--color-primary);
}

.input-box .textarea {
  flex: 1;
  background: transparent;
  border: none;
  padding: var(--space-1);
  resize: none;
}

.input-box .textarea:focus {
  box-shadow: none;
}

.input-actions {
  display: flex;
  align-items: center;
  gap: var(--space-1);
}

.action-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  color: var(--text-muted);
  cursor: pointer;
  transition: all var(--duration-fast);
}

.action-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.action-btn.active {
  color: var(--color-primary);
}

.action-btn svg {
  width: 18px;
  height: 18px;
  fill: currentColor;
}

.send-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary);
  border: none;
  border-radius: var(--radius-md);
  color: white;
  cursor: pointer;
  transition: all var(--duration-fast);
}

.send-btn:hover:not(:disabled) {
  background: var(--color-primary-hover);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-btn svg {
  width: 18px;
  height: 18px;
  fill: currentColor;
}

/* 移动端 */
.sidebar-overlay {
  display: none;
}

@media (max-width: 768px) {
  .nav-rail {
    width: 48px;
  }

  .nav-rail-btn {
    width: 36px;
    height: 36px;
  }

  .nav-rail-btn svg {
    width: 20px;
    height: 20px;
  }

  .chat-sidebar {
    position: fixed;
    left: 48px;
    top: 0;
    bottom: 0;
    z-index: var(--z-modal);
    transform: translateX(-100%);
    transition: transform var(--duration-normal) var(--ease-out);
    width: 280px;
    border-right: 1px solid var(--border-subtle);
  }

  .chat-sidebar.open {
    transform: translateX(0);
  }

  /* 移动端忽略折叠状态 */
  .chat-sidebar.collapsed {
    width: 280px;
    border-right: 1px solid var(--border-subtle);
  }

  .sidebar-overlay {
    display: block;
    position: fixed;
    inset: 0;
    left: 48px;
    background: rgba(0, 0, 0, 0.5);
    z-index: calc(var(--z-modal) - 1);
  }

  .chat-messages {
    padding: var(--space-4);
  }

  .chat-input-area {
    padding: var(--space-3) var(--space-4) var(--space-4);
  }
}
</style>
