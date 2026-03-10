import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    const message = error.response?.data?.detail || error.message || '请求失败'
    console.error('API Error:', message)
    return Promise.reject(new Error(message))
  }
)

// 知识库API
export const knowledgeAPI = {
  // 获取所有知识库
  getAll: () => apiClient.get('/knowledge'),

  // 创建知识库
  create: (data: { name: string; description?: string }) =>
    apiClient.post('/knowledge', data),

  // 获取知识库详情
  get: (id: number) => apiClient.get(`/knowledge/${id}`),

  // 删除知识库
  delete: (id: number) => apiClient.delete(`/knowledge/${id}`),

  // 获取知识库文档列表
  getDocuments: (id: number) => apiClient.get(`/knowledge/${id}/documents`)
}

// 文件上传API
export const uploadAPI = {
  // 上传文件
  upload: (kbId: number, file: File, onProgress?: (progress: number) => void) => {
    const formData = new FormData()
    formData.append('file', file)

    return apiClient.post(`/upload/${kbId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(progress)
        }
      }
    })
  },

  // 删除文档
  deleteDocument: (docId: number) => apiClient.delete(`/upload/documents/${docId}`)
}

// 聊天API
export const chatAPI = {
  // 发送消息
  sendMessage: (data: {
    message: string
    session_id?: number
    kb_ids?: number[]
    use_web_search?: boolean
  }) => apiClient.post('/chat', data),

  // 获取所有会话
  getSessions: () => apiClient.get('/chat/sessions'),

  // 获取会话详情
  getSession: (id: number) => apiClient.get(`/chat/sessions/${id}`),

  // 删除会话
  deleteSession: (id: number) => apiClient.delete(`/chat/sessions/${id}`)
}

export default apiClient
