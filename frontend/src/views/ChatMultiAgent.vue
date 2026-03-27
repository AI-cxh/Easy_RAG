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

    <!-- 左侧面板：会话列表 + 工具面板 -->
    <aside class="chat-sidebar" :class="{ open: sidebarOpen, collapsed: sidebarCollapsed }">
      <!-- 会话列表区域 -->
      <div class="sidebar-sessions">
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
              v-for="(session, index) in sessions"
              :key="session.id"
              :class="['session-item', { active: currentSessionId === session.id }]"
              :style="{ animationDelay: `${index * 30}ms` }"
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
                <button class="btn-icon btn-icon-sm delete-btn" @click="handleDeleteSession(session.id)" title="删除">
                  <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 工具面板区域 -->
      <div class="sidebar-tools">
        <ToolsPanel />
      </div>
    </aside>

    <!-- 右侧对话区域 -->
    <main class="chat-main">
      <!-- 顶部工具栏 -->
      <header class="chat-header">
        <button class="nav-toggle" @click="toggleSidebar" title="历史记录">
          <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/>
          </svg>
        </button>
        <h1 class="header-title">多Agent协同</h1>
      </header>

      <!-- 消息区域 -->
      <div class="chat-messages" ref="messagesRef">
        <div v-if="!hasUserInteracted" class="welcome-screen">
          <h2 class="welcome-title">欢迎使用多Agent协同</h2>
          <p class="welcome-desc">多个专业Agent协同完成复杂任务</p>
          <div class="welcome-tips">
            <div class="tip-item animate-slide-up stagger-1">
              <div class="tip-icon">
                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/>
                </svg>
              </div>
              <div class="tip-text">
                <span class="tip-title">多Agent协同</span>
                <span class="tip-desc">检索、分析、写作Agent协作</span>
              </div>
            </div>
            <div class="tip-item animate-slide-up stagger-2">
              <div class="tip-icon tip-icon-accent">
                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
                </svg>
              </div>
              <div class="tip-text">
                <span class="tip-title">任务规划</span>
                <span class="tip-desc">自动分解复杂任务</span>
              </div>
            </div>
            <div class="tip-item animate-slide-up stagger-3">
              <div class="tip-icon tip-icon-warm">
                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                </svg>
              </div>
              <div class="tip-text">
                <span class="tip-title">执行可视化</span>
                <span class="tip-desc">展示完整执行流程</span>
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
                  <!-- 多Agent执行流程 -->
                  <AgentFlow
                    v-if="msg.agentPlan && msg.agentPlan.length > 0"
                    :plan="msg.agentPlan"
                    :current-task-id="msg.currentTaskId"
                    :completed-tasks="msg.completedTasks || []"
                    :logs="msg.agentLogs || []"
                  />
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
            <button
              v-if="isSending"
              class="stop-btn"
              @click="stopGeneration"
              title="停止生成"
            >
              <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M6 6h12v12H6z"/>
              </svg>
            </button>
            <button
              v-else
              class="send-btn"
              :disabled="!inputMessage.trim()"
              @click="handleSend"
            >
              <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
              </svg>
            </button>
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

    <!-- 重命名对话框 -->
    <Teleport to="body">
      <div v-if="editingSessionId" class="dialog-overlay" @click.self="cancelSessionEdit">
        <div class="dialog">
          <div class="dialog-header">
            <h3 class="dialog-title">重命名对话</h3>
            <button class="dialog-close" @click="cancelSessionEdit">&times;</button>
          </div>
          <div class="dialog-body">
            <div class="form-group">
              <label class="form-label">名称</label>
              <input
                v-model="editingSessionName"
                type="text"
                class="input"
                placeholder="输入新名称"
                @keydown.enter="handleRename"
                ref="renameInputRef"
              />
            </div>
          </div>
          <div class="dialog-footer">
            <button class="btn btn-secondary" @click="cancelSessionEdit">取消</button>
            <button class="btn btn-primary" @click="handleRename">保存</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 删除确认对话框 -->
    <Teleport to="body">
      <div v-if="deletingSessionId" class="dialog-overlay" @click.self="cancelDeleteSession">
        <div class="dialog dialog-danger">
          <div class="dialog-header">
            <h3 class="dialog-title">删除对话</h3>
            <button class="dialog-close" @click="cancelDeleteSession">&times;</button>
          </div>
          <div class="dialog-body">
            <p class="dialog-message">确定要删除对话 "<strong>{{ deletingSessionName }}</strong>" 吗？</p>
            <p class="dialog-hint">此操作无法撤销。</p>
          </div>
          <div class="dialog-footer">
            <button class="btn btn-secondary" @click="cancelDeleteSession">取消</button>
            <button class="btn btn-danger" @click="confirmDeleteSession">删除</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { multiAgentAPI, chatAPI } from '../api/client'
