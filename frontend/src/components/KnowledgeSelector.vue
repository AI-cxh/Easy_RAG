<template>
  <div class="knowledge-selector">
    <div class="selector-header">
      <h3>选择知识库</h3>
      <label class="toggle-switch">
        <input
          type="checkbox"
          :checked="useWebSearch"
          @change="toggleWebSearch"
        />
        <span>网络搜索</span>
      </label>
    </div>
    <div v-if="loading" class="loading">
      <span class="spinner"></span>
    </div>
    <div v-else class="knowledge-list">
      <label
        v-for="kb in knowledgeBases"
        :key="kb.id"
        class="knowledge-item"
      >
        <input
          type="checkbox"
          :value="kb.id"
          :checked="selectedKbIds.includes(kb.id)"
          @change="toggleKb(kb.id)"
        />
        <div class="kb-info">
          <span class="kb-name">{{ kb.name }}</span>
          <span v-if="kb.description" class="kb-description">{{ kb.description }}</span>
        </div>
      </label>
      <div v-if="knowledgeBases.length === 0" class="empty-state">
        暂无知识库，请先创建知识库
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { knowledgeAPI } from '../api/client'

interface KnowledgeBase {
  id: number
  name: string
  description?: string
}

interface Props {
  selectedKbIds: number[]
  useWebSearch: boolean
}

interface Emits {
  (event: 'update:selectedKbIds', value: number[]): void
  (event: 'update:useWebSearch', value: boolean): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const knowledgeBases = ref<KnowledgeBase[]>([])
const loading = ref(false)

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

const toggleKb = (kbId: number) => {
  if (props.selectedKbIds.includes(kbId)) {
    emit('update:selectedKbIds', props.selectedKbIds.filter(id => id !== kbId))
  } else {
    emit('update:selectedKbIds', [...props.selectedKbIds, kbId])
  }
}

const toggleWebSearch = (event: Event) => {
  emit('update:useWebSearch', (event.target as HTMLInputElement).checked)
}

onMounted(() => {
  loadKnowledgeBases()
})

defineExpose({
  loadKnowledgeBases
})
</script>

<style scoped>
.knowledge-selector {
  background-color: var(--card-bg);
  border-radius: 8px;
  padding: 16px;
  box-shadow: var(--shadow-sm);
}

.selector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.selector-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.toggle-switch {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  cursor: pointer;
  user-select: none;
}

.toggle-switch input {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.loading {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.knowledge-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 300px;
  overflow-y: auto;
}

.knowledge-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.knowledge-item:hover {
  border-color: var(--primary-color);
  background-color: rgba(74, 144, 217, 0.05);
}

.knowledge-item input[type="checkbox"] {
  flex-shrink: 0;
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.kb-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.kb-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.kb-description {
  font-size: 12px;
  color: var(--text-secondary);
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.empty-state {
  text-align: center;
  padding: 20px;
  color: var(--text-secondary);
  font-size: 14px;
}
</style>
