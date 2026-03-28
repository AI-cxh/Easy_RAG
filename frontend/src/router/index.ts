import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/rag'
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/Login.vue'),
      meta: { guest: true }
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('../views/Register.vue'),
      meta: { guest: true }
    },
    {
      path: '/init',
      name: 'InitAdmin',
      component: () => import('../views/InitAdmin.vue'),
      meta: { guest: true }
    },
    {
      path: '/rag',
      name: 'RAG',
      component: () => import('../views/ChatRAG.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/agentic',
      name: 'Agentic',
      component: () => import('../views/ChatAgentic.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/multi-agent',
      name: 'MultiAgent',
      component: () => import('../views/ChatMultiAgent.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/knowledge',
      name: 'KnowledgeList',
      component: () => import('../views/KnowledgeList.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/knowledge/:kbId/documents',
      name: 'DocumentList',
      component: () => import('../views/DocumentList.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/knowledge/:kbId/documents/:docId/chunks',
      name: 'ChunkList',
      component: () => import('../views/ChunkList.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/settings',
      name: 'Settings',
      component: () => import('../views/Settings.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/users',
      name: 'UserManagement',
      component: () => import('../views/UserManagement.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    }
  ]
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const { isAuthenticated, isAdmin, checkNeedsInit } = useAuth()

  // 检查是否需要初始化admin
  if (!isAuthenticated.value && to.path !== '/init' && to.meta.requiresAuth) {
    const needsInit = await checkNeedsInit()
    if (needsInit) {
      return next('/init')
    }
  }

  // 游客可访问的页面
  if (to.meta.guest) {
    // 已登录用户访问登录/注册页，重定向到首页
    if (isAuthenticated.value) {
      return next('/')
    }
    return next()
  }

  // 需要认证的页面
  if (to.meta.requiresAuth && !isAuthenticated.value) {
    return next({ path: '/login', query: { redirect: to.fullPath } })
  }

  // 需要管理员权限的页面
  if (to.meta.requiresAdmin && !isAdmin.value) {
    return next('/')
  }

  next()
})

export default router
