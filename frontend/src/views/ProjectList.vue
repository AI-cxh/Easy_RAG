<template>
  <div class="project-layout">
    <AppNavRail />

    <div class="main-wrapper">
      <header class="page-header">
        <div>
          <h1 class="page-title">项目工作区</h1>
          <p class="page-desc">选择当前项目后，知识库和会话都会自动按项目隔离。</p>
        </div>
        <div class="header-actions">
          <button class="btn btn-secondary" :disabled="!currentProject" @click="startRenameProject">重命名项目</button>
          <button class="btn btn-danger" :disabled="!currentProject" @click="handleDeleteProject">删除项目</button>
          <button class="btn btn-primary" @click="showCreate = true">新建项目</button>
        </div>
      </header>

      <div class="content-grid">
        <div class="project-grid">
          <div
            v-for="project in projects"
            :key="project.id"
            class="project-card"
            :class="{ active: currentProjectId === project.id }"
            @click="handleSelectProject(project.id)"
          >
            <div class="project-head">
              <h3>{{ project.name }}</h3>
              <span class="project-role">{{ project.role || 'member' }}</span>
            </div>
            <p class="project-desc-card">{{ project.description || '暂无描述' }}</p>
            <div class="project-meta">
              <span>{{ currentProjectId === project.id ? '当前项目' : '点击切换' }}</span>
            </div>
          </div>
        </div>

        <aside class="memory-panel">
          <div class="memory-panel-header">
            <div>
              <h2 class="memory-title">项目记忆</h2>
              <p class="memory-desc">
                {{ currentProject ? `当前项目：${currentProject.name}` : '请先选择项目' }}
              </p>
            </div>
            <button class="btn btn-secondary" :disabled="!currentProject" @click="startCreateMemory">
              新增记忆
            </button>
          </div>

          <div v-if="!currentProject" class="memory-empty">
            选择一个项目后，可以为它维护长期背景、输出偏好和执行规则。
          </div>

          <div v-else class="memory-list">
            <div v-if="memoryLoading" class="memory-empty">加载中...</div>
            <div v-else-if="projectMemories.length === 0" class="memory-empty">
              还没有项目记忆。建议先添加 2-3 条固定规则。
            </div>
            <div v-else class="memory-items">
              <article v-for="memory in projectMemories" :key="memory.id" class="memory-card">
                <div class="memory-card-head">
                  <div class="memory-tags">
                    <span class="memory-type">{{ memoryTypeLabel(memory.memory_type) }}</span>
                    <span v-if="!memory.enabled" class="memory-disabled">停用</span>
                    <span v-if="memory.pinned" class="memory-pinned">置顶</span>
                  </div>
                  <div class="memory-actions">
                    <button
                      class="toggle-switch"
                      :class="{ active: memory.enabled }"
                      :title="memory.enabled ? '点击停用' : '点击启用'"
                      @click="handleToggleMemory(memory)"
                    >
                      <span class="toggle-slider"></span>
                    </button>
                    <button class="btn-icon btn-icon-sm" title="编辑" @click="startEditMemory(memory)">
                      <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
                      </svg>
                    </button>
                    <button class="btn-icon btn-icon-sm delete-btn" title="删除" @click="handleDeleteMemory(memory.id)">
                      <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                      </svg>
                    </button>
                  </div>
                </div>
                <p class="memory-content">{{ memory.content }}</p>
              </article>
            </div>
          </div>
        </aside>
      </div>

      <Teleport to="body">
        <div v-if="showCreate" class="dialog-overlay" @click.self="showCreate = false">
          <div class="dialog">
            <div class="dialog-header">
              <h3 class="dialog-title">新建项目</h3>
              <button class="dialog-close" @click="showCreate = false">&times;</button>
            </div>
            <div class="dialog-body">
              <div class="form-group">
                <label class="form-label">项目名称</label>
                <input v-model="form.name" class="input" type="text" placeholder="输入项目名称" />
              </div>
              <div class="form-group">
                <label class="form-label">项目描述</label>
                <textarea v-model="form.description" class="input textarea" rows="3" placeholder="输入项目描述" />
              </div>
            </div>
            <div class="dialog-footer">
              <button class="btn btn-secondary" @click="showCreate = false">取消</button>
              <button class="btn btn-primary" :disabled="creating" @click="handleCreate">
                {{ creating ? '创建中...' : '创建项目' }}
              </button>
            </div>
          </div>
        </div>
      </Teleport>

      <Teleport to="body">
        <div v-if="showMemoryDialog" class="dialog-overlay" @click.self="closeMemoryDialog">
          <div class="dialog">
            <div class="dialog-header">
              <h3 class="dialog-title">{{ editingMemoryId ? '编辑项目记忆' : '新增项目记忆' }}</h3>
              <button class="dialog-close" @click="closeMemoryDialog">&times;</button>
            </div>
            <div class="dialog-body">
              <div class="form-group">
                <label class="form-label">类型</label>
                <select v-model="memoryForm.memory_type" class="input">
                  <option value="context">背景信息</option>
                  <option value="preference">输出偏好</option>
                  <option value="instruction">执行规则</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">内容</label>
                <textarea
                  v-model="memoryForm.content"
                  class="input textarea"
                  rows="4"
                  placeholder="例如：默认用中文回答，结论先行。"
                />
              </div>
              <label class="checkbox-row">
                <input v-model="memoryForm.enabled" type="checkbox" />
                <span>启用记忆</span>
              </label>
              <label class="checkbox-row">
                <input v-model="memoryForm.pinned" type="checkbox" />
                <span>置顶记忆</span>
              </label>
            </div>
            <div class="dialog-footer">
              <button class="btn btn-secondary" @click="closeMemoryDialog">取消</button>
              <button class="btn btn-primary" :disabled="memorySaving" @click="submitMemory">
                {{ memorySaving ? '保存中...' : '保存' }}
              </button>
            </div>
          </div>
        </div>
      </Teleport>

      <Teleport to="body">
        <div v-if="showRename" class="dialog-overlay" @click.self="showRename = false">
          <div class="dialog">
            <div class="dialog-header">
              <h3 class="dialog-title">重命名项目</h3>
              <button class="dialog-close" @click="showRename = false">&times;</button>
            </div>
            <div class="dialog-body">
              <div class="form-group">
                <label class="form-label">项目名称</label>
                <input v-model="renameForm.name" class="input" type="text" placeholder="输入项目名称" />
              </div>
              <div class="form-group">
                <label class="form-label">项目描述</label>
                <textarea v-model="renameForm.description" class="input textarea" rows="3" placeholder="输入项目描述" />
              </div>
            </div>
            <div class="dialog-footer">
              <button class="btn btn-secondary" @click="showRename = false">取消</button>
              <button class="btn btn-primary" :disabled="renaming" @click="submitRenameProject">
                {{ renaming ? '保存中...' : '保存' }}
              </button>
            </div>
          </div>
        </div>
      </Teleport>

      <Teleport to="body">
        <div v-if="showDeleteConfirm" class="dialog-overlay" @click.self="showDeleteConfirm = false">
          <div class="dialog dialog-danger">
            <div class="dialog-header">
              <h3 class="dialog-title">确认删除项目</h3>
              <button class="dialog-close" @click="showDeleteConfirm = false">&times;</button>
            </div>
            <div class="dialog-body">
              <div class="confirm-content">
                <div class="confirm-icon">
                  <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
                  </svg>
                </div>
                <div class="confirm-text">
                  <p class="confirm-main">确定要删除项目「<strong>{{ currentProject?.name }}</strong>」吗？</p>
                  <p class="confirm-hint">此操作将同时删除该项目下的所有知识库、文档和会话记录，且无法恢复。</p>
                </div>
              </div>
            </div>
            <div class="dialog-footer">
              <button class="btn btn-secondary" @click="showDeleteConfirm = false">取消</button>
              <button class="btn btn-danger" :disabled="deleting" @click="confirmDeleteProject">
                {{ deleting ? '删除中...' : '确认删除' }}
              </button>
            </div>
          </div>
        </div>
      </Teleport>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import AppNavRail from '../components/AppNavRail.vue'
