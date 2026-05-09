<template>
  <Transition name="drawer">
    <div v-if="visible" class="memory-drawer-overlay" @click.self="$emit('close')">
      <div class="memory-drawer">
        <div class="drawer-header">
          <div>
            <h3 class="drawer-title">
              <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" class="title-icon">
                <path d="M12 2a7 7 0 0 0-7 7c0 2.38 1.19 4.48 3 5.74V18a2 2 0 0 0 2 2h4a2 2 0 0 0 2-2v-3.26A6.98 6.98 0 0 0 12 2zm2 15.5V18h-4v-.5h4zM14.85 13H9.15A5 5 0 1 1 14.85 13z"/>
              </svg>
              个人长期记忆
            </h3>
            <p class="drawer-subtitle">mem0 自动沉淀的跨会话记忆</p>
          </div>
          <div class="header-actions">
            <button class="icon-btn" :disabled="loading" @click="$emit('refresh')" title="刷新">
              <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M17.65 6.35A7.95 7.95 0 0 0 12 4V1L7 6l5 5V6a6 6 0 1 1-5.65 8H4.26A8 8 0 1 0 17.65 6.35z"/>
              </svg>
            </button>
            <button class="icon-btn" @click="$emit('close')" title="关闭">
              <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
              </svg>
            </button>
          </div>
        </div>

        <div class="drawer-content">
          <div v-if="loading" class="empty-state">
            <span class="spinner"></span>
            <p>正在加载长期记忆...</p>
          </div>

          <div v-else-if="error" class="empty-state error-state">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2 1 21h22L12 2zm1 16h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
            </svg>
            <p>{{ error }}</p>
          </div>

          <div v-else-if="memories.length === 0" class="empty-state">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 3a6 6 0 0 0-3 11.2V17a1 1 0 0 0 1 1h4a1 1 0 0 0 1-1v-2.8A6 6 0 0 0 12 3zm2 13h-4v-.8l-.46-.29A4 4 0 1 1 14.46 15l-.46.29V16zM10 20h4v2h-4v-2z"/>
            </svg>
            <p>还没有长期记忆</p>
          </div>

          <div v-else class="memory-list">
            <article v-for="memory in memories" :key="memory.id" class="memory-item">
              <div class="memory-meta">
                <span class="memory-type">{{ sessionTypeLabel(memory.metadata?.session_type) }}</span>
                <span v-if="memory.metadata?.project_id" class="memory-badge">项目 {{ memory.metadata.project_id }}</span>
                <span v-if="memory.metadata?.session_id" class="memory-badge">会话 {{ memory.metadata.session_id }}</span>
              </div>
              <p class="memory-content">{{ memory.memory }}</p>
              <div class="memory-footer">
                <span class="memory-time">{{ formatMemoryTime(memory.updated_at || memory.created_at) }}</span>
                <button
                  class="delete-memory-btn"
                  :disabled="deletingId === memory.id"
                  @click="$emit('delete', memory.id)"
                >
                  {{ deletingId === memory.id ? '删除中...' : '删除' }}
                </button>
              </div>
            </article>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import type { UserMemory } from '../api/client'

interface Props {
  visible: boolean
  memories: UserMemory[]
  loading?: boolean
  deletingId?: string
  error?: string
}

withDefaults(defineProps<Props>(), {
  loading: false,
  deletingId: '',
  error: ''
})

defineEmits<{
  (e: 'close'): void
  (e: 'refresh'): void
  (e: 'delete', memoryId: string): void
}>()

const sessionTypeLabel = (sessionType?: string) => {
  if (sessionType === 'agentic') return 'Agentic'
  if (sessionType === 'multi_agent') return 'Multi-Agent'
  if (sessionType === 'rag') return 'RAG'
  return '长期记忆'
}

const formatMemoryTime = (time?: string | null) => {
  if (!time) return '时间未知'
  const date = new Date(time)
  if (Number.isNaN(date.getTime())) return '时间未知'
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.memory-drawer-overlay {
  position: fixed;
  inset: 0;
  z-index: var(--z-modal);
  display: flex;
  justify-content: flex-end;
  background: rgba(61, 54, 50, 0.3);
  backdrop-filter: blur(4px);
}

.memory-drawer {
  width: min(460px, 92vw);
  height: 100%;
  background: var(--bg-primary);
  border-left: 1px solid var(--border-default);
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-xl);
}

.drawer-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-4);
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--border-subtle);
  background: var(--bg-elevated);
}

.drawer-title {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin: 0;
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.drawer-subtitle {
  margin: 6px 0 0;
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.title-icon {
  width: 20px;
  height: 20px;
  fill: var(--color-primary);
}

.header-actions {
  display: flex;
  gap: var(--space-1);
}

.icon-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: var(--radius-lg);
  color: var(--text-muted);
  cursor: pointer;
  transition: all var(--duration-fast);
}

.icon-btn:hover:not(:disabled) {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.icon-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.icon-btn svg {
  width: 20px;
  height: 20px;
  fill: currentColor;
}

.drawer-content {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-4);
}

.memory-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.memory-item {
  padding: var(--space-4);
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
}

.memory-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-2);
  margin-bottom: var(--space-3);
}

.memory-type,
.memory-badge {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 0 10px;
  border-radius: 999px;
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
}

.memory-type {
  color: #325c85;
  background: rgba(96, 155, 210, 0.14);
  border: 1px solid rgba(96, 155, 210, 0.24);
}

.memory-badge {
  color: var(--text-secondary);
  background: var(--bg-secondary);
}

.memory-content {
  margin: 0;
  white-space: pre-wrap;
  line-height: 1.65;
  color: var(--text-primary);
}

.memory-footer {
  margin-top: var(--space-4);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
}

.memory-time {
  font-size: var(--text-xs);
  color: var(--text-muted);
}

.delete-memory-btn {
  min-height: 30px;
  padding: 0 12px;
  border-radius: var(--radius-md);
  border: 1px solid rgba(200, 84, 78, 0.24);
  background: rgba(200, 84, 78, 0.08);
  color: #9a332f;
  font-size: var(--text-xs);
  cursor: pointer;
}

.delete-memory-btn:hover:not(:disabled) {
  background: rgba(200, 84, 78, 0.14);
}

.delete-memory-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.empty-state {
  min-height: 240px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-3);
  color: var(--text-muted);
  text-align: center;
}

.empty-state svg {
  width: 44px;
  height: 44px;
  fill: currentColor;
  opacity: 0.5;
}

.error-state {
  color: #9a332f;
}

.spinner {
  width: 26px;
  height: 26px;
  border: 2px solid var(--border-default);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.drawer-enter-active,
.drawer-leave-active {
  transition: opacity var(--duration-normal);
}

.drawer-enter-active .memory-drawer,
.drawer-leave-active .memory-drawer {
  transition: transform var(--duration-normal);
}

.drawer-enter-from,
.drawer-leave-to {
  opacity: 0;
}

.drawer-enter-from .memory-drawer,
.drawer-leave-to .memory-drawer {
  transform: translateX(100%);
}
</style>
