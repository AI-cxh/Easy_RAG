<template>
  <div class="layout">
    <AppNavRail />
    <div class="main-content">
      <div class="user-management">
        <div class="page-header">
          <div class="header-info">
            <h1>用户管理</h1>
            <p class="page-desc">管理用户账号、权限和状态</p>
          </div>
          <button class="btn btn-primary" @click="showCreateDialog = true">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
            </svg>
            创建用户
          </button>
        </div>

        <!-- 统计卡片 -->
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-value">{{ stats.total }}</div>
            <div class="stat-label">用户总数</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ stats.admins }}</div>
            <div class="stat-label">管理员</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ stats.pending }}</div>
            <div class="stat-label">待审核</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ stats.approved }}</div>
            <div class="stat-label">已通过</div>
          </div>
        </div>

        <!-- 搜索和筛选 -->
        <div class="toolbar">
          <div class="search-box">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
            </svg>
            <input
              v-model="searchQuery"
              type="text"
              class="input"
              placeholder="搜索用户名或邮箱..."
              @keyup.enter="handleSearch"
            />
          </div>
          <div class="filter-group">
            <select v-model="statusFilter" class="input filter-select" @change="loadUsers">
              <option value="">全部状态</option>
              <option value="pending">待审核</option>
              <option value="approved">已通过</option>
              <option value="rejected">已拒绝</option>
            </select>
            <select v-model="roleFilter" class="input filter-select" @change="loadUsers">
              <option value="">全部角色</option>
              <option value="admin">管理员</option>
              <option value="user">普通用户</option>
            </select>
            <button class="btn btn-secondary" @click="loadUsers">
              <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
              </svg>
              刷新
            </button>
          </div>
        </div>

        <div v-if="loading" class="loading">加载中...</div>

        <div v-else-if="filteredUsers.length === 0" class="empty">暂无用户数据</div>

        <div v-else class="user-table-container">
          <table class="user-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>用户名</th>
                <th>邮箱</th>
                <th>角色</th>
                <th>状态</th>
                <th>注册时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in filteredUsers" :key="user.id">
                <td>{{ user.id }}</td>
                <td>
                  <span class="username" @click="showUserDetail(user)">{{ user.username }}</span>
                </td>
                <td>{{ user.email }}</td>
                <td>
                  <span class="role-badge" :class="user.role">
                    {{ user.role === 'admin' ? '管理员' : '普通用户' }}
                  </span>
                </td>
                <td>
                  <span class="status-badge" :class="user.status">
                    {{ statusText(user.status) }}
                  </span>
                </td>
                <td>{{ formatDate(user.created_at) }}</td>
                <td>
                  <div class="action-buttons">
                    <!-- 待审核状态 -->
                    <template v-if="user.status === 'pending'">
                      <button class="btn-icon approve" @click="handleApprove(user.id)" title="通过">
                        <svg viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
                      </button>
                      <button class="btn-icon reject" @click="handleReject(user.id)" title="拒绝">
                        <svg viewBox="0 0 24 24"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
                      </button>
                    </template>
                    <!-- 编辑 -->
                    <button class="btn-icon edit" @click="startEdit(user)" title="编辑">
                      <svg viewBox="0 0 24 24"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/></svg>
                    </button>
                    <!-- 重置密码 -->
                    <button class="btn-icon reset" @click="startResetPassword(user)" title="重置密码">
                      <svg viewBox="0 0 24 24"><path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"/></svg>
                    </button>
                    <!-- 删除（不能删除自己和唯一的管理员） -->
                    <button
                      v-if="user.role !== 'admin' || adminCount > 1"
                      class="btn-icon delete"
                      @click="handleDelete(user.id)"
                      title="删除"
                    >
                      <svg viewBox="0 0 24 24"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="error" class="error-message">{{ error }}</div>
      </div>
    </div>

    <!-- 创建用户对话框 -->
    <Teleport to="body">
      <div v-if="showCreateDialog" class="dialog-overlay" @click.self="showCreateDialog = false">
        <div class="dialog">
          <div class="dialog-header">
            <h3>创建用户</h3>
            <button class="dialog-close" @click="showCreateDialog = false">&times;</button>
          </div>
          <div class="dialog-body">
            <div class="form-group">
              <label>用户名 <span class="required">*</span></label>
              <input v-model="createForm.username" type="text" class="input" placeholder="请输入用户名" />
            </div>
            <div class="form-group">
              <label>邮箱 <span class="required">*</span></label>
              <input v-model="createForm.email" type="email" class="input" placeholder="请输入邮箱" />
            </div>
            <div class="form-group">
              <label>密码 <span class="required">*</span></label>
              <input v-model="createForm.password" type="password" class="input" placeholder="请输入密码" />
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>角色</label>
                <select v-model="createForm.role" class="input">
                  <option value="user">普通用户</option>
                  <option value="admin">管理员</option>
                </select>
              </div>
              <div class="form-group">
                <label>状态</label>
                <select v-model="createForm.status" class="input">
                  <option value="approved">已通过</option>
                  <option value="pending">待审核</option>
                </select>
              </div>
            </div>
          </div>
          <div class="dialog-footer">
            <button class="btn btn-secondary" @click="showCreateDialog = false">取消</button>
            <button class="btn btn-primary" @click="handleCreate" :disabled="actionLoading">
              {{ actionLoading ? '创建中...' : '创建' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 编辑用户对话框 -->
    <Teleport to="body">
      <div v-if="editingUser" class="dialog-overlay" @click.self="cancelEdit">
        <div class="dialog">
          <div class="dialog-header">
            <h3>编辑用户</h3>
            <button class="dialog-close" @click="cancelEdit">&times;</button>
          </div>
          <div class="dialog-body">
            <div class="form-group">
              <label>用户名</label>
              <input v-model="editForm.username" type="text" class="input" />
            </div>
            <div class="form-group">
              <label>邮箱</label>
              <input v-model="editForm.email" type="email" class="input" />
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>角色</label>
                <select v-model="editForm.role" class="input">
                  <option value="user">普通用户</option>
                  <option value="admin">管理员</option>
                </select>
              </div>
              <div class="form-group">
                <label>状态</label>
                <select v-model="editForm.status" class="input">
                  <option value="pending">待审核</option>
                  <option value="approved">已通过</option>
                  <option value="rejected">已拒绝</option>
                </select>
              </div>
            </div>
          </div>
          <div class="dialog-footer">
            <button class="btn btn-secondary" @click="cancelEdit">取消</button>
            <button class="btn btn-primary" @click="handleUpdate" :disabled="actionLoading">
              {{ actionLoading ? '保存中...' : '保存' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 重置密码对话框 -->
    <Teleport to="body">
      <div v-if="resetPasswordUser" class="dialog-overlay" @click.self="cancelResetPassword">
        <div class="dialog">
          <div class="dialog-header">
            <h3>重置密码</h3>
            <button class="dialog-close" @click="cancelResetPassword">&times;</button>
          </div>
          <div class="dialog-body">
            <p class="dialog-message">为用户 <strong>{{ resetPasswordUser.username }}</strong> 设置新密码</p>
            <div class="form-group">
              <label>新密码 <span class="required">*</span></label>
              <input v-model="resetPasswordForm.newPassword" type="password" class="input" placeholder="请输入新密码" />
            </div>
            <div class="form-group">
              <label>确认密码 <span class="required">*</span></label>
              <input v-model="resetPasswordForm.confirmPassword" type="password" class="input" placeholder="请再次输入新密码" />
            </div>
          </div>
          <div class="dialog-footer">
            <button class="btn btn-secondary" @click="cancelResetPassword">取消</button>
            <button class="btn btn-primary" @click="handleResetPassword" :disabled="actionLoading">
              {{ actionLoading ? '重置中...' : '确认重置' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 用户详情对话框 -->
    <Teleport to="body">
      <div v-if="detailUser" class="dialog-overlay" @click.self="detailUser = null">
        <div class="dialog dialog-wide">
          <div class="dialog-header">
            <h3>用户详情</h3>
            <button class="dialog-close" @click="detailUser = null">&times;</button>
          </div>
          <div class="dialog-body">
            <div class="user-detail-grid">
              <div class="detail-item">
                <span class="detail-label">用户名</span>
                <span class="detail-value">{{ detailUser.username }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">邮箱</span>
                <span class="detail-value">{{ detailUser.email }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">角色</span>
                <span class="detail-value">
                  <span class="role-badge" :class="detailUser.role">
                    {{ detailUser.role === 'admin' ? '管理员' : '普通用户' }}
                  </span>
                </span>
              </div>
              <div class="detail-item">
                <span class="detail-label">状态</span>
                <span class="detail-value">
                  <span class="status-badge" :class="detailUser.status">
                    {{ statusText(detailUser.status) }}
                  </span>
                </span>
              </div>
              <div class="detail-item">
                <span class="detail-label">注册时间</span>
                <span class="detail-value">{{ formatDate(detailUser.created_at) }}</span>
              </div>
              <div class="detail-item" v-if="detailUser.approved_at">
                <span class="detail-label">审核时间</span>
                <span class="detail-value">{{ formatDate(detailUser.approved_at) }}</span>
              </div>
            </div>
            <div class="user-stats">
              <h4>资源统计</h4>
              <div class="stats-row">
                <div class="stat-item">
                  <span class="stat-num">{{ detailUser.stats?.kb_count || 0 }}</span>
                  <span class="stat-text">知识库</span>
                </div>
                <div class="stat-item">
                  <span class="stat-num">{{ detailUser.stats?.doc_count || 0 }}</span>
                  <span class="stat-text">文档</span>
                </div>
                <div class="stat-item">
                  <span class="stat-num">{{ detailUser.stats?.chunk_count || 0 }}</span>
                  <span class="stat-text">分块</span>
                </div>
              </div>
            </div>
          </div>
          <div class="dialog-footer">
            <button class="btn btn-secondary" @click="detailUser = null">关闭</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuth, type User, type UserDetail } from '../composables/useAuth'
import AppNavRail from '../components/AppNavRail.vue'

const {
  fetchUsers, approveUser, rejectUser, deleteUser,
  createUser, getUserDetail, updateUser, resetUserPassword
} = useAuth()

const users = ref<User[]>([])
const loading = ref(true)
const actionLoading = ref(false)
const statusFilter = ref('')
const roleFilter = ref('')
const searchQuery = ref('')
const error = ref('')

// 统计
const stats = computed(() => ({
  total: users.value.length,
  admins: users.value.filter(u => u.role === 'admin').length,
  pending: users.value.filter(u => u.status === 'pending').length,
  approved: users.value.filter(u => u.status === 'approved').length
}))

const adminCount = computed(() => users.value.filter(u => u.role === 'admin').length)

// 筛选后的用户列表
const filteredUsers = computed(() => {
  let result = users.value
  if (statusFilter.value) {
    result = result.filter(u => u.status === statusFilter.value)
  }
  if (roleFilter.value) {
    result = result.filter(u => u.role === roleFilter.value)
  }
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(u =>
      u.username.toLowerCase().includes(query) ||
      u.email.toLowerCase().includes(query)
    )
  }
  return result
})

// 创建用户
const showCreateDialog = ref(false)
const createForm = ref({
  username: '',
  email: '',
  password: '',
  role: 'user' as 'admin' | 'user',
  status: 'approved' as 'pending' | 'approved' | 'rejected'
})

// 编辑用户
const editingUser = ref<User | null>(null)
const editForm = ref({
  username: '',
  email: '',
  role: '' as 'admin' | 'user',
  status: '' as 'pending' | 'approved' | 'rejected'
})

// 重置密码
const resetPasswordUser = ref<User | null>(null)
const resetPasswordForm = ref({
  newPassword: '',
  confirmPassword: ''
})

// 用户详情
const detailUser = ref<UserDetail | null>(null)

onMounted(() => {
  loadUsers()
})

async function loadUsers() {
  loading.value = true
  error.value = ''
  try {
    users.value = await fetchUsers()
  } catch (e: any) {
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  // 筛选由 computed 处理
}

async function handleApprove(userId: number) {
  error.value = ''
  try {
    await approveUser(userId)
    await loadUsers()
  } catch (e: any) {
    error.value = e.message || '操作失败'
  }
}

async function handleReject(userId: number) {
  error.value = ''
  try {
    await rejectUser(userId)
    await loadUsers()
  } catch (e: any) {
    error.value = e.message || '操作失败'
  }
}

async function handleDelete(userId: number) {
  if (!confirm('确定要删除该用户吗？此操作不可恢复。')) return

  error.value = ''
  try {
    await deleteUser(userId)
    await loadUsers()
  } catch (e: any) {
    error.value = e.message || '删除失败'
  }
}

async function handleCreate() {
  if (!createForm.value.username || !createForm.value.email || !createForm.value.password) {
    error.value = '请填写必填项'
    return
  }

  actionLoading.value = true
  error.value = ''
  try {
    await createUser(createForm.value)
    showCreateDialog.value = false
    createForm.value = { username: '', email: '', password: '', role: 'user', status: 'approved' }
    await loadUsers()
  } catch (e: any) {
    error.value = e.message || '创建失败'
  } finally {
    actionLoading.value = false
  }
}

function startEdit(user: User) {
  editingUser.value = user
  editForm.value = {
    username: user.username,
    email: user.email,
    role: user.role,
    status: user.status
  }
}

function cancelEdit() {
  editingUser.value = null
}

async function handleUpdate() {
  if (!editingUser.value) return

  actionLoading.value = true
  error.value = ''
  try {
    await updateUser(editingUser.value.id, editForm.value)
    cancelEdit()
    await loadUsers()
  } catch (e: any) {
    error.value = e.message || '更新失败'
  } finally {
    actionLoading.value = false
  }
}

function startResetPassword(user: User) {
  resetPasswordUser.value = user
  resetPasswordForm.value = { newPassword: '', confirmPassword: '' }
}

function cancelResetPassword() {
  resetPasswordUser.value = null
}

async function handleResetPassword() {
  if (!resetPasswordUser.value) return

  if (!resetPasswordForm.value.newPassword || resetPasswordForm.value.newPassword.length < 6) {
    error.value = '密码长度至少6位'
    return
  }

  if (resetPasswordForm.value.newPassword !== resetPasswordForm.value.confirmPassword) {
    error.value = '两次输入的密码不一致'
    return
  }

  actionLoading.value = true
  error.value = ''
  try {
    await resetUserPassword(resetPasswordUser.value.id, resetPasswordForm.value.newPassword)
    cancelResetPassword()
    alert('密码重置成功')
  } catch (e: any) {
    error.value = e.message || '重置失败'
  } finally {
    actionLoading.value = false
  }
}

async function showUserDetail(user: User) {
  try {
    detailUser.value = await getUserDetail(user.id)
  } catch (e: any) {
    error.value = e.message || '获取详情失败'
  }
}

function statusText(status: string): string {
  const map: Record<string, string> = {
    pending: '待审核',
    approved: '已通过',
    rejected: '已拒绝'
  }
  return map[status] || status
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
  background: var(--bg-primary);
}

.main-content {
  flex: 1;
  overflow: auto;
}

.user-management {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.page-desc {
  color: var(--text-secondary);
  font-size: 14px;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn svg {
  width: 16px;
  height: 16px;
  fill: currentColor;
}

.btn-primary {
  background: var(--color-primary);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-dark);
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--bg-hover);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: var(--bg-elevated);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  border: 1px solid var(--border-subtle);
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--color-primary);
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 4px;
}

/* 工具栏 */
.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.search-box {
  flex: 1;
  min-width: 200px;
  max-width: 400px;
  position: relative;
}

.search-box svg {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  fill: var(--text-muted);
}

.search-box .input {
  padding-left: 40px;
}

.status-select {
  width: 120px;
}

.filter-group {
  display: flex;
  gap: 12px;
  align-items: center;
}

.filter-select {
  width: 120px;
}

.filter-group .btn {
  white-space: nowrap;
  flex-shrink: 0;
}

.input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  font-size: 14px;
  background: var(--bg-elevated);
  color: var(--text-primary);
}

.input:focus {
  outline: none;
  border-color: var(--color-primary);
}

/* 表格 */
.user-table-container {
  background: var(--bg-elevated);
  border-radius: 12px;
  border: 1px solid var(--border-subtle);
  overflow: hidden;
}

.user-table {
  width: 100%;
  border-collapse: collapse;
}

.user-table th,
.user-table td {
  padding: 14px 16px;
  text-align: left;
  border-bottom: 1px solid var(--border-subtle);
}

.user-table th {
  background: var(--bg-secondary);
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 13px;
}

.user-table td {
  font-size: 14px;
  color: var(--text-primary);
}

.user-table tr:hover td {
  background: var(--bg-hover);
}

.username {
  color: var(--color-primary);
  cursor: pointer;
  font-weight: 500;
}

.username:hover {
  text-decoration: underline;
}

/* 徽章 */
.role-badge, .status-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.role-badge.admin {
  background: #e3f2fd;
  color: #1976d2;
}

.role-badge.user {
  background: #f5f5f5;
  color: #666;
}

.status-badge.pending {
  background: #fff3e0;
  color: #f57c00;
}

.status-badge.approved {
  background: #e8f5e9;
  color: #388e3c;
}

.status-badge.rejected {
  background: #ffebee;
  color: #d32f2f;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: 6px;
}

.btn-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-icon svg {
  width: 18px;
  height: 18px;
  fill: currentColor;
}

.btn-icon.approve {
  background: #e8f5e9;
  color: #388e3c;
}

.btn-icon.approve:hover {
  background: #388e3c;
  color: white;
}

.btn-icon.reject {
  background: #fff3e0;
  color: #f57c00;
}

.btn-icon.reject:hover {
  background: #f57c00;
  color: white;
}

.btn-icon.edit {
  background: #e3f2fd;
  color: #1976d2;
}

.btn-icon.edit:hover {
  background: #1976d2;
  color: white;
}

.btn-icon.reset {
  background: #f3e5f5;
  color: #7b1fa2;
}

.btn-icon.reset:hover {
  background: #7b1fa2;
  color: white;
}

.btn-icon.delete {
  background: #ffebee;
  color: #d32f2f;
}

.btn-icon.delete:hover {
  background: #d32f2f;
  color: white;
}

/* 对话框 */
.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog {
  background: var(--bg-elevated);
  border-radius: 12px;
  width: 90%;
  max-width: 480px;
  max-height: 90vh;
  overflow: auto;
}

.dialog-wide {
  max-width: 600px;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-subtle);
}

.dialog-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.dialog-close {
  background: none;
  border: none;
  font-size: 24px;
  color: var(--text-muted);
  cursor: pointer;
  line-height: 1;
}

.dialog-body {
  padding: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid var(--border-subtle);
}

.dialog-message {
  margin-bottom: 16px;
  color: var(--text-primary);
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.required {
  color: #d32f2f;
}

.form-row {
  display: flex;
  gap: 16px;
}

.form-row .form-group {
  flex: 1;
}

/* 用户详情 */
.user-detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.detail-value {
  font-size: 14px;
  color: var(--text-primary);
}

.user-stats {
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 16px;
}

.user-stats h4 {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 12px 0;
}

.stats-row {
  display: flex;
  gap: 24px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-num {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-primary);
}

.stat-text {
  font-size: 12px;
  color: var(--text-secondary);
}

.loading, .empty {
  text-align: center;
  padding: 60px;
  color: var(--text-muted);
}

.error-message {
  margin-top: 16px;
  padding: 12px;
  background: #ffebee;
  color: #c62828;
  border-radius: 6px;
  text-align: center;
}
</style>
