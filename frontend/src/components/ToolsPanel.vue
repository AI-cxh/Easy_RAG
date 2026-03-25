<template>
  <div class="tools-panel">
    <div class="panel-header">
      <h3 class="panel-title">可用工具</h3>
      <span class="tool-count">{{ tools.length }}</span>
    </div>

    <div v-if="loading" class="loading-state">
      <span class="spinner-small"></span>
    </div>

    <div v-else-if="tools.length === 0" class="empty-state">
      <p>暂无可用工具</p>
    </div>

    <div v-else class="tools-list">
      <!-- 内置工具 -->
      <div v-if="builtinTools.length > 0" class="tool-group">
        <div class="group-header">
          <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" class="group-icon">
            <path d="M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z"/>
          </svg>
          <span>内置工具</span>
        </div>
        <div
          v-for="tool in builtinTools"
          :key="tool.name"
          class="tool-item"
          :title="tool.description"
        >
          <div class="tool-name">{{ formatToolName(tool.name) }}</div>
          <div class="tool-desc">{{ tool.description }}</div>
        </div>
      </div>

      <!-- MCP工具 -->
      <div v-if="mcpTools.length > 0" class="tool-group">
        <div class="group-header">
          <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" class="group-icon mcp-icon">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
          </svg>
          <span>MCP工具</span>
        </div>
        <div
          v-for="tool in mcpTools"
          :key="tool.name"
          class="tool-item mcp"
          :title="tool.description"
        >
          <div class="tool-name">{{ formatToolName(tool.name) }}</div>
          <div class="tool-desc">{{ tool.description || '无描述' }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { mcpAPI, type Tool } from '../api/client'

const loading = ref(false)
const builtinTools = ref<Tool[]>([])
const mcpTools = ref<Tool[]>([])

const tools = computed(() => [...builtinTools.value, ...mcpTools.value])

const loadTools = async () => {
  loading.value = true
  try {
    const result = await mcpAPI.getAllTools()
    builtinTools.value = result.builtin_tools || []
    mcpTools.value = result.mcp_tools || []
  } catch (error) {
    console.error('Failed to load tools:', error)
  } finally {
    loading.value = false
  }
}

const formatToolName = (name: string) => {
  // 将下划线或连字符转换为空格，并首字母大写
  return name
    .replace(/[-_]/g, ' ')
    .replace(/\b\w/g, c => c.toUpperCase())
}

onMounted(() => {
  loadTools()
})
</script>

<style scoped>
.tools-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--bg-secondary);
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--border-subtle);
}

.panel-title {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0;
}

.tool-count {
  font-size: var(--text-xs);
  padding: var(--space-1) var(--space-2);
  background: var(--color-primary-light);
  color: var(--color-primary);
  border-radius: var(--radius-full);
}

.loading-state {
  display: flex;
  justify-content: center;
  padding: var(--space-6);
}

.spinner-small {
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-default);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  text-align: center;
  padding: var(--space-6);
  color: var(--text-muted);
  font-size: var(--text-sm);
}

.tools-list {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-2);
}

.tool-group {
  margin-bottom: var(--space-3);
}

.group-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.group-icon {
  width: 14px;
  height: 14px;
  fill: var(--text-muted);
}

.group-icon.mcp-icon {
  fill: var(--color-accent);
}

.tool-item {
  padding: var(--space-2) var(--space-3);
  margin-bottom: var(--space-1);
  background: var(--bg-elevated);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-subtle);
  transition: all var(--duration-fast);
}

.tool-item:hover {
  border-color: var(--border-default);
  background: var(--bg-hover);
}

.tool-item.mcp {
  border-left: 2px solid var(--color-accent);
}

.tool-name {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-primary);
  margin-bottom: var(--space-1);
}

.tool-desc {
  font-size: var(--text-xs);
  color: var(--text-muted);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