import { useProject } from '../composables/useProject'
import { projectAPI, type ProjectMemory } from '../api/client'

const { projects, currentProjectId, currentProject, loadProjects, createProject, setCurrentProject, updateProject, deleteProject } = useProject()

const showCreate = ref(false)
const creating = ref(false)
const showRename = ref(false)
const renaming = ref(false)
const showDeleteConfirm = ref(false)
const deleting = ref(false)
const form = ref({
  name: '',
  description: ''
})
const renameForm = ref({
  name: '',
  description: ''
})
const projectMemories = ref<ProjectMemory[]>([])
const memoryLoading = ref(false)
const memorySaving = ref(false)
const showMemoryDialog = ref(false)
const editingMemoryId = ref<number | null>(null)
const memoryForm = ref({
  content: '',
  memory_type: 'context',
  enabled: true,
  pinned: false
})

const memoryTypeLabel = (type: string) => {
  if (type === 'instruction') return '执行规则'
  if (type === 'preference') return '输出偏好'
  return '背景信息'
}

const loadProjectMemories = async () => {
  if (!currentProjectId.value) {
    projectMemories.value = []
    return
  }

  memoryLoading.value = true
  try {
    projectMemories.value = await projectAPI.getMemories(currentProjectId.value)
  } catch (error) {
    alert(error instanceof Error ? error.message : '加载项目记忆失败')
  } finally {
    memoryLoading.value = false
  }
}

