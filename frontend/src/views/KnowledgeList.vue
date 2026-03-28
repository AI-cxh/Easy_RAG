<template>
  <div class="knowledge-layout">
    <AppNavRail />

    <div class="main-wrapper">
      <header class="page-header">
        <h1 class="page-title">知识库管理</h1>
        <div class="header-actions">
          <button class="btn btn-primary" @click="showCreateDialog = true">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
            </svg>
            新建知识库
          </button>
        </div>
      </header>

      <!-- 统计卡片 -->
      <div class="stats-grid">
        <div class="stat-card" @click="filterByStat('all')">
          <div class="stat-content">
            <div class="stat-value">{{ stats.total_kbs }}</div>
            <div class="stat-label">知识库总数</div>
          </div>
          <div class="stat-action">全部</div>
        </div>
        <div class="stat-card" @click="filterByStat('docs')">
          <div class="stat-content">
            <div class="stat-value">{{ stats.total_docs }}</div>
            <div class="stat-label">全部文档数</div>
          </div>
          <div class="stat-action">全部</div>
        </div>
        <div class="stat-card" @click="filterByStat('with_docs')">
          <div class="stat-content">
            <div class="stat-value">{{ stats.kbs_with_docs }}</div>
            <div class="stat-label">含文档的知识库</div>
          </div>
          <div class="stat-action">全部</div>
        </div>
      </div>

      <!-- 操作栏 -->
      <div class="toolbar">
        <div class="search-box">
          <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
          </svg>
          <input
            v-model="searchQuery"
            type="text"
            class="input"
            placeholder="搜索知识库名称..."
            @keyup.enter="handleSearch"
          />
        </div>
        <button class="btn btn-secondary" @click="handleSearch">
          搜索
        </button>
        <button class="btn btn-ghost" @click="loadKnowledgeBases">
          <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
          </svg>
          刷新
        </button>
      </div>

      <!-- 知识库表格 -->
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>名称</th>
              <th>Embedding 模型</th>
              <th>Collection</th>
              <th>文档数</th>
              <th>负责人</th>
              <th>创建时间</th>
              <th>修改时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="8" class="loading-cell">
                <span class="spinner"></span>
                加载中...
              </td>
            </tr>
            <tr v-else-if="knowledgeBases.length === 0">
              <td colspan="8" class="empty-cell">
                暂无知识库
              </td>
            </tr>
            <tr v-for="kb in knowledgeBases" :key="kb.id">
              <td>
                <router-link :to="`/knowledge/${kb.id}/documents`" class="kb-name">
                  {{ kb.name }}
                </router-link>
              </td>
              <td>{{ kb.embedding_model || 'BAAI/bge-m3' }}</td>
              <td>
                <span class="tag tag-primary">kb_{{ kb.id }}</span>
              </td>
              <td>{{ kb.doc_count || 0 }}</td>
              <td>{{ kb.owner || '-' }}</td>
              <td>{{ formatDate(kb.created_at) }}</td>
              <td>{{ kb.updated_at ? formatDate(kb.updated_at) : '-' }}</td>
              <td>
                <div class="action-btns">
                  <button class="btn-icon btn-icon-sm" @click="startEditKb(kb)" title="编辑">
                    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
                    </svg>
                  </button>
                  <button class="btn-icon btn-icon-sm delete-btn" @click="confirmDeleteKb(kb)" title="删除">
                    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页 -->
      <Pagination
        v-if="total > 0"
        :total="total"
        :page="currentPage"
        :page-size="pageSize"
        @update:page="handlePageChange"
      />
    </div>

    <!-- 创建知识库对话框 -->
    <Teleport to="body">
      <div v-if="showCreateDialog" class="dialog-overlay" @click.self="showCreateDialog = false">
        <div class="dialog">
          <div class="dialog-header">
            <h3 class="dialog-title">新建知识库</h3>
            <button class="dialog-close" @click="showCreateDialog = false">&times;</button>
          </div>
          <div class="dialog-body">
            <div class="form-group">
              <label class="form-label">名称 <span class="required">*</span></label>
              <input v-model="newKbForm.name" type="text" class="input" placeholder="输入知识库名称" />
            </div>
            <div class="form-group">
              <label class="form-label">描述</label>
              <textarea v-model="newKbForm.description" class="input textarea" placeholder="输入描述（可选）" rows="2" />
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">分块大小</label>
                <input v-model.number="newKbForm.chunk_size" type="number" class="input" min="100" max="10000" />
                <span class="form-hint">字符数 (100-10000)</span>
              </div>
              <div class="form-group">
                <label class="form-label">分块重叠</label>
                <input v-model.number="newKbForm.chunk_overlap" type="number" class="input" min="0" max="2000" />
                <span class="form-hint">字符数 (0-2000)</span>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">Embedding 模型</label>
              <input v-model="newKbForm.embedding_model" type="text" class="input" placeholder="BAAI/bge-m3" />
            </div>
            <div class="form-group">
              <label class="form-label">负责人</label>
              <input v-model="newKbForm.owner" type="text" class="input" placeholder="负责人姓名" />
            </div>
          </div>
          <div class="dialog-footer">
            <button class="btn btn-secondary" @click="showCreateDialog = false">取消</button>
            <button class="btn btn-primary" @click="createKb" :disabled="creating">
              {{ creating ? '创建中...' : '创建' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 编辑知识库对话框 -->
    <Teleport to="body">
      <div v-if="editingKb" class="dialog-overlay" @click.self="cancelEdit">
        <div class="dialog dialog-wide">
          <div class="dialog-header">
            <h3 class="dialog-title">编辑知识库</h3>
            <button class="dialog-close" @click="cancelEdit">&times;</button>
          </div>
          <div class="dialog-body">
            <div class="form-group">
              <label class="form-label">名称</label>
              <input v-model="editingName" type="text" class="input" placeholder="输入知识库名称" />
            </div>
            <div class="form-group">
              <label class="form-label">描述</label>
              <textarea v-model="editingDescription" class="input textarea" placeholder="输入描述（可选）" rows="2" />
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">分块大小</label>
                <input v-model.number="editingChunkSize" type="number" class="input" min="100" max="10000" />
              </div>
              <div class="form-group">
                <label class="form-label">分块重叠</label>
                <input v-model.number="editingChunkOverlap" type="number" class="input" min="0" max="2000" />
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">Embedding 模型</label>
              <input v-model="editingEmbeddingModel" type="text" class="input" />
            </div>
            <div class="form-group">
              <label class="form-label">负责人</label>
              <input v-model="editingOwner" type="text" class="input" />
            </div>
          </div>
          <div class="dialog-footer">
            <button class="btn btn-secondary" @click="cancelEdit">取消</button>
            <button class="btn btn-primary" @click="saveKb">保存</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 删除确认对话框 -->
    <Teleport to="body">
      <div v-if="deletingKb" class="dialog-overlay" @click.self="cancelDelete">
        <div class="dialog dialog-confirm">
          <div class="dialog-header">
            <h3 class="dialog-title">
              <svg class="dialog-icon warning" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
              </svg>
              确认删除
            </h3>
            <button class="dialog-close" @click="cancelDelete">&times;</button>
          </div>
          <div class="dialog-body">
            <p class="confirm-message">
              确定要删除知识库 <strong>{{ deletingKb.name }}</strong> 吗？
            </p>
            <p class="confirm-warning">
              <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
              </svg>
              此操作将同时删除该知识库下的所有文档和分块数据，且无法恢复。
            </p>
          </div>
          <div class="dialog-footer">
            <button class="btn btn-secondary" @click="cancelDelete">取消</button>
            <button class="btn btn-danger" @click="executeDelete" :disabled="deleting">
              {{ deleting ? '删除中...' : '确认删除' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AppNavRail from '../components/AppNavRail.vue'
import Pagination from '../components/Pagination.vue'

interface KnowledgeBase {
  id: number
  name: string
  description?: string
  chunk_size: number
  chunk_overlap: number
  embedding_model: string
  owner: string
  doc_count: number
  created_at: string
  updated_at?: string
}

interface Stats {
  total_kbs: number
  total_docs: number
  kbs_with_docs: number
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

const knowledgeBases = ref<KnowledgeBase[]>([])
const stats = ref<Stats>({ total_kbs: 0, total_docs: 0, kbs_with_docs: 0 })
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const searchQuery = ref('')

const showCreateDialog = ref(false)
const creating = ref(false)
const newKbForm = ref({
  name: '',
  description: '',
  chunk_size: 1000,
  chunk_overlap: 200,
  embedding_model: 'BAAI/bge-m3',
  owner: ''
})

const editingKb = ref<KnowledgeBase | null>(null)
const editingName = ref('')
const editingDescription = ref('')
const editingChunkSize = ref(1000)
const editingChunkOverlap = ref(200)
const editingEmbeddingModel = ref('')
const editingOwner = ref('')

const deletingKb = ref<KnowledgeBase | null>(null)
const deleting = ref(false)

const loadStats = async () => {
  try {
    const response = await fetch(`${API_BASE}/knowledge/stats`)
    if (response.ok) {
      stats.value = await response.json()
    }
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

const loadKnowledgeBases = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      page: currentPage.value.toString(),
      page_size: pageSize.value.toString(),
      search: searchQuery.value
    })
    const response = await fetch(`${API_BASE}/knowledge?${params}`)
    if (response.ok) {
      const data = await response.json()
      knowledgeBases.value = data.items
      total.value = data.total
    }
  } catch (error) {
    console.error('Failed to load knowledge bases:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadKnowledgeBases()
}

const handlePageChange = (page: number) => {
  currentPage.value = page
  loadKnowledgeBases()
}

const filterByStat = (type: string) => {
  // 可以根据统计类型进行筛选，这里暂时不做特殊处理
  loadKnowledgeBases()
}

const createKb = async () => {
  if (!newKbForm.value.name.trim()) {
    alert('请输入知识库名称')
    return
  }

  creating.value = true
  try {
    const response = await fetch(`${API_BASE}/knowledge`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newKbForm.value)
    })
    if (response.ok) {
      showCreateDialog.value = false
      newKbForm.value = {
        name: '',
        description: '',
        chunk_size: 1000,
        chunk_overlap: 200,
        embedding_model: 'text-embedding-ada-002',
        owner: ''
      }
      await loadStats()
      await loadKnowledgeBases()
    } else {
      const error = await response.text()
      alert(error || '创建失败')
    }
  } catch (error) {
    console.error('Failed to create knowledge base:', error)
    alert('创建失败')
  } finally {
    creating.value = false
  }
}

const startEditKb = (kb: KnowledgeBase) => {
  editingKb.value = kb
  editingName.value = kb.name
  editingDescription.value = kb.description || ''
  editingChunkSize.value = kb.chunk_size
  editingChunkOverlap.value = kb.chunk_overlap
  editingEmbeddingModel.value = kb.embedding_model
  editingOwner.value = kb.owner
}

const cancelEdit = () => {
  editingKb.value = null
}

const saveKb = async () => {
  if (!editingKb.value || !editingName.value.trim()) return

  try {
    const response = await fetch(`${API_BASE}/knowledge/${editingKb.value.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: editingName.value.trim(),
        description: editingDescription.value.trim() || null,
        chunk_size: editingChunkSize.value,
        chunk_overlap: editingChunkOverlap.value,
        embedding_model: editingEmbeddingModel.value.trim() || null,
        owner: editingOwner.value.trim() || null
      })
    })
    if (response.ok) {
      cancelEdit()
      await loadKnowledgeBases()
    } else {
      const error = await response.text()
      alert(error || '更新失败')
    }
  } catch (error) {
    console.error('Failed to update knowledge base:', error)
    alert('更新失败')
  }
}

const confirmDeleteKb = (kb: KnowledgeBase) => {
  deletingKb.value = kb
}

const cancelDelete = () => {
  deletingKb.value = null
}

const executeDelete = async () => {
  if (!deletingKb.value) return

  deleting.value = true
  try {
    const response = await fetch(`${API_BASE}/knowledge/${deletingKb.value.id}`, { method: 'DELETE' })
    if (response.ok) {
      deletingKb.value = null
      await loadStats()
      await loadKnowledgeBases()
    } else {
      const error = await response.text()
      alert(error || '删除失败')
    }
  } catch (error) {
    console.error('Failed to delete knowledge base:', error)
    alert('删除失败')
  } finally {
    deleting.value = false
  }
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  loadStats()
  loadKnowledgeBases()
})
</script>

<style scoped>
.knowledge-layout {
  display: flex;
  height: 100vh;
  background: var(--bg-primary);
}

.main-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  padding: 0 clamp(var(--space-4), 4vw, var(--space-8));
  overflow-y: auto;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-6) 0;
  border-bottom: 1px solid var(--border-subtle);
  margin-bottom: var(--space-6);
}

.page-title {
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0;
}

.header-actions .btn svg {
  width: 16px;
  height: 16px;
  fill: currentColor;
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.stat-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--bg-elevated);
  border-radius: var(--radius-xl);
  padding: var(--space-5);
  border: 1px solid var(--border-subtle);
  cursor: pointer;
  transition: all var(--duration-fast);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.stat-value {
  font-family: var(--font-display);
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
  color: var(--color-primary);
}

.stat-label {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin-top: var(--space-1);
}

.stat-action {
  font-size: var(--text-xs);
  color: var(--color-primary);
  padding: var(--space-2) var(--space-3);
  background: var(--color-primary-light);
  border-radius: var(--radius-full);
}

/* 工具栏 */
.toolbar {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}

.search-box {
  flex: 1;
  max-width: 400px;
  position: relative;
}

.search-box svg {
  position: absolute;
  left: var(--space-3);
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  fill: var(--text-muted);
}

.search-box .input {
  padding-left: var(--space-10);
}

.toolbar .btn svg {
  width: 16px;
  height: 16px;
  fill: currentColor;
}

/* 表格 */
.table-container {
  flex: 1;
  min-height: 0;
  background: var(--bg-elevated);
  border-radius: var(--radius-xl);
  border: 1px solid var(--border-subtle);
  overflow: auto;
  margin-bottom: var(--space-4);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table thead {
  position: sticky;
  top: 0;
  z-index: 1;
}

.data-table th,
.data-table td {
  padding: var(--space-4);
  text-align: left;
  border-bottom: 1px solid var(--border-subtle);
}

.data-table th {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--text-secondary);
  background: var(--bg-secondary);
}

.data-table td {
  font-size: var(--text-sm);
  color: var(--text-primary);
}

.data-table tr:hover td {
  background: var(--bg-hover);
}

.loading-cell,
.empty-cell {
  text-align: center;
  padding: var(--space-10) !important;
  color: var(--text-muted);
}

.loading-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-3);
}

.kb-name {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: var(--font-medium);
}

.kb-name:hover {
  text-decoration: underline;
}

.action-btns {
  display: flex;
  gap: var(--space-1);
}

/* 表单 */
.form-row {
  display: flex;
  gap: var(--space-4);
}

.form-row .form-group {
  flex: 1;
}

.form-hint {
  display: block;
  font-size: var(--text-xs);
  color: var(--text-muted);
  margin-top: var(--space-1);
}

.dialog-wide {
  max-width: 520px;
}

/* 删除确认对话框 */
.dialog-confirm {
  max-width: 420px;
}

.dialog-title {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.dialog-icon {
  width: 20px;
  height: 20px;
  fill: currentColor;
}

.dialog-icon.warning {
  fill: var(--color-warning, #f59e0b);
}

.confirm-message {
  font-size: var(--text-base);
  color: var(--text-primary);
  margin: 0 0 var(--space-4) 0;
}

.confirm-message strong {
  color: var(--color-primary);
}

.confirm-warning {
  display: flex;
  align-items: flex-start;
  gap: var(--space-2);
  font-size: var(--text-sm);
  color: var(--color-warning, #f59e0b);
  background: rgba(245, 158, 11, 0.1);
  padding: var(--space-3);
  border-radius: var(--radius-md);
  margin: 0;
}

.confirm-warning svg {
  width: 16px;
  height: 16px;
  fill: var(--color-warning, #f59e0b);
  flex-shrink: 0;
  margin-top: 2px;
}

.btn-danger {
  background: var(--color-danger, #ef4444);
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: var(--color-danger-dark, #dc2626);
}

.btn-danger:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
