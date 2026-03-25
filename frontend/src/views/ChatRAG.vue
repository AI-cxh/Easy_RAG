<template>
  <div class="chat-layout">
    <!-- 左侧固定导航栏 -->
    <AppNavRail />

    <!-- 移动端侧边栏遮罩 -->
    <div
      v-if="sidebarOpen"
      class="sidebar-overlay"
      @click="sidebarOpen = false"
    />

    <!-- 左侧会话列表 -->
    <AppSidebar
      :sessions="sessions"
      :loading="loadingSessions"
      :current-session-id="currentSessionId"
      :sidebar-open="sidebarOpen"
      :sidebar-collapsed="sidebarCollapsed"
      @new-chat="newChat"
      @select-session="handleSelectSession"
      @delete-session="handleDeleteSession"
      @rename-session="handleRenameSession"
    />

    <!-- 右侧对话区域 -->
    <main class="chat-main">
      <!-- 顶部工具栏 -->
      <header class="chat-header">
        <button class="nav-toggle" @click="toggleSidebar" title="历史记录">
          <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/>
          </svg>
        </button>
        <h1 class="header-title">Easy RAG</h1>
      </header>

      <!-- 消息区域 -->
      <div class="chat-messages" ref="messagesRef">
        <div v-if="!hasUserInteracted" class="welcome-screen">
          <h2 class="welcome-title">欢迎使用Easy RAG</h2>
          <p class="welcome-desc">基于知识库的传统检索问答</p>
          <div class="welcome-tips">
            <div class="tip-item animate-slide-up stagger-1">
              <div class="tip-icon">
                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-1 9H9V9h10v2zm-4 4H9v-2h6v2zm4-8H9V5h10v2z"/>
                </svg>
              </div>
              <div class="tip-text">
                <span class="tip-title">选择知识库</span>
                <span class="tip-desc">从已上传的文档中检索</span>
              </div>
            </div>
            <div class="tip-item animate-slide-up stagger-2">
              <div class="tip-icon tip-icon-accent">
                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
                </svg>
              </div>
              <div class="tip-text">
                <span class="tip-title">精准检索</span>
                <span class="tip-desc">基于向量相似度匹配</span>
              </div>
            </div>
            <div class="tip-item animate-slide-up stagger-3">
              <div class="tip-icon tip-icon-warm">
                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                </svg>
              </div>
              <div class="tip-text">
                <span class="tip-title">联网搜索</span>
                <span class="tip-desc">获取更多实时信息</span>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="messages-container">
          <div
            v-for="(msg, index) in messages"
            :key="index"
            :class="['message', msg.role]"
          >
            <!-- 用户消息 -->
            <template v-if="msg.role === 'user'">
              <div class="message-content">
                <div class="message-wrapper">
                  <div v-if="editingIndex === index" class="edit-input-wrapper">
                    <textarea
                      v-model="editingContent"
                      class="textarea"
                      rows="3"
                      ref="editInputRef"
                      @keydown.enter.exact.ctrl="saveEdit(index)"
                      @keydown.escape="cancelEdit"
                    ></textarea>
                    <div class="edit-actions">
                      <button class="btn btn-secondary" @click="cancelEdit">取消</button>
                      <button class="btn btn-primary" @click="saveEdit(index)">保存</button>
                    </div>
                  </div>
                  <template v-else>
                    <div class="message-text">{{ msg.content }}</div>
                    <div class="message-actions">
                      <button
                        v-if="isLastUserMessage(index)"
                        class="action-icon"
                        @click="startEdit(index)"
                        title="编辑"
                      >
                        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
                        </svg>
                      </button>
                      <button class="action-icon" @click="copyMessage(msg.content)" title="复制">
                        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
                        </svg>
                      </button>
                    </div>
                  </template>
                </div>
              </div>
            </template>

            <!-- 助手消息 -->
            <template v-else>
              <div class="message-avatar">
                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                </svg>
              </div>
              <div class="message-content">
                <div class="message-wrapper">
                  <div class="message-text markdown" v-html="renderMarkdown(msg.content)"></div>
                  <span v-if="!msg.content && isSending && index === messages.length - 1" class="typing-indicator">
                    <span></span><span></span><span></span>
                  </span>
                  <!-- 知识库来源信息 -->
                  <div v-if="msg.sources?.length" class="message-sources">
                    <span class="sources-label">参考来源:</span>
                    <span v-for="(source, i) in msg.sources" :key="i" class="source-tag">{{ source }}</span>
                  </div>
                  <!-- 联网搜索来源 -->
                  <div v-if="msg.search_results?.length" class="message-sources web-sources">
                    <span class="sources-label">联网搜索来源:</span>
                    <a
                      v-for="(result, i) in msg.search_results"
                      :key="i"
                      :href="result.url"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="source-link"
                      :title="result.snippet"
                    >
                      <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" class="link-icon">
                        <path d="M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H7c-2.76 0-5 2.24-5 5s2.24 5 5 5h4v-1.9H7c-1.71 0-3.1-1.39-3.1-3.1zM8 13h8v-2H8v2zm9-6h-4v1.9h4c1.71 0 3.1 1.39 3.1 3.1s-1.39 3.1-3.1 3.1h-4V17h4c2.76 0 5-2.24 5-5s-2.24-5-5-5z"/>
                      </svg>
                      {{ result.title || result.url }}
                    </a>
                  </div>
                  <!-- 消息操作按钮 -->
                  <div class="message-actions">
                    <button class="action-icon" @click="copyMessage(msg.content)" title="复制">
                      <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
                      </svg>
                    </button>
                    <button
                      v-if="index === messages.length - 1 && !isSending"
                      class="action-icon"
                      @click="regenerateResponse"
                      title="重新回答"
                    >
                      <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </template>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="chat-input-area">
        <div class="input-wrapper">
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
            <div class="input-toolbar">
              <div class="toolbar-left">
                <!-- 知识库选择 -->
                <div class="kb-dropdown">
                  <button
                    class="toolbar-btn"
                    :class="{ active: selectedKbIds.length > 0 }"
                    @click="showKbDropdown = !showKbDropdown"
                  >
                    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path d="M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-1 9H9V9h10v2zm-4 4H9v-2h6v2zm4-8H9V5h10v2z"/>
                    </svg>
                    <span>{{ selectedKbIds.length > 0 ? `已选 ${selectedKbIds.length} 个` : '知识库' }}</span>
                    <svg class="dropdown-arrow" :class="{ open: showKbDropdown }" viewBox="0 0 24 24">
                      <path d="M7 10l5 5 5-5z"/>
                    </svg>
                  </button>
                  <div v-if="showKbDropdown" class="kb-dropdown-menu">
                    <div class="dropdown-header">选择知识库</div>
                    <div v-if="knowledgeBases.length === 0" class="dropdown-empty">
                      暂无知识库
                    </div>
                    <div v-else class="dropdown-list">
                      <label
                        v-for="kb in knowledgeBases"
                        :key="kb.id"
                        class="dropdown-item"
                        :class="{ selected: selectedKbIds.includes(kb.id) }"
                      >
                        <input
                          type="checkbox"
                          :checked="selectedKbIds.includes(kb.id)"
                          @change="toggleKb(kb.id)"
                        />
                        <span class="item-check"></span>
                        <span class="item-name">{{ kb.name }}</span>
                      </label>
                    </div>
                  </div>
                </div>
                <!-- 网络搜索 -->
                <button
                  class="toolbar-btn"
                  :class="{ active: useWebSearch }"
                  @click="useWebSearch = !useWebSearch"
                  title="网络搜索"
                >
                  <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                  </svg>
                  <span>联网搜索</span>
                </button>
              </div>
              <div class="toolbar-right">
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
      </div>
    </main>

    <!-- 复制成功提示 -->
    <Transition name="toast">
      <div v-if="copySuccess" class="copy-toast">
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
        </svg>
        <span>已复制到剪贴板</span>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { chatAPI, knowledgeAPI } from '../api/client'
