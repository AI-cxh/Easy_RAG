import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/rag'
    },
    {
      path: '/rag',
      name: 'RAG',
      component: () => import('../views/ChatRAG.vue')
    },
    {
      path: '/agentic',
      name: 'Agentic',
      component: () => import('../views/ChatAgentic.vue')
    },
    {
      path: '/multi-agent',
      name: 'MultiAgent',
      component: () => import('../views/ChatMultiAgent.vue')
    },
    {
      path: '/knowledge',
      name: 'KnowledgeList',
      component: () => import('../views/KnowledgeList.vue')
    },
    {
      path: '/knowledge/:kbId/documents',
      name: 'DocumentList',
      component: () => import('../views/DocumentList.vue')
    },
    {
      path: '/knowledge/:kbId/documents/:docId/chunks',
      name: 'ChunkList',
      component: () => import('../views/ChunkList.vue')
    },
    {
      path: '/settings',
      name: 'Settings',
      component: () => import('../views/Settings.vue')
    }
  ]
})

export default router
