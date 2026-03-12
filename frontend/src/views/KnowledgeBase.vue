<template>
  <div class="knowledge-layout">
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
    <div class="kb-main-wrapper">
      <!-- 顶部导航 -->
      <header class="kb-header">
        <h1 class="header-title">知识库管理</h1>
        <button class="btn btn-primary" @click="showCreateDialog = true">
          <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
          </svg>
          创建知识库
        </button>
      </header>

    <div class="kb-content">
      <!-- 左侧知识库列表 -->
      <aside class="kb-sidebar">
        <div class="sidebar-title">
          <span>知识库</span>
          <span class="count">{{ knowledgeBases.length }}</span>
        </div>

        <div v-if="loading" class="loading-state">
          <span class="spinner"></span>
        </div>

        <div v-else class="kb-list">
          <div
            v-for="kb in knowledgeBases"
            :key="kb.id"
            :class="['kb-item', { active: selectedKbId === kb.id }]"
            @click="selectKb(kb)"
          >
            <div class="kb-info">
              <span class="kb-name">{{ kb.name }}</span>
              <span v-if="kb.description" class="kb-desc">{{ kb.description }}</span>
            </div>
            <div class="kb-actions" @click.stop>
              <button class="btn-icon btn-icon-sm" @click="startEditKb(kb)" title="重命名">
                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
                </svg>
              </button>
              <button class="btn-icon btn-icon-sm delete-btn" @click="deleteKb(kb.id)" title="删除">
                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                </svg>
              </button>
            </div>
          </div>

          <div v-if="knowledgeBases.length === 0" class="empty-list">
            <p>暂无知识库</p>
          </div>
        </div>
      </aside>

      <!-- 右侧详情面板 -->
      <main class="kb-main">
        <div v-if="!selectedKbId" class="empty-main">
          <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-1 9H9V9h10v2zm-4 4H9v-2h6v2zm4-8H9V5h10v2z"/>
          </svg>
          <p>选择一个知识库查看详情</p>
        </div>

        <div v-else class="kb-detail">
          <div class="detail-header">
            <h2 class="detail-title">{{ selectedKb?.name }}</h2>
            <p v-if="selectedKb?.description" class="detail-desc">{{ selectedKb?.description }}</p>
          </div>

          <!-- 上传区域 -->
          <div class="upload-area">
            <div
              class="upload-zone"
              :class="{ dragover: isDragover }"
              @drop="handleDrop"
              @dragover.prevent="isDragover = true"
              @dragleave.prevent="isDragover = false"
              @click="triggerUpload"
            >
              <input
                ref="fileInputRef"
                type="file"
                accept=".txt,.md,.pdf,.docx"
                multiple
                hidden
                @change="handleFileSelect"
              />
              <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM14 13v4h-4v-4H7l5-5 5 5h-3z"/>
              </svg>
              <p>拖拽文件到这里或点击上传</p>
              <span>支持 .txt, .md, .pdf, .docx</span>
            </div>

            <div v-if="uploadProgress !== null" class="upload-progress">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
              </div>
              <span>{{ uploadProgress }}%</span>
            </div>
          </div>

          <!-- 文档列表 -->
          <div class="docs-section">
            <div class="section-header">
              <h3>文档列表</h3>
              <span class="doc-count">{{ documents.length }} 个文档</span>
            </div>

            <div v-if="loadingDocs" class="loading-state">
              <span class="spinner"></span>
            </div>

            <div v-else-if="documents.length === 0" class="empty-docs">
              <p>暂无文档</p>
              <span>上传文件后自动处理</span>
            </div>

            <div v-else class="doc-list">
              <div v-for="doc in documents" :key="doc.id" class="doc-item">
                <div class="doc-icon">
                  <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm4 18H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>
                  </svg>
                </div>
                <div class="doc-info">
                  <span class="doc-name">{{ doc.filename }}</span>
                  <span class="doc-meta">{{ formatFileSize(doc.file_size) }} · {{ doc.chunk_count }} 个分块</span>
                </div>
                <button class="btn-icon btn-icon-sm delete-btn" @click="deleteDoc(doc.id)" title="删除">
                  <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>

    <!-- 创建知识库对话框 -->
    <Teleport to="body">
      <div v-if="showCreateDialog" class="dialog-overlay" @click.self="showCreateDialog = false">
        <div class="dialog">
          <div class="dialog-header">
            <h3 class="dialog-title">创建知识库</h3>
            <button class="dialog-close" @click="showCreateDialog = false">&times;</button>
          </div>
          <div class="dialog-body">
            <div class="form-group">
              <label class="form-label">名称 <span class="required">*</span></label>
              <input
                v-model="newKbForm.name"
                type="text"
                class="input"
                placeholder="输入知识库名称"
              />
            </div>
            <div class="form-group">
              <label class="form-label">描述</label>
              <textarea
                v-model="newKbForm.description"
                class="input textarea"
                placeholder="输入描述（可选）"
                rows="3"
              />
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

    <!-- 重命名对话框 -->
    <Teleport to="body">
      <div v-if="editingKbId" class="dialog-overlay" @click.self="cancelKbEdit">
        <div class="dialog">
          <div class="dialog-header">
            <h3 class="dialog-title">重命名知识库</h3>
            <button class="dialog-close" @click="cancelKbEdit">&times;</button>
          </div>
          <div class="dialog-body">
            <div class="form-group">
              <label class="form-label">名称</label>
              <input
                v-model="editingName"
                type="text"
                class="input"
                placeholder="输入新名称"
                @keydown.enter="saveKbName(editingKbId!)"
              />
            </div>
          </div>
          <div class="dialog-footer">
            <button class="btn btn-secondary" @click="cancelKbEdit">取消</button>
            <button class="btn btn-primary" @click="saveKbName(editingKbId!)">保存</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { knowledgeAPI, uploadAPI } from '../api/client'

