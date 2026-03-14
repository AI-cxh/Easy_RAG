<template>
  <div class="settings-layout">
    <!-- 左侧固定导航栏 -->
    <nav class="nav-rail">
      <router-link to="/chat" class="nav-rail-btn" title="历史记录">
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/>
        </svg>
      </router-link>
      <router-link to="/knowledge" class="nav-rail-btn" title="知识库管理">
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path d="M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-1 9H9V9h10v2zm-4 4H9v-2h6v2zm4-8H9V5h10v2z"/>
        </svg>
      </router-link>
      <router-link to="/settings" class="nav-rail-btn" title="设置">
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path d="M19.14 12.94c.04-.31.06-.63.06-.94 0-.31-.02-.63-.06-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.04.31-.06.63-.06.94s.02.63.06.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/>
        </svg>
      </router-link>
    </nav>

    <!-- 主内容区 -->
    <div class="settings-main-wrapper">
      <!-- 顶部导航 -->
      <header class="settings-header">
        <h1 class="header-title">模型设置</h1>
      </header>

    <div class="settings-content">
      <!-- 大模型设置 -->
      <div class="settings-card animate-slide-up stagger-1">
        <div class="card-header">
          <div class="card-icon llm-icon">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
            </svg>
          </div>
          <div class="card-title-group">
            <h2 class="card-title">大语言模型 (LLM)</h2>
            <p class="card-desc">用于对话生成的语言模型</p>
          </div>
        </div>
        <div class="card-body">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">模型名称</label>
              <input
                v-model="settings.llm.model"
                type="text"
                class="input"
                placeholder="例如: deepseek-chat"
              />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">API Key</label>
              <input
                v-model="settings.llm.apiKey"
                type="password"
                class="input"
                placeholder="输入 API Key"
              />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">API URL</label>
              <input
                v-model="settings.llm.apiUrl"
                type="text"
                class="input"
                placeholder="例如: https://api.deepseek.com"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Embedding 模型设置 -->
      <div class="settings-card animate-slide-up stagger-2">
        <div class="card-header">
          <div class="card-icon embedding-icon">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M21 3H3c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h18c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H3V5h18v14zM5 15h14v3H5z"/>
            </svg>
          </div>
          <div class="card-title-group">
            <h2 class="card-title">嵌入模型 (Embedding)</h2>
            <p class="card-desc">用于文本向量化的嵌入模型</p>
          </div>
        </div>
        <div class="card-body">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">模型名称</label>
              <input
                v-model="settings.embedding.model"
                type="text"
                class="input"
                placeholder="例如: BAAI/bge-m3"
              />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">API Key</label>
              <input
                v-model="settings.embedding.apiKey"
                type="password"
                class="input"
                placeholder="输入 API Key"
              />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">API URL</label>
              <input
                v-model="settings.embedding.apiUrl"
                type="text"
                class="input"
                placeholder="例如: https://api.siliconflow.cn/v1"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Rerank 模型设置 -->
      <div class="settings-card animate-slide-up stagger-3">
        <div class="card-header">
          <div class="card-icon rerank-icon">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M3 18h6v-2H3v2zM3 6v2h18V6H3zm0 7h12v-2H3v2z"/>
            </svg>
          </div>
          <div class="card-title-group">
            <h2 class="card-title">重排序模型 (Rerank)</h2>
            <p class="card-desc">用于检索结果重排序的模型（可选）</p>
          </div>
        </div>
        <div class="card-body">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">模型名称</label>
              <input
                v-model="settings.rerank.model"
                type="text"
                class="input"
                placeholder="例如: BAAI/bge-reranker-v2-m3"
              />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">API Key</label>
              <input
                v-model="settings.rerank.apiKey"
                type="password"
                class="input"
                placeholder="输入 API Key"
              />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">API URL</label>
              <input
                v-model="settings.rerank.apiUrl"
                type="text"
                class="input"
                placeholder="例如: https://api.siliconflow.cn/v1"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- MCP 服务器设置 -->
      <div class="settings-card animate-slide-up stagger-4">
        <div class="card-header">
          <div class="card-icon mcp-icon">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
            </svg>
          </div>
          <div class="card-title-group">
            <h2 class="card-title">MCP 服务器</h2>
            <p class="card-desc">连接外部MCP服务器扩展Agent能力</p>
          </div>
          <div class="card-actions">
            <span class="status-badge" :class="mcpInitialized ? 'connected' : 'disconnected'">
              {{ mcpInitialized ? '已连接' : '未连接' }}
            </span>
          </div>
        </div>
        <div class="card-body">
          <!-- 服务器列表 -->
          <div class="mcp-servers-list" v-if="mcpServers.length > 0">
            <div class="server-item" v-for="server in mcpServers" :key="server.name">
              <div class="server-info">
                <span class="server-name">{{ server.name }}</span>
                <span class="server-transport">{{ server.transport }}</span>
                <span class="server-status" :class="server.status">{{ server.status }}</span>
              </div>
              <button class="btn-icon btn-danger" @click="removeMCPServer(server.name)" title="删除">
                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                </svg>
              </button>
            </div>
          </div>
          <div class="empty-state" v-else>
            <p>暂无配置的MCP服务器</p>
          </div>

          <!-- 工具列表 -->
          <div class="mcp-tools-section" v-if="mcpTools.length > 0">
            <h4 class="section-title">已加载工具 ({{ mcpTools.length }})</h4>
            <div class="tools-list">
              <span class="tool-tag" v-for="tool in mcpTools" :key="tool.name" :title="tool.description">
                {{ tool.name }}
              </span>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="mcp-actions">
            <button class="btn btn-secondary" @click="showAddServerForm = !showAddServerForm">
              {{ showAddServerForm ? '取消' : '添加服务器' }}
            </button>
            <button class="btn btn-secondary" @click="reloadMCP" :disabled="mcpLoading">
              {{ mcpLoading ? '加载中...' : '重新加载' }}
            </button>
          </div>

          <!-- 添加服务器表单 -->
          <div class="add-server-form" v-if="showAddServerForm">
            <h4 class="form-title">添加MCP服务器</h4>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">服务器名称</label>
                <input v-model="newServer.name" type="text" class="input" placeholder="例如: filesystem" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">传输类型</label>
                <select v-model="newServer.transport" class="input">
                  <option value="stdio">stdio (本地进程)</option>
                  <option value="http">http (HTTP服务)</option>
                  <option value="streamable-http">streamable-http</option>
                </select>
              </div>
            </div>
            <template v-if="newServer.transport === 'stdio'">
              <div class="form-row">
                <div class="form-group">
                  <label class="form-label">命令</label>
                  <input v-model="newServer.command" type="text" class="input" placeholder="例如: python" />
                </div>
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label class="form-label">参数 (逗号分隔)</label>
                  <input v-model="newServer.args" type="text" class="input" placeholder="例如: /path/to/server.py" />
                </div>
              </div>
            </template>
            <template v-else>
              <div class="form-row">
                <div class="form-group">
                  <label class="form-label">URL</label>
                  <input v-model="newServer.url" type="text" class="input" placeholder="例如: http://localhost:8001/mcp" />
                </div>
              </div>
            </template>
            <div class="form-actions">
              <button class="btn btn-primary" @click="addMCPServer">添加</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 保存按钮 -->
      <div class="settings-actions animate-slide-up stagger-5">
        <button class="btn btn-secondary" @click="loadSettings">
          重置
        </button>
        <button class="btn btn-primary" @click="saveSettings" :disabled="saving">
          {{ saving ? '保存中...' : '保存设置' }}
        </button>
      </div>
    </div>
    </div>
  </div>

