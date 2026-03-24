const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

// 知识库API
export const knowledgeAPI = {
  // 获取所有知识库
  getAll: async () => {
    const response = await fetch(`${API_BASE_URL}/knowledge`)
    if (!response.ok) {
      const error = await response.text()
      throw new Error(error || '请求失败')
    }
    return response.json()
  },

  // 创建知识库
  create: async (data: {
    name: string
    description?: string
    chunk_size?: number
    chunk_overlap?: number
  }) => {
    const response = await fetch(`${API_BASE_URL}/knowledge`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })
    if (!response.ok) {
      const error = await response.text()
      throw new Error(error || '创建知识库失败')
    }
    return response.json()
  },

  // 获取知识库详情
  get: async (id: number) => {
    const response = await fetch(`${API_BASE_URL}/knowledge/${id}`)
    if (!response.ok) {
      const error = await response.text()
      throw new Error(error || '请求失败')
    }
    return response.json()
  },

  // 删除知识库
  delete: async (id: number) => {
    const response = await fetch(`${API_BASE_URL}/knowledge/${id}`, {
      method: 'DELETE'
    })
    if (!response.ok) {
      const error = await response.text()
      throw new Error(error || '请求失败')
    }
    return response.json()
  },

  // 获取知识库文档列表
  getDocuments: async (id: number) => {
    const response = await fetch(`${API_BASE_URL}/knowledge/${id}/documents`)
    if (!response.ok) {
      const error = await response.text()
      throw new Error(error || '请求失败')
    }
    return response.json()
  },

  // 重命名知识库
  update: async (id: number, data: {
    name: string
    description?: string
    chunk_size?: number
    chunk_overlap?: number
  }) => {
    const response = await fetch(`${API_BASE_URL}/knowledge/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })
    if (!response.ok) {
      const error = await response.text()
      throw new Error(error || '请求失败')
    }
    return response.json()
  }
}

// 文件上传API
export const uploadAPI = {
  // 上传文件
  upload: async (kbId: number, file: File, onProgress?: (progress: number) => void) => {
    const formData = new FormData()
    formData.append('file', file)

    // 使用 XMLHttpRequest 来支持上传进度
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest()
      xhr.open('POST', `${API_BASE_URL}/upload/${kbId}`)

      xhr.upload.onprogress = (event) => {
        if (onProgress && event.lengthComputable) {
          const progress = Math.round((event.loaded / event.total) * 100)
          onProgress(progress)
        }
      }

      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve(xhr.response ? JSON.parse(xhr.response) : {})
        } else {
          // 尝试解析错误响应
          let errorMsg = '上传文件失败'
          try {
            const errorResponse = xhr.response ? JSON.parse(xhr.response) : null
            if (errorResponse?.detail) {
              errorMsg = errorResponse.detail
            } else if (xhr.statusText) {
              errorMsg = xhr.statusText
            }
          } catch {
            if (xhr.statusText) {
              errorMsg = xhr.statusText
            }
          }
          reject(new Error(errorMsg))
        }
      }

      xhr.onerror = () => {
        reject(new Error('上传文件失败'))
      }

      xhr.send(formData)
    })
  },

  // 删除文档
  deleteDocument: async (docId: number) => {
    const response = await fetch(`${API_BASE_URL}/upload/documents/${docId}`, {
      method: 'DELETE'
    })
    if (!response.ok) {
      const error = await response.text()
      throw new Error(error || '请求失败')
    }
    return response.json()
  }
}

// 聊天API - 流式响应
export interface StreamMessage {
  type: 'chunk' | 'end' | 'error'
  content?: string
  session_id?: number
  sources?: string[]
  search_results?: Array<{ title: string; url: string; snippet?: string }>
  message?: string
}

export const chatAPI = {
  // 发送消息 - 流式响应
  sendMessageStream: async (
    data: {
      message: string
      session_id?: number
      kb_ids?: number[]
      use_web_search?: boolean
      session_type?: string
    },
    onChunk: (message: StreamMessage) => void
  ): Promise<{ sessionId: number; sources?: string[]; searchResults?: any[] }> => {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })

    if (!response.ok) {
      const error = await response.text()
      throw new Error(error || '请求失败')
    }

    const reader = response.body?.getReader()
    const decoder = new TextDecoder()

    if (!reader) {
      throw new Error('无法读取响应流')
    }

    let sessionId: number | undefined
    let sources: string[] | undefined
    let searchResults: any[] | undefined
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()

      if (done) break

      // 解码并追加到缓冲区
      buffer += decoder.decode(value, { stream: true })

      // 处理 SSE 格式的消息
      const lines = buffer.split('\n')
      buffer = lines.pop() || '' // 保留最后一个不完整的行

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            onChunk(data)

            if (data.type === 'end') {
              sessionId = data.session_id
              sources = data.sources
              searchResults = data.search_results
            }
          } catch (e) {
            console.error('Failed to parse SSE data:', e)
          }
        }
      }
    }

    return {
      sessionId: sessionId || data.session_id,
      sources,
      searchResults
    }
  },

  // 获取所有会话
  getSessions: async (sessionType?: string) => {
    const url = sessionType
      ? `${API_BASE_URL}/chat/sessions?session_type=${sessionType}`
      : `${API_BASE_URL}/chat/sessions`
    const response = await fetch(url)
    if (!response.ok) {
      const error = await response.text()
      throw new Error(error || '请求失败')
    }
    return response.json()
  },

  // 获取会话详情
  getSession: async (id: number) => {
    const response = await fetch(`${API_BASE_URL}/chat/sessions/${id}`)
    if (!response.ok) {
      const error = await response.text()
      throw new Error(error || '请求失败')
    }
    return response.json()
  },

  // 删除会话
  deleteSession: async (id: number) => {
    const response = await fetch(`${API_BASE_URL}/chat/sessions/${id}`, {
      method: 'DELETE'
    })
    if (!response.ok) {
      const error = await response.text()
      throw new Error(error || '请求失败')
    }
    return response.json()
  },

  // 重命名会话
  renameSession: async (id: number, title: string) => {
    const response = await fetch(`${API_BASE_URL}/chat/sessions/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ title })
    })
    if (!response.ok) {
      const error = await response.text()
      throw new Error(error || '请求失败')
    }
    return response.json()
  }
}

