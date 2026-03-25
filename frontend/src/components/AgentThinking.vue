<template>
  <div class="agent-thinking" v-if="steps.length > 0">
    <div class="thinking-header" @click="expanded = !expanded">
      <svg class="thinking-icon" :class="{ rotated: expanded }" viewBox="0 0 24 24">
        <path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/>
      </svg>
      <span class="thinking-title">Agent 思考过程</span>
      <span class="thinking-count">{{ steps.length }} 步</span>
    </div>

    <div class="thinking-content" v-show="expanded">
      <div
        v-for="(step, index) in steps"
        :key="index"
        class="thinking-step"
        :class="step.type"
      >
        <div class="step-header">
          <span class="step-icon">
            <svg v-if="step.type === 'thought'" viewBox="0 0 24 24">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
            <svg v-else-if="step.type === 'tool_call'" viewBox="0 0 24 24">
              <path d="M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z"/>
            </svg>
            <svg v-else-if="step.type === 'tool_result'" viewBox="0 0 24 24">
              <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
            </svg>
          </span>
          <span class="step-type">{{ getStepLabel(step.type) }}</span>
          <span v-if="step.tool_name" class="step-tool">{{ step.tool_name }}</span>
        </div>

        <div class="step-content">
          <div v-if="step.tool_args && Object.keys(step.tool_args).length > 0" class="tool-args">
            <span class="args-label">参数:</span>
            <code class="args-value">{{ JSON.stringify(step.tool_args, null, 2) }}</code>
          </div>
          <div class="step-text">{{ step.content }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { ThinkingStep } from '../api/client'

defineProps<{
  steps: ThinkingStep[]
}>()

const expanded = ref(true)

const getStepLabel = (type: string): string => {
  const labels: Record<string, string> = {
    thought: '思考',
    tool_call: '调用工具',
    tool_result: '工具结果'
  }
  return labels[type] || type
}
</script>

<style scoped>
.agent-thinking {
  background: linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%);
  border: 1px solid #e0e7ff;
  border-radius: 12px;
  margin: 8px 0;
  overflow: hidden;
}

.thinking-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  user-select: none;
  transition: background 0.2s;
}

.thinking-header:hover {
  background: rgba(99, 102, 241, 0.05);
}

.thinking-icon {
  width: 20px;
  height: 20px;
  fill: #6366f1;
  transition: transform 0.2s;
}

.thinking-icon.rotated {
  transform: rotate(90deg);
}

.thinking-title {
  font-weight: 600;
  color: #4f46e5;
  margin-left: 8px;
  font-size: 14px;
}

.thinking-count {
  margin-left: auto;
  background: #e0e7ff;
  color: #4f46e5;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
}

.thinking-content {
  padding: 0 16px 16px;
  max-height: 400px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: #e0e7ff transparent;
}

.thinking-content::-webkit-scrollbar {
  width: 6px;
}

.thinking-content::-webkit-scrollbar-track {
  background: transparent;
}

.thinking-content::-webkit-scrollbar-thumb {
  background: #c7d2fe;
  border-radius: 3px;
}

.thinking-content::-webkit-scrollbar-thumb:hover {
  background: #a5b4fc;
}

.thinking-step {
  padding: 12px;
  margin-top: 8px;
  background: white;
  border-radius: 8px;
  border-left: 3px solid;
}

.thinking-step.thought {
  border-left-color: #10b981;
}

.thinking-step.tool_call {
  border-left-color: #f59e0b;
}

.thinking-step.tool_result {
  border-left-color: #3b82f6;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.step-icon {
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.step-icon svg {
  width: 16px;
  height: 16px;
}

.thinking-step.thought .step-icon svg {
  fill: #10b981;
}

.thinking-step.tool_call .step-icon svg {
  fill: #f59e0b;
}

.thinking-step.tool_result .step-icon svg {
  fill: #3b82f6;
}

.step-type {
  font-weight: 600;
  font-size: 13px;
  color: #374151;
}

.step-tool {
  background: #fef3c7;
  color: #92400e;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-family: 'Consolas', 'Monaco', monospace;
}

.step-content {
  font-size: 13px;
  color: #4b5563;
}

.tool-args {
  margin-bottom: 8px;
  padding: 8px;
  background: #f9fafb;
  border-radius: 6px;
}

.args-label {
  font-weight: 500;
  color: #6b7280;
  font-size: 12px;
  display: block;
  margin-bottom: 4px;
}

.args-value {
  display: block;
  font-size: 11px;
  color: #1f2937;
  white-space: pre-wrap;
  word-break: break-all;
}

.step-text {
  line-height: 1.5;
  word-break: break-word;
  overflow-wrap: break-word;
}
</style>
