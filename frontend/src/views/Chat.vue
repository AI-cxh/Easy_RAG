<template>
  <div class="chat-page">
    <!-- 左侧对话历史列表 -->
    <div class="sidebar">
      <div class="sidebar-header">
        <h2>对话历史</h2>
        <button class="btn-icon" @click="toggleNewChat" title="开启新对话">
          <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
          </svg>
        </button>
      </div>
      <div v-if="loadingSessions" class="loading">
        <span class="spinner"></span>
      </div>
      <div v-else class="session-list">
        <div
          v-for="session in sessions"
          :key="session.id"
          :class="['session-item', { 'active': currentSessionId === session.id }]"
          @click="loadSession(session.id)"
        >
          <div class="session-title">{{ session.title }}</div>
          <div class="session-meta">
            {{ formatDate(session.created_at) }}
          </div>
          <button class="btn-icon delete-session" @click.stop="deleteSession(session.id)">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
            </svg>
          </button>
        </div>
        <div v-if="sessions.length === 0" class="empty-sessions">
          暂无对话历史
        </div>
      </div>
    </div>

    <!-- 右侧对话区域 -->
    <div class="chat-area">
      <div class="chat-header">
        <h1 class="chat-title">布妞 - 您的私人助手</h1>
      </div>

      <!-- 消息列表 -->
      <div class="messages-container">
        <div class="welcome-message" v-if="messages.length === 0 && !hasUserInteracted">
          <div class="avatar avatar-large assistant-avatar">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
          </div>
          <p class="welcome-text">您好，我是您的私人助手布妞，可通过上传文件或联网搜索为您解答问题。</p>
        </div>

        <MessageList :messages="messages" />
      </div>

      <!-- 输入区域 -->
      <div class="input-area">
        <!-- 选项按钮 -->
        <div class="options-bar">
          <button
            :class="['option-btn', 'web-search-btn', { 'active': useWebSearch }]"
            @click="useWebSearch = !useWebSearch"
          >
            <svg class="btn-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
            </svg>
            <span>网络搜索</span>
          </button>

          <div class="dropdown-wrapper" ref="kbDropdownRef">
            <button
              :class="['option-btn', 'kb-btn', { 'active': selectedKbIds.length > 0, 'open': showKbDropdown }]"
              @click="showKbDropdown = !showKbDropdown"
            >
              <svg class="btn-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-1 9H9V9h10v2zm-4 4H9v-2h6v2zm4-8H9V5h10v2z"/>
              </svg>
              <span>知识库{{ selectedKbIds.length > 0 ? ` (${selectedKbIds.length})` : '' }}</span>
              <svg class="dropdown-arrow" :class="{ 'open': showKbDropdown }" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M7 10l5 5 5-5z"/>
              </svg>
            </button>

            <!-- 知识库下拉列表 -->
            <div v-if="showKbDropdown" class="kb-dropdown">
              <div v-if="loadingKbs" class="loading-small">
                <span class="spinner"></span>
              </div>
              <div v-else-if="knowledgeBases.length === 0" class="empty-dropdown">
                暂无知识库
              </div>
              <label v-else v-for="kb in knowledgeBases" :key="kb.id" class="kb-dropdown-item">
                <input
                  type="checkbox"
                  :value="kb.id"
                  :checked="selectedKbIds.includes(kb.id)"
                  @change="toggleKb(kb.id)"
                />
                <span class="kb-name">{{ kb.name }}</span>
              </label>
            </div>
          </div>
        </div>

        <!-- 输入框 -->
        <div class="input-wrapper">
          <textarea
            v-model="inputMessage"
            placeholder="输入你的消息... (Shift+Enter 换行, Enter 发送)"
            class="message-input"
            rows="1"
            :disabled="isLoading"
            @keydown="handleKeydown"
            ref="textareaRef"
            @input="autoResize"
          />
          <button
            class="send-button btn btn-primary"
            :disabled="!inputMessage.trim() || isLoading"
            @click="sendMessage"
          >
            <svg v-if="!isLoading" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
            </svg>
            <span v-else><span class="spinner"></span></span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import MessageList from '../components/MessageList.vue'
import { chatAPI } from '../api/client'

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

const messages = ref<Message[]>([])
const inputMessage = ref('')
const textareaRef = ref<HTMLTextAreaElement>()
const isLoading = ref(false)
const currentSessionId = ref<number>()
const sessions = ref<ChatSession[]>([])
const loadingSessions = ref(false)
const selectedKbIds = ref<number[]>([])
const useWebSearch = ref(false)
const showKbDropdown = ref(false)
const kbDropdownRef = ref()
const knowledgeBases = ref<any[]>([])
const loadingKbs = ref(false)
const hasUserInteracted = ref(false)

