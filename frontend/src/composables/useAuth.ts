import { ref, computed } from 'vue'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

export interface User {
  id: number
  username: string
  email: string
  role: 'admin' | 'user'
  status: 'pending' | 'approved' | 'rejected'
  created_at: string
  approved_at?: string
}

export interface UserStats {
  kb_count: number
  doc_count: number
  chunk_count: number
}

export interface UserDetail extends User {
  stats: UserStats
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
  user: User
}

// 响应式状态
const user = ref<User | null>(null)
const token = ref<string | null>(localStorage.getItem('token'))
const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))

// 初始化用户信息
const storedUser = localStorage.getItem('user')
if (storedUser && token.value) {
  try {
    user.value = JSON.parse(storedUser)
  } catch {
    localStorage.removeItem('user')
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
  }
}

export function useAuth() {
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isApproved = computed(() => user.value?.status === 'approved')

  async function login(username: string, password: string): Promise<AuthTokens> {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || '登录失败')
    }

    const data: AuthTokens = await response.json()

    // 保存状态
    token.value = data.access_token
    refreshToken.value = data.refresh_token
    user.value = data.user

    localStorage.setItem('token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    localStorage.setItem('user', JSON.stringify(data.user))

    return data
  }

  async function register(username: string, email: string, password: string): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || '注册失败')
    }

    return await response.json()
  }

  function logout() {
    token.value = null
    refreshToken.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }

  async function refreshAccessToken(): Promise<boolean> {
    if (!refreshToken.value) return false

    try {
      const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken.value })
      })

      if (!response.ok) {
        logout()
        return false
      }

      const data: AuthTokens = await response.json()
      token.value = data.access_token
      refreshToken.value = data.refresh_token
      user.value = data.user

      localStorage.setItem('token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      localStorage.setItem('user', JSON.stringify(data.user))

      return true
    } catch {
      logout()
      return false
    }
  }

  async function checkNeedsInit(): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/check-init`)
      if (!response.ok) return false
      const data = await response.json()
      return data.needs_init
    } catch {
      return false
    }
  }

  async function initAdmin(username: string, email: string, password: string): Promise<AuthTokens> {
    const response = await fetch(`${API_BASE_URL}/auth/init-admin`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || '初始化失败')
    }

    const data: AuthTokens = await response.json()

    token.value = data.access_token
    refreshToken.value = data.refresh_token
    user.value = data.user

    localStorage.setItem('token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    localStorage.setItem('user', JSON.stringify(data.user))

    return data
  }

  async function changePassword(oldPassword: string, newPassword: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/auth/change-password`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token.value}`
      },
      body: JSON.stringify({ old_password: oldPassword, new_password: newPassword })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || '修改密码失败')
    }
  }

  async function fetchUsers(): Promise<User[]> {
    const response = await fetch(`${API_BASE_URL}/auth/users`, {
      headers: { 'Authorization': `Bearer ${token.value}` }
    })

    if (!response.ok) {
      throw new Error('获取用户列表失败')
    }

    const data = await response.json()
    return data.items
  }

  async function approveUser(userId: number): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/auth/users/${userId}/approve`, {
      method: 'PUT',
      headers: { 'Authorization': `Bearer ${token.value}` }
    })

    if (!response.ok) {
      throw new Error('审核失败')
    }

    return await response.json()
  }

  async function rejectUser(userId: number): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/auth/users/${userId}/reject`, {
      method: 'PUT',
      headers: { 'Authorization': `Bearer ${token.value}` }
    })

    if (!response.ok) {
      throw new Error('拒绝失败')
    }

    return await response.json()
  }

  async function deleteUser(userId: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/auth/users/${userId}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token.value}` }
    })

    if (!response.ok) {
      throw new Error('删除用户失败')
    }
  }

  // ============ 管理员用户管理 ============

  async function createUser(data: {
    username: string
    email: string
    password: string
    role?: 'admin' | 'user'
    status?: 'pending' | 'approved' | 'rejected'
  }): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/auth/users`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token.value}`
      },
      body: JSON.stringify(data)
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || '创建用户失败')
    }

    return await response.json()
  }

  async function getUserDetail(userId: number): Promise<UserDetail> {
    const response = await fetch(`${API_BASE_URL}/auth/users/${userId}`, {
      headers: { 'Authorization': `Bearer ${token.value}` }
    })

    if (!response.ok) {
      throw new Error('获取用户详情失败')
    }

    return await response.json()
  }

  async function updateUser(userId: number, data: {
    username?: string
    email?: string
    role?: 'admin' | 'user'
    status?: 'pending' | 'approved' | 'rejected'
  }): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/auth/users/${userId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token.value}`
      },
      body: JSON.stringify(data)
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || '更新用户失败')
    }

    return await response.json()
  }

  async function resetUserPassword(userId: number, newPassword: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/auth/users/${userId}/reset-password`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token.value}`
      },
      body: JSON.stringify({ new_password: newPassword })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || '重置密码失败')
    }
  }

  return {
    user,
    token,
    isAuthenticated,
    isAdmin,
    isApproved,
    login,
    register,
    logout,
    refreshAccessToken,
    checkNeedsInit,
    initAdmin,
    changePassword,
    fetchUsers,
    approveUser,
    rejectUser,
    deleteUser,
    createUser,
    getUserDetail,
    updateUser,
    resetUserPassword
  }
}
