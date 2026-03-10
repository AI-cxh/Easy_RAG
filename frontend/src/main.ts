import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import './styles/main.css'
import Chat from './views/Chat.vue'
import KnowledgeBase from './views/KnowledgeBase.vue'

// 创建路由
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/chat' },
    { path: '/chat', name: 'Chat', component: Chat },
    { path: '/knowledge', name: 'Knowledge', component: KnowledgeBase }
  ]
})

const app = createApp(App)
app.use(router)
app.mount('#app')