const resetMemoryForm = () => {
  editingMemoryId.value = null
  memoryForm.value = {
    content: '',
    memory_type: 'context',
    enabled: true,
    pinned: false
  }
}

const startCreateMemory = () => {
  resetMemoryForm()
  showMemoryDialog.value = true
}

const startEditMemory = (memory: ProjectMemory) => {
  editingMemoryId.value = memory.id
  memoryForm.value = {
    content: memory.content,
    memory_type: memory.memory_type,
    enabled: memory.enabled ?? true,
    pinned: memory.pinned
  }
  showMemoryDialog.value = true
}

const closeMemoryDialog = () => {
  showMemoryDialog.value = false
  resetMemoryForm()
}

const submitMemory = async () => {
  if (!currentProjectId.value) {
    alert('请先选择项目')
    return
  }
  if (!memoryForm.value.content.trim()) {
    alert('请输入记忆内容')
    return
  }

  memorySaving.value = true
  try {
    const payload = {
      content: memoryForm.value.content.trim(),
      memory_type: memoryForm.value.memory_type,
      enabled: memoryForm.value.enabled,
      pinned: memoryForm.value.pinned
    }

    if (editingMemoryId.value) {
      await projectAPI.updateMemory(currentProjectId.value, editingMemoryId.value, payload)
    } else {
      await projectAPI.createMemory(currentProjectId.value, payload)
    }
    await loadProjectMemories()
    closeMemoryDialog()
  } catch (error) {
    alert(error instanceof Error ? error.message : '保存项目记忆失败')
  } finally {
    memorySaving.value = false
  }
}

const handleToggleMemory = async (memory: ProjectMemory) => {
  if (!currentProjectId.value) return

  try {
    await projectAPI.updateMemory(currentProjectId.value, memory.id, {
      enabled: !memory.enabled
    })
    await loadProjectMemories()
  } catch (error) {
    alert(error instanceof Error ? error.message : '切换记忆状态失败')
  }
}

const handleDeleteMemory = async (memoryId: number) => {
  if (!currentProjectId.value) return
  if (!window.confirm('确定要删除这条项目记忆吗？')) return

  try {
    await projectAPI.deleteMemory(currentProjectId.value, memoryId)
    await loadProjectMemories()
  } catch (error) {
    alert(error instanceof Error ? error.message : '删除项目记忆失败')
  }
}

const handleSelectProject = (projectId: number) => {
  setCurrentProject(projectId)
}

const startRenameProject = () => {
  if (!currentProject.value) return
  renameForm.value = {
    name: currentProject.value.name,
    description: currentProject.value.description || ''
  }
  showRename.value = true
}

const submitRenameProject = async () => {
  if (!currentProject.value) return
  if (!renameForm.value.name.trim()) {
    alert('请输入项目名称')
    return
  }

  renaming.value = true
  try {
    await updateProject(currentProject.value.id, {
      name: renameForm.value.name.trim(),
      description: renameForm.value.description.trim() || undefined
    })
    showRename.value = false
  } catch (error) {
    alert(error instanceof Error ? error.message : '重命名项目失败')
  } finally {
    renaming.value = false
  }
}

const handleDeleteProject = () => {
  if (!currentProject.value) return
  showDeleteConfirm.value = true
}

const confirmDeleteProject = async () => {
  if (!currentProject.value) return

  deleting.value = true
  try {
    await deleteProject(currentProject.value.id)
    showDeleteConfirm.value = false
    await loadProjects()
  } catch (error) {
    alert(error instanceof Error ? error.message : '删除项目失败')
  } finally {
    deleting.value = false
  }
}

const handleCreate = async () => {
  if (!form.value.name.trim()) {
    alert('请输入项目名称')
    return
  }

  creating.value = true
  try {
    await createProject({
      name: form.value.name.trim(),
      description: form.value.description.trim() || undefined
    })
    form.value = { name: '', description: '' }
    showCreate.value = false
  } catch (error) {
    alert(error instanceof Error ? error.message : '创建项目失败')
  } finally {
    creating.value = false
  }
}

onMounted(() => {
  loadProjects()
})