// 设置API
export const settingsAPI = {
  // 获取设置
  get: async () => {
    const response = await fetch(`${API_BASE_URL}/settings`)
    if (!response.ok) {
      const error = await response.text()
      throw new Error(error || '请求失败')
    }
    return response.json()
  },

  // 保存设置
  save: async (settings: any) => {
    const response = await fetch(`${API_BASE_URL}/settings`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(settings)
    })
    if (!response.ok) {
      const error = await response.text()
      throw new Error(error || '保存失败')
    }
    return response.json()
  }
}

// Agent聊天API - 流式响应
export interface AgentStreamMessage {
  type: 'chunk' | 'thought' | 'tool_call' | 'tool_result' | 'end' | 'error'
  content?: string
  session_id?: number
  tool_name?: string
  tool_args?: Record<string, any>
  thinking_steps?: Array<{
    type: string
    content: string
    tool_name?: string
    tool_args?: Record<string, any>
  }>
  search_results?: Array<{ title: string; url: string; snippet?: string }>
  sources?: string[]
  message?: string
}

export interface ThinkingStep {
  type: 'thought' | 'tool_call' | 'tool_result'
  content: string
  tool_name?: string
  tool_args?: Record<string, any>
}

export const agentAPI = {
  // 发送消息 - 流式响应
  sendMessageStream: async (
    data: {
      message: string
      session_id?: number
      kb_ids?: number[]
      use_web_search?: boolean
      show_thinking?: boolean
    },
    onChunk: (message: AgentStreamMessage) => void
  ): Promise<{
    sessionId: number
    thinkingSteps?: ThinkingStep[]
    searchResults?: Array<{ title: string; url: string; snippet?: string }>
    sources?: string[]
  }> => {
    const response = await fetch(`${API_BASE_URL}/chat/agent`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })

    if (!response.ok) {
      const error = await response.text()
      throw new Error(error || '请求失败')
    }

    const reader = response.body?.getReader()
    const decoder = new TextDecoder()

    if (!reader) {
      throw new Error('无法读取响应流')
    }

    let sessionId: number | undefined
    let thinkingSteps: ThinkingStep[] = []
    let searchResults: Array<{ title: string; url: string; snippet?: string }> = []
    let sources: string[] = []
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()

      if (done) break

      // 解码并追加到缓冲区
      buffer += decoder.decode(value, { stream: true })

      // 处理 SSE 格式的消息
      const lines = buffer.split('\n')
      buffer = lines.pop() || '' // 保留最后一个不完整的行

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const msgData = JSON.parse(line.slice(6))
            onChunk(msgData)

            if (msgData.type === 'end') {
              sessionId = msgData.session_id
              thinkingSteps = msgData.thinking_steps || []
              searchResults = msgData.search_results || []
              sources = msgData.sources || []
            }
          } catch (e) {
            console.error('Failed to parse SSE data:', e)
          }
        }
      }
    }

    return {
      sessionId: sessionId || data.session_id!,
      thinkingSteps,
      searchResults,
      sources
    }
  }
}

// MCP API
export interface MCPServerConfig {
  name: string
  transport: 'stdio' | 'http' | 'sse' | 'streamable-http'
  command?: string
  args?: string[]
  url?: string
}

export interface MCPServer extends MCPServerConfig {
  status: string
}

export interface MCPTool {
  name: string
  description?: string
}

export interface MCPStatus {
  initialized: boolean
  servers: MCPServer[]
  tools: MCPTool[]
}