interface KnowledgeBase {
  id: number
  name: string
  description?: string
  created_at?: string
}

interface Document {
  id: number
  filename: string
  file_size: number
  chunk_count: number
}

const knowledgeBases = ref<KnowledgeBase[]>([])
const selectedKbId = ref<number | null>(null)
const documents = ref<Document[]>([])
const loading = ref(false)
const loadingDocs = ref(false)
const showCreateDialog = ref(false)
const creating = ref(false)
const fileInputRef = ref<HTMLInputElement>()

const editingKbId = ref<number>()
const editingName = ref('')

const newKbForm = ref({
  name: '',
  description: ''
})

const isDragover = ref(false)
const uploadProgress = ref<number | null>(null)

const selectedKb = computed(() =>
  knowledgeBases.value.find(kb => kb.id === selectedKbId.value)
)

const loadKnowledgeBases = async () => {
  loading.value = true
  try {
    knowledgeBases.value = await knowledgeAPI.getAll()
  } catch (error) {
    console.error('Failed to load knowledge bases:', error)
  } finally {
    loading.value = false
  }
}

const selectKb = (kb: KnowledgeBase) => {
  selectedKbId.value = kb.id
  loadDocuments()
}

const loadDocuments = async () => {
  if (!selectedKbId.value) return

  loadingDocs.value = true
  try {
    const result = await knowledgeAPI.getDocuments(selectedKbId.value)
    documents.value = result.documents
  } catch (error) {
    console.error('Failed to load documents:', error)
  } finally {
    loadingDocs.value = false
  }
}

const createKb = async () => {
  if (!newKbForm.value.name.trim()) {
    alert('请输入知识库名称')
    return
  }

  creating.value = true
  try {
    const result = await knowledgeAPI.create(newKbForm.value)
    showCreateDialog.value = false
    newKbForm.value = { name: '', description: '' }
    await loadKnowledgeBases()
    if (result && result.id) {
      selectKb(result)
    }
  } catch (error: any) {
    console.error('Failed to create knowledge base:', error)
    alert(error.message || '创建知识库失败')
  } finally {
    creating.value = false
  }
}

const deleteKb = async (id: number) => {
  if (!confirm('确定要删除该知识库及其所有文档吗？')) return

  try {
    await knowledgeAPI.delete(id)
    if (selectedKbId.value === id) {
      selectedKbId.value = null
      documents.value = []
    }
    await loadKnowledgeBases()
  } catch (error: any) {
    console.error('Failed to delete knowledge base:', error)
    alert(error.message || '删除知识库失败')
  }
}

const startEditKb = (kb: KnowledgeBase) => {
  editingKbId.value = kb.id
  editingName.value = kb.name
}

const saveKbName = async (kbId: number) => {
  if (!editingName.value.trim()) {
    cancelKbEdit()
    return
  }

  try {
    await knowledgeAPI.update(kbId, { name: editingName.value.trim() })
    await loadKnowledgeBases()
  } catch (error: any) {
    console.error('Failed to rename knowledge base:', error)
    alert(error.message || '重命名失败')
  } finally {
    cancelKbEdit()
  }
}

const cancelKbEdit = () => {
  editingKbId.value = undefined
  editingName.value = ''
}

const triggerUpload = () => {
  fileInputRef.value?.click()
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files ? Array.from(target.files) : []
  if (files.length > 0) {
    uploadFiles(files)
  }
  target.value = ''
}

const handleDrop = (event: DragEvent) => {
  event.preventDefault()
  isDragover.value = false

  const files = event.dataTransfer?.files
  if (files) {
    uploadFiles(Array.from(files))
  }
}

const uploadFiles = async (files: File[]) => {
  if (!selectedKbId.value) return

  for (const file of files) {
    try {
      await uploadAPI.upload(selectedKbId.value, file, (progress) => {
        uploadProgress.value = progress
      })
      await loadDocuments()
    } catch (error: any) {
      console.error('Failed to upload file:', error)
      alert(`上传文件 ${file.name} 失败: ${error.message}`)
    }
  }
  uploadProgress.value = null
}