</template>


<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { settingsAPI, mcpAPI, type MCPServer, type MCPTool } from '../api/client'

interface ModelSettings {
  model: string
  apiKey: string
  apiUrl: string
}

interface Settings {
  llm: ModelSettings
  embedding: ModelSettings
  rerank: ModelSettings
}

const settings = ref<Settings>({
  llm: { model: '', apiKey: '', apiUrl: '' },
  embedding: { model: '', apiKey: '', apiUrl: '' },
  rerank: { model: '', apiKey: '', apiUrl: '' }
})

const saving = ref(false)

// MCP相关状态
const mcpServers = ref<MCPServer[]>([])
const mcpTools = ref<MCPTool[]>([])
const mcpInitialized = ref(false)
const mcpLoading = ref(false)

// 新增MCP服务器表单
const showAddServerForm = ref(false)
const newServer = ref({
  name: '',
  transport: 'stdio' as 'stdio' | 'http' | 'streamable-http',
  command: '',
  args: '',
  url: ''
})

const loadSettings = async () => {
  try {
    const result = await settingsAPI.get()
    if (result) {
      settings.value = result
    }
  } catch (error) {
    console.error('Failed to load settings:', error)
  }
}

const saveSettings = async () => {
  saving.value = true
  try {
    await settingsAPI.save(settings.value)
    alert('设置已保存，重启后端服务生效')
  } catch (error) {
    console.error('Failed to save settings:', error)
    alert('保存失败')
  } finally {
    saving.value = false
  }
}

