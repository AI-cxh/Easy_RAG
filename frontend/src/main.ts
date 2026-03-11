import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// 样式引入顺序：设计令牌 -> 布局 -> 组件
import './styles/tokens.css'
import './styles/layout.css'
import './styles/components.css'

const app = createApp(App)
app.use(router)
app.mount('#app')
