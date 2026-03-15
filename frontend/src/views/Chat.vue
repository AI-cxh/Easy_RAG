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
          <h2 class="welcome-title">欢迎使用 Easy RAG</h2>
          <p class="welcome-desc">基于知识库的智能问答助手</p>
          <div class="welcome-tips">
            <div class="tip-item animate-slide-up stagger-1">
              <div class="tip-icon">
                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-1 9H9V9h10v2zm-4 4H9v-2h6v2zm4-8H9V5h10v2z"/>
                </svg>
              </div>
              <div class="tip-text">
                <span class="tip-title">上传文档</span>
                <span class="tip-desc">构建专属知识库</span>
              </div>
            </div>
            <div class="tip-item animate-slide-up stagger-2">
              <div class="tip-icon tip-icon-accent">
                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
                </svg>
              </div>
              <div class="tip-text">
                <span class="tip-title">智能检索</span>
                <span class="tip-desc">精准定位答案</span>
              </div>
            </div>
            <div class="tip-item animate-slide-up stagger-3">
              <div class="tip-icon tip-icon-warm">
                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                </svg>
              </div>
              <div class="tip-text">
                <span class="tip-title">网络搜索</span>
                <span class="tip-desc">获取更多信息</span>
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
            <!-- 用户消息：靠右显示，无头像 -->
            <template v-if="msg.role === 'user'">
              <div class="message-content">
                <div class="message-wrapper">
                  <!-- 编辑模式 -->
                  <template v-if="editingMessageIndex === index">
                    <div class="message-edit-box">
                      <textarea
                        v-model="editingMessageContent"
                        class="edit-textarea"
                        placeholder="编辑消息..."
                        @keydown.enter.ctrl="saveMessageEdit(index)"
                        @keydown.escape="cancelMessageEdit"
                      ></textarea>
                      <div class="edit-actions">
                        <button class="edit-btn cancel" @click="cancelMessageEdit">取消</button>
                        <button class="edit-btn save" @click="saveMessageEdit(index)">保存并发送</button>
                      </div>
                    </div>
                  </template>
                  <!-- 正常显示模式 -->
                  <template v-else>
                    <div class="message-text">{{ msg.content }}</div>
                    <!-- 用户消息操作按钮 -->
                    <div class="message-actions">
                      <button v-if="index === lastUserMessageIndex" class="action-icon" @click="startEditMessage(index)" title="编辑">
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

            <!-- 助手消息：左侧显示，有头像 -->
            <template v-else>
              <div class="message-avatar">
                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                </svg>
              </div>
              <div class="message-content">
                <div class="message-wrapper">
                  <!-- Agent思考过程 -->
                  <AgentThinking v-if="msg.thinkingSteps && msg.thinkingSteps.length > 0" :steps="msg.thinkingSteps" />
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
                  <!-- 助手消息操作按钮 -->
                  <div v-if="msg.content && !isSending" class="message-actions">
                    <button class="action-icon" @click="copyMessage(msg.content)" title="复制">
                      <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
                      </svg>
                    </button>
                    <button class="action-icon" @click="regenerateResponse(index)" title="再次回答">
                      <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74C4.46 8.97 4 10.43 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z"/>
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
            <!-- 底部工具栏 -->
            <div class="input-toolbar">
              <div class="toolbar-left">
                <!-- Agent模式切换 -->
                <button
                  class="toolbar-btn agent-mode-btn"
                  :class="{ active: useAgentMode }"
                  @click="useAgentMode = !useAgentMode"
                  title="Agent模式"
                >
                  <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                  </svg>
                  <span>{{ useAgentMode ? 'Agent' : 'RAG' }}</span>
                </button>
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
                  <!-- 向上展开的下拉列表 -->
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
                @keydown.enter="saveSessionName(editingSessionId!)"
                ref="renameInputRef"
              />
            </div>
          </div>
          <div class="dialog-footer">
            <button class="btn btn-secondary" @click="cancelSessionEdit">取消</button>
            <button class="btn btn-primary" @click="saveSessionName(editingSessionId!)">保存</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { chatAPI, knowledgeAPI, agentAPI } from '../api/client'
import type { ThinkingStep } from '../api/client'
import { marked } from 'marked'
import AgentThinking from '../components/AgentThinking.vue'

