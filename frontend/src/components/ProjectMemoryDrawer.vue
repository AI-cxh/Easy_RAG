<template>
  <Transition name="drawer">
    <div v-if="visible" class="memory-drawer-overlay" @click.self="$emit('close')">
      <div class="memory-drawer">
        <div class="drawer-header">
          <div>
            <h3 class="drawer-title">
              <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" class="title-icon">
                <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-2 12H7v-2h10v2zm0-4H7V9h10v2zm0-4H7V5h10v2z"/>
              </svg>
              当前项目记忆
            </h3>
            <p class="drawer-subtitle">{{ projectName || '未选择项目' }}</p>
          </div>
          <button class="close-btn" @click="$emit('close')" title="关闭">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
            </svg>
          </button>
        </div>

        <div class="drawer-content">
          <div v-if="loading" class="empty-state">
            <span class="spinner"></span>
            <p>正在加载项目记忆...</p>
          </div>

          <div v-else-if="!projectId" class="empty-state">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
            </svg>
            <p>请先选择一个项目</p>
          </div>

          <div v-else-if="activeMemories.length === 0" class="empty-state">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 14H7v-2h5v2zm5-4H7v-2h10v2zm0-4H7V7h10v2z"/>
            </svg>
            <p>当前项目还没有启用中的记忆</p>
          </div>

          <div v-else class="memory-list">
            <div
              v-for="memory in activeMemories"
              :key="memory.id"
              class="memory-item"
            >
              <div class="memory-meta">
                <span class="memory-type" :class="`type-${memory.memory_type}`">
                  {{ getMemoryTypeLabel(memory.memory_type) }}
                </span>
                <span v-if="memory.pinned" class="memory-badge">置顶</span>
              </div>
              <div class="memory-content">{{ memory.content }}</div>
            </div>
          </div>

          <div v-if="disabledMemories.length > 0" class="disabled-section">
            <div class="disabled-header">已停用记忆</div>
            <div class="memory-list disabled-list">
              <div
                v-for="memory in disabledMemories"
                :key="memory.id"
                class="memory-item disabled-item"
              >
                <div class="memory-meta">
                  <span class="memory-type" :class="`type-${memory.memory_type}`">
                    {{ getMemoryTypeLabel(memory.memory_type) }}
                  </span>
                  <span class="memory-badge muted-badge">停用</span>
                </div>
                <div class="memory-content">{{ memory.content }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ProjectMemory } from '../api/client'

interface Props {
  visible: boolean
  projectId?: number
  projectName?: string
  memories: ProjectMemory[]
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  projectId: undefined,
  projectName: '',
  loading: false
})

defineEmits<{
  (e: 'close'): void
}>()

const activeMemories = computed(() =>
  [...(props.memories || [])]
    .filter(memory => memory.enabled)
    .sort((a, b) => Number(b.pinned) - Number(a.pinned) || b.id - a.id)
)

const disabledMemories = computed(() =>
  [...(props.memories || [])]
    .filter(memory => !memory.enabled)
    .sort((a, b) => Number(b.pinned) - Number(a.pinned) || b.id - a.id)
)

const getMemoryTypeLabel = (memoryType: string) => {
  if (memoryType === 'instruction') return '规则'
  if (memoryType === 'preference') return '偏好'
  return '背景'
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
  width: min(440px, 92vw);
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

.close-btn {
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

.close-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.close-btn svg {
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
  gap: var(--space-2);
  margin-bottom: var(--space-3);
  flex-wrap: wrap;
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
  border: 1px solid transparent;
}

.type-context {
  color: #8f3b2f;
  background: rgba(216, 133, 112, 0.14);
  border-color: rgba(216, 133, 112, 0.24);
}

.type-preference {
  color: #325c85;
  background: rgba(96, 155, 210, 0.14);
  border-color: rgba(96, 155, 210, 0.24);
}

.type-instruction {
  color: #3d6b4f;
  background: rgba(96, 168, 122, 0.14);
  border-color: rgba(96, 168, 122, 0.24);
}

.memory-badge {
  color: var(--text-secondary);
  background: var(--bg-secondary);
}

.muted-badge {
  color: var(--text-muted);
}

.memory-content {
  white-space: pre-wrap;
  line-height: 1.65;
  color: var(--text-primary);
}

.disabled-section {
  margin-top: var(--space-5);
  padding-top: var(--space-4);
  border-top: 1px solid var(--border-subtle);
}

.disabled-header {
  margin-bottom: var(--space-3);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
}

.disabled-item {
  opacity: 0.72;
}

.empty-state {
  min-height: 220px;
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
</style>
