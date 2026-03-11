<template>
  <div class="chat-page">
    <!-- 左侧会话列表 -->
    <SessionSidebar
      :sessions="sessions"
      :current-session-id="currentSessionId"
      :loading="loadingSessions"
      @select="loadSession"
      @delete="deleteSession"
      @rename="renameSession"
      @new-chat="newChat"
    />

    <!-- 右侧对话区域 -->
    <div class="chat-area">
      <ChatHeader />

      <MessagePanel
        :messages="messages"
        :has-interacted="hasUserInteracted"
      />

      <ComposerBar
        :use-web-search="useWebSearch"
        :selected-kb-ids="selectedKbIds"
        :knowledge-bases="knowledgeBases"
        :loading-kbs="loadingKbs"
        :disabled="isSending"
        @send="sendMessage"
        @toggle-web-search="useWebSearch = !useWebSearch"
        @toggle-kb="toggleKb"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import SessionSidebar from '../components/chat/SessionSidebar.vue'
import ChatHeader from '../components/chat/ChatHeader.vue'
import MessagePanel from '../components/chat/MessagePanel.vue'
import ComposerBar from '../components/chat/ComposerBar.vue'
import { chatAPI, knowledgeAPI } from '../api/client'

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

const selectedKbIds = ref<number[]>([])
const useWebSearch = ref(false)
const knowledgeBases = ref<any[]>([])
const loadingKbs = ref(false)

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
  loadingKbs.value = true
  try {
    knowledgeBases.value = await knowledgeAPI.getAll()
  } catch (error) {
    console.error('Failed to load knowledge bases:', error)
  } finally {
    loadingKbs.value = false
  }
}

// 会话操作
const loadSession = async (sessionId: number) => {
  try {
    const result = await chatAPI.getSession(sessionId)
    currentSessionId.value = sessionId
    messages.value = result.messages || []
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
    }
    await loadSessions()
    saveState()
  } catch (error) {
    console.error('Failed to delete session:', error)
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

// 发送消息
const sendMessage = async (message: string) => {
  hasUserInteracted.value = true

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: message
  })
  saveState()

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
.chat-page {
  display: flex;
  height: 100vh;
  background-color: var(--bg-base);
}

.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 移动端响应式 */
@media (max-width: 768px) {
  .chat-page {
    flex-direction: column;
  }
}
</style>