// 类型定义
interface Message {
  role: 'user' | 'assistant'
  content: string
  sources?: string[]
  search_results?: Array<{ title: string; url: string; snippet?: string }>
  thinkingSteps?: ThinkingStep[]
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
const useAgentMode = ref(true)  // 默认使用Agent模式
const knowledgeBases = ref<any[]>([])
const inputMessage = ref('')
const showKbDropdown = ref(false)
const copySuccess = ref(false)
const editingSessionId = ref<number>()
const editingSessionName = ref('')
const renameInputRef = ref<HTMLInputElement>()

// 消息编辑状态
const editingMessageIndex = ref<number>()
const editingMessageContent = ref('')

// 获取最新用户消息的索引
const lastUserMessageIndex = computed(() => {
  for (let i = messages.value.length - 1; i >= 0; i--) {
    if (messages.value[i].role === 'user') {
      return i
    }
  }
  return -1
})

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
    // 转换字段名：thinking_steps -> thinkingSteps
    messages.value = (result.messages || []).map((msg: any) => ({
      ...msg,
      thinkingSteps: msg.thinking_steps || msg.thinkingSteps,
      searchResults: msg.search_results || msg.searchResults
    }))
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
  editingSessionId.value = session.id
  editingSessionName.value = session.title
  nextTick(() => {
    renameInputRef.value?.focus()
    renameInputRef.value?.select()
  })
}

const saveSessionName = async (sessionId: number) => {
  if (!editingSessionName.value.trim()) {
    cancelSessionEdit()
    return
  }

  try {
    await chatAPI.renameSession(sessionId, editingSessionName.value.trim())
    await loadSessions()
  } catch (error) {
    console.error('Failed to rename session:', error)
  } finally {
    cancelSessionEdit()
  }
}

const cancelSessionEdit = () => {
  editingSessionId.value = undefined
  editingSessionName.value = ''
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
      search_results: undefined,
      thinkingSteps: undefined
    })
    scrollToBottom()

    if (useAgentMode.value) {
      // Agent模式
      const result = await agentAPI.sendMessageStream(
        {
          message,
          session_id: currentSessionId.value,
          kb_ids: selectedKbIds.value.length > 0 ? selectedKbIds.value : undefined,
          use_web_search: useWebSearch.value,
          show_thinking: true
        },
        (chunk) => {
          if (chunk.type === 'chunk' && chunk.content) {
            messages.value[assistantIndex].content += chunk.content
            scrollToBottom()
          } else if (chunk.type === 'thought') {
            // 思考过程
            if (!messages.value[assistantIndex].thinkingSteps) {
              messages.value[assistantIndex].thinkingSteps = []
            }
            messages.value[assistantIndex].thinkingSteps!.push({
              type: 'thought',
              content: chunk.content || ''
            })
            scrollToBottom()
          } else if (chunk.type === 'tool_call') {
            // 工具调用
            if (!messages.value[assistantIndex].thinkingSteps) {
              messages.value[assistantIndex].thinkingSteps = []
            }
            messages.value[assistantIndex].thinkingSteps!.push({
              type: 'tool_call',
              content: chunk.content || '',
              tool_name: chunk.tool_name,
              tool_args: chunk.tool_args
            })
            scrollToBottom()
          } else if (chunk.type === 'tool_result') {
            // 工具结果
            if (!messages.value[assistantIndex].thinkingSteps) {
              messages.value[assistantIndex].thinkingSteps = []
            }
            messages.value[assistantIndex].thinkingSteps!.push({
              type: 'tool_result',
              content: chunk.content || '',
              tool_name: chunk.tool_name
            })
            scrollToBottom()
          } else if (chunk.type === 'error') {
            console.error('Stream error:', chunk.message)
            messages.value[assistantIndex].content = '抱歉，发生了错误，请稍后重试。'
          }
        }
      )

      currentSessionId.value = result.sessionId
      messages.value[assistantIndex].thinkingSteps = result.thinkingSteps
      // 保存搜索结果和来源
      if (result.searchResults && result.searchResults.length > 0) {
        messages.value[assistantIndex].search_results = result.searchResults
      }
      if (result.sources && result.sources.length > 0) {
        messages.value[assistantIndex].sources = result.sources
      }
    } else {
      // 传统RAG模式
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
    }

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

