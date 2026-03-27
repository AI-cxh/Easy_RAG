<template>
  <div class="knowledge-layout">
    <AppNavRail />

    <div class="main-wrapper">
      <header class="page-header">
        <div class="header-left">
          <Breadcrumb :items="breadcrumbItems" />
          <div class="kb-info" v-if="knowledgeBase">
            <h1 class="page-title">{{ knowledgeBase.name }}</h1>
            <span class="tag tag-primary">kb_{{ kbId }}</span>
          </div>
        </div>
        <div class="header-actions">
          <button class="btn btn-secondary" @click="goBack">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/>
            </svg>
            返回知识库
          </button>
          <button class="btn btn-primary" @click="triggerUpload">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M9 16h6v-6h4l-7-7-7 7h4zm-4 2h14v2H5z"/>
            </svg>
            上传文档
          </button>
          <input
            ref="fileInputRef"
            type="file"
            accept=".txt,.md,.pdf,.docx"
            multiple
            hidden
            @change="handleFileSelect"
          />
        </div>
      </header>

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
            placeholder="搜索文档名称..."
            @keyup.enter="handleSearch"
          />
        </div>
        <select v-model="statusFilter" class="input status-select" @change="handleSearch">
          <option value="">全部状态</option>
          <option value="pending">待处理</option>
          <option value="processing">处理中</option>
          <option value="completed">已完成</option>
          <option value="failed">失败</option>
        </select>
        <button class="btn btn-secondary" @click="handleSearch">搜索</button>
        <button class="btn btn-ghost" @click="loadDocuments">
          <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
          </svg>
          刷新
        </button>
      </div>

      <!-- 上传进度 -->
      <div v-if="uploadingFiles.length > 0" class="upload-progress">
        <div class="progress-info">
          <span class="progress-text">正在处理: {{ uploadingFiles[uploadingFiles.length - 1] }}</span>
          <span v-if="uploadProgress !== null" class="progress-percent">{{ uploadProgress }}%</span>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: (uploadProgress || 0) + '%' }"></div>
        </div>
      </div>

      <!-- 文档表格 -->
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>文档名称</th>
              <th>来源</th>
              <th>处理模式</th>
              <th>状态</th>
              <th>启用</th>
              <th>分块数</th>
              <th>类型</th>
              <th>大小</th>
              <th>更新时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="10" class="loading-cell">
                <span class="spinner"></span>
                加载中...
              </td>
            </tr>
            <tr v-else-if="documents.length === 0">
              <td colspan="10" class="empty-cell">
                暂无文档
              </td>
            </tr>
            <tr v-for="doc in documents" :key="doc.id">
              <td>
                <router-link :to="`/knowledge/${kbId}/documents/${doc.id}/chunks`" class="doc-name">
                  {{ doc.filename }}
                </router-link>
              </td>
              <td>{{ doc.source || 'upload' }}</td>
              <td>{{ doc.processing_mode || 'auto' }}</td>
              <td>
                <span :class="['status-tag', doc.status]">{{ getStatusText(doc.status) }}</span>
              </td>
              <td>
                <label class="toggle-switch">
                  <input type="checkbox" :checked="doc.enabled" @change="toggleDocument(doc)" />
                  <span class="toggle-slider"></span>
                </label>
              </td>
              <td>{{ doc.chunk_count }}</td>
              <td>{{ doc.file_type || getFileType(doc.filename) }}</td>
              <td>{{ formatFileSize(doc.file_size) }}</td>
              <td>{{ formatDate(doc.updated_at || doc.created_at) }}</td>
              <td>
                <div class="action-btns">
                  <button class="btn-icon btn-icon-sm" @click="viewChunks(doc)" title="查看分块">
                    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>
                    </svg>
                  </button>
                  <button class="btn-icon btn-icon-sm" @click="downloadDocument(doc)" title="下载">
                    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>
                    </svg>
                  </button>
                  <button class="btn-icon btn-icon-sm delete-btn" @click="deleteDocument(doc.id)" title="删除">
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppNavRail from '../components/AppNavRail.vue'
import Breadcrumb from '../components/Breadcrumb.vue'
import Pagination from '../components/Pagination.vue'

interface Document {
  id: number
  kb_id: number
  filename: string
  file_path: string
  file_size: number
  file_type: string
  chunk_count: number
  source: string
  processing_mode: string
  status: string
  enabled: boolean
  created_at: string
  updated_at?: string
}

interface KnowledgeBase {
  id: number
  name: string
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

const route = useRoute()
const router = useRouter()
const kbId = computed(() => Number(route.params.kbId))

const knowledgeBase = ref<KnowledgeBase | null>(null)
const documents = ref<Document[]>([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const searchQuery = ref('')
const statusFilter = ref('')

const fileInputRef = ref<HTMLInputElement>()
const uploadProgress = ref<number | null>(null)
const uploadingFiles = ref<string[]>([]) // 正在上传的文件名列表

const breadcrumbItems = computed(() => [
  { label: '知识库管理', to: '/knowledge' },
  { label: '文档管理' }
])

const loadKnowledgeBase = async () => {
  try {
    const response = await fetch(`${API_BASE}/knowledge/${kbId.value}`)
    if (response.ok) {
      knowledgeBase.value = await response.json()
    }
  } catch (error) {
    console.error('Failed to load knowledge base:', error)
  }
}

const loadDocuments = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      page: currentPage.value.toString(),
      page_size: pageSize.value.toString(),
      search: searchQuery.value,
      status: statusFilter.value
    })
    const response = await fetch(`${API_BASE}/knowledge/${kbId.value}/documents?${params}`)
    if (response.ok) {
      const data = await response.json()
      documents.value = data.items
      total.value = data.total
    }
  } catch (error) {
    console.error('Failed to load documents:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadDocuments()
}

const handlePageChange = (page: number) => {
  currentPage.value = page
  loadDocuments()
}

const goBack = () => {
  router.push('/knowledge')
}

const triggerUpload = () => {
  fileInputRef.value?.click()
}

const handleFileSelect = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files ? Array.from(target.files) : []
  if (files.length > 0) {
    await uploadFiles(files)
  }
  target.value = ''
}