// 从 localStorage 加载保存的状态
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

// 保存状态到 localStorage
const saveState = () => {
  localStorage.setItem('chatState', JSON.stringify({
    messages: messages.value,
    sessionId: currentSessionId.value,
    selectedKbIds: selectedKbIds.value,
    useWebSearch: useWebSearch.value,
    hasUserInteracted: hasUserInteracted.value
  }))
}

// 加载知识库列表
const loadKnowledgeBases = async () => {
  loadingKbs.value = true
  try {
    const result = await fetch('/api/knowledge')
    knowledgeBases.value = await result.json()
  } catch (error) {
    console.error('Failed to load knowledge bases:', error)
  } finally {
    loadingKbs.value = false
  }
}

// 加载会话列表
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

// 加载指定会话
const loadSession = async (sessionId: number) => {
  try {
    const result = await chatAPI.getSession(sessionId)
    currentSessionId.value = sessionId
    // 加载会话消息
    messages.value = result.messages || []
    saveState()
  } catch (error) {
    console.error('Failed to load session:', error)
  }
}

// 删除会话
const deleteSession = async (sessionId: number) => {
  if (!confirm('确定要删除该对话吗？')) return

  try {
    await chatAPI.deleteSession(sessionId)
    if (currentSessionId.value === sessionId) {
      currentSessionId.value = undefined
      messages.value = []
    }
    await loadSessions()
    saveState()
  } catch (error) {
    console.error('Failed to delete session:', error)
  }
}

// 开启新对话
const toggleNewChat = () => {
  currentSessionId.value = undefined
  messages.value = []
  hasUserInteracted.value = false
  saveState()
}

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}

const autoResize = () => {
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto'
    textareaRef.value.style.height = Math.min(textareaRef.value.scrollHeight, 200) + 'px'
  }
}

const toggleKb = (kbId: number) => {
  if (selectedKbIds.value.includes(kbId)) {
    selectedKbIds.value = selectedKbIds.value.filter(id => id !== kbId)
  } else {
    selectedKbIds.value.push(kbId)
  }
  saveState()
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return

  const message = inputMessage.value
  inputMessage.value = ''
  hasUserInteracted.value = true

  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto'
  }

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: message
  })
  saveState()

  isLoading.value = true

  try {
    // 添加一个空的助手消息用于流式更新
    const assistantMessageIndex = messages.value.length
    messages.value.push({
      role: 'assistant',
      content: '',
      sources: undefined,
      search_results: undefined
    })

    const result = await chatAPI.sendMessageStream(
      {
        message,
        session_id: currentSessionId.value,
        kb_ids: selectedKbIds.value,
        use_web_search: useWebSearch.value
      },
      (chunk) => {
        // 处理流式数据块
        if (chunk.type === 'chunk' && chunk.content) {
          messages.value[assistantMessageIndex].content += chunk.content
        } else if (chunk.type === 'error') {
          console.error('Stream error:', chunk.message)
          messages.value[assistantMessageIndex].content = '抱歉，发生了错误，请稍后重试。'
        }
      }
    )

    currentSessionId.value = result.sessionId
    messages.value[assistantMessageIndex].sources = result.sources
    messages.value[assistantMessageIndex].search_results = result.searchResults
    saveState()

    // 刷新会话列表
    await loadSessions()
  } catch (error) {
    console.error('Chat error:', error)
    messages.value.push({
      role: 'assistant',
      content: '抱歉，发生了错误，请稍后重试。'
    })
  } finally {
    isLoading.value = false
  }
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days === 0) {
    return '今天 ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  } else if (days === 1) {
    return '昨天'
  } else if (days < 7) {
    return `${days}天前`
  } else {
    return date.toLocaleDateString('zh-CN')
  }
}

// 点击外部关闭下拉框
const handleClickOutside = (event: MouseEvent) => {
  if (kbDropdownRef.value && !kbDropdownRef.value.contains(event.target as Node)) {
    showKbDropdown.value = false
  }
}