import { useSession, type SessionType, type ChatSession } from '../composables/useSession'
import { marked } from 'marked'
import hljs from 'highlight.js'
import DOMPurify from 'dompurify'
import katex from 'katex'
import AppNavRail from '../components/AppNavRail.vue'
import AgentFlow from '../components/AgentFlow.vue'
import ToolsPanel from '../components/ToolsPanel.vue'
import 'highlight.js/styles/github-dark.css'
import 'katex/dist/katex.min.css'

// 会话类型
const SESSION_TYPE: SessionType = 'multi_agent'
const { sessions, loading: loadingSessions, loadSessions, deleteSession: deleteSessionFromList, renameSession: renameSessionInList } = useSession(SESSION_TYPE)

// 重命名相关状态
const editingSessionId = ref<number>()
const editingSessionName = ref('')
const renameInputRef = ref<HTMLInputElement>()

// 删除确认对话框状态
const deletingSessionId = ref<number>()
const deletingSessionName = ref('')

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

const startRename = (session: ChatSession) => {
  editingSessionId.value = session.id
  editingSessionName.value = session.title
  nextTick(() => {
    renameInputRef.value?.focus()
    renameInputRef.value?.select()
  })
}

const cancelSessionEdit = () => {
  editingSessionId.value = undefined
  editingSessionName.value = ''
}

const handleRename = () => {
  if (!editingSessionId.value || !editingSessionName.value.trim()) {
    cancelSessionEdit()
    return
  }
  handleRenameSession(editingSessionId.value, editingSessionName.value.trim())
  cancelSessionEdit()
}

// 类型定义
interface Message {
  role: 'user' | 'assistant'
  content: string
  sources?: string[]
  search_results?: Array<{ title: string; url: string; snippet?: string }>
  agentPlan?: Array<{ id: string; agent_type: string; description: string; priority: number }>
  currentTaskId?: string
  completedTasks?: string[]
  agentLogs?: Array<{ type: string; content: string; tool_name?: string }>
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
const abortController = ref<AbortController | null>(null)

const inputMessage = ref('')
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
      searchResults: msg.search_results || msg.searchResults,
      agentPlan: msg.agent_plan || msg.agentPlan,
      agentLogs: msg.agent_logs || msg.agentLogs,
      completedTasks: msg.completed_tasks || msg.completedTasks,
      currentTaskId: msg.current_task_id || msg.currentTaskId
    }))
    hasUserInteracted.value = messages.value.length > 0
  } catch (error) {
    console.error('Failed to load session:', error)
  }
}

const handleDeleteSession = async (sessionId: number) => {
  // 找到会话名称
  const session = sessions.value.find(s => s.id === sessionId)
  deletingSessionId.value = sessionId
  deletingSessionName.value = session?.title || '这个对话'
}

const confirmDeleteSession = async () => {
  if (!deletingSessionId.value) return

  const sessionId = deletingSessionId.value
  cancelDeleteSession()

  const success = await deleteSessionFromList(sessionId)
  if (success && currentSessionId.value === sessionId) {
    currentSessionId.value = undefined
    messages.value = []
    hasUserInteracted.value = false
  }
}

