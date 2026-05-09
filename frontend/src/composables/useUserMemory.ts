import { ref } from 'vue'
import { userMemoryAPI, type UserMemory } from '../api/client'

export function useUserMemory() {
  const showUserMemoryDrawer = ref(false)
  const loadingUserMemories = ref(false)
  const deletingUserMemoryId = ref('')
  const userMemoryError = ref('')
  const userMemories = ref<UserMemory[]>([])

  const loadUserMemories = async () => {
    loadingUserMemories.value = true
    userMemoryError.value = ''
    try {
      userMemories.value = await userMemoryAPI.getList()
    } catch (error) {
      console.error('Failed to load user memories:', error)
      userMemoryError.value = error instanceof Error ? error.message : '获取长期记忆失败'
      userMemories.value = []
    } finally {
      loadingUserMemories.value = false
    }
  }

  const openUserMemoryDrawer = async () => {
    showUserMemoryDrawer.value = true
    await loadUserMemories()
  }

  const deleteUserMemory = async (memoryId: string) => {
    if (!memoryId || deletingUserMemoryId.value) return
    deletingUserMemoryId.value = memoryId
    userMemoryError.value = ''
    try {
      await userMemoryAPI.delete(memoryId)
      userMemories.value = userMemories.value.filter(memory => memory.id !== memoryId)
    } catch (error) {
      console.error('Failed to delete user memory:', error)
      userMemoryError.value = error instanceof Error ? error.message : '删除长期记忆失败'
    } finally {
      deletingUserMemoryId.value = ''
    }
  }

  const closeUserMemoryDrawer = () => {
    showUserMemoryDrawer.value = false
  }

  return {
    showUserMemoryDrawer,
    loadingUserMemories,
    deletingUserMemoryId,
    userMemoryError,
    userMemories,
    loadUserMemories,
    openUserMemoryDrawer,
    deleteUserMemory,
    closeUserMemoryDrawer
  }
}
