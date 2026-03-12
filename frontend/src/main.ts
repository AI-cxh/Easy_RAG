import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// 引入字体
import '@fontsource/inter/latin.css'
import '@fontsource/inter/latin-400.css'
import '@fontsource/inter/latin-500.css'
import '@fontsource/inter/latin-600.css'
import '@fontsource/inter/latin-700.css'
import '@fontsource-variable/jetbrains-mono'

// 样式引入顺序：设计令牌 -> 布局 -> 组件
import './styles/tokens.css'
import './styles/layout.css'
import './styles/components.css'

const app = createApp(App)
app.use(router)
app.mount('#app')
