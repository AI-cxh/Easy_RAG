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
            <path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>
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
/**
 * 消息渲染组件
 * 渲染链：Markdown -> DOMPurify sanitize -> v-html
 * 安全说明：所有用户输入经过 marked 解析后，通过 DOMPurify 清洗，防止 XSS 攻击
 */
import { marked } from 'marked'
import hljs from 'highlight.js'
import DOMPurify from 'dompurify'
import 'highlight.js/styles/github-dark.css'

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

// 配置 DOMPurify 允许的标签和属性
const ALLOWED_TAGS = [
  'a', 'b', 'i', 'strong', 'em', 'u', 's', 'br', 'p', 'div', 'span',
  'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
  'ul', 'ol', 'li', 'dl', 'dt', 'dd',
  'table', 'thead', 'tbody', 'tr', 'th', 'td',
  'pre', 'code', 'blockquote',
  'hr', 'img'
]

const ALLOWED_ATTR = [
  'href', 'title', 'alt', 'src', 'width', 'height',
  'class', 'id', 'target', 'rel'
]

// 配置 DOMPurify 钩子：为外链添加安全属性
DOMPurify.addHook('afterSanitizeAttributes', (node) => {
  if (node.tagName === 'A') {
    const href = node.getAttribute('href')
    if (href && (href.startsWith('http://') || href.startsWith('https://'))) {
      node.setAttribute('target', '_blank')
      node.setAttribute('rel', 'noopener noreferrer')
    }
  }
})

const renderMessage = (content: string) => {
  // 渲染链：Markdown -> sanitize -> v-html
  const rawHtml = marked.parse(content) as string
  return DOMPurify.sanitize(rawHtml, {
    ALLOWED_TAGS,
    ALLOWED_ATTR
  })
}
</script>

<style scoped>
.message-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
  padding: var(--space-6);
}

.message {
  display: flex;
  gap: var(--space-3);
  animation: fadeIn var(--duration-normal) var(--ease-out);
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
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-avatar {
  background: linear-gradient(135deg, #64748b 0%, #475569 100%);
  color: white;
}

.assistant-avatar {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-accent) 100%);
  color: white;
  box-shadow: var(--shadow-glow-primary);
}

.avatar svg {
  width: 20px;
  height: 20px;
  fill: currentColor;
}

.message-body {
  max-width: 75%;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.message-content {
  padding: var(--space-4);
  border-radius: var(--radius-xl);
  word-wrap: break-word;
  overflow-wrap: break-word;
  line-height: var(--leading-relaxed);
  font-size: var(--text-base);
}

.message.user .message-content {
  background: var(--msg-user-bg);
  color: var(--msg-user-text);
  border-bottom-right-radius: var(--radius-sm);
}

.message.assistant .message-content {
  background: var(--msg-assistant-bg);
  border: 1px solid var(--msg-assistant-border);
  border-bottom-left-radius: var(--radius-sm);
}

.message-sources,
.message-search-results {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-xs);
  color: var(--text-muted);
  padding: var(--space-2) 0;
}

.source-icon,
.search-icon {
  width: 14px;
  height: 14px;
  fill: currentColor;
  flex-shrink: 0;
}

.source-label,
.search-label {
  font-weight: var(--font-medium);
}

.search-results {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.search-result-link {
  color: var(--color-primary);
  text-decoration: none;
  padding: var(--space-1) var(--space-2);
  background: var(--color-primary-light);
  border-radius: var(--radius-sm);
  transition: all var(--duration-fast);
}

.search-result-link:hover {
  background: var(--color-primary);
  color: white;
}

/* Markdown 样式覆盖 */
.message :deep(pre) {
  margin: var(--space-3) 0;
  padding: var(--space-4);
  background: #1e293b;
  border-radius: var(--radius-lg);
  overflow-x: auto;
}

.message.user :deep(pre) {
  background: rgba(0, 0, 0, 0.2);
}

.message :deep(code) {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
}

.message :deep(p) {
  margin: 0 0 var(--space-3);
}

.message :deep(p:last-child) {
  margin-bottom: 0;
}

.message :deep(ul),
.message :deep(ol) {
  margin: var(--space-2) 0;
  padding-left: var(--space-5);
}

.message :deep(li) {
  margin-bottom: var(--space-1);
}

.message :deep(a) {
  color: inherit;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.message.user :deep(a) {
  color: rgba(255, 255, 255, 0.9);
}

.message.assistant :deep(a) {
  color: var(--color-primary);
}

@media (max-width: 768px) {
  .message-list {
    padding: var(--space-4);
    gap: var(--space-4);
  }

  .message-body {
    max-width: 85%;
  }

  .message-content {
    padding: var(--space-3);
  }
}
</style>
