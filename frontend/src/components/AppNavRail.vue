<template>
  <nav class="nav-rail">
    <router-link to="/rag" class="nav-rail-btn" :class="{ active: isActive('/rag') }" title="普通RAG">
      <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
      </svg>
    </router-link>
    <router-link to="/agentic" class="nav-rail-btn" :class="{ active: isActive('/agentic') }" title="Agentic RAG">
      <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
      </svg>
    </router-link>
    <router-link to="/multi-agent" class="nav-rail-btn" :class="{ active: isActive('/multi-agent') }" title="多Agent协同">
      <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/>
      </svg>
    </router-link>
    <div class="nav-divider"></div>
    <router-link to="/knowledge" class="nav-rail-btn" title="知识库管理">
      <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path d="M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-1 9H9V9h10v2zm-4 4H9v-2h6v2zm4-8H9V5h10v2z"/>
      </svg>
    </router-link>
    <router-link v-if="isAdmin" to="/users" class="nav-rail-btn" :class="{ active: isActive('/users') }" title="用户管理">
      <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
      </svg>
    </router-link>
    <router-link v-if="isAdmin" to="/settings" class="nav-rail-btn" title="设置">
      <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path d="M19.14 12.94c.04-.31.06-.63.06-.94 0-.31-.02-.63-.06-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.04.31-.06.63-.06.94s.02.63.06.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/>
      </svg>
    </router-link>

    <!-- 底部用户区域 -->
    <div class="nav-spacer"></div>
    <div class="nav-divider"></div>
    <div class="user-section">
      <div class="user-avatar" :title="user?.username" @click="showUserMenu = !showUserMenu">
        {{ userInitial }}
      </div>
      <div v-if="showUserMenu" class="user-menu">
        <div class="user-info">
          <div class="user-name">{{ user?.username }}</div>
          <div class="user-role">{{ user?.role === 'admin' ? '管理员' : '普通用户' }}</div>
        </div>
        <button class="menu-item" @click="handleLogout">
          <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"/>
          </svg>
          退出登录
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const route = useRoute()
const router = useRouter()
const { user, isAdmin, logout } = useAuth()

const showUserMenu = ref(false)

const isActive = (path: string) => {
  return route.path === path || route.path.startsWith(path + '/')
}

const userInitial = computed(() => {
  return user.value?.username?.charAt(0).toUpperCase() || '?'
})

function handleLogout() {
  showUserMenu.value = false
  logout()
  router.push('/login')
}

// 点击外部关闭菜单
document.addEventListener('click', (e) => {
  const target = e.target as HTMLElement
  if (!target.closest('.user-section')) {
    showUserMenu.value = false
  }
})
</script>

<style scoped>
.nav-rail {
  width: clamp(56px, 8vw, 72px);
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-4) 0;
  gap: var(--space-2);
  flex-shrink: 0;
}

.nav-rail-btn {
  width: clamp(36px, 5vw, 44px);
  height: clamp(36px, 5vw, 44px);
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: var(--radius-lg);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--duration-normal) var(--ease-soft);
  text-decoration: none;
  position: relative;
}

.nav-rail-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: var(--color-primary-light);
  opacity: 0;
  transform: scale(0.8);
  transition: all var(--duration-normal) var(--ease-spring);
}

.nav-rail-btn:hover {
  color: var(--text-primary);
}

.nav-rail-btn:hover::before {
  opacity: 1;
  transform: scale(1);
}

.nav-rail-btn.router-link-active,
.nav-rail-btn.active {
  color: var(--color-primary);
}

.nav-rail-btn.router-link-active::before,
.nav-rail-btn.active::before {
  opacity: 1;
  transform: scale(1);
}

.nav-rail-btn svg {
  width: clamp(18px, 2.5vw, 22px);
  height: clamp(18px, 2.5vw, 22px);
  fill: currentColor;
  position: relative;
  z-index: 1;
}

.nav-divider {
  height: 1px;
  width: 24px;
  background: var(--border-subtle);
  margin: var(--space-2) 0;
}

.nav-spacer {
  flex: 1;
}

.user-section {
  position: relative;
}

.user-avatar {
  width: clamp(36px, 5vw, 44px);
  height: clamp(36px, 5vw, 44px);
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: var(--radius-lg);
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: transform var(--duration-fast);
}

.user-avatar:hover {
  transform: scale(1.05);
}

.user-menu {
  position: absolute;
  left: 100%;
  bottom: 0;
  margin-left: 8px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  min-width: 160px;
  overflow: hidden;
  animation: slideRight var(--duration-fast) var(--ease-soft);
  z-index: 1000;
}

.user-info {
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--border-subtle);
}

.user-name {
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.user-role {
  font-size: var(--text-xs);
  color: var(--text-muted);
  margin-top: 2px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  width: 100%;
  padding: var(--space-3) var(--space-4);
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: all var(--duration-fast);
  text-align: left;
}

.menu-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.menu-item svg {
  width: 16px;
  height: 16px;
  fill: currentColor;
}

@keyframes slideRight {
  from {
    opacity: 0;
    transform: translateX(-8px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
</style>