// 复制消息
const copyMessage = async (content: string) => {
  try {
    await navigator.clipboard.writeText(content)
    showCopySuccess()
  } catch (error) {
    console.error('Copy failed:', error)
    // 降级处理
    const textarea = document.createElement('textarea')
    textarea.value = content
    document.body.appendChild(textarea)
    textarea.select()
    document.execCommand('copy')
    document.body.removeChild(textarea)
    showCopySuccess()
  }
}

// 显示复制成功提示
const showCopySuccess = () => {
  copySuccess.value = true
  setTimeout(() => {
    copySuccess.value = false
  }, 1500)
}

// 开始编辑用户消息
const startEditMessage = (index: number) => {
  const msg = messages.value[index]
  if (msg.role !== 'user') return

  editingMessageIndex.value = index
  editingMessageContent.value = msg.content
  nextTick(() => {
    const textarea = document.querySelector('.edit-textarea') as HTMLTextAreaElement
    if (textarea) {
      textarea.focus()
      textarea.select()
    }
  })
}

// 取消编辑消息
const cancelMessageEdit = () => {
  editingMessageIndex.value = undefined
  editingMessageContent.value = ''
}

// 保存编辑的消息并重新发送
const saveMessageEdit = async (index: number) => {
  const newContent = editingMessageContent.value.trim()
  if (!newContent) {
    cancelMessageEdit()
    return
  }

  // 更新消息内容
  messages.value[index].content = newContent
  cancelMessageEdit()

  // 删除该用户消息之后的助手回复（如果有的话）
  if (index < messages.value.length - 1 && messages.value[index + 1].role === 'assistant') {
    messages.value = messages.value.slice(0, index + 1)
  }

  saveState()

  // 重新发送消息获取回答
  isSending.value = true

  try {
    const assistantIndex = messages.value.length
    messages.value.push({
      role: 'assistant',
      content: '',
      sources: undefined,
      search_results: undefined,
      thinkingSteps: undefined
    })
    scrollToBottom()

    if (useAgentMode.value) {
      // Agent模式
      const result = await agentAPI.sendMessageStream(
        {
          message: newContent,
          session_id: currentSessionId.value,
          kb_ids: selectedKbIds.value.length > 0 ? selectedKbIds.value : undefined,
          use_web_search: useWebSearch.value,
          show_thinking: true
        },
        (chunk) => {
          if (chunk.type === 'chunk' && chunk.content) {
            messages.value[assistantIndex].content += chunk.content
            scrollToBottom()
          } else if (chunk.type === 'thought') {
            if (!messages.value[assistantIndex].thinkingSteps) {
              messages.value[assistantIndex].thinkingSteps = []
            }
            messages.value[assistantIndex].thinkingSteps!.push({
              type: 'thought',
              content: chunk.content || ''
            })
            scrollToBottom()
          } else if (chunk.type === 'tool_call') {
            if (!messages.value[assistantIndex].thinkingSteps) {
              messages.value[assistantIndex].thinkingSteps = []
            }
            messages.value[assistantIndex].thinkingSteps!.push({
              type: 'tool_call',
              content: chunk.content || '',
              tool_name: chunk.tool_name,
              tool_args: chunk.tool_args
            })
            scrollToBottom()
          } else if (chunk.type === 'tool_result') {
            if (!messages.value[assistantIndex].thinkingSteps) {
              messages.value[assistantIndex].thinkingSteps = []
            }
            messages.value[assistantIndex].thinkingSteps!.push({
              type: 'tool_result',
              content: chunk.content || '',
              tool_name: chunk.tool_name
            })
            scrollToBottom()
          } else if (chunk.type === 'error') {
            console.error('Stream error:', chunk.message)
            messages.value[assistantIndex].content = '抱歉，发生了错误，请稍后重试。'
          }
        }
      )

      currentSessionId.value = result.sessionId
      messages.value[assistantIndex].thinkingSteps = result.thinkingSteps
      // 保存搜索结果和来源
      if (result.searchResults && result.searchResults.length > 0) {
        messages.value[assistantIndex].search_results = result.searchResults
      }
      if (result.sources && result.sources.length > 0) {
        messages.value[assistantIndex].sources = result.sources
      }
    } else {
      // 传统RAG模式
      const result = await chatAPI.sendMessageStream(
        {
          message: newContent,
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
    }

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

// 再次生成回答
const regenerateResponse = async (assistantIndex: number) => {
  // 找到对应的用户消息
  const userIndex = assistantIndex - 1
  if (userIndex < 0 || messages.value[userIndex].role !== 'user') return

  const userMessage = messages.value[userIndex].content

  // 删除当前及之后的消息
  messages.value = messages.value.slice(0, userIndex + 1)
  saveState()

  // 重新发送
  isSending.value = true

  try {
    const newAssistantIndex = messages.value.length
    messages.value.push({
      role: 'assistant',
      content: '',
      sources: undefined,
      search_results: undefined,
      thinkingSteps: undefined
    })
    scrollToBottom()

    if (useAgentMode.value) {
      // Agent模式
      const result = await agentAPI.sendMessageStream(
        {
          message: userMessage,
          session_id: currentSessionId.value,
          kb_ids: selectedKbIds.value.length > 0 ? selectedKbIds.value : undefined,
          use_web_search: useWebSearch.value,
          show_thinking: true
        },
        (chunk) => {
          if (chunk.type === 'chunk' && chunk.content) {
            messages.value[newAssistantIndex].content += chunk.content
            scrollToBottom()
          } else if (chunk.type === 'thought') {
            if (!messages.value[newAssistantIndex].thinkingSteps) {
              messages.value[newAssistantIndex].thinkingSteps = []
            }
            messages.value[newAssistantIndex].thinkingSteps!.push({
              type: 'thought',
              content: chunk.content || ''
            })
            scrollToBottom()
          } else if (chunk.type === 'tool_call') {
            if (!messages.value[newAssistantIndex].thinkingSteps) {
              messages.value[newAssistantIndex].thinkingSteps = []
            }
            messages.value[newAssistantIndex].thinkingSteps!.push({
              type: 'tool_call',
              content: chunk.content || '',
              tool_name: chunk.tool_name,
              tool_args: chunk.tool_args
            })
            scrollToBottom()
          } else if (chunk.type === 'tool_result') {
            if (!messages.value[newAssistantIndex].thinkingSteps) {
              messages.value[newAssistantIndex].thinkingSteps = []
            }
            messages.value[newAssistantIndex].thinkingSteps!.push({
              type: 'tool_result',
              content: chunk.content || '',
              tool_name: chunk.tool_name
            })
            scrollToBottom()
          } else if (chunk.type === 'error') {
            console.error('Stream error:', chunk.message)
            messages.value[newAssistantIndex].content = '抱歉，发生了错误，请稍后重试。'
          }
        }
      )

      currentSessionId.value = result.sessionId
      messages.value[newAssistantIndex].thinkingSteps = result.thinkingSteps
      // 保存搜索结果和来源
      if (result.searchResults && result.searchResults.length > 0) {
        messages.value[newAssistantIndex].search_results = result.searchResults
      }
      if (result.sources && result.sources.length > 0) {
        messages.value[newAssistantIndex].sources = result.sources
      }
    } else {
      // 传统RAG模式
      const result = await chatAPI.sendMessageStream(
        {
          message: userMessage,
          session_id: currentSessionId.value,
          kb_ids: selectedKbIds.value,
          use_web_search: useWebSearch.value
        },
        (chunk) => {
          if (chunk.type === 'chunk' && chunk.content) {
            messages.value[newAssistantIndex].content += chunk.content
            scrollToBottom()
          } else if (chunk.type === 'error') {
            console.error('Stream error:', chunk.message)
            messages.value[newAssistantIndex].content = '抱歉，发生了错误，请稍后重试。'
          }
        }
      )

      currentSessionId.value = result.sessionId
      messages.value[newAssistantIndex].sources = result.sources
      messages.value[newAssistantIndex].search_results = result.searchResults
    }

    saveState()
    await loadSessions()
  } catch (error) {
    console.error('Regenerate error:', error)
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
  width: var(--nav-rail-width);
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-4) 0;
  gap: var(--space-2);
  flex-shrink: 0;
}

.nav-rail-btn {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: var(--radius-lg);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--duration-normal) var(--ease-soft);
  text-decoration: none;
  position: relative;
}

.nav-rail-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: var(--color-primary-light);
  opacity: 0;
  transform: scale(0.8);
  transition: all var(--duration-normal) var(--ease-spring);
}

.nav-rail-btn:hover {
  color: var(--text-primary);
}

.nav-rail-btn:hover::before {
  opacity: 1;
  transform: scale(1);
}

.nav-rail-btn.router-link-active {
  color: var(--color-primary);
}

.nav-rail-btn.router-link-active::before {
  opacity: 1;
  transform: scale(1);
}

.nav-rail-btn svg {
  width: 22px;
  height: 22px;
  fill: currentColor;
  position: relative;
  z-index: 1;
}

/* 侧边栏 */
.chat-sidebar {
  width: var(--sidebar-width);
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

.sidebar-header {
  padding: var(--space-5);
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

/* 主内容区 */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.chat-header {
  height: var(--header-height);
  padding: 0 var(--space-8);
  display: flex;
  align-items: center;
  border-bottom: 1px solid var(--border-subtle);
  background: rgba(250, 248, 245, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.header-title {
  font-family: var(--font-display);
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0;
  letter-spacing: -0.01em;
}

/* 消息区域 */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-8);
}

/* 欢迎屏幕 */
.welcome-screen {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  padding: var(--space-8);
}

.welcome-title {
  font-family: var(--font-display);
  font-size: var(--text-4xl);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-3);
  letter-spacing: -0.02em;
}

.welcome-desc {
  font-size: var(--text-base);
  color: var(--text-secondary);
  margin: 0 0 var(--space-10);
}

.welcome-tips {
  display: flex;
  flex-direction: row;
  gap: var(--space-4);
  max-width: 800px;
}

.tip-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-5);
  background: var(--bg-elevated);
  border-radius: var(--radius-xl);
  border: 1px solid var(--border-subtle);
  text-align: center;
  flex: 1;
  transition: all var(--duration-normal) var(--ease-soft);
}

.tip-item:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
}

