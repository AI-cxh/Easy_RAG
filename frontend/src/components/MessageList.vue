<template>
  <div class="message-list">
    <div
      v-for="(message, index) in messages"
      :key="index"
      :class="['message', message.role]"
    >
      <div class="message-avatar">
        <div v-if="message.role === 'user'" class="avatar user-avatar">
          <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
          </svg>
        </div>
        <div v-else class="avatar assistant-avatar">
          <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
          </svg>
        </div>
      </div>
      <div class="message-body">
        <div class="message-content" v-html="renderMessage(message.content)" />
        <div v-if="message.sources && message.sources.length" class="message-sources">
          <svg class="source-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
          </svg>
          <span class="source-label">来源:</span>
          {{ message.sources.join(', ') }}
        </div>
        <div v-if="message.search_results && message.search_results.length" class="message-search-results">
          <svg class="search-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
          </svg>
          <span class="search-label">搜索结果:</span>
          <div class="search-results">
            <a
              v-for="(result, i) in message.search_results"
              :key="i"
              :href="result.url"
              target="_blank"
              class="search-result-link"
            >
              {{ result.title }}
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'

interface Message {
  role: 'user' | 'assistant'
  content: string
  sources?: string[]
  search_results?: Array<{ title: string; url: string; snippet?: string }>
}

interface Props {
  messages: Message[]
}

defineProps<Props>()

// 配置 marked
marked.setOptions({
  highlight: (code: string, lang: string) => {
    const language = hljs.getLanguage(lang) ? lang : 'plaintext'
    return hljs.highlight(code, { language }).value
  },
  breaks: true,
  gfm: true
})

const renderMessage = (content: string) => {
  return marked.parse(content)
}
</script>

<style scoped>
.message-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.message {
  display: flex;
  gap: 12px;
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-avatar {
  background-color: #6c757d;
  color: white;
}

.assistant-avatar {
  background-color: var(--primary-color);
  color: white;
}

.avatar svg {
  width: 20px;
  height: 20px;
  fill: currentColor;
}

.message-body {
  max-width: 80%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.message-content {
  padding: 12px 16px;
  border-radius: 16px;
  word-wrap: break-word;
  overflow-wrap: break-word;
  line-height: 1.6;
}

.message.user .message-content {
  background-color: var(--user-msg-bg);
  color: white;
  border-bottom-right-radius: 4px;
}

.message.assistant .message-content {
  background-color: var(--assistant-msg-bg);
  border: 1px solid var(--border-color);
  border-bottom-left-radius: 4px;
}

.message-sources,
.message-search-results {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-secondary);
  padding: 8px 0;
}

.source-icon,
.search-icon {
  width: 14px;
  height: 14px;
  fill: currentColor;
  flex-shrink: 0;
}

.search-results {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.search-result-link {
  color: var(--primary-color);
  text-decoration: none;
  opacity: 0.9;
}

.search-result-link:hover {
  text-decoration: underline;
  opacity: 1;
}

/* Markdown 样式覆盖 */
.message :deep(.markdown) {
  font-size: 14px;
}

.message :deep(pre) {
  background-color: rgba(0, 0, 0, 0.1);
}

.message.assistant :deep(pre) {
  background-color: #f6f8fa;
}

.message :deep(code) {
  background-color: rgba(0, 0, 0, 0.15);
}

.message.assistant :deep(code) {
  background-color: #f6f8fa;
}

.message :deep(a) {
  color: inherit;
  text-decoration: underline;
}

.message :deep(a:hover) {
  text-decoration: none;
}
</style>
