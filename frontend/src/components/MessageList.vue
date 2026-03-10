<template>
  <div class="message-list">
    <div
      v-for="(message, index) in messages"
      :key="index"
      :class="['message', message.role]"
    >
      <div class="message-content" v-html="renderMessage(message.content)" />
      <div v-if="message.sources && message.sources.length" class="message-sources">
        <strong>来源:</strong>
        {{ message.sources.join(', ') }}
      </div>
      <div v-if="message.search_results && message.search_results.length" class="message-search-results">
        <strong>搜索结果:</strong>
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
  gap: 16px;
  padding: 20px;
}

.message {
  max-width: 80%;
  border-radius: 12px;
  padding: 12px 16px;
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.message.user {
  align-self: flex-end;
  background-color: var(--user-msg-bg);
  color: white;
  border-bottom-right-radius: 4px;
}

.message.assistant {
  align-self: flex-start;
  background-color: var(--assistant-msg-bg);
  border: 1px solid var(--border-color);
  border-bottom-left-radius: 4px;
}

.message-content {
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.message-sources {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  font-size: 12px;
  opacity: 0.9;
}

.message-search-results {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  font-size: 12px;
}

.search-results {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 4px;
}

.search-result-link {
  color: inherit;
  text-decoration: underline;
  opacity: 0.9;
}

.search-result-link:hover {
  opacity: 1;
  text-decoration: none;
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
