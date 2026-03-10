<template>
  <div class="chat-page">
    <div class="sidebar">
      <div class="sidebar-header">
        <h2>聊天选项</h2>
      </div>
      <KnowledgeSelector
        v-model:selected-kb-ids="selectedKbIds"
        v-model:use-web-search="useWebSearch"
        ref="knowledgeSelectorRef"
      />
      <div class="new-chat-section">
        <button class="btn btn-primary" @click="startNewChat">新建对话</button>
      </div>
    </div>
    <div class="chat-area">
      <ChatBoard
        ref="chatBoardRef"
        :is-loading="isLoading"
        @send="handleSend"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import ChatBoard from '../components/ChatBoard.vue'
import KnowledgeSelector from '../components/KnowledgeSelector.vue'
import { chatAPI } from '../api/client'

const router = useRouter()
const chatBoardRef = ref()
const knowledgeSelectorRef = ref()
const selectedKbIds = ref<number[]>([])
const useWebSearch = ref(false)
const isLoading = ref(false)
const currentSessionId = ref<number>()

const handleSend = async ({ message }: { message: string }) => {
  if (isLoading.value) return

  // 添加用户消息
  chatBoardRef.value?.addMessage({
    role: 'user',
    content: message
  })

  isLoading.value = true

  try {
    const response = await chatAPI.sendMessage({
      message,
      session_id: currentSessionId.value,
      kb_ids: selectedKbIds.value,
      use_web_search: useWebSearch.value
    })

    currentSessionId.value = response.session_id

    // 添加助手消息
    chatBoardRef.value?.addMessage({
      role: 'assistant',
      content: response.response,
      sources: response.sources,
      search_results: response.search_results
    })
  } catch (error) {
    console.error('Chat error:', error)
    chatBoardRef.value?.addMessage({
      role: 'assistant',
      content: '抱歉，发生了错误，请稍后重试。'
    })
  } finally {
    isLoading.value = false
  }
}

const startNewChat = () => {
  currentSessionId.value = undefined
  chatBoardRef.value?.clearMessages()
}
</script>

<style scoped>
.chat-page {
  display: flex;
  gap: 20px;
  height: calc(100vh - 108px);
}

.sidebar {
  width: 300px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.sidebar-header {
  background-color: var(--card-bg);
  border-radius: 8px;
  padding: 16px;
  box-shadow: var(--shadow-sm);
}

.sidebar-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.new-chat-section {
  background-color: var(--card-bg);
  border-radius: 8px;
  padding: 16px;
  box-shadow: var(--shadow-sm);
}

.new-chat-section .btn {
  width: 100%;
}

.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: var(--card-bg);
  border-radius: 8px;
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

@media (max-width: 768px) {
  .chat-page {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    max-height: 400px;
  }
}
</style>