// MCP相关方法
const loadMCPStatus = async () => {
  mcpLoading.value = true
  try {
    const status = await mcpAPI.getStatus()
    mcpInitialized.value = status.initialized
    mcpServers.value = status.servers
    mcpTools.value = status.tools
  } catch (error) {
    console.error('Failed to load MCP status:', error)
  } finally {
    mcpLoading.value = false
  }
}

const addMCPServer = async () => {
  if (!newServer.value.name) {
    alert('请输入服务器名称')
    return
  }

  try {
    const config: any = {
      name: newServer.value.name,
      transport: newServer.value.transport
    }

    if (newServer.value.transport === 'stdio') {
      if (!newServer.value.command) {
        alert('stdio模式需要输入命令')
        return
      }
      config.command = newServer.value.command
      if (newServer.value.args) {
        config.args = newServer.value.args.split(',').map(s => s.trim())
      }
    } else {
      if (!newServer.value.url) {
        alert('HTTP模式需要输入URL')
        return
      }
      config.url = newServer.value.url
    }

    await mcpAPI.addServer(config)
    await loadMCPStatus()

    // 重置表单
    showAddServerForm.value = false
    newServer.value = {
      name: '',
      transport: 'stdio',
      command: '',
      args: '',
      url: ''
    }
  } catch (error: any) {
    alert(error.message || '添加服务器失败')
  }
}

const removeMCPServer = async (name: string) => {
  if (!confirm(`确定要删除服务器 "${name}" 吗？`)) {
    return
  }

  try {
    await mcpAPI.removeServer(name)
    await loadMCPStatus()
  } catch (error: any) {
    alert(error.message || '删除服务器失败')
  }
}

const reloadMCP = async () => {
  try {
    await mcpAPI.reload()
    await loadMCPStatus()
    alert('MCP服务器已重新加载')
  } catch (error: any) {
    alert(error.message || '重新加载失败')
  }
}

onMounted(() => {
  loadSettings()
  loadMCPStatus()
})
</script>


<style scoped>
.settings-layout {
  display: flex;
  height: 100vh;
  background: var(--bg-primary);
}

/* 左侧固定导航栏 */
.nav-rail {
  width: var(--nav-rail-width);
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-4) 0;
  gap: var(--space-2);
  flex-shrink: 0;
}

.nav-rail-btn {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: var(--radius-lg);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--duration-normal) var(--ease-soft);
  text-decoration: none;
  position: relative;
}

.nav-rail-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: var(--color-primary-light);
  opacity: 0;
  transform: scale(0.8);
  transition: all var(--duration-normal) var(--ease-spring);
}

.nav-rail-btn:hover {
  color: var(--text-primary);
}

.nav-rail-btn:hover::before {
  opacity: 1;
  transform: scale(1);
}

.nav-rail-btn.router-link-active {
  color: var(--color-primary);
}

.nav-rail-btn.router-link-active::before {
  opacity: 1;
  transform: scale(1);
}

.nav-rail-btn svg {
  width: 22px;
  height: 22px;
  fill: currentColor;
  position: relative;
  z-index: 1;
}

/* 主内容区包装 */
.settings-main-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

/* 顶部导航 */
.settings-header {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: 0 var(--space-8);
  height: var(--header-height);
  background: rgba(250, 248, 245, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border-subtle);
}

