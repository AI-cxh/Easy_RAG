<template>
  <div class="composer-bar">
    <!-- 选项按钮 -->
    <div class="options-bar">
      <button
        :class="['option-btn', { 'active': useWebSearch }]"
        @click="$emit('toggleWebSearch')"
      >
        <svg class="option-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
        </svg>
        <span>网络搜索</span>
      </button>

      <div class="dropdown-wrapper" ref="dropdownRef">
        <button
          :class="['option-btn', { 'active': selectedKbIds.length > 0, 'open': showDropdown }]"
          @click="toggleDropdown"
        >
          <svg class="option-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-1 9H9V9h10v2zm-4 4H9v-2h6v2zm4-8H9V5h10v2z"/>
          </svg>
          <span>知识库{{ selectedKbIds.length > 0 ? ` (${selectedKbIds.length})` : '' }}</span>
          <svg class="dropdown-arrow" :class="{ 'open': showDropdown }" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M7 10l5 5 5-5z"/>
          </svg>
        </button>

        <!-- 知识库下拉列表 -->
        <div v-if="showDropdown" class="dropdown-menu">
          <div v-if="loadingKbs" class="dropdown-loading">
            <span class="spinner spinner-sm"></span>
          </div>
          <div v-else-if="knowledgeBases.length === 0" class="dropdown-empty">
            暂无知识库
          </div>
          <label v-else v-for="kb in knowledgeBases" :key="kb.id" class="dropdown-item">
            <input
              type="checkbox"
              :value="kb.id"
              :checked="selectedKbIds.includes(kb.id)"
              @change="$emit('toggleKb', kb.id)"
            />
            <span>{{ kb.name }}</span>
          </label>
        </div>
      </div>
    </div>

    <!-- 输入框 -->
    <div class="input-wrapper">
      <textarea
        v-model="inputText"
        placeholder="输入你的消息... (Shift+Enter 换行, Enter 发送)"
        class="message-input"
        rows="1"
        :disabled="disabled"
        @keydown="handleKeydown"
        ref="textareaRef"
        @input="autoResize"
      />
      <button
        class="btn btn-primary send-btn"
        :disabled="!inputText.trim() || disabled"
        @click="send"
      >
        <svg v-if="!disabled" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
        </svg>
        <span v-else class="spinner"></span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

interface KnowledgeBase {
  id: number
  name: string
}

interface Props {
  useWebSearch: boolean
  selectedKbIds: number[]
  knowledgeBases: KnowledgeBase[]
  loadingKbs: boolean
  disabled: boolean
}

defineProps<Props>()

const emit = defineEmits<{
  (e: 'send', message: string): void
  (e: 'toggleWebSearch'): void
  (e: 'toggleKb', id: number): void
}>()

const inputText = ref('')
const textareaRef = ref<HTMLTextAreaElement>()
const showDropdown = ref(false)
const dropdownRef = ref()

const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value
}

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    send()
  }
}

const autoResize = () => {
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto'
    textareaRef.value.style.height = Math.min(textareaRef.value.scrollHeight, 200) + 'px'
  }
}

const send = () => {
  if (inputText.value.trim()) {
    emit('send', inputText.value.trim())
    inputText.value = ''
    if (textareaRef.value) {
      textareaRef.value.style.height = 'auto'
    }
  }
}

// 点击外部关闭下拉框
const handleClickOutside = (event: MouseEvent) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    showDropdown.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.composer-bar {
  background-color: var(--bg-card);
  border-top: 1px solid var(--border-base);
  padding: var(--spacing-lg) var(--spacing-2xl);
}

.options-bar {
  display: flex;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
  align-items: center;
}

.option-btn {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-lg);
  border: 1px solid var(--border-base);
  border-radius: var(--radius-full);
  background-color: transparent;
  font-size: var(--font-size-base);
  cursor: pointer;
  transition: all var(--transition-normal);
  color: var(--text-secondary);
}

.option-btn:hover {
  background-color: var(--bg-base);
  border-color: var(--color-primary);
}

.option-btn.active {
  background-color: var(--color-primary-light);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.option-icon {
  width: 18px;
  height: 18px;
  fill: currentColor;
}

.dropdown-wrapper {
  position: relative;
}

.dropdown-arrow {
  width: 16px;
  height: 16px;
  transition: transform var(--transition-normal);
}

.dropdown-arrow.open {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  min-width: 200px;
  background-color: var(--bg-card);
  border: 1px solid var(--border-base);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  z-index: var(--z-dropdown);
  max-height: 300px;
  overflow-y: auto;
  padding: var(--spacing-sm);
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background-color var(--transition-normal);
}

.dropdown-item:hover {
  background-color: var(--bg-base);
}

.dropdown-item input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.dropdown-loading,
.dropdown-empty {
  padding: var(--spacing-lg);
  text-align: center;
  color: var(--text-secondary);
  font-size: var(--font-size-base);
}

.input-wrapper {
  display: flex;
  gap: var(--spacing-md);
  align-items: flex-end;
}

.message-input {
  flex: 1;
  resize: none;
  min-height: 48px;
  max-height: 200px;
  padding: 14px var(--spacing-lg);
  border: 1px solid var(--border-base);
  border-radius: var(--radius-xl);
  font-family: inherit;
  font-size: 15px;
  line-height: var(--line-height-normal);
  transition: all var(--transition-normal);
  background-color: var(--bg-base);
  color: var(--text-primary);
}

.message-input:focus {
  outline: none;
  border-color: var(--color-primary);
  background-color: var(--bg-card);
  box-shadow: 0 0 0 3px var(--color-primary-light);
}

.message-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.message-input::placeholder {
  color: var(--text-secondary);
}

.send-btn {
  width: 48px;
  height: 48px;
  padding: 0;
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  justify-content: center;
}

.send-btn svg {
  width: 20px;
  height: 20px;
  fill: white;
}

@media (max-width: 768px) {
  .composer-bar {
    padding: var(--spacing-md) var(--spacing-lg);
  }

  .options-bar {
    flex-wrap: wrap;
  }

  .option-btn {
    min-height: 44px;
  }
}
</style>