watch(currentProjectId, () => {
  loadProjectMemories()
}, { immediate: true })
</script>

<style scoped>
.project-layout {
  display: flex;
  min-height: 100vh;
  background: var(--bg-primary);
}

.main-wrapper {
  flex: 1;
  padding: var(--space-6);
}

.content-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(320px, 420px);
  gap: var(--space-5);
  align-items: start;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.header-actions {
  display: flex;
  gap: var(--space-3);
  flex-wrap: wrap;
  justify-content: flex-end;
}

.page-title {
  margin: 0;
  font-size: var(--text-2xl);
}

.page-desc {
  margin: var(--space-2) 0 0;
  color: var(--text-secondary);
}

.project-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--space-4);
}

.project-card {
  padding: var(--space-5);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  background: var(--bg-elevated);
  cursor: pointer;
}

.project-card.active {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-md);
}

.project-head {
  display: flex;
  justify-content: space-between;
  gap: var(--space-3);
  align-items: center;
}

.project-head h3 {
  margin: 0;
}

.project-role {
  font-size: var(--text-xs);
  color: var(--color-primary);
  background: var(--color-primary-light);
  padding: 4px 8px;
  border-radius: var(--radius-full);
}

.project-desc-card {
  min-height: 44px;
  color: var(--text-secondary);
}

.project-meta {
  font-size: var(--text-sm);
  color: var(--text-muted);
}

.memory-panel {
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  padding: var(--space-5);
  position: sticky;
  top: var(--space-6);
}

.memory-panel-header {
  display: flex;
  justify-content: space-between;
  gap: var(--space-3);
  align-items: flex-start;
  margin-bottom: var(--space-4);
}

.memory-title {
  margin: 0;
  font-size: var(--text-xl);
}

.memory-desc {
  margin: var(--space-2) 0 0;
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.memory-empty {
  color: var(--text-muted);
  font-size: var(--text-sm);
  padding: var(--space-4);
  border: 1px dashed var(--border-default);
  border-radius: var(--radius-lg);
  background: var(--bg-secondary);
}

.memory-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.memory-items {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.memory-card {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  background: var(--bg-secondary);
}

.memory-card-head {
  display: flex;
  justify-content: space-between;
  gap: var(--space-3);
  align-items: flex-start;
  margin-bottom: var(--space-3);
}

.memory-tags {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.memory-type,
.memory-disabled,
.memory-pinned {
  font-size: var(--text-xs);
  padding: 4px 8px;
  border-radius: var(--radius-full);
}

.memory-type {
  color: var(--color-primary);
  background: var(--color-primary-light);
}

.memory-pinned {
  color: #8a5600;
  background: #fff4d6;
}

.memory-disabled {
  color: #7a2e2e;
  background: #fde8e8;
}

.memory-actions {
  display: flex;
  gap: var(--space-2);
  align-items: center;
}

.toggle-switch {
  position: relative;
  width: 36px;
  height: 20px;
  padding: 0;
  border: none;
  border-radius: 10px;
  background: var(--border-default);
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.toggle-switch:hover {
  background: var(--text-muted);
}

.toggle-switch.active {
  background: var(--color-primary);
}

.toggle-switch.active:hover {
  background: var(--color-primary);
  opacity: 0.9;
}

.toggle-slider {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  transition: transform 0.2s ease;
  pointer-events: none;
}

.toggle-switch.active .toggle-slider {
  transform: translateX(16px);
}

.memory-content {
  margin: 0;
  color: var(--text-primary);
  line-height: 1.6;
  white-space: pre-wrap;
}

.checkbox-row {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--text-primary);
}

@media (max-width: 960px) {
  .content-grid {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
  }

  .memory-panel {
    position: static;
  }
}

.confirm-content {
  display: flex;
  gap: var(--space-4);
  align-items: flex-start;
}

.confirm-icon {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  border-radius: var(--radius-full);
  background: #fef2f2;
  display: flex;
  align-items: center;
  justify-content: center;
}

.confirm-icon svg {
  width: 24px;
  height: 24px;
  fill: #dc2626;
}

.confirm-text {
  flex: 1;
}

.confirm-main {
  margin: 0 0 var(--space-2);
  font-size: var(--text-base);
  color: var(--text-primary);
}

.confirm-main strong {
  color: var(--color-primary);
}

.confirm-hint {
  margin: 0;
  font-size: var(--text-sm);
  color: var(--text-secondary);
  line-height: 1.5;
}

.dialog-danger .dialog-header {
  border-bottom-color: #fecaca;
}

.dialog-danger .dialog-title {
  color: #b91c1c;
}
</style>