onMounted(() => {
  loadSavedState()
  loadSessions()
  loadKnowledgeBases()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.chat-page {
  display: flex;
  height: 100vh;
  background-color: var(--bg-color);
}

/* 左侧边栏 */
.sidebar {
  width: 280px;
  background-color: var(--card-bg);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  border-bottom: 1px solid var(--border-color);
}

.sidebar-header h2 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.btn-icon {
  width: 32px;
  height: 32px;
  border: none;
  background-color: transparent;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
  color: var(--text-secondary);
  padding: 0;
}

.btn-icon svg {
  width: 20px;
  height: 20px;
  fill: currentColor;
}

.btn-icon:hover {
  background-color: var(--bg-color);
  color: var(--text-primary);
}

.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.session-item {
  position: relative;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 4px;
}

.session-item:hover {
  background-color: var(--bg-color);
}

.session-item.active {
  background-color: rgba(74, 144, 217, 0.1);
}

.session-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 4px;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
  padding-right: 24px;
}

.session-meta {
  font-size: 12px;
  color: var(--text-secondary);
}

.delete-session {
  position: absolute;
  top: 8px;
  right: 8px;
  opacity: 0;
  transition: opacity 0.2s;
}

.session-item:hover .delete-session {
  opacity: 1;
}

.delete-session:hover {
  background-color: rgba(231, 76, 60, 0.1);
  color: var(--danger-color);
}

.empty-sessions {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-secondary);
  font-size: 14px;
}

.loading {
  display: flex;
  justify-content: center;
  padding: 20px;
}

/* 右侧对话区域 */
.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-header {
  padding: 16px 24px;
  background-color: var(--card-bg);
  border-bottom: 1px solid var(--border-color);
}

.chat-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
}

.welcome-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.avatar-large {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background-color: var(--primary-color);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
}

.avatar-large svg {
  width: 48px;
  height: 48px;
  fill: currentColor;
}

.welcome-text {
  font-size: 18px;
  color: var(--text-primary);
  max-width: 500px;
  line-height: 1.6;
}

/* 输入区域 */
.input-area {
  background-color: var(--card-bg);
  border-top: 1px solid var(--border-color);
  padding: 16px 24px;
}

.options-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
  align-items: center;
}

.option-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: 1px solid var(--border-color);
  border-radius: 20px;
  background-color: transparent;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  color: var(--text-secondary);
}

.option-btn:hover {
  background-color: var(--bg-color);
  border-color: var(--primary-color);
}

.option-btn.active {
  background-color: rgba(74, 144, 217, 0.1);
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.option-btn .btn-icon {
  width: 18px;
  height: 18px;
}

.option-btn .btn-icon svg {
  width: 16px;
  height: 16px;
}

.dropdown-wrapper {
  position: relative;
}

.kb-btn.open {
  background-color: var(--bg-color);
}

.dropdown-arrow {
  width: 16px;
  height: 16px;
  transition: transform 0.2s;
}

.dropdown-arrow.open {
  transform: rotate(180deg);
}

.kb-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  min-width: 200px;
  background-color: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  box-shadow: var(--shadow-md);
  z-index: 100;
  max-height: 300px;
  overflow-y: auto;
  padding: 8px;
}

.kb-dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.kb-dropdown-item:hover {
  background-color: var(--bg-color);
}

.kb-dropdown-item input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.kb-dropdown-item .kb-name {
  font-size: 14px;
  color: var(--text-primary);
}

.loading-small {
  padding: 20px;
  text-align: center;
}

.empty-dropdown {
  padding: 16px;
  text-align: center;
  color: var(--text-secondary);
  font-size: 14px;
}

.input-wrapper {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.message-input {
  flex: 1;
  resize: none;
  min-height: 48px;
  max-height: 200px;
  padding: 14px 16px;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  font-family: inherit;
  font-size: 15px;
  line-height: 1.5;
  transition: all 0.2s;
  background-color: var(--bg-color);
}

.message-input:focus {
  outline: none;
  border-color: var(--primary-color);
  background-color: var(--card-bg);
  box-shadow: 0 0 0 3px rgba(74, 144, 217, 0.1);
}

.message-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.message-input::placeholder {
  color: var(--text-secondary);
}

.send-button {
  width: 48px;
  height: 48px;
  padding: 0;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.send-button svg {
  width: 20px;
  height: 20px;
  fill: white;
}

.send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 响应式 */
@media (max-width: 768px) {
  .chat-page {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    height: 60px;
    border-right: none;
    border-bottom: 1px solid var(--border-color);
  }

  .sidebar-header {
    padding: 12px 16px;
  }

  .session-list {
    display: none;
  }

  .chat-header {
    padding: 12px 16px;
  }

  .messages-container {
    padding: 16px;
  }

  .input-area {
    padding: 12px 16px;
  }

  .options-bar {
    flex-wrap: wrap;
  }
}
</style>