.tip-icon {
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary-light);
  border-radius: var(--radius-xl);
  flex-shrink: 0;
}

.tip-icon svg {
  width: 26px;
  height: 26px;
  fill: var(--color-primary);
}

.tip-icon-accent {
  background: var(--color-accent-light);
}

.tip-icon-accent svg {
  fill: var(--color-accent);
}

.tip-icon-warm {
  background: var(--color-warning-light);
}

.tip-icon-warm svg {
  fill: var(--color-warning);
}

.tip-text {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.tip-title {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.tip-desc {
  font-size: var(--text-xs);
  color: var(--text-muted);
}

.messages-container {
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
}

.message {
  display: flex;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
  animation: slideUp var(--duration-normal) var(--ease-spring);
}

.message.user {
  justify-content: flex-end;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
}

.user .message-avatar {
  display: none;
}

.message.assistant .message-avatar {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-subtle);
}

.message.assistant .message-avatar svg {
  width: 18px;
  height: 18px;
  fill: var(--text-secondary);
}

.message-content {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.message.user .message-content {
  align-items: flex-end;
}

.message-wrapper {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: var(--space-2);
}

.message.user .message-wrapper {
  align-items: flex-end;
}

.message-text {
  padding: var(--space-4) var(--space-5);
  border-radius: var(--radius-xl);
  font-size: var(--text-sm);
  line-height: 1.7;
  max-width: 600px;
}

.message.user .message-text {
  background: var(--gradient-accent);
  color: white;
  border-bottom-right-radius: var(--radius-lg);
  box-shadow: 0 2px 8px rgba(196, 125, 94, 0.2);
}

.message.assistant .message-text {
  background: var(--bg-elevated);
  color: var(--text-primary);
  border: 1px solid var(--border-subtle);
  border-bottom-left-radius: var(--radius-lg);
}

.message-sources {
  margin-top: var(--space-2);
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  align-items: center;
  padding: 0 var(--space-1);
}

.sources-label {
  font-size: var(--text-xs);
  color: var(--text-muted);
}

.source-tag {
  font-size: var(--text-xs);
  padding: var(--space-1) var(--space-3);
  background: var(--bg-tertiary);
  border-radius: var(--radius-full);
  color: var(--text-secondary);
}

/* 联网搜索来源链接 */
.web-sources {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-2);
}

.source-link {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--text-xs);
  padding: var(--space-1) var(--space-3);
  background: var(--bg-tertiary);
  border-radius: var(--radius-full);
  color: var(--color-primary);
  text-decoration: none;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  transition: all var(--duration-fast);
}

