import { ref, computed } from 'vue'
import { chatAPI } from '../api/client'

export type SessionType = 'rag' | 'agentic' | 'multi_agent'

export interface ChatSession {
  id: number
  title: string
  session_type: string
  created_at: string
}

// 全局会话状态
const sessionsMap = ref<Record<SessionType, ChatSession[]>>({
  rag: [],
  agentic: [],
  multi_agent: []
})
const loadingMap = ref<Record<SessionType, boolean>>({
  rag: false,
  agentic: false,
  multi_agent: false
})

export function useSession(sessionType: SessionType) {
  const sessions = computed(() => sessionsMap.value[sessionType])
  const loading = computed(() => loadingMap.value[sessionType])

  // 加载会话列表
  const loadSessions = async () => {
    loadingMap.value[sessionType] = true
    try {
      const result = await chatAPI.getSessions(sessionType)
      sessionsMap.value[sessionType] = result.sessions || result || []
    } catch (error) {
      console.error('Failed to load sessions:', error)
    } finally {
      loadingMap.value[sessionType] = false
    }
  }

  // 删除会话
  const deleteSession = async (sessionId: number) => {
    if (!confirm('确定要删除该对话吗？')) return false

    try {
      await chatAPI.deleteSession(sessionId)
      sessionsMap.value[sessionType] = sessionsMap.value[sessionType].filter(s => s.id !== sessionId)
      return true
    } catch (error) {
      console.error('Failed to delete session:', error)
      return false
    }
  }

  // 重命名会话
  const renameSession = async (sessionId: number, title: string) => {
    try {
      await chatAPI.renameSession(sessionId, title)
      const index = sessionsMap.value[sessionType].findIndex(s => s.id === sessionId)
      if (index !== -1) {
        sessionsMap.value[sessionType][index].title = title
      }
      return true
    } catch (error) {
      console.error('Failed to rename session:', error)
      return false
    }
  }

  // 添加新会话到列表开头
  const addSession = (session: ChatSession) => {
    sessionsMap.value[sessionType] = [session, ...sessionsMap.value[sessionType]]
  }

  // 更新会话标题
  const updateSessionTitle = (sessionId: number, title: string) => {
    const index = sessionsMap.value[sessionType].findIndex(s => s.id === sessionId)
    if (index !== -1) {
      sessionsMap.value[sessionType][index].title = title
    }
  }

  return {
    sessions,
    loading,
    loadSessions,
    deleteSession,
    renameSession,
    addSession,
    updateSessionTitle
  }
}
