<template>
  <div class="file-uploader">
    <!-- 隐藏的文件输入 -->
    <input
      ref="fileInput"
      type="file"
      multiple
      accept=".txt,.md,.pdf,.docx"
      class="hidden-input"
      @change="handleFileSelect"
    />

    <!-- 上传按钮 -->
    <button
      class="upload-btn"
      :disabled="uploading"
      @click="triggerUpload"
      title="上传文件"
    >
      <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM14 13v4h-4v-4H7l5-5 5 5h-3z"/>
      </svg>
    </button>

    <!-- 已上传文件列表 -->
    <div v-if="uploadedFiles.length > 0" class="file-list">
      <div
        v-for="file in uploadedFiles"
        :key="file.id"
        class="file-tag"
      >
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" class="file-icon">
          <path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>
        </svg>
        <span class="file-name">{{ file.filename }}</span>
        <button
          class="remove-btn"
          @click="removeFile(file.id)"
          title="移除文件"
        >
          <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- 上传进度 -->
    <Transition name="progress">
      <div v-if="uploading" class="progress-container">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: `${progress}%` }"></div>
        </div>
        <span class="progress-text">{{ progress }}%</span>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { chatAPI } from '../api/client'

interface UploadedFile {
  id: number
  filename: string
  file_size: number
  chunk_count: number
}

const props = defineProps<{
  sessionId?: number
}>()

const emit = defineEmits<{
  (e: 'uploaded', data: { sessionId: number; kbId: number; files: UploadedFile[] }): void
  (e: 'error', message: string): void
}>()

// 状态
const fileInput = ref<HTMLInputElement>()
const uploading = ref(false)
const progress = ref(0)
const uploadedFiles = ref<UploadedFile[]>([])
const currentKbId = ref<number>()
const currentSessionId = ref<number>()

// 触发文件选择
const triggerUpload = () => {
  fileInput.value?.click()
}

// 处理文件选择
const handleFileSelect = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (!files || files.length === 0) return

  await uploadFiles(Array.from(files))

  // 清空 input 以便重复选择同一文件
  target.value = ''
}

// 上传文件
const uploadFiles = async (files: File[]) => {
  if (files.length === 0) return

  uploading.value = true
  progress.value = 0

  try {
    const response = await chatAPI.uploadFiles(files, props.sessionId || currentSessionId.value, (p) => {
      progress.value = p
    })

    const { session_id, kb_id, documents } = response

    currentKbId.value = kb_id
    currentSessionId.value = session_id

    // 添加到已上传文件列表
    uploadedFiles.value.push(...documents)

    // 触发上传成功事件
    emit('uploaded', {
      sessionId: session_id,
      kbId: kb_id,
      files: documents
    })
  } catch (error) {
    const message = error instanceof Error ? error.message : '上传文件失败'
    emit('error', message)
  } finally {
    uploading.value = false
    progress.value = 0
  }
}

// 从列表移除文件
const removeFile = (fileId: number) => {
  uploadedFiles.value = uploadedFiles.value.filter(f => f.id !== fileId)
}

// 获取当前知识库ID
const getKbId = () => currentKbId.value

// 获取当前会话ID
const getSessionId = () => currentSessionId.value

// 清空状态
const clearFiles = () => {
  uploadedFiles.value = []
  currentKbId.value = undefined
  currentSessionId.value = undefined
  progress.value = 0
}

// 暴露方法给父组件
defineExpose({
  getKbId,
  getSessionId,
  clearFiles,
  uploadedFiles
})
</script>

<style scoped>
.file-uploader {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.hidden-input {
  display: none;
}

.upload-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--duration-fast);
}

.upload-btn:hover:not(:disabled) {
  background: var(--bg-hover);
  border-color: var(--border-strong);
  color: var(--text-primary);
}

.upload-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.upload-btn svg {
  width: 18px;
  height: 18px;
  fill: currentColor;
}

.file-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.file-tag {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-1) var(--space-3);
  background: var(--bg-tertiary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  color: var(--text-secondary);
  max-width: 200px;
  animation: fadeIn var(--duration-fast) var(--ease-out);
}

.file-icon {
  width: 14px;
  height: 14px;
  fill: var(--color-primary);
  flex-shrink: 0;
}

.file-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.remove-btn {
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  cursor: pointer;
  transition: all var(--duration-fast);
  flex-shrink: 0;
  margin-left: var(--space-1);
}

.remove-btn:hover {
  background: var(--color-danger-light);
  color: var(--color-danger);
}

.remove-btn svg {
  width: 12px;
  height: 12px;
  fill: currentColor;
}

.progress-container {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  background: var(--bg-tertiary);
  border-radius: var(--radius-lg);
  min-width: 120px;
}

.progress-bar {
  flex: 1;
  height: 4px;
  background: var(--bg-primary);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--gradient-accent);
  border-radius: var(--radius-full);
  transition: width var(--duration-fast) var(--ease-out);
}

.progress-text {
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
  min-width: 32px;
  text-align: right;
}

/* 动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.progress-enter-active,
.progress-leave-active {
  transition: all var(--duration-normal) var(--ease-out);
}

.progress-enter-from,
.progress-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

/* 移动端适配 */
@media (max-width: 768px) {
  .file-tag {
    max-width: 150px;
  }
}
</style>