.header-title {
  flex: 1;
  font-family: var(--font-display);
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0;
  letter-spacing: -0.01em;
}

/* 内容区域 */
.settings-content {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-8);
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
}

/* 设置卡片 */
.settings-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-2xl);
  margin-bottom: var(--space-5);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  transition: all var(--duration-normal) var(--ease-soft);
}

.settings-card:hover {
  box-shadow: var(--shadow-md);
}

.card-header {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-5);
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-subtle);
}

.card-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: transform var(--duration-normal) var(--ease-spring);
}

.settings-card:hover .card-icon {
  transform: scale(1.05);
}

.card-icon svg {
  width: 24px;
  height: 24px;
  fill: currentColor;
}

.llm-icon {
  background: var(--color-primary-light);
  color: var(--color-primary);
}

.embedding-icon {
  background: var(--color-accent-light);
  color: var(--color-accent);
}

.rerank-icon {
  background: var(--color-warning-light);
  color: var(--color-warning);
}

.mcp-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.card-title-group {
  flex: 1;
}

.card-title {
  font-family: var(--font-display);
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0;
}

.card-desc {
  font-size: var(--text-xs);
  color: var(--text-muted);
  margin: var(--space-1) 0 0;
}

.card-body {
  padding: var(--space-5);
}

.form-row {
  margin-bottom: var(--space-4);
}

.form-row:last-child {
  margin-bottom: 0;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.form-label {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
}

/* 操作按钮 */
.settings-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  margin-top: var(--space-6);
}

/* 响应式 */
@media (max-width: 768px) {
  .settings-header {
    padding: 0 var(--space-5);
  }

  .settings-content {
    padding: var(--space-5);
  }

  .card-header {
    padding: var(--space-4);
  }

  .card-body {
    padding: var(--space-4);
  }
}

/* MCP 相关样式 */
.card-actions {
  margin-left: auto;
}

.status-badge {
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
}

.status-badge.connected {
  background: var(--color-success-light, #d1fae5);
  color: var(--color-success, #059669);
}

.status-badge.disconnected {
  background: var(--color-error-light, #fee2e2);
  color: var(--color-error, #dc2626);
}

.mcp-servers-list {
  margin-bottom: var(--space-4);
}

.server-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3);
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-2);
}

.server-info {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.server-name {
  font-weight: var(--font-medium);
  color: var(--text-primary);
}

.server-transport {
  font-size: var(--text-xs);
  padding: var(--space-1) var(--space-2);
  background: var(--bg-elevated);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
}

.server-status {
  font-size: var(--text-xs);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-md);
}

.server-status.connected {
  background: var(--color-success-light, #d1fae5);
  color: var(--color-success, #059669);
}

.server-status.configured {
  background: var(--color-warning-light, #fef3c7);
  color: var(--color-warning, #d97706);
}

.btn-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-soft);
  background: transparent;
}

.btn-icon svg {
  width: 18px;
  height: 18px;
  fill: currentColor;
}

.btn-icon.btn-danger {
  color: var(--color-error, #dc2626);
}

.btn-icon.btn-danger:hover {
  background: var(--color-error-light, #fee2e2);
}

.empty-state {
  text-align: center;
  padding: var(--space-6);
  color: var(--text-muted);
}

.mcp-tools-section {
  margin-bottom: var(--space-4);
  padding-top: var(--space-4);
  border-top: 1px solid var(--border-subtle);
}

.section-title {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
  margin: 0 0 var(--space-3) 0;
}

.tools-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.tool-tag {
  font-size: var(--text-xs);
  padding: var(--space-1) var(--space-2);
  background: var(--color-primary-light);
  color: var(--color-primary);
  border-radius: var(--radius-md);
}

.mcp-actions {
  display: flex;
  gap: var(--space-3);
  margin-top: var(--space-4);
}

.add-server-form {
  margin-top: var(--space-4);
  padding: var(--space-4);
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
}

.form-title {
  font-size: var(--text-md);
  font-weight: var(--font-medium);
  color: var(--text-primary);
  margin: 0 0 var(--space-4) 0;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: var(--space-4);
}

select.input {
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23666' d='M6 8L1 3h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  padding-right: 36px;
}

</style>