const uploadFiles = async (files: File[]) => {
  for (const file of files) {
    // 添加临时文档记录显示处理中状态
    const tempDoc: Document = {
      id: -Date.now(), // 临时ID
      kb_id: kbId.value,
      filename: file.name,
      file_path: '',
      file_size: file.size,
      file_type: getFileType(file.name),
      chunk_count: 0,
      source: 'upload',
      processing_mode: 'auto',
      status: 'processing',
      enabled: true,
      created_at: new Date().toISOString()
    }
    documents.value.unshift(tempDoc)

    uploadingFiles.value.push(file.name)

    try {
      const formData = new FormData()
      formData.append('file', file)

      await new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest()
        xhr.open('POST', `${API_BASE}/upload/${kbId.value}`)

        xhr.upload.onprogress = (e) => {
          if (e.lengthComputable) {
            uploadProgress.value = Math.round((e.loaded / e.total) * 100)
          }
        }

        xhr.onload = () => {
          if (xhr.status >= 200 && xhr.status < 300) {
            resolve(xhr.response)
          } else {
            reject(new Error('上传失败'))
          }
        }

        xhr.onerror = () => reject(new Error('上传失败'))
        xhr.send(formData)
      })

      // 上传成功后刷新列表
      await loadDocuments()
    } catch (error) {
      console.error('Failed to upload file:', error)
      // 移除临时记录
      documents.value = documents.value.filter(d => d.id !== tempDoc.id)
      alert(`上传文件 ${file.name} 失败`)
    } finally {
      uploadingFiles.value = uploadingFiles.value.filter(f => f !== file.name)
    }
  }
  uploadProgress.value = null
}

const toggleDocument = async (doc: Document) => {
  try {
    const response = await fetch(`${API_BASE}/upload/documents/${doc.id}/toggle`, {
      method: 'PUT'
    })
    if (response.ok) {
      doc.enabled = !doc.enabled
    }
  } catch (error) {
    console.error('Failed to toggle document:', error)
  }
}

const viewChunks = (doc: Document) => {
  router.push(`/knowledge/${kbId.value}/documents/${doc.id}/chunks`)
}

const downloadDocument = (doc: Document) => {
  // 创建下载链接
  const link = document.createElement('a')
  link.href = doc.file_path
  link.download = doc.filename
  link.click()
}

const deleteDocument = async (docId: number) => {
  if (!confirm('确定要删除该文档吗？')) return

  try {
    const response = await fetch(`${API_BASE}/upload/documents/${docId}`, {
      method: 'DELETE'
    })
    if (response.ok) {
      await loadDocuments()
    } else {
      const error = await response.text()
      alert(error || '删除失败')
    }
  } catch (error) {
    console.error('Failed to delete document:', error)
    alert('删除失败')
  }
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    pending: '待处理',
    processing: '处理中',
    completed: '已完成',
    failed: '失败'
  }
  return statusMap[status] || status
}

const getFileType = (filename: string) => {
  const ext = filename.split('.').pop()?.toLowerCase() || ''
  const typeMap: Record<string, string> = {
    txt: 'text',
    md: 'markdown',
    pdf: 'pdf',
    docx: 'docx'
  }
  return typeMap[ext] || ext
}

const formatFileSize = (bytes?: number) => {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let size = bytes
  let unitIndex = 0
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  return `${size.toFixed(1)} ${units[unitIndex]}`
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
  loadKnowledgeBase()
  loadDocuments()
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

.kb-info {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.page-title {
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0;
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

.status-select {
  width: 120px;
}

.toolbar .btn svg {
  width: 16px;
  height: 16px;
  fill: currentColor;
}

/* 上传进度 */
.upload-progress {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  padding: var(--space-4);
  background: var(--color-primary-light);
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-4);
}

.progress-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.progress-text {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-primary-dark);
}

.progress-percent {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--color-primary);
}

.progress-bar {
  height: 6px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--gradient-accent);
  border-radius: var(--radius-full);
  transition: width var(--duration-fast);
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

.doc-name {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: var(--font-medium);
}

.doc-name:hover {
  text-decoration: underline;
}

/* 状态标签 */
.status-tag {
  display: inline-block;
  padding: var(--space-1) var(--space-2);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  border-radius: var(--radius-md);
}

.status-tag.completed {
  background: var(--color-success-light);
  color: var(--color-success-dark);
}

.status-tag.pending {
  background: var(--color-warning-light);
  color: #8b6914;
}

.status-tag.processing {
  background: var(--color-primary-light);
  color: var(--color-primary-dark);
}

.status-tag.failed {
  background: var(--color-danger-light);
  color: var(--color-danger);
}

/* 开关 */
.toggle-switch {
  position: relative;
  display: inline-block;
  width: 36px;
  height: 20px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  inset: 0;
  background: var(--bg-tertiary);
  border-radius: var(--radius-full);
  transition: var(--duration-fast);
}

.toggle-slider::before {
  position: absolute;
  content: '';
  height: 14px;
  width: 14px;
  left: 3px;
  bottom: 3px;
  background: white;
  border-radius: 50%;
  transition: var(--duration-fast);
}

.toggle-switch input:checked + .toggle-slider {
  background: var(--color-primary);
}

.toggle-switch input:checked + .toggle-slider::before {
  transform: translateX(16px);
}

.action-btns {
  display: flex;
  gap: var(--space-1);
}
</style>