export const mcpAPI = {
  // 获取MCP状态
  getStatus: async (): Promise<MCPStatus> => {
    const response = await fetch(`${API_BASE_URL}/mcp/status`)
    if (!response.ok) {
      const error = await response.text()
      throw new Error(error || '请求失败')
    }
    return response.json()
  },

  // 获取服务器列表
  getServers: async (): Promise<MCPServer[]> => {
    const response = await fetch(`${API_BASE_URL}/mcp/servers`)
    if (!response.ok) {
      const error = await response.text()
      throw new Error(error || '请求失败')
    }
    return response.json()
  },

  // 添加服务器
  addServer: async (config: MCPServerConfig): Promise<MCPServer> => {
    const response = await fetch(`${API_BASE_URL}/mcp/servers`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(config)
    })
    if (!response.ok) {
      const error = await response.text()
      throw new Error(error || '添加服务器失败')
    }
    return response.json()
  },

  // 删除服务器
  removeServer: async (name: string) => {
    const response = await fetch(`${API_BASE_URL}/mcp/servers/${encodeURIComponent(name)}`, {
      method: 'DELETE'
    })
    if (!response.ok) {
      const error = await response.text()
      throw new Error(error || '删除服务器失败')
    }
    return response.json()
  },

  // 获取工具列表
  getTools: async (): Promise<MCPTool[]> => {
    const response = await fetch(`${API_BASE_URL}/mcp/tools`)
    if (!response.ok) {
      const error = await response.text()
      throw new Error(error || '请求失败')
    }
    return response.json()
  },

  // 重新加载MCP服务器
  reload: async () => {
    const response = await fetch(`${API_BASE_URL}/mcp/reload`, {
      method: 'POST'
    })
    if (!response.ok) {
      const error = await response.text()
      throw new Error(error || '重新加载失败')
    }
    return response.json()
  }
}


// Multi-Agent API
export interface MultiAgentStreamMessage {
  type: 'planning' | 'plan' | 'task_start' | 'task_complete' | 'thought' | 'tool_call' | 'tool_result' | 'analysis' | 'answer' | 'error' | 'result' | 'done'
  task_id?: string
  agent_type?: string
  description?: string
  content?: string
  status?: string
  tasks?: Array<{
    id: string
    agent_type: string
    description: string
    priority: number
  }>
  session_id?: number
  sources?: string[]
  search_results?: Array<{ title: string; url: string; snippet?: string }>
}

export interface AgentTaskInfo {
  id: string
  agent_type: string
  description: string
  status: 'pending' | 'running' | 'completed' | 'failed'
}

export const multiAgentAPI = {
  // 多Agent聊天 - 流式响应
  sendMessageStream: async (
    data: {
      message: string
      session_id?: number
      kb_ids?: number[]
      use_web_search?: boolean
      show_process?: boolean
    },
    onChunk: (message: MultiAgentStreamMessage) => void
  ): Promise<{
    sessionId: number
    sources?: string[]
    searchResults?: Array<{ title: string; url: string; snippet?: string }>
  }> => {
    const response = await fetch(`${API_BASE_URL}/chat/multi-agent`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })

    if (!response.ok) {
      const error = await response.text()
      throw new Error(error || '请求失败')
    }

    const reader = response.body?.getReader()
    const decoder = new TextDecoder()

    if (!reader) {
      throw new Error('无法读取响应流')
    }

    let sessionId: number | undefined
    let sources: string[] = []
    let searchResults: Array<{ title: string; url: string; snippet?: string }> = []
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })

      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const msgData = JSON.parse(line.slice(6))
            onChunk(msgData)

            if (msgData.type === 'done') {
              sessionId = msgData.session_id
              sources = msgData.sources || []
              searchResults = msgData.search_results || []
            }
          } catch (e) {
            console.error('Failed to parse SSE data:', e)
          }
        }
      }
    }

    return {
      sessionId: sessionId || data.session_id!,
      sources,
      searchResults
    }
  },

  // 获取Agent类型列表
  getAgentTypes: async () => {
    const response = await fetch(`${API_BASE_URL}/agents/types/list`)
    if (!response.ok) {
      const error = await response.text()
      throw new Error(error || '请求失败')
    }
    return response.json()
  },

  // 获取所有Agent配置
  getAgents: async () => {
    const response = await fetch(`${API_BASE_URL}/agents`)
    if (!response.ok) {
      const error = await response.text()
      throw new Error(error || '请求失败')
    }
    return response.json()
  },

  // 创建自定义Agent
  createAgent: async (data: {
    name: string
    type: string
    description?: string
    system_prompt?: string
    tools?: string[]
    model_name?: string
    temperature?: number
  }) => {
    const response = await fetch(`${API_BASE_URL}/agents`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })
    if (!response.ok) {
      const error = await response.text()
      throw new Error(error || '创建Agent失败')
    }
    return response.json()
  },

  // 更新Agent配置
  updateAgent: async (id: number, data: {
    name?: string
    description?: string
    system_prompt?: string
    tools?: string[]
    model_name?: string
    temperature?: number
    is_active?: boolean
  }) => {
    const response = await fetch(`${API_BASE_URL}/agents/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })
    if (!response.ok) {
      const error = await response.text()
      throw new Error(error || '更新Agent失败')
    }
    return response.json()
  },

  // 删除Agent
  deleteAgent: async (id: number) => {
    const response = await fetch(`${API_BASE_URL}/agents/${id}`, {
      method: 'DELETE'
    })
    if (!response.ok) {
      const error = await response.text()
      throw new Error(error || '删除Agent失败')
    }
    return response.json()
  }
}