import { useSession, type SessionType } from '../composables/useSession'
import { marked } from 'marked'
import hljs from 'highlight.js'
import DOMPurify from 'dompurify'
import katex from 'katex'
import AppNavRail from '../components/AppNavRail.vue'
import AppSidebar from '../components/AppSidebar.vue'
import 'highlight.js/styles/github-dark.css'
import 'katex/dist/katex.min.css'

// 会话类型
const SESSION_TYPE: SessionType = 'rag'
const { sessions, loading: loadingSessions, loadSessions, deleteSession: deleteSessionFromList, renameSession: renameSessionInList } = useSession(SESSION_TYPE)

// 类型定义
interface Message {
  role: 'user' | 'assistant'
  content: string
  sources?: string[]
  search_results?: Array<{ title: string; url: string; snippet?: string }>
}

// 状态
const messages = ref<Message[]>([])
const currentSessionId = ref<number>()
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
const showKbDropdown = ref(false)
const copySuccess = ref(false)
const editingIndex = ref<number>()
const editingContent = ref('')
const editInputRef = ref<HTMLTextAreaElement>()

// 配置 marked
marked.setOptions({
  highlight: (code: string, lang: string) => {
    const language = hljs.getLanguage(lang) ? lang : 'plaintext'
    return hljs.highlight(code, { language }).value
  },
  breaks: true,
  gfm: true
})

