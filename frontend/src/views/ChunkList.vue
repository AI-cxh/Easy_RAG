<template>
  <div class="knowledge-layout">
    <AppNavRail />

    <div class="main-wrapper">
      <header class="page-header">
        <div class="header-left">
          <Breadcrumb :items="breadcrumbItems" />
          <div class="doc-info" v-if="document">
            <h1 class="page-title">{{ document.filename }}</h1>
            <span class="doc-meta">知识库 ID: {{ kbId }}</span>
          </div>
        </div>
        <div class="header-actions">
          <button class="btn btn-secondary" @click="goBack">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/>
            </svg>
            返回文档
          </button>
          <button class="btn btn-secondary" @click="rebuildVectors" :disabled="rebuilding">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
            </svg>
            {{ rebuilding ? '重建中...' : '重建向量' }}
          </button>
          <button class="btn btn-primary" @click="showCreateDialog = true">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
            </svg>
            新建分块
          </button>
        </div>
      </header>

      <!-- 操作栏 -->
      <div class="toolbar">
        <select v-model="enabledFilter" class="input status-select" @change="handleFilterChange">
          <option :value="null">全部状态</option>
          <option :value="true">已启用</option>
          <option :value="false">已禁用</option>
        </select>
        <button class="btn btn-ghost" @click="loadChunks">
          <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
          </svg>
          刷新
        </button>
        <div class="batch-actions" v-if="selectedChunks.length > 0">
          <span class="selected-count">已选 {{ selectedChunks.length }} 项</span>
          <button class="btn btn-secondary btn-sm" @click="batchEnable">批量启用</button>
          <button class="btn btn-secondary btn-sm" @click="batchDisable">批量禁用</button>
        </div>
        <div class="batch-actions" v-else>
          <button class="btn btn-ghost btn-sm" @click="enableAll">全量启用</button>
          <button class="btn btn-ghost btn-sm" @click="disableAll">全量禁用</button>
        </div>
      </div>

      <!-- 分块表格 -->
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th class="checkbox-col">
                <input type="checkbox" v-model="selectAll" @change="handleSelectAll" />
              </th>
              <th>序号</th>
              <th>内容</th>
              <th>状态</th>
              <th>字符数</th>
              <th>Token 数</th>
              <th>更新时间</th>
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
            <tr v-else-if="chunks.length === 0">
              <td colspan="8" class="empty-cell">
                暂无分块
              </td>
            </tr>
            <tr v-for="(chunk, index) in chunks" :key="chunk.id">
              <td class="checkbox-col">
                <input
                  type="checkbox"
                  :value="chunk.id"
                  v-model="selectedChunks"
                />
              </td>
              <td>{{ (currentPage - 1) * pageSize + index + 1 }}</td>
              <td class="content-cell">
                <div class="content-preview">{{ chunk.content }}</div>
              </td>
              <td>
                <span :class="['status-tag', chunk.enabled ? 'enabled' : 'disabled']">
                  {{ chunk.enabled ? '启用' : '禁用' }}
                </span>
              </td>
              <td>{{ chunk.char_count }}</td>
              <td>{{ chunk.token_count }}</td>
              <td>{{ formatDate(chunk.updated_at || chunk.created_at) }}</td>
              <td>
                <div class="action-btns">
                  <button class="btn-icon btn-icon-sm" @click="editChunk(chunk)" title="编辑">
                    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
                    </svg>
                  </button>
                  <button class="btn-icon btn-icon-sm" @click="toggleChunk(chunk)" title="切换状态">
                    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path d="M17 7H7a5 5 0 0 0 0 10h10a5 5 0 0 0 0-10zm0 8H7a3 3 0 0 1 0-6h10a3 3 0 0 1 0 6z"/>
                    </svg>
                  </button>
                  <button class="btn-icon btn-icon-sm delete-btn" @click="deleteChunk(chunk.id)" title="删除">
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

    <!-- 新建分块对话框 -->
    <Teleport to="body">
      <div v-if="showCreateDialog" class="dialog-overlay" @click.self="showCreateDialog = false">
        <div class="dialog dialog-wide">
          <div class="dialog-header">
            <h3 class="dialog-title">新建分块</h3>
            <button class="dialog-close" @click="showCreateDialog = false">&times;</button>
          </div>
          <div class="dialog-body">
            <div class="form-group">
              <label class="form-label">内容 <span class="required">*</span></label>
              <textarea
                v-model="newChunkContent"
                class="input textarea"
                placeholder="输入分块内容"
                rows="10"
              ></textarea>
              <div class="content-stats">
                字符数: {{ newChunkContent.length }} | Token 数: {{ estimateTokens(newChunkContent) }}
              </div>
            </div>
          </div>
          <div class="dialog-footer">
            <button class="btn btn-secondary" @click="showCreateDialog = false">取消</button>
            <button class="btn btn-primary" @click="createChunk" :disabled="creating">
              {{ creating ? '创建中...' : '创建' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 编辑分块对话框 -->
    <Teleport to="body">
      <div v-if="editingChunk" class="dialog-overlay" @click.self="cancelEdit">
        <div class="dialog dialog-wide">
          <div class="dialog-header">
            <h3 class="dialog-title">编辑分块</h3>
            <button class="dialog-close" @click="cancelEdit">&times;</button>
          </div>
          <div class="dialog-body">
            <div class="form-group">
              <label class="form-label">内容</label>
              <textarea
                v-model="editingContent"
                class="input textarea"
                rows="10"
              ></textarea>
              <div class="content-stats">
                字符数: {{ editingContent.length }} | Token 数: {{ estimateTokens(editingContent) }}
              </div>
            </div>
          </div>
          <div class="dialog-footer">
            <button class="btn btn-secondary" @click="cancelEdit">取消</button>
            <button class="btn btn-primary" @click="saveChunk">保存</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 重建向量确认对话框 -->
    <Teleport to="body">
      <div v-if="showRebuildDialog" class="dialog-overlay" @click.self="showRebuildDialog = false">
        <div class="dialog">
          <div class="dialog-header">
            <h3 class="dialog-title">重建向量</h3>
            <button class="dialog-close" @click="showRebuildDialog = false">&times;</button>
          </div>
          <div class="dialog-body">
            <p class="dialog-message">确定要重建该文档的向量吗？</p>
            <p class="dialog-hint">此操作将根据当前启用的分块重新生成向量，可能需要一些时间。</p>
          </div>
          <div class="dialog-footer">
            <button class="btn btn-secondary" @click="showRebuildDialog = false">取消</button>
            <button class="btn btn-primary" @click="confirmRebuild" :disabled="rebuilding">
              {{ rebuilding ? '重建中...' : '确认重建' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 结果提示对话框 -->
    <Teleport to="body">
      <div v-if="showResultDialog" class="dialog-overlay" @click.self="showResultDialog = false">
        <div class="dialog" :class="{ 'dialog-success': resultSuccess, 'dialog-danger': !resultSuccess }">
          <div class="dialog-header">
            <h3 class="dialog-title">{{ resultSuccess ? '操作成功' : '操作失败' }}</h3>
            <button class="dialog-close" @click="showResultDialog = false">&times;</button>
          </div>
          <div class="dialog-body">
            <p class="dialog-message">{{ resultMessage }}</p>
          </div>
          <div class="dialog-footer">
            <button class="btn" :class="resultSuccess ? 'btn-primary' : 'btn-secondary'" @click="showResultDialog = false">
              确定
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppNavRail from '../components/AppNavRail.vue'
import Breadcrumb from '../components/Breadcrumb.vue'
import Pagination from '../components/Pagination.vue'
import { knowledgeAPI, chunkAPI } from '../api/client'

interface Chunk {
  id: number
  doc_id: number
  content: string
  char_count: number
  token_count: number
  enabled: boolean
  sort_order: number
  created_at: string
  updated_at?: string
}

interface Document {
  id: number
  filename: string
}

const route = useRoute()
const router = useRouter()
const kbId = computed(() => Number(route.params.kbId))
const docId = computed(() => Number(route.params.docId))

const document = ref<Document | null>(null)
const chunks = ref<Chunk[]>([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const enabledFilter = ref<boolean | null>(null)

const selectedChunks = ref<number[]>([])
const selectAll = ref(false)

const showCreateDialog = ref(false)
const creating = ref(false)
const newChunkContent = ref('')

const editingChunk = ref<Chunk | null>(null)
const editingContent = ref('')

const rebuilding = ref(false)
const showRebuildDialog = ref(false)
const showResultDialog = ref(false)
const resultSuccess = ref(false)
const resultMessage = ref('')

const breadcrumbItems = computed(() => [
  { label: '知识库管理', to: '/knowledge' },
  { label: '文档管理', to: `/knowledge/${kbId.value}/documents` },
  { label: '切片管理' }
])

const loadDocument = async () => {
  try {
    const data = await knowledgeAPI.getDocuments(kbId.value)
    document.value = data.items.find((d: Document) => d.id === docId.value)
  } catch (error) {
    console.error('Failed to load document:', error)
  }
}

const loadChunks = async () => {
  loading.value = true
  try {
    const data = await chunkAPI.getList(docId.value, {
      page: currentPage.value,
      page_size: pageSize.value,
      enabled: enabledFilter.value ?? undefined
    })
    chunks.value = data.items
    total.value = data.total
  } catch (error) {
    console.error('Failed to load chunks:', error)
  } finally {
    loading.value = false
  }
}

const handleFilterChange = () => {
  currentPage.value = 1
  loadChunks()
}

const handlePageChange = (page: number) => {
  currentPage.value = page
  loadChunks()
}

const handleSelectAll = () => {
  if (selectAll.value) {
    selectedChunks.value = chunks.value.map(c => c.id)
  } else {
    selectedChunks.value = []
  }
}

const goBack = () => {
  router.push(`/knowledge/${kbId.value}/documents`)
}

const estimateTokens = (text: string) => {
  // 简单估算：英文约4字符=1token，中文约1.5字符=1token
  const chineseChars = (text.match(/[\u4e00-\u9fa5]/g) || []).length
  const otherChars = text.length - chineseChars
  return Math.ceil(chineseChars / 1.5 + otherChars / 4)
}

const createChunk = async () => {
  if (!newChunkContent.value.trim()) {
    alert('请输入分块内容')
    return
  }

  creating.value = true
  try {
    await chunkAPI.create(docId.value, newChunkContent.value)
    showCreateDialog.value = false
    newChunkContent.value = ''
    await loadChunks()
  } catch (error) {
    console.error('Failed to create chunk:', error)
    alert(error instanceof Error ? error.message : '创建失败')
  } finally {
    creating.value = false
  }
}

const editChunk = (chunk: Chunk) => {
  editingChunk.value = chunk
  editingContent.value = chunk.content
}

const cancelEdit = () => {
  editingChunk.value = null
  editingContent.value = ''
}

const saveChunk = async () => {
  if (!editingChunk.value) return

  try {
    await chunkAPI.update(editingChunk.value.id, { content: editingContent.value })
    cancelEdit()
    await loadChunks()
  } catch (error) {
    console.error('Failed to update chunk:', error)
    alert(error instanceof Error ? error.message : '更新失败')
  }
}

const toggleChunk = async (chunk: Chunk) => {
  try {
    await chunkAPI.toggle(chunk.id)
    chunk.enabled = !chunk.enabled
  } catch (error) {
    console.error('Failed to toggle chunk:', error)
    alert(error instanceof Error ? error.message : '操作失败')
  }
}

const deleteChunk = async (chunkId: number) => {
  if (!confirm('确定要删除该分块吗？')) return

  try {
    await chunkAPI.delete(chunkId)
    await loadChunks()
  } catch (error) {
    console.error('Failed to delete chunk:', error)
    alert(error instanceof Error ? error.message : '删除失败')
  }
}

const batchEnable = async () => {
  if (selectedChunks.value.length === 0) return

  try {
    await chunkAPI.batchEnable(selectedChunks.value)
    selectedChunks.value = []
    selectAll.value = false
    await loadChunks()
  } catch (error) {
    console.error('Failed to batch enable:', error)
    alert(error instanceof Error ? error.message : '操作失败')
  }
}

const batchDisable = async () => {
  if (selectedChunks.value.length === 0) return

  try {
    await chunkAPI.batchDisable(selectedChunks.value)
    selectedChunks.value = []
    selectAll.value = false
    await loadChunks()
  } catch (error) {
    console.error('Failed to batch disable:', error)
    alert(error instanceof Error ? error.message : '操作失败')
  }
}

const enableAll = async () => {
  try {
    await chunkAPI.enableAll(docId.value)
    await loadChunks()
  } catch (error) {
    console.error('Failed to enable all:', error)
    alert(error instanceof Error ? error.message : '操作失败')
  }
}

const disableAll = async () => {
  try {
    await chunkAPI.disableAll(docId.value)
    await loadChunks()
  } catch (error) {
    console.error('Failed to disable all:', error)
    alert(error instanceof Error ? error.message : '操作失败')
  }
}

const rebuildVectors = () => {
  showRebuildDialog.value = true
}

const confirmRebuild = async () => {
  showRebuildDialog.value = false
  rebuilding.value = true

  try {
    const data = await chunkAPI.rebuildVectors(docId.value)
    resultSuccess.value = true
    resultMessage.value = data.message || '向量重建完成'
  } catch (error) {
    console.error('Failed to rebuild vectors:', error)
    resultSuccess.value = false
    resultMessage.value = error instanceof Error ? error.message : '重建失败'
  } finally {
    rebuilding.value = false
    showResultDialog.value = true
  }
}

const formatDate = (dateStr?: string) => {
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
  loadDocument()
  loadChunks()
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
  align-items: flex-start;
  justify-content: space-between;
  padding: var(--space-6) 0;
  border-bottom: 1px solid var(--border-subtle);
  margin-bottom: var(--space-6);
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.doc-info {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.page-title {
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0;
}

.doc-meta {
  font-size: var(--text-sm);
  color: var(--text-muted);
}

.header-actions {
  display: flex;
  gap: var(--space-3);
}

.header-actions .btn svg {
  width: 16px;
  height: 16px;
  fill: currentColor;
}

/* 工具栏 */
.toolbar {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
  flex-wrap: wrap;
}

.status-select {
  width: 120px;
}

.toolbar .btn svg {
  width: 16px;
  height: 16px;
  fill: currentColor;
}

.batch-actions {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-left: auto;
}

.selected-count {
  font-size: var(--text-sm);
  color: var(--text-secondary);
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
  padding: var(--space-3) var(--space-4);
  text-align: left;
  border-bottom: 1px solid var(--border-subtle);
}

.data-table th {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--text-secondary);
  background: var(--bg-secondary);
  white-space: nowrap;
}

.data-table td {
  font-size: var(--text-sm);
  color: var(--text-primary);
}

.data-table tr:hover td {
  background: var(--bg-hover);
}

.checkbox-col {
  width: 40px;
  text-align: center;
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

.content-cell {
  max-width: 400px;
}

.content-preview {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.5;
}

/* 状态标签 */
.status-tag {
  display: inline-block;
  padding: var(--space-1) var(--space-2);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  border-radius: var(--radius-md);
}

.status-tag.enabled {
  background: var(--color-success-light);
  color: var(--color-success-dark);
}

.status-tag.disabled {
  background: var(--bg-tertiary);
  color: var(--text-muted);
}

.action-btns {
  display: flex;
  gap: var(--space-1);
}

/* 对话框 */
.dialog-wide {
  max-width: 640px;
}

.content-stats {
  font-size: var(--text-xs);
  color: var(--text-muted);
  margin-top: var(--space-2);
}

.textarea {
  min-height: 200px;
  font-family: var(--font-mono);
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
  z-index: 1000;
}

.dialog {
  background: var(--bg-elevated);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  width: min(400px, 90vw);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
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
  transition: all 0.15s;
}

.dialog-close:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.dialog-body {
  padding: var(--space-5);
}

.dialog-message {
  margin: 0;
  font-size: var(--text-base);
  color: var(--text-primary);
  line-height: 1.6;
}

.dialog-hint {
  margin: var(--space-2) 0 0;
  font-size: var(--text-sm);
  color: var(--text-muted);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-5);
  border-top: 1px solid var(--border-subtle);
}

.dialog-success .dialog-header {
  background: rgba(34, 197, 94, 0.08);
}

.dialog-success .dialog-title {
  color: var(--color-success);
}

.dialog-danger .dialog-header {
  background: rgba(220, 38, 38, 0.08);
}

.dialog-danger .dialog-title {
  color: var(--color-danger);
}
</style>
