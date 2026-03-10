<template>
  <div class="file-upload">
    <div
      class="upload-zone"
      :class="{ 'dragover': isDragover, 'disabled': disabled }"
      @drop="handleDrop"
      @dragover.prevent="isDragover = true"
      @dragleave.prevent="isDragover = false"
      @click="triggerFileInput"
    >
      <input
        ref="fileInputRef"
        type="file"
        accept=".txt,.md,.pdf,.docx"
        multiple
        style="display: none"
        @change="handleFileSelect"
      />
      <div class="upload-content">
        <svg class="upload-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 16l-6-6h4V4h4v6h4l-6 6zm-2 4v-2h4v2H10z"/>
        </svg>
        <p class="upload-text">{{ disabled ? '知识库不存在' : '拖拽文件到这里或点击上传' }}</p>
        <p class="upload-hint">支持 .txt, .md, .pdf, .docx 格式</p>
      </div>
    </div>

    <div v-if="uploadProgress !== null" class="upload-progress">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
      </div>
      <span class="progress-text">上传中... {{ uploadProgress }}%</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Props {
  kbId?: number | null
  disabled?: boolean
}

interface Emits {
  (event: 'upload', files: File[]): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const fileInputRef = ref<HTMLInputElement>()
const isDragover = ref(false)
const uploadProgress = ref<number | null>(null)

const triggerFileInput = () => {
  if (!props.disabled && fileInputRef.value) {
    fileInputRef.value.click()
  }
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files ? Array.from(target.files) : []
  if (files.length > 0) {
    emit('upload', files)
  }
  // Reset input to allow selecting the same file again
  target.value = ''
}

const handleDrop = (event: DragEvent) => {
  event.preventDefault()
  isDragover.value = false

  if (props.disabled) return

  const files = event.dataTransfer?.files
  if (files) {
    emit('upload', Array.from(files))
  }
}

const updateProgress = (progress: number) => {
  uploadProgress.value = progress
}

const resetProgress = () => {
  uploadProgress.value = null
}

defineExpose({
  updateProgress,
  resetProgress
})
</script>

<style scoped>
.file-upload {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.upload-zone {
  border: 2px dashed var(--border-color);
  border-radius: 8px;
  padding: 32px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background-color: var(--card-bg);
}

.upload-zone:not(.disabled):hover {
  border-color: var(--primary-color);
  background-color: rgba(74, 144, 217, 0.05);
}

.upload-zone.dragover {
  border-color: var(--primary-color);
  background-color: rgba(74, 144, 217, 0.1);
  transform: scale(1.02);
}

.upload-zone.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.upload-icon {
  width: 48px;
  height: 48px;
  fill: var(--text-secondary);
  transition: fill 0.2s;
}

.upload-zone:not(.disabled):hover .upload-icon {
  fill: var(--primary-color);
}

.upload-text {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-primary);
}

.upload-hint {
  font-size: 13px;
  color: var(--text-secondary);
}

.upload-progress {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.progress-bar {
  height: 8px;
  background-color: var(--bg-color);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: var(--primary-color);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 13px;
  color: var(--text-secondary);
  text-align: center;
}
</style>
