<template>
  <div class="chat-board">
    <MessageList :messages="messages" />
    <div class="input-area">
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
        <span v-if="!isLoading">发送</span>
        <span v-else><span class="spinner"></span></span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import MessageList from './MessageList.vue'

interface Message {
  role: 'user' | 'assistant'
  content: string
  sources?: string[]
  search_results?: Array<{ title: string; url: string; snippet?: string }>
}

interface Props {
  isLoading: boolean
  sessionId?: number
}

interface Emits {
  (event: 'send', data: { message: string; sessionId?: number }): void
}

defineProps<Props>()
const emit = defineEmits<Emits>()

const inputMessage = ref('')
const textareaRef = ref<HTMLTextAreaElement>()
const messages = ref<Message[]>([])

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}

const autoResize = () => {
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto'
    textareaRef.value.style.height = textareaRef.value.scrollHeight + 'px'
  }
}

const sendMessage = () => {
  if (!inputMessage.value.trim()) return

  const message = inputMessage.value
  inputMessage.value = ''

  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto'
  }

  emit('send', { message })
}

const addMessage = (message: Message) => {
  messages.value.push(message)
}

const clearMessages = () => {
  messages.value = []
}

defineExpose({
  addMessage,
  clearMessages
})
</script>

<style scoped>
.chat-board {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.message-list {
  flex: 1;
  overflow-y: auto;
}

.input-area {
  display: flex;
  gap: 10px;
  padding: 16px;
  background-color: var(--card-bg);
  border-top: 1px solid var(--border-color);
  align-items: flex-end;
}

.message-input {
  flex: 1;
  resize: none;
  min-height: 44px;
  max-height: 200px;
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.5;
  transition: border-color 0.2s;
}

.message-input:focus {
  outline: none;
  border-color: var(--primary-color);
}

.message-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.send-button {
  height: 44px;
  min-width: 80px;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