const cancelDeleteSession = () => {
  deletingSessionId.value = undefined
  deletingSessionName.value = ''
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

// 停止生成
const stopGeneration = () => {
  if (abortController.value) {
    abortController.value.abort()
    abortController.value = null
  }
  isSending.value = false
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
  abortController.value = new AbortController()

  try {
    const assistantIndex = messages.value.length
    messages.value.push({
      role: 'assistant',
      content: '',
      agentPlan: [],
      agentLogs: [],
      completedTasks: []
    })
    scrollToBottom()

    const result = await multiAgentAPI.sendMessageStream(
      {
        message,
        session_id: currentSessionId.value,
        show_process: true
      },
      (chunk) => {
        if (chunk.type === 'answer' && chunk.content) {
          messages.value[assistantIndex].content += chunk.content
          scrollToBottom()
        } else if (chunk.type === 'planning') {
          if (!messages.value[assistantIndex].agentLogs) {
            messages.value[assistantIndex].agentLogs = []
          }
          messages.value[assistantIndex].agentLogs!.push({
            type: 'thought',
            content: chunk.content || ''
          })
          scrollToBottom()
        } else if (chunk.type === 'plan') {
          messages.value[assistantIndex].agentPlan = chunk.tasks || []
          scrollToBottom()
        } else if (chunk.type === 'task_start') {
          messages.value[assistantIndex].currentTaskId = chunk.task_id
          if (!messages.value[assistantIndex].completedTasks) {
            messages.value[assistantIndex].completedTasks = []
          }
          if (!messages.value[assistantIndex].agentLogs) {
            messages.value[assistantIndex].agentLogs = []
          }
          messages.value[assistantIndex].agentLogs!.push({
            type: 'thought',
            content: `开始执行: ${chunk.description || ''}`
          })
          scrollToBottom()
        } else if (chunk.type === 'task_complete') {
          if (!messages.value[assistantIndex].completedTasks) {
            messages.value[assistantIndex].completedTasks = []
          }
          messages.value[assistantIndex].completedTasks!.push(chunk.task_id || '')
          scrollToBottom()
        } else if (chunk.type === 'thought') {
          if (!messages.value[assistantIndex].agentLogs) {
            messages.value[assistantIndex].agentLogs = []
          }
          messages.value[assistantIndex].agentLogs!.push({
            type: 'thought',
            content: chunk.content || ''
          })
          scrollToBottom()
        } else if (chunk.type === 'tool_call') {
          if (!messages.value[assistantIndex].agentLogs) {
            messages.value[assistantIndex].agentLogs = []
          }
          messages.value[assistantIndex].agentLogs!.push({
            type: 'tool_call',
            content: chunk.content || '',
            tool_name: chunk.tool_name
          })
          scrollToBottom()
        } else if (chunk.type === 'tool_result') {
          if (!messages.value[assistantIndex].agentLogs) {
            messages.value[assistantIndex].agentLogs = []
          }
          messages.value[assistantIndex].agentLogs!.push({
            type: 'tool_result',
            content: chunk.content || '',
            tool_name: chunk.tool_name
          })
          scrollToBottom()
        } else if (chunk.type === 'error') {
          console.error('Stream error:', chunk.content)
          messages.value[assistantIndex].content = chunk.content || '抱歉，发生了错误，请稍后重试。'
        }
      },
      abortController.value.signal
    )

    currentSessionId.value = result.sessionId
    if (result.searchResults && result.searchResults.length > 0) {
      messages.value[assistantIndex].search_results = result.searchResults
    }
    if (result.sources && result.sources.length > 0) {
      messages.value[assistantIndex].sources = result.sources
    }

    await loadSessions()
  } catch (error: any) {
    if (error.name === 'AbortError') {
      // 用户主动取消，不显示错误
      console.log('Request aborted by user')
    } else {
      console.error('Chat error:', error)
      messages.value.push({ role: 'assistant', content: '抱歉，发生了错误，请稍后重试。' })
    }
  } finally {
    isSending.value = false
    abortController.value = null
  }
}

// 初始化
onMounted(() => {
  loadSessions()
})
</script>

<style scoped>
@import '../assets/chat.css';

/* 侧边栏样式 */
.chat-sidebar {
  width: clamp(280px, 30vw, 360px);
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  transition: width var(--duration-normal) var(--ease-spring);
}

.chat-sidebar.collapsed {
  width: 0;
  border-right: none;
  overflow: hidden;
}

.sidebar-sessions {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

.sidebar-header {
  padding: clamp(var(--space-3), 2vw, var(--space-5));
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
  padding: 0 var(--space-3);
}

.loading-state {
  display: flex;
  justify-content: center;
  padding: var(--space-8);
}

.spinner {
  width: 24px;
  height: 24px;
  border: 2px solid var(--border-default);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
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
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-soft);
  animation: slideIn var(--duration-slow) var(--ease-spring) backwards;
}

.session-item:hover {
  background: var(--bg-hover);
  transform: translateX(4px);
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

.btn-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  color: var(--text-muted);
  cursor: pointer;
  transition: all var(--duration-fast);
}

.btn-icon:hover {
  background: var(--bg-hover);
  border-color: var(--border-strong);
  color: var(--text-primary);
}

.btn-icon svg {
  width: 14px;
  height: 14px;
  fill: currentColor;
}

.delete-btn:hover {
  color: var(--color-danger);
  border-color: var(--color-danger);
}

.sidebar-tools {
  flex-shrink: 0;
  border-top: 1px solid var(--border-subtle);
  max-height: 40%;
  overflow-y: auto;
}

/* 按钮样式 */
.btn {
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-lg);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  cursor: pointer;
  transition: all var(--duration-fast);
}

