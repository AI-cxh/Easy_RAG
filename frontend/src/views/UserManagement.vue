<template>
  <div class="layout">
    <AppNavRail />
    <div class="main-content">
      <div class="user-management">
        <div class="page-header">
          <h1>用户管理</h1>
          <p class="page-desc">审核注册用户、管理账号状态</p>
        </div>

        <div class="filter-bar">
          <select v-model="statusFilter" @change="loadUsers">
            <option value="">全部状态</option>
            <option value="pending">待审核</option>
            <option value="approved">已通过</option>
            <option value="rejected">已拒绝</option>
          </select>
        </div>

        <div v-if="loading" class="loading">加载中...</div>

        <div v-else-if="users.length === 0" class="empty">暂无用户数据</div>

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
              <tr v-for="user in users" :key="user.id">
                <td>{{ user.id }}</td>
                <td>{{ user.username }}</td>
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
                    <button
                      v-if="user.status === 'pending'"
                      class="btn approve"
                      @click="handleApprove(user.id)"
                      :disabled="actionLoading === user.id"
                    >
                      通过
                    </button>
                    <button
                      v-if="user.status === 'pending'"
                      class="btn reject"
                      @click="handleReject(user.id)"
                      :disabled="actionLoading === user.id"
                    >
                      拒绝
                    </button>
                    <button
                      v-if="user.role !== 'admin'"
                      class="btn delete"
                      @click="handleDelete(user.id)"
                      :disabled="actionLoading === user.id"
                    >
                      删除
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuth, type User } from '../composables/useAuth'
import AppNavRail from '../components/AppNavRail.vue'

const { fetchUsers, approveUser, rejectUser, deleteUser } = useAuth()

const users = ref<User[]>([])
const loading = ref(true)
const actionLoading = ref<number | null>(null)
const statusFilter = ref('')
const error = ref('')

onMounted(() => {
  loadUsers()
})

async function loadUsers() {
  loading.value = true
  error.value = ''
  try {
    users.value = await fetchUsers()
    if (statusFilter.value) {
      users.value = users.value.filter(u => u.status === statusFilter.value)
    }
  } catch (e: any) {
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

async function handleApprove(userId: number) {
  actionLoading.value = userId
  error.value = ''
  try {
    await approveUser(userId)
    await loadUsers()
  } catch (e: any) {
    error.value = e.message || '操作失败'
  } finally {
    actionLoading.value = null
  }
}

async function handleReject(userId: number) {
  actionLoading.value = userId
  error.value = ''
  try {
    await rejectUser(userId)
    await loadUsers()
  } catch (e: any) {
    error.value = e.message || '操作失败'
  } finally {
    actionLoading.value = null
  }
}

async function handleDelete(userId: number) {
  if (!confirm('确定要删除该用户吗？此操作不可恢复。')) return

  actionLoading.value = userId
  error.value = ''
  try {
    await deleteUser(userId)
    await loadUsers()
  } catch (e: any) {
    error.value = e.message || '操作失败'
  } finally {
    actionLoading.value = null
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
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.page-desc {
  color: #666;
  font-size: 14px;
}

.filter-bar {
  margin-bottom: 20px;
}

.filter-bar select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

.loading, .empty {
  text-align: center;
  padding: 40px;
  color: #666;
}

.user-table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.user-table {
  width: 100%;
  border-collapse: collapse;
}

.user-table th,
.user-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.user-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.user-table td {
  font-size: 14px;
  color: #555;
}

.role-badge {
  display: inline-block;
  padding: 4px 8px;
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

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
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

.action-buttons {
  display: flex;
  gap: 8px;
}

.btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn.approve {
  background: #4caf50;
  color: white;
}

.btn.reject {
  background: #ff9800;
  color: white;
}

.btn.delete {
  background: #f44336;
  color: white;
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
