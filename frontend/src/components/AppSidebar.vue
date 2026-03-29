<template>
  <div class="sidebar-wrapper">
    <aside class="chat-sidebar" :class="{ open: sidebarOpen, collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <button class="btn btn-primary new-chat-btn" @click="$emit('newChat')">
          <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
          </svg>
          <span class="btn-text">新对话</span>
        </button>
      </div>

    <div class="sidebar-content">
      <div v-if="loading" class="loading-state">
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
          @click="$emit('selectSession', session.id)"
        >
          <div class="session-content">
            <div class="session-title-row">
              <span class="session-title">{{ session.title }}</span>
              <span
                v-if="isAdmin && session.username && session.username !== user?.username"
                class="user-badge"
              >
                {{ session.username }}
              </span>
            </div>
            <span class="session-time">{{ formatTime(session.created_at) }}</span>
          </div>
          <div class="session-actions" @click.stop>
            <button class="btn-icon btn-icon-sm" @click="startRename(session)" title="重命名">
              <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
              </svg>
            </button>
            <button class="btn-icon btn-icon-sm delete-btn" @click="handleDelete(session.id)" title="删除">
              <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

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
                @keydown.enter="handleRename"
                ref="renameInputRef"
              />
            </div>
          </div>
          <div class="dialog-footer">
            <button class="btn btn-secondary" @click="cancelSessionEdit">取消</button>
            <button class="btn btn-primary" @click="handleRename">保存</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 删除确认对话框 -->
    <Teleport to="body">
      <div v-if="deletingSessionId" class="dialog-overlay" @click.self="cancelDelete">
        <div class="dialog dialog-danger">
          <div class="dialog-header">
            <h3 class="dialog-title">删除对话</h3>
            <button class="dialog-close" @click="cancelDelete">&times;</button>
          </div>
          <div class="dialog-body">
            <p class="dialog-message">确定要删除对话 "<strong>{{ deletingSessionName }}</strong>" 吗？</p>
            <p class="dialog-hint">此操作无法撤销。</p>
          </div>
          <div class="dialog-footer">
            <button class="btn btn-secondary" @click="cancelDelete">取消</button>
            <button class="btn btn-danger" @click="confirmDelete">删除</button>
          </div>
        </div>
      </div>
    </Teleport>
  </aside>

  <!-- 折叠按钮 - 放在外部确保折叠后仍可见 -->
  <button
    class="collapse-btn"
    :class="{ collapsed: sidebarCollapsed }"
    @click="$emit('toggleCollapse')"
    :title="sidebarCollapsed ? '展开侧边栏' : '收起侧边栏'"
  >
    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/>
    </svg>
  </button>
</div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import type { ChatSession } from '../composables/useSession'
import { useAuth } from '../composables/useAuth'

const props = defineProps<{
  sessions: ChatSession[]
  loading: boolean
  currentSessionId?: number
  sidebarOpen: boolean
  sidebarCollapsed: boolean
}>()

const { isAdmin, user } = useAuth()

const emit = defineEmits<{
  (e: 'newChat'): void
  (e: 'selectSession', sessionId: number): void
  (e: 'deleteSession', sessionId: number): void
  (e: 'renameSession', sessionId: number, title: string): void
  (e: 'toggleCollapse'): void
}>()

const editingSessionId = ref<number>()
const editingSessionName = ref('')
const renameInputRef = ref<HTMLInputElement>()

// 删除确认对话框状态
const deletingSessionId = ref<number>()
const deletingSessionName = ref('')

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

const startRename = (session: ChatSession) => {
  editingSessionId.value = session.id
  editingSessionName.value = session.title
  nextTick(() => {
    renameInputRef.value?.focus()
    renameInputRef.value?.select()
  })
}

const cancelSessionEdit = () => {
  editingSessionId.value = undefined
  editingSessionName.value = ''
}

const handleRename = () => {
  if (!editingSessionId.value || !editingSessionName.value.trim()) {
    cancelSessionEdit()
    return
  }
  emit('renameSession', editingSessionId.value, editingSessionName.value.trim())
  cancelSessionEdit()
}

const handleDelete = (sessionId: number) => {
  // 找到会话名称
  const session = props.sessions.find(s => s.id === sessionId)
  deletingSessionId.value = sessionId
  deletingSessionName.value = session?.title || '这个对话'
}

const confirmDelete = () => {
  if (!deletingSessionId.value) return
  emit('deleteSession', deletingSessionId.value)
  cancelDelete()
}

const cancelDelete = () => {
  deletingSessionId.value = undefined
  deletingSessionName.value = ''
}
</script>