.btn-primary {
  background: var(--color-primary);
  color: white;
  border: 1px solid var(--color-primary);
}

.btn-primary:hover {
  opacity: 0.9;
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  border: 1px solid var(--border-default);
}

.btn-secondary:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

/* 对话框样式 */
.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal);
}

.dialog {
  background: var(--bg-elevated);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  width: min(400px, 90vw);
  animation: slideUp var(--duration-normal) var(--ease-spring);
}

.dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--border-subtle);
}

.dialog-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0;
}

.dialog-close {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  color: var(--text-muted);
  font-size: 20px;
  cursor: pointer;
  transition: all var(--duration-fast);
}

.dialog-close:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.dialog-body {
  padding: var(--space-5);
}

.form-group {
  margin-bottom: var(--space-4);
}

.form-label {
  display: block;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
  margin-bottom: var(--space-2);
}

.input {
  width: 100%;
  padding: var(--space-3);
  background: var(--bg-primary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  color: var(--text-primary);
  font-size: var(--text-base);
  transition: border-color var(--duration-fast);
}

.input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-5);
  border-top: 1px solid var(--border-subtle);
}

/* 删除对话框样式 */
.dialog-danger .dialog-header {
  background: rgba(220, 38, 38, 0.08);
}

.dialog-danger .dialog-title {
  color: var(--color-danger);
}

.dialog-message {
  margin: 0;
  font-size: var(--text-base);
  color: var(--text-primary);
  line-height: 1.6;
}

.dialog-message strong {
  color: var(--text-primary);
  font-weight: var(--font-semibold);
}

.dialog-hint {
  margin: var(--space-2) 0 0;
  font-size: var(--text-sm);
  color: var(--text-muted);
}

.btn-danger {
  background: var(--color-danger);
  color: white;
  border: 1px solid var(--color-danger);
}

.btn-danger:hover {
  background: #b91c1c;
  border-color: #b91c1c;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .chat-sidebar {
    position: fixed;
    left: clamp(56px, 8vw, 72px);
    top: 0;
    bottom: 0;
    z-index: var(--z-modal);
    transform: translateX(-100%);
    transition: transform var(--duration-normal) var(--ease-spring);
    width: clamp(260px, 70vw, 320px);
    border-right: 1px solid var(--border-subtle);
  }

  .chat-sidebar.open {
    transform: translateX(0);
  }

  .chat-sidebar.collapsed {
    width: clamp(260px, 70vw, 320px);
    border-right: 1px solid var(--border-subtle);
  }

  .session-actions {
    opacity: 1;
  }

  .sidebar-tools {
    max-height: 30%;
  }
}

/* 停止按钮样式 */
.stop-btn {
  width: clamp(32px, 5vw, 40px);
  height: clamp(32px, 5vw, 40px);
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-danger);
  border: none;
  border-radius: var(--radius-lg);
  color: white;
  cursor: pointer;
  transition: all var(--duration-normal) var(--ease-soft);
  box-shadow: 0 2px 8px rgba(220, 38, 38, 0.25);
  flex-shrink: 0;
}

.stop-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 16px rgba(220, 38, 38, 0.35);
}

.stop-btn svg {
  width: clamp(14px, 2vw, 18px);
  height: clamp(14px, 2vw, 18px);
  fill: currentColor;
}

/* 输入框行内布局 */
.input-box {
  flex-direction: row;
  align-items: flex-end;
  gap: var(--space-2);
}

.input-box .textarea {
  padding-right: 0;
}
</style>
