<template>
  <div class="session-sidebar">
    <div class="sidebar-header">
      <h2>对话历史</h2>
      <button class="btn-icon" @click="$emit('newChat')" title="开启新对话">
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
        </svg>
      </button>
    </div>

    <div v-if="loading" class="loading">
      <span class="spinner"></span>
    </div>

    <div v-else class="session-list">
      <div
        v-for="session in sessions"
        :key="session.id"
        :class="['session-item', { 'active': currentSessionId === session.id }]"
        @click="$emit('select', session.id)"
      >
        <div class="session-content">
          <div v-if="editingId === session.id" class="session-edit">
            <input
              v-model="editingTitle"
              ref="editInputRef"
              class="edit-input"
              @blur="saveEdit(session.id)"
              @keydown.enter="saveEdit(session.id)"
              @keydown.esc="cancelEdit"
            />
          </div>
          <div v-else class="session-info">
            <div class="session-title">{{ session.title }}</div>
            <div class="session-meta">{{ formatDate(session.created_at) }}</div>
          </div>
        </div>
        <div class="session-actions">
          <button
            v-if="editingId !== session.id"
            class="btn-icon edit-btn"
            @click.stop="startEdit(session)"
            title="重命名"
          >
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
            </svg>
          </button>
          <button class="btn-icon delete-btn" @click.stop="$emit('delete', session.id)">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
            </svg>
          </button>
        </div>
      </div>

      <div v-if="sessions.length === 0" class="empty-state">
        暂无对话历史
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface ChatSession {
  id: number
  title: string
  created_at: string
}

interface Props {
  sessions: ChatSession[]
  currentSessionId?: number
  loading: boolean
}

defineProps<Props>()

const emit = defineEmits<{
  (e: 'select', id: number): void
  (e: 'delete', id: number): void
  (e: 'rename', id: number, title: string): void
  (e: 'newChat'): void
}>()

// 编辑相关
const editingId = ref<number>()
const editingTitle = ref('')
const editInputRef = ref<HTMLInputElement>()

const startEdit = (session: ChatSession) => {
  editingId.value = session.id
  editingTitle.value = session.title
  setTimeout(() => {
    editInputRef.value?.focus()
    editInputRef.value?.select()
  }, 0)
}

const saveEdit = (sessionId: number) => {
  if (editingTitle.value.trim()) {
    emit('rename', sessionId, editingTitle.value.trim())
  }
  cancelEdit()
}

const cancelEdit = () => {
  editingId.value = undefined
  editingTitle.value = ''
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days === 0) {
    return '今天 ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  } else if (days === 1) {
    return '昨天'
  } else if (days < 7) {
    return `${days}天前`
  } else {
    return date.toLocaleDateString('zh-CN')
  }
}
</script>

<style scoped>
.session-sidebar {
  width: 280px;
  background-color: var(--bg-card);
  border-right: 1px solid var(--border-base);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-xl);
  border-bottom: 1px solid var(--border-base);
}

.sidebar-header h2 {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.session-list {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-md);
}

.session-item {
  padding: var(--spacing-md);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-normal);
  margin-bottom: var(--spacing-xs);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.session-item:hover {
  background-color: var(--bg-base);
}

.session-item.active {
  background-color: var(--color-primary-light);
}

.session-content {
  flex: 1;
  min-width: 0;
}

.session-title {
  font-size: var(--font-size-base);
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: var(--spacing-xs);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.session-meta {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

.session-actions {
  display: flex;
  gap: var(--spacing-xs);
  opacity: 0;
  transition: opacity var(--transition-normal);
}

.session-item:hover .session-actions {
  opacity: 1;
}

.edit-btn:hover {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
}

.delete-btn:hover {
  background-color: var(--color-danger-light);
  color: var(--color-danger);
}

.session-edit {
  width: 100%;
}

.edit-input {
  width: 100%;
  padding: var(--spacing-xs) var(--spacing-sm);
  border: 1px solid var(--border-base);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-base);
  font-family: inherit;
  background-color: var(--bg-base);
  color: var(--text-primary);
}

.edit-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.loading {
  display: flex;
  justify-content: center;
  padding: var(--spacing-xl);
}

.empty-state {
  text-align: center;
  padding: var(--spacing-3xl) var(--spacing-xl);
  color: var(--text-secondary);
  font-size: var(--font-size-base);
}

/* 移动端响应式 */
@media (max-width: 768px) {
  .session-sidebar {
    position: fixed;
    left: 0;
    top: 60px;
    bottom: 0;
    width: 280px;
    transform: translateX(-100%);
    transition: transform var(--transition-slow);
    z-index: var(--z-dropdown);
  }

  .session-sidebar.open {
    transform: translateX(0);
  }
}
</style>