// 渲染数学公式
const renderMath = (text: string): string => {
  text = text.replace(/\$\$([\s\S]+?)\$\$/g, (_, math) => {
    try {
      return katex.renderToString(math.trim(), { displayMode: true, throwOnError: false, output: 'html' })
    } catch (e) {
      return `<span class="katex-error">${math}</span>`
    }
  })
  text = text.replace(/(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)/g, (_, math) => {
    try {
      return katex.renderToString(math.trim(), { displayMode: false, throwOnError: false, output: 'html' })
    } catch (e) {
      return `<span class="katex-error">${math}</span>`
    }
  })
  return text
}

// Markdown 渲染
const renderMarkdown = (content: string) => {
  if (!content) return ''
  const withMath = renderMath(content)
  const rawHtml = marked.parse(withMath) as string
  return DOMPurify.sanitize(rawHtml, {
    ALLOWED_TAGS: ['a', 'b', 'i', 'strong', 'em', 'u', 's', 'br', 'p', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'dl', 'dt', 'dd', 'table', 'thead', 'tbody', 'tfoot', 'tr', 'th', 'td', 'caption', 'colgroup', 'col', 'pre', 'code', 'blockquote', 'hr', 'img', 'math', 'semantics', 'mrow', 'mi', 'mo', 'mn', 'mfrac', 'msup', 'msub', 'msubsup', 'munder', 'mover', 'munderover', 'mroot', 'msqrt', 'mtable', 'mtr', 'mtd', 'mtext', 'mspace', 'mfenced', 'menclose', 'mpadded', 'mphantom', 'mglyph', 'maction', 'merror', 'annotation', 'annotation-xml'],
    ALLOWED_ATTR: ['href', 'title', 'alt', 'src', 'width', 'height', 'class', 'id', 'target', 'rel', 'colspan', 'rowspan', 'align', 'valign', 'xmlns', 'display', 'scriptlevel', 'mathvariant', 'mathsize', 'mathcolor', 'mathbackground', 'stretchy', 'symmetric', 'maxsize', 'minsize', 'largeop', 'movablelimits', 'accent', 'accentunder', 'delimiter', 'separator', 'notation', 'linethickness', 'spacing', 'columnalign', 'rowalign', 'columnspacing', 'rowspacing', 'frame', 'framespacing', 'equalcolumns', 'equalrows', 'side', 'width', 'height', 'depth', 'lspace', 'rspace', 'operator', 'form']
  })
}

