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
      <div class="settings-card">
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
      <div class="settings-card">
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
      <div class="settings-card">
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

      <!-- 保存按钮 -->
      <div class="settings-actions">
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
import { settingsAPI } from '../api/client'

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

onMounted(() => {
  loadSettings()
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
  width: 56px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-3) 0;
  gap: var(--space-2);
  flex-shrink: 0;
}

.nav-rail-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--duration-fast);
  text-decoration: none;
  position: relative;
}

.nav-rail-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.nav-rail-btn.router-link-active {
  color: var(--color-primary);
  background: var(--color-primary-light);
}

.nav-rail-btn svg {
  width: 22px;
  height: 22px;
  fill: currentColor;
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
  padding: 0 var(--space-6);
  height: 56px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-subtle);
}

.header-title {
  flex: 1;
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0;
}

/* 内容区域 */
.settings-content {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-6);
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
}

/* 设置卡片 */
.settings-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  margin-bottom: var(--space-4);
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-4);
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-subtle);
}

.card-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.card-icon svg {
  width: 20px;
  height: 20px;
  fill: currentColor;
}

.llm-icon {
  background: rgba(99, 102, 241, 0.15);
  color: #6366f1;
}

.embedding-icon {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

.rerank-icon {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
}

.card-title-group {
  flex: 1;
}

.card-title {
  font-size: var(--text-base);
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
  padding: var(--space-4);
}

.form-row {
  margin-bottom: var(--space-3);
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
  margin-top: var(--space-4);
}

/* 响应式 */
@media (max-width: 768px) {
  .settings-header {
    padding: 0 var(--space-4);
  }

  .settings-content {
    padding: var(--space-4);
  }
}

</style>