.source-link:hover {
  background: var(--color-primary);
  color: white;
}

.source-link .link-icon {
  width: 12px;
  height: 12px;
  flex-shrink: 0;
}

/* 消息操作按钮 */
.message.assistant .message-actions {
  display: flex;
  gap: var(--space-1);
  opacity: 1;
}

.message.user .message-actions {
  display: flex;
  gap: var(--space-1);
  opacity: 0;
  transition: opacity var(--duration-fast);
}

.message.user:hover .message-actions {
  opacity: 1;
}

.action-icon {
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

.action-icon:hover {
  background: var(--bg-hover);
  border-color: var(--border-strong);
  color: var(--text-primary);
  transform: translateY(-1px);
}

.action-icon svg {
  width: 14px;
  height: 14px;
  fill: currentColor;
}

/* 消息编辑框 */
.message-edit-box {
  width: 100%;
}

.edit-textarea {
  width: 100%;
  min-height: 80px;
  padding: var(--space-3);
  background: var(--bg-elevated);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  color: var(--text-primary);
  font-size: var(--text-base);
  line-height: 1.5;
  resize: vertical;
  transition: border-color var(--duration-fast);
}

.edit-textarea:focus {
  outline: none;
  border-color: var(--color-primary);
}

.edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-2);
  margin-top: var(--space-2);
}

