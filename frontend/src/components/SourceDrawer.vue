<template>
  <Transition name="drawer">
    <div v-if="visible" class="source-drawer-overlay" @click.self="$emit('close')">
      <div class="source-drawer">
        <div class="drawer-header">
          <h3 class="drawer-title">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" class="title-icon">
              <path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>
            </svg>
            参考来源详情
          </h3>
          <button class="close-btn" @click="$emit('close')" title="关闭">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
            </svg>
          </button>
        </div>

        <div class="drawer-content">
          <div v-if="!sources || sources.length === 0" class="empty-state">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
            </svg>
            <p>暂无参考来源</p>
          </div>

          <div v-else class="source-list">
            <div
              v-for="(source, index) in sources"
              :key="index"
              class="source-item"
            >
              <div class="source-header">
                <span class="source-index">#{{ index + 1 }}</span>
                <div class="source-meta">
                  <span class="kb-name">{{ source.kb_name }}</span>
                  <span class="doc-name">{{ source.doc_name }}</span>
                </div>
              </div>

              <div v-if="source.rerank_score !== null && source.rerank_score !== undefined" class="score-bar">
                <div class="score-label">
                  <span>相关度</span>
                  <span class="score-value">{{ (source.rerank_score * 100).toFixed(1) }}%</span>
                </div>
                <div class="score-track">
                  <div
                    class="score-fill"
                    :style="{ width: `${Math.min(source.rerank_score * 100, 100)}%` }"
                    :class="getScoreClass(source.rerank_score)"
                  ></div>
                </div>
              </div>

              <div class="source-content">
                {{ source.content }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
interface SourceDetail {
  kb_name: string
  doc_name: string
  content: string
  rerank_score?: number
  distance?: number
}

interface Props {
  visible: boolean
  sources: SourceDetail[]
}

defineProps<Props>()
defineEmits<{
  (e: 'close'): void
}>()

const getScoreClass = (score: number) => {
  if (score >= 0.8) return 'score-high'
  if (score >= 0.5) return 'score-medium'
  return 'score-low'
}
</script>

<style scoped>
.source-drawer-overlay {
  position: fixed;
  inset: 0;
  z-index: var(--z-modal);
  display: flex;
  justify-content: flex-end;
  background: rgba(61, 54, 50, 0.3);
  backdrop-filter: blur(4px);
}

.source-drawer {
  width: min(420px, 90vw);
  height: 100%;
  background: var(--bg-primary);
  border-left: 1px solid var(--border-default);
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-xl);
}

.drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
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

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: var(--text-muted);
}

.empty-state svg {
  width: 48px;
  height: 48px;
  fill: var(--text-muted);
  margin-bottom: var(--space-3);
  opacity: 0.5;
}

.empty-state p {
  margin: 0;
  font-size: var(--text-sm);
}

.source-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.source-item {
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  overflow: hidden;
  transition: all var(--duration-fast);
}

.source-item:hover {
  border-color: var(--border-default);
  box-shadow: var(--shadow-sm);
}

.source-header {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-subtle);
}

.source-index {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: var(--color-primary);
  color: white;
  border-radius: var(--radius-md);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  flex-shrink: 0;
}

.source-meta {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  min-width: 0;
}

.kb-name {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-primary);
}

.doc-name {
  font-size: var(--text-xs);
  color: var(--text-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.score-bar {
  padding: var(--space-3) var(--space-4);
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-subtle);
}

.score-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-2);
  font-size: var(--text-xs);
  color: var(--text-secondary);
}

.score-value {
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.score-track {
  height: 6px;
  background: var(--bg-primary);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.score-fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width var(--duration-normal) var(--ease-out);
}

.score-high {
  background: linear-gradient(90deg, var(--color-success), #22c55e);
}

.score-medium {
  background: linear-gradient(90deg, var(--color-warning), #f59e0b);
}

.score-low {
  background: linear-gradient(90deg, var(--color-primary), #94a3b8);
}

.source-content {
  padding: var(--space-4);
  font-size: var(--text-sm);
  line-height: 1.7;
  color: var(--text-secondary);
  max-height: 200px;
  overflow-y: auto;
}

/* Drawer 动画 */
.drawer-enter-active,
.drawer-leave-active {
  transition: all var(--duration-normal) var(--ease-out);
}

.drawer-enter-active .source-drawer,
.drawer-leave-active .source-drawer {
  transition: transform var(--duration-normal) var(--ease-out);
}

.drawer-enter-from,
.drawer-leave-to {
  background: transparent;
}

.drawer-enter-from .source-drawer,
.drawer-leave-to .source-drawer {
  transform: translateX(100%);
}

/* 移动端适配 */
@media (max-width: 768px) {
  .source-drawer {
    width: 100%;
  }
}
</style>
