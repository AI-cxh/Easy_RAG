<template>
  <div class="agent-flow">
    <div class="flow-header">
      <span class="flow-title">Agent执行流程</span>
      <button class="flow-toggle" @click="expanded = !expanded">
        <svg :class="{ rotated: expanded }" viewBox="0 0 24 24">
          <path d="M7 10l5 5 5-5z"/>
        </svg>
      </button>
    </div>

    <Transition name="expand">
      <div v-if="expanded" class="flow-content">
        <!-- 执行计划 -->
        <div v-if="plan && plan.length > 0" class="plan-section">
          <div class="section-title">执行计划</div>
          <div class="plan-timeline">
            <div
              v-for="(task, index) in plan"
              :key="task.id"
              class="plan-item"
              :class="{
                active: currentTaskId === task.id,
                completed: completedTasks.includes(task.id)
              }"
            >
              <div class="plan-marker">
                <span v-if="completedTasks.includes(task.id)" class="check-icon">
                  <svg viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
                </span>
                <span v-else-if="currentTaskId === task.id" class="loading-icon">
                  <svg viewBox="0 0 24 24"><path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8z"/></svg>
                </span>
                <span v-else class="step-number">{{ index + 1 }}</span>
              </div>
              <div class="plan-info">
                <span class="plan-agent">{{ getAgentLabel(task.agent_type) }}</span>
                <span class="plan-task">{{ task.description }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 执行日志 -->
        <div v-if="logs.length > 0" class="logs-section">
          <div class="section-title">执行日志</div>
          <div class="logs-list">
            <div
              v-for="(log, index) in logs"
              :key="index"
              class="log-item"
              :class="log.type"
            >
              <span class="log-icon">
                <svg v-if="log.type === 'thought'" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>
                <svg v-else-if="log.type === 'tool_call'" viewBox="0 0 24 24"><path d="M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z"/></svg>
                <svg v-else-if="log.type === 'tool_result'" viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
                <svg v-else viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"/></svg>
              </span>
              <div class="log-content">
                <span v-if="log.tool_name" class="log-tool">{{ log.tool_name }}</span>
                <span class="log-text">{{ log.content }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface AgentTask {
  id: string
  agent_type: string
  description: string
  priority: number
}

interface LogEntry {
  type: string
  content: string
  tool_name?: string
}

const props = defineProps<{
  plan?: AgentTask[]
  currentTaskId?: string
  completedTasks?: string[]
  logs?: LogEntry[]
}>()

const expanded = ref(true)

const agentLabels: Record<string, string> = {
  retrieval: '检索Agent',
  analysis: '分析Agent',
  writing: '写作Agent',
  orchestrator: '主控Agent',
  custom: '自定义Agent'
}

const getAgentLabel = (type: string) => agentLabels[type] || type
</script>

<style scoped>
.agent-flow {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-3);
  overflow: hidden;
}

.flow-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-2) var(--space-3);
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-subtle);
}

.flow-title {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--text-secondary);
}

.flow-toggle {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  cursor: pointer;
  transition: all var(--duration-fast);
}

.flow-toggle:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.flow-toggle svg {
  width: 18px;
  height: 18px;
  fill: currentColor;
  transition: transform var(--duration-normal);
}

.flow-toggle svg.rotated {
  transform: rotate(180deg);
}

.flow-content {
  padding: var(--space-3);
  max-height: 500px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: var(--border-default) transparent;
}

.flow-content::-webkit-scrollbar {
  width: 6px;
}

.flow-content::-webkit-scrollbar-track {
  background: transparent;
}

.flow-content::-webkit-scrollbar-thumb {
  background: var(--border-default);
  border-radius: 3px;
}

.flow-content::-webkit-scrollbar-thumb:hover {
  background: var(--border-strong);
}

.section-title {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--text-muted);
  margin-bottom: var(--space-2);
}

.plan-section {
  margin-bottom: var(--space-4);
}

.plan-timeline {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.plan-item {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-2);
  border-radius: var(--radius-md);
  transition: background var(--duration-fast);
}

.plan-item.active {
  background: var(--color-primary-light);
}

.plan-item.completed {
  opacity: 0.7;
}

.plan-marker {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-elevated);
  border: 2px solid var(--border-default);
  border-radius: 50%;
  flex-shrink: 0;
}

.plan-item.active .plan-marker {
  border-color: var(--color-primary);
  background: var(--color-primary);
}

.plan-item.completed .plan-marker {
  border-color: var(--color-success);
  background: var(--color-success);
}

.step-number {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--text-muted);
}

.plan-item.active .step-number,
.plan-item.completed .step-number {
  color: white;
}

.check-icon svg,
.loading-icon svg {
  width: 14px;
  height: 14px;
  fill: white;
}

.loading-icon svg {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.plan-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.plan-agent {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--color-primary);
}

.plan-task {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.logs-section {
  margin-top: var(--space-3);
}

.logs-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  max-height: 200px;
  overflow-y: auto;
}

.log-item {
  display: flex;
  align-items: flex-start;
  gap: var(--space-2);
  padding: var(--space-2);
  background: var(--bg-elevated);
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
}

.log-icon {
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.log-icon svg {
  width: 14px;
  height: 14px;
  fill: var(--text-muted);
}

.log-item.thought .log-icon svg {
  fill: var(--color-primary);
}

.log-item.tool_call .log-icon svg {
  fill: var(--color-accent);
}

.log-item.tool_result .log-icon svg {
  fill: var(--color-success);
}

.log-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.log-tool {
  font-weight: var(--font-semibold);
  color: var(--color-accent);
}

.log-text {
  color: var(--text-secondary);
  word-break: break-word;
  overflow-wrap: break-word;
}

/* Expand transition */
.expand-enter-active,
.expand-leave-active {
  transition: all var(--duration-normal) var(--ease-soft);
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
}

.expand-enter-to,
.expand-leave-from {
  max-height: 500px;
}
</style>