.edit-btn {
  padding: var(--space-1) var(--space-3);
  font-size: var(--text-sm);
  font-weight: 500;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--duration-fast);
}

.edit-btn.cancel {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-default);
  color: var(--text-secondary);
}

.edit-btn.cancel:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.edit-btn.save {
  background: var(--color-primary);
  border: 1px solid var(--color-primary);
  color: white;
}

.edit-btn.save:hover {
  opacity: 0.9;
}

/* 打字指示器 */
.typing-indicator {
  display: inline-flex;
  gap: 5px;
  padding: var(--space-2);
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: var(--color-primary);
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

/* 输入区域 */
.chat-input-area {
  padding: var(--space-5) var(--space-8) var(--space-8);
  background: linear-gradient(to top, var(--bg-primary) 70%, transparent);
}

.input-wrapper {
  max-width: 800px;
  margin: 0 auto;
}

.input-box {
  display: flex;
  flex-direction: column;
  background: var(--bg-elevated);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-2xl);
  padding: var(--space-3) var(--space-4);
  transition: all var(--duration-normal) var(--ease-soft);
  box-shadow: var(--shadow-sm);
}

.input-box:focus-within {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-md), 0 0 0 3px var(--color-primary-light);
}

.input-box .textarea {
  flex: 1;
  background: transparent;
  border: none;
  padding: var(--space-2);
  resize: none;
  font-size: var(--text-base);
  min-height: 24px;
}

.input-box .textarea:focus {
  box-shadow: none;
}

/* 底部工具栏 */
.input-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: var(--space-2);
  margin-top: var(--space-2);
  border-top: 1px solid var(--border-subtle);
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.toolbar-right {
  display: flex;
  align-items: center;
}

.toolbar-btn {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  background: transparent;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  color: var(--text-secondary);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-soft);
}

.toolbar-btn:hover {
  background: var(--bg-hover);
  border-color: var(--border-strong);
  color: var(--text-primary);
}

.toolbar-btn.active {
  background: var(--color-primary-light);
  border-color: var(--color-primary);
  color: var(--color-primary-dark);
}

