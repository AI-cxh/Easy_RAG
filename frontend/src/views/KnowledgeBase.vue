<template>
  <div class="knowledge-page">
    <div class="page-header">
      <h1>知识库管理</h1>
      <button class="btn btn-primary" @click="showCreateDialog = true">创建知识库</button>
    </div>

    <div class="content-grid" style="margin-top: 24px;">
      <div class="left-panel">
        <h2 style="margin-bottom: 16px;">知识库列表</h2>
        <div v-if="loading" class="loading">
          <span class="spinner"></span>
        </div>
        <div v-else class="kb-list">
          <div
            v-for="kb in knowledgeBases"
            :key="kb.id"
            :class="['kb-card', { 'selected': selectedKbId === kb.id }]"
            @click="selectKb(kb)"
          >
            <div class="kb-header">
              <h3>{{ kb.name }}</h3>
              <button class="btn btn-danger btn-sm" @click.stop="deleteKb(kb.id)">删除</button>
            </div>
            <p v-if="kb.description" class="kb-description">{{ kb.description }}</p>
            <div class="kb-footer">
              <span class="doc-count">{{ kb.documents.length }} 个文档</span>
            </div>
          </div>
          <div v-if="knowledgeBases.length === 0" class="empty-state">
            暂无知识库，点击"创建知识库"开始使用
          </div>
        </div>
      </div>

      <div class="right-panel">
        <div v-if="!selectedKbId" class="empty-panel">
          <svg class="empty-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 15v-6H9.5v-2h3V6h2v3h3v2h-3v6h-2z"/>
          </svg>
          <p>选择一个知识库查看详情</p>
        </div>
        <div v-else class="panel-content">
          <div class="panel-header">
            <h2>{{ selectedKb?.name }}</h2>
          </div>

          <div class="upload-section">
            <h3>上传文件</h3>
            <FileUpload
              :kb-id="selectedKbId"
              :disabled="false"
              ref="fileUploadRef"
              @upload="handleFileUpload"
            />
          </div>

          <div class="document-list-section">
            <div class="section-header">
              <h3>文档列表</h3>
              <button v-if="loadingDocs" class="btn btn-sm" :disabled="true">
                <span class="spinner"></span>
              </button>
              <button v-else class="btn btn-sm btn-secondary" @click="loadDocuments">
                刷新
              </button>
            </div>
            <div v-if="documents.length === 0" class="empty-docs">
              暂无文档，上传文件后自动处理
            </div>
            <div v-else class="doc-list">
              <div v-for="doc in documents" :key="doc.id" class="doc-item">
                <div class="doc-info">
                  <span class="doc-name">{{ doc.filename }}</span>
                  <span class="doc-meta">{{ formatFileSize(doc.file_size) }} · {{ doc.chunk_count }} 个分块</span>
                </div>
                <button class="btn btn-danger btn-sm" @click="deleteDoc(doc.id)">删除</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- 创建知识库对话框 -->
  <Teleport to="body">
    <div v-if="showCreateDialog" class="dialog-overlay" @click.self="showCreateDialog = false">
      <div class="dialog">
        <div class="dialog-header">
          <h3>创建知识库</h3>
          <button class="dialog-close" @click="showCreateDialog = false">&times;</button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label for="kbName">名称 <span class="required">*</span></label>
            <input
              id="kbName"
              v-model="newKbForm.name"
              type="text"
              placeholder="输入知识库名称"
            />
          </div>
          <div class="form-group">
            <label for="kbDesc">描述</label>
            <textarea
              id="kbDesc"
              v-model="newKbForm.description"
              placeholder="输入知识库描述（可选）"
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
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { knowledgeAPI, uploadAPI } from '../api/client'
import FileUpload from '../components/FileUpload.vue'

interface KnowledgeBase {
  id: number
  name: string
  description?: string
  documents: any[]
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
const fileUploadRef = ref()

const newKbForm = ref({
  name: '',
  description: ''
})

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
    // 自动选中新创建的知识库
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

const handleFileUpload = async (files: File[]) => {
  if (!selectedKbId.value) {
    alert('请先选择一个知识库')
    return
  }

  for (const file of files) {
    try {
      await uploadAPI.upload(selectedKbId.value, file, (progress) => {
        fileUploadRef.value?.updateProgress(progress)
      })
      await loadDocuments()
    } catch (error: any) {
      console.error('Failed to upload file:', error)
      alert(`上传文件 ${file.name} 失败: ${error.message}`)
    }
  }
  fileUploadRef.value?.resetProgress()
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
.knowledge-page {
  display: flex;
  flex-direction: column;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
}

.content-grid {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 20px;
}

.left-panel,
.right-panel {
  background-color: var(--card-bg);
  border-radius: 8px;
  padding: 20px;
  box-shadow: var(--shadow-sm);
  min-height: 500px;
}

.loading {
  display: flex;
  justify-content: center;
  padding: 40px;
}

.kb-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.kb-card {
  padding: 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.kb-card:hover {
  border-color: var(--primary-color);
  box-shadow: var(--shadow-sm);
}

.kb-card.selected {
  border-color: var(--primary-color);
  background-color: rgba(74, 144, 217, 0.05);
}

.kb-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.kb-header h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}

.kb-description {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.kb-footer {
  display: flex;
  justify-content: flex-end;
}

.doc-count {
  font-size: 12px;
  color: var(--text-secondary);
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

.empty-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-secondary);
}

.empty-icon {
  width: 64px;
  height: 64px;
  margin-bottom: 16px;
  opacity: 0.3;
}

.panel-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.panel-header h2 {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}

.upload-section h3,
.document-list-section h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.empty-docs {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-secondary);
  font-size: 14px;
}

.doc-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.doc-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
}

.doc-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.doc-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.doc-meta {
  font-size: 12px;
  color: var(--text-secondary);
}

.btn-sm {
  padding: 4px 12px;
  font-size: 12px;
}

/* 对话框样式 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog {
  background-color: var(--card-bg);
  border-radius: 8px;
  padding: 24px;
  min-width: 400px;
  max-width: 500px;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.dialog-header h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.dialog-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
}

.dialog-close:hover {
  color: var(--text-primary);
}

.dialog-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.required {
  color: var(--danger-color);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

@media (max-width: 768px) {
  .content-grid {
    grid-template-columns: 1fr;
  }

  .left-panel {
    min-height: auto;
  }
}
</style>