// 切换侧边栏
const toggleSidebar = () => {
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

// 加载知识库
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
    messages.value = (result.messages || []).map((msg: any) => ({
      ...msg,
      searchResults: msg.search_results || msg.searchResults
    }))
    hasUserInteracted.value = messages.value.length > 0
  } catch (error) {
    console.error('Failed to load session:', error)
  }
}

const handleDeleteSession = async (sessionId: number) => {
  const success = await deleteSessionFromList(sessionId)
  if (success && currentSessionId.value === sessionId) {
    currentSessionId.value = undefined
    messages.value = []
    hasUserInteracted.value = false
  }
}

const handleRenameSession = async (sessionId: number, title: string) => {
  await renameSessionInList(sessionId, title)
}

const newChat = () => {
  currentSessionId.value = undefined
  messages.value = []
  hasUserInteracted.value = false
  sidebarOpen.value = false
}

// 知识库操作
const toggleKb = (kbId: number) => {
  if (selectedKbIds.value.includes(kbId)) {
    selectedKbIds.value = selectedKbIds.value.filter(id => id !== kbId)
  } else {
    selectedKbIds.value.push(kbId)
  }
}

// 复制消息
const copyMessage = async (content: string) => {
  try {
    await navigator.clipboard.writeText(content)
    copySuccess.value = true
    setTimeout(() => {
      copySuccess.value = false
    }, 2000)
  } catch (error) {
    console.error('Failed to copy:', error)
  }
}

// 判断是否是最后一条用户消息
const isLastUserMessage = (index: number) => {
  for (let i = messages.value.length - 1; i >= 0; i--) {
    if (messages.value[i].role === 'user') {
      return i === index
    }
  }
  return false
}

// 编辑消息
const startEdit = (index: number) => {
  editingIndex.value = index
  editingContent.value = messages.value[index].content
  nextTick(() => {
    editInputRef.value?.focus()
  })
}

const cancelEdit = () => {
  editingIndex.value = undefined
  editingContent.value = ''
}

const saveEdit = async (index: number) => {
  if (!editingContent.value.trim()) return

  messages.value[index].content = editingContent.value.trim()
  cancelEdit()

  // 删除该消息之后的所有消息
  if (index < messages.value.length - 1) {
    messages.value = messages.value.slice(0, index + 1)
  }

  // 重新发送消息
  const userMessage = messages.value[index].content
  messages.value = messages.value.slice(0, index)
  inputMessage.value = userMessage
  await handleSend()
}

// 重新生成回答
const regenerateResponse = async () => {
  if (messages.value.length < 2 || isSending.value) return

  // 找到最后一条用户消息
  const lastUserIndex = messages.value.map(m => m.role).lastIndexOf('user')
  if (lastUserIndex === -1) return

  // 删除最后一条助手消息
  messages.value.pop()

  // 重新发送
  const userMessage = messages.value[lastUserIndex].content
  messages.value = messages.value.slice(0, lastUserIndex)
  inputMessage.value = userMessage
  await handleSend()
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

  messages.value.push({ role: 'user', content: message })
  scrollToBottom()

  isSending.value = true

  try {
    const assistantIndex = messages.value.length
    messages.value.push({ role: 'assistant', content: '' })
    scrollToBottom()

    const result = await chatAPI.sendMessageStream(
      {
        message,
        session_id: currentSessionId.value,
        kb_ids: selectedKbIds.value,
        use_web_search: useWebSearch.value,
        session_type: SESSION_TYPE
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

    await loadSessions()
  } catch (error) {
    console.error('Chat error:', error)
    messages.value.push({ role: 'assistant', content: '抱歉，发生了错误，请稍后重试。' })
  } finally {
    isSending.value = false
  }
}

// 初始化
onMounted(() => {
  loadSessions()
  loadKnowledgeBases()
})
</script>

<style scoped>
@import '../assets/chat.css';
</style>