<style scoped>
.sidebar-wrapper {
  position: relative;
  display: flex;
  flex-shrink: 0;
}

.chat-sidebar {
  width: clamp(220px, 25vw, 300px);
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

/* 折叠按钮 */
.collapse-btn {
  position: absolute;
  top: 50%;
  left: calc(clamp(220px, 25vw, 300px) - 14px);
  transform: translateY(-50%);
  width: 28px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  color: var(--text-muted);
  cursor: pointer;
  transition: all var(--duration-fast);
  z-index: 10;
  opacity: 0;
}

.sidebar-wrapper:hover .collapse-btn {
  opacity: 1;
}

.collapse-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
  box-shadow: var(--shadow-sm);
}

.collapse-btn svg {
  width: 18px;
  height: 18px;
  fill: currentColor;
  transition: transform var(--duration-normal) var(--ease-spring);
}

.collapse-btn.collapsed {
  left: 0;
  opacity: 1;
}

.collapse-btn.collapsed svg {
  transform: rotate(180deg);
}

.sidebar-header {
  padding: clamp(var(--space-3), 2vw, var(--space-5));
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

.session-title-row {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.session-title {
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

.user-badge {
  font-size: var(--text-xs);
  padding: 1px var(--space-2);
  background: var(--color-accent-light);
  color: var(--color-accent);
  border-radius: var(--radius-full);
  flex-shrink: 0;
  font-weight: var(--font-medium);
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

.btn-icon {
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

.btn-icon:hover {
  background: var(--bg-hover);
  border-color: var(--border-strong);
  color: var(--text-primary);
}

.btn-icon svg {
  width: 14px;
  height: 14px;
  fill: currentColor;
}

.delete-btn:hover {
  color: var(--color-danger);
  border-color: var(--color-danger);
}

/* 对话框样式 */
.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal);
}

.dialog {
  background: var(--bg-elevated);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  width: min(400px, 90vw);
  animation: slideUp var(--duration-normal) var(--ease-spring);
}

.dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--border-subtle);
}

.dialog-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0;
}

.dialog-close {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  color: var(--text-muted);
  font-size: 20px;
  cursor: pointer;
  transition: all var(--duration-fast);
}

.dialog-close:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.dialog-body {
  padding: var(--space-5);
}

.form-group {
  margin-bottom: var(--space-4);
}

.form-label {
  display: block;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
  margin-bottom: var(--space-2);
}

.input {
  width: 100%;
  padding: var(--space-3);
  background: var(--bg-primary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  color: var(--text-primary);
  font-size: var(--text-base);
  transition: border-color var(--duration-fast);
}

.input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-5);
  border-top: 1px solid var(--border-subtle);
}

.btn {
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-lg);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  cursor: pointer;
  transition: all var(--duration-fast);
}

.btn-primary {
  background: var(--color-primary);
  color: white;
  border: 1px solid var(--color-primary);
}

.btn-primary:hover {
  opacity: 0.9;
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  border: 1px solid var(--border-default);
}

.btn-secondary:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.btn-danger {
  background: var(--color-danger);
  color: white;
  border: 1px solid var(--color-danger);
}

.btn-danger:hover {
  background: #b91c1c;
  border-color: #b91c1c;
}

/* 删除对话框样式 */
.dialog-danger .dialog-header {
  background: rgba(220, 38, 38, 0.08);
}

.dialog-danger .dialog-title {
  color: var(--color-danger);
}

.dialog-message {
  margin: 0;
  font-size: var(--text-base);
  color: var(--text-primary);
  line-height: 1.6;
}

.dialog-message strong {
  color: var(--text-primary);
  font-weight: var(--font-semibold);
}

.dialog-hint {
  margin: var(--space-2) 0 0;
  font-size: var(--text-sm);
  color: var(--text-muted);
}

/* 移动端适配 */
@media (max-width: 768px) {
  .sidebar-wrapper {
    position: static;
  }

  .chat-sidebar {
    position: fixed;
    left: clamp(56px, 8vw, 72px);
    top: 0;
    bottom: 0;
    z-index: var(--z-modal);
    transform: translateX(-100%);
    transition: transform var(--duration-normal) var(--ease-spring);
    width: clamp(220px, 70vw, 280px);
    border-right: 1px solid var(--border-subtle);
  }

  .chat-sidebar.open {
    transform: translateX(0);
  }

  .chat-sidebar.collapsed {
    width: clamp(220px, 70vw, 280px);
    border-right: 1px solid var(--border-subtle);
  }

  .session-actions {
    opacity: 1;
  }

  .collapse-btn {
    display: none;
  }
}
</style>