.toolbar-btn.agent-mode-btn.active {
  background: linear-gradient(135deg, #e0e7ff 0%, #f0f4ff 100%);
  border-color: #6366f1;
  color: #4f46e5;
}

.toolbar-btn svg {
  width: 18px;
  height: 18px;
  fill: currentColor;
}

.dropdown-arrow {
  width: 16px !important;
  height: 16px !important;
  transition: transform var(--duration-fast) var(--ease-soft);
}

.dropdown-arrow.open {
  transform: rotate(180deg);
}

/* 知识库下拉菜单 */
.kb-dropdown {
  position: relative;
}

.kb-dropdown-menu {
  position: absolute;
  bottom: calc(100% + var(--space-2));
  left: 0;
  min-width: 200px;
  max-width: 280px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  overflow: hidden;
  animation: slideUp var(--duration-normal) var(--ease-spring);
  z-index: var(--z-dropdown);
}

.dropdown-header {
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--text-muted);
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-subtle);
}

.dropdown-empty {
  padding: var(--space-4);
  text-align: center;
  font-size: var(--text-sm);
  color: var(--text-muted);
}

.dropdown-list {
  max-height: 240px;
  overflow-y: auto;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  cursor: pointer;
  transition: background var(--duration-fast);
}

.dropdown-item:hover {
  background: var(--bg-hover);
}

.dropdown-item.selected {
  background: var(--color-primary-light);
}

.dropdown-item input[type="checkbox"] {
  display: none;
}

.item-check {
  width: 18px;
  height: 18px;
  border: 2px solid var(--border-default);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--duration-fast);
  flex-shrink: 0;
}

.dropdown-item.selected .item-check {
  background: var(--color-primary);
  border-color: var(--color-primary);
}

.dropdown-item.selected .item-check::after {
  content: '';
  width: 6px;
  height: 10px;
  border: 2px solid white;
  border-top: none;
  border-left: none;
  transform: rotate(45deg) translateY(-1px);
}

.item-name {
  font-size: var(--text-sm);
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.send-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--gradient-accent);
  border: none;
  border-radius: var(--radius-lg);
  color: white;
  cursor: pointer;
  transition: all var(--duration-normal) var(--ease-soft);
  box-shadow: 0 2px 8px rgba(196, 125, 94, 0.25);
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 4px 16px rgba(196, 125, 94, 0.35);
}

.send-btn:active:not(:disabled) {
  transform: scale(0.98);
}

.send-btn:disabled {
  opacity: 0.4;
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
    width: 56px;
  }

  .nav-rail-btn {
    width: 40px;
    height: 40px;
  }

  .nav-rail-btn svg {
    width: 20px;
    height: 20px;
  }

  .chat-sidebar {
    position: fixed;
    left: 56px;
    top: 0;
    bottom: 0;
    z-index: var(--z-modal);
    transform: translateX(-100%);
    transition: transform var(--duration-normal) var(--ease-spring);
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
    left: 56px;
    background: rgba(61, 54, 50, 0.3);
    backdrop-filter: blur(4px);
    z-index: calc(var(--z-modal) - 1);
  }

  .chat-messages {
    padding: var(--space-5);
  }

  .chat-input-area {
    padding: var(--space-4) var(--space-5) var(--space-5);
  }

  .welcome-title {
    font-size: var(--text-3xl);
  }

  .welcome-tips {
    flex-direction: column;
    max-width: 280px;
  }

  .tip-item {
    flex-direction: row;
    text-align: left;
    padding: var(--space-4);
  }

  .tip-icon {
    width: 44px;
    height: 44px;
  }

  .tip-icon svg {
    width: 22px;
    height: 22px;
  }

  .toolbar-btn span {
    display: none;
  }

  .kb-dropdown-menu {
    left: auto;
    right: 0;
    min-width: 180px;
  }

  .message-actions {
    opacity: 1;
  }

  .message-text {
    max-width: calc(100vw - 140px);
  }
}

/* 复制成功提示 */
.copy-toast {
  position: fixed;
  bottom: 100px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-5);
  background: var(--text-primary);
  color: var(--bg-primary);
  border-radius: var(--radius-full);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  box-shadow: var(--shadow-lg);
  z-index: var(--z-toast);
}

.copy-toast svg {
  width: 18px;
  height: 18px;
  fill: currentColor;
}

/* Toast 动画 */
.toast-enter-active,
.toast-leave-active {
  transition: all var(--duration-normal) var(--ease-spring);
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(20px);
}
</style>