const deleteDoc = async (id: number) => {
  if (!confirm('确定要删除该文档吗？')) return

  try {
    await uploadAPI.deleteDocument(id)
    await loadDocuments()
  } catch (error: any) {
    console.error('Failed to delete document:', error)
    alert(error.message || '删除文档失败')
  }
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

onMounted(() => {
  loadKnowledgeBases()
})
</script>

<style scoped>
.knowledge-layout {
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
.kb-main-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

/* 顶部导航 */
.kb-header {
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

.kb-header .btn svg {
  width: 16px;
  height: 16px;
  fill: currentColor;
}

/* 内容区域 */
.kb-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* 侧边栏 */
.kb-sidebar {
  width: 280px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
}

.sidebar-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
}

.count {
  background: var(--bg-hover);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
}

.kb-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 var(--space-2);
}

.kb-item {
  display: flex;
  align-items: center;
  padding: var(--space-3);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--duration-fast);
}

.kb-item:hover {
  background: var(--bg-hover);
}

.kb-item.active {
  background: var(--color-primary-light);
}

.kb-info {
  flex: 1;
  min-width: 0;
}

.kb-name {
  display: block;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.kb-desc {
  display: block;
  font-size: var(--text-xs);
  color: var(--text-muted);
  margin-top: var(--space-1);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.kb-actions {
  display: flex;
  gap: var(--space-1);
  opacity: 0;
  transition: opacity var(--duration-fast);
}

.kb-item:hover .kb-actions {
  opacity: 1;
}

.delete-btn:hover {
  color: var(--color-danger);
}

.empty-list {
  text-align: center;
  padding: var(--space-8);
  color: var(--text-muted);
  font-size: var(--text-sm);
}

/* 主内容区 */
.kb-main {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-6);
}

.empty-main {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-muted);
}

.empty-main svg {
  width: 48px;
  height: 48px;
  fill: currentColor;
  opacity: 0.5;
  margin-bottom: var(--space-3);
}

.empty-main p {
  font-size: var(--text-sm);
}

.kb-detail {
  max-width: 800px;
}

.detail-header {
  margin-bottom: var(--space-6);
}

.detail-title {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-1);
}

.detail-desc {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0;
}

/* 上传区域 */
.upload-area {
  margin-bottom: var(--space-6);
}

.upload-zone {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-8);
  border: 2px dashed var(--border-default);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--duration-fast);
}

.upload-zone:hover,
.upload-zone.dragover {
  border-color: var(--color-primary);
  background: var(--color-primary-light);
}

.upload-zone svg {
  width: 40px;
  height: 40px;
  fill: var(--text-muted);
  margin-bottom: var(--space-3);
}

.upload-zone p {
  font-size: var(--text-sm);
  color: var(--text-primary);
  margin: 0;
}

.upload-zone span {
  font-size: var(--text-xs);
  color: var(--text-muted);
  margin-top: var(--space-1);
}

.upload-progress {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-top: var(--space-3);
}

.progress-bar {
  flex: 1;
  height: 4px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--color-primary);
  transition: width var(--duration-fast);
}

.upload-progress span {
  font-size: var(--text-xs);
  color: var(--text-muted);
}

/* 文档列表 */
.docs-section {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-3);
}

.section-header h3 {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-primary);
  margin: 0;
}

.doc-count {
  font-size: var(--text-xs);
  color: var(--text-muted);
}

.empty-docs {
  text-align: center;
  padding: var(--space-8);
}

.empty-docs p {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0;
}

.empty-docs span {
  font-size: var(--text-xs);
  color: var(--text-muted);
}

.doc-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.doc-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
}

.doc-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary-light);
  border-radius: var(--radius-md);
}

.doc-icon svg {
  width: 16px;
  height: 16px;
  fill: var(--color-primary);
}

.doc-info {
  flex: 1;
  min-width: 0;
}

.doc-name {
  display: block;
  font-size: var(--text-sm);
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.doc-meta {
  font-size: var(--text-xs);
  color: var(--text-muted);
}

.doc-item .delete-btn {
  opacity: 0;
  transition: opacity var(--duration-fast);
}

.doc-item:hover .delete-btn {
  opacity: 1;
}

.loading-state {
  display: flex;
  justify-content: center;
  padding: var(--space-8);
}

/* 响应式 */
@media (max-width: 768px) {
  .kb-header {
    padding: 0 var(--space-4);
  }

  .kb-content {
    flex-direction: column;
  }

  .kb-sidebar {
    width: 100%;
    max-height: 200px;
    border-right: none;
    border-bottom: 1px solid var(--border-subtle);
  }

  .kb-main {
    padding: var(--space-4);
  }
}
</style>
