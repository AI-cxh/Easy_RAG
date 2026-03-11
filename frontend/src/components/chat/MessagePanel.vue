<template>
  <div class="message-panel">
    <!-- 欢迎消息 -->
    <div v-if="messages.length === 0 && !hasInteracted" class="welcome-message">
      <div class="avatar avatar-large assistant-avatar">
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
      </div>
      <p class="welcome-text">{{ welcomeText }}</p>
    </div>

    <!-- 消息列表 -->
    <MessageList v-else :messages="messages" />
  </div>
</template>

<script setup lang="ts">
import MessageList from '../MessageList.vue'

interface Message {
  role: 'user' | 'assistant'
  content: string
  sources?: string[]
  search_results?: Array<{ title: string; url: string; snippet?: string }>
}

interface Props {
  messages: Message[]
  hasInteracted: boolean
  welcomeText?: string
}

withDefaults(defineProps<Props>(), {
  welcomeText: '您好，我是您的私人助手布妞，可通过上传文件或联网搜索为您解答问题。'
})
</script>

<style scoped>
.message-panel {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-2xl);
  display: flex;
  flex-direction: column;
}

.welcome-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px var(--spacing-xl);
  text-align: center;
  flex: 1;
}

.avatar-large {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background-color: var(--color-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--spacing-2xl);
}

.avatar-large svg {
  width: 48px;
  height: 48px;
  fill: currentColor;
}

.welcome-text {
  font-size: var(--font-size-xl);
  color: var(--text-primary);
  max-width: 500px;
  line-height: var(--line-height-relaxed);
}

@media (max-width: 768px) {
  .message-panel {
    padding: var(--spacing-lg);
  }
}
</style>
