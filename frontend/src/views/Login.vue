<template>
  <div class="login-container" @mousemove="handleMouseMove" ref="containerRef">
    <!-- 动态背景 -->
    <div class="bg-gradient"></div>
    <div class="bg-pattern"></div>
    <div
      class="mouse-glow"
      :style="{ left: mouseGlow.x + 'px', top: mouseGlow.y + 'px' }"
    ></div>

    <!-- 浮动装饰元素 -->
    <div class="floating-shapes">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
    </div>

    <!-- 登录卡片 -->
    <div class="login-card" :class="{ 'card-hovered': isCardHovered }"
      @mouseenter="isCardHovered = true"
      @mouseleave="isCardHovered = false">
      <!-- Logo 区域 -->
      <div class="logo-section">
        <div class="logo-icon">
          <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M24 4L42 14V34L24 44L6 34V14L24 4Z" stroke="currentColor" stroke-width="2" fill="none"/>
            <path d="M24 4V44" stroke="currentColor" stroke-width="1.5" opacity="0.5"/>
            <path d="M6 14L42 34" stroke="currentColor" stroke-width="1.5" opacity="0.5"/>
            <path d="M42 14L6 34" stroke="currentColor" stroke-width="1.5" opacity="0.5"/>
            <circle cx="24" cy="24" r="6" fill="currentColor" opacity="0.2"/>
          </svg>
        </div>
        <h1 class="login-title">Easy RAG</h1>
        <p class="login-subtitle">智能知识库管理系统</p>
      </div>

      <!-- 表单区域 -->
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group" :class="{ 'focused': focusedField === 'username', 'has-value': username }">
          <div class="input-wrapper">
            <div class="input-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
            </div>
            <input
              id="username"
              v-model="username"
              type="text"
              required
              :disabled="loading"
              @focus="focusedField = 'username'"
              @blur="focusedField = ''"
              autocomplete="username"
            />
            <label for="username">用户名</label>
            <div class="input-border"></div>
          </div>
        </div>

        <div class="form-group" :class="{ 'focused': focusedField === 'password', 'has-value': password }">
          <div class="input-wrapper">
            <div class="input-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
              </svg>
            </div>
            <input
              id="password"
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              required
              :disabled="loading"
              @focus="focusedField = 'password'"
              @blur="focusedField = ''"
              autocomplete="current-password"
            />
            <label for="password">密码</label>
            <div class="input-border"></div>
            <button type="button" class="password-toggle" @click="showPassword = !showPassword" tabindex="-1">
              <svg v-if="!showPassword" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                <line x1="1" y1="1" x2="23" y2="23"/>
              </svg>
            </button>
          </div>
        </div>

        <div v-if="error" class="error-message">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          <span>{{ error }}</span>
        </div>

        <button type="submit" class="login-btn" :disabled="loading || !username || !password">
          <span class="btn-text">{{ loading ? '登录中...' : '登录' }}</span>
          <span class="btn-icon">
            <svg v-if="loading" class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10" stroke-dasharray="60" stroke-dashoffset="20"/>
            </svg>
          </span>
          <div class="btn-ripple"></div>
        </button>
      </form>

      <!-- 底部链接 -->
      <div class="login-footer">
        <p>还没有账号？<router-link to="/register">立即注册</router-link></p>
      </div>
    </div>

    <!-- 底部版权 -->
    <div class="copyright">
      <p>Powered by Easy RAG</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const route = useRoute()
const { login } = useAuth()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')
const showPassword = ref(false)
const focusedField = ref('')
const isCardHovered = ref(false)
const containerRef = ref<HTMLElement | null>(null)

const mouseGlow = reactive({ x: -200, y: -200 })

function handleMouseMove(e: MouseEvent) {
  if (containerRef.value) {
    const rect = containerRef.value.getBoundingClientRect()
    mouseGlow.x = e.clientX - rect.left - 150
    mouseGlow.y = e.clientY - rect.top - 150
  }
}

async function handleLogin() {
  if (!username.value || !password.value) return

  loading.value = true
  error.value = ''

  try {
    await login(username.value, password.value)
    const redirect = route.query.redirect as string || '/'
    router.push(redirect)
  } catch (e: any) {
    error.value = e.message || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
@import '@fontsource/dm-sans/400.css';
@import '@fontsource/dm-sans/500.css';
@import '@fontsource/dm-sans/700.css';
@import '@fontsource/cormorant-garamond/600.css';

/* 使用与全局一致的变量 */
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
  background: #faf8f5;
}

/* 背景渐变 - 使用温暖色调 */
.bg-gradient {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 80% 50% at 50% -20%, rgba(196, 125, 94, 0.08), transparent),
    radial-gradient(ellipse 60% 40% at 80% 100%, rgba(122, 158, 126, 0.06), transparent),
    radial-gradient(ellipse 50% 30% at 20% 80%, rgba(212, 165, 116, 0.05), transparent);
  animation: gradientShift 20s ease-in-out infinite;
}

@keyframes gradientShift {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.8; transform: scale(1.05); }
}

/* 装饰图案背景 */
.bg-pattern {
  position: absolute;
  inset: 0;
  opacity: 0.4;
  background-image: radial-gradient(rgba(196, 125, 94, 0.08) 1px, transparent 1px);
  background-size: 32px 32px;
}

/* 鼠标跟随光晕 */
.mouse-glow {
  position: absolute;
  width: 300px;
  height: 300px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(196, 125, 94, 0.1) 0%, transparent 70%);
  pointer-events: none;
  transition: left 0.4s ease-out, top 0.4s ease-out;
  will-change: transform;
}

/* 浮动装饰形状 */
.floating-shapes {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.shape {
  position: absolute;
  border-radius: 50%;
  opacity: 0.6;
}

.shape-1 {
  width: 400px;
  height: 400px;
  top: -100px;
  right: -100px;
  background: radial-gradient(circle, rgba(196, 125, 94, 0.06) 0%, transparent 70%);
  animation: floatShape 25s ease-in-out infinite;
}

.shape-2 {
  width: 300px;
  height: 300px;
  bottom: -50px;
  left: -50px;
  background: radial-gradient(circle, rgba(122, 158, 126, 0.05) 0%, transparent 70%);
  animation: floatShape 20s ease-in-out infinite reverse;
}

.shape-3 {
  width: 200px;
  height: 200px;
  top: 50%;
  left: 10%;
  background: radial-gradient(circle, rgba(212, 165, 116, 0.04) 0%, transparent 70%);
  animation: floatShape 18s ease-in-out infinite;
  animation-delay: -5s;
}

@keyframes floatShape {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -30px) scale(1.05); }
  66% { transform: translate(-20px, 20px) scale(0.95); }
}

/* 登录卡片 */
.login-card {
  position: relative;
  width: 100%;
  max-width: 420px;
  margin: 20px;
  padding: 48px 40px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 24px;
  border: 1px solid rgba(61, 54, 50, 0.06);
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.5) inset,
    0 25px 50px -12px rgba(61, 54, 50, 0.08);
  animation: cardEnter 0.8s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
  opacity: 0;
  transform: translateY(30px);
}

@keyframes cardEnter {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-card::before {
  content: '';
  position: absolute;
  inset: -1px;
  border-radius: 24px;
  padding: 1px;
  background: linear-gradient(135deg, rgba(196, 125, 94, 0.2), transparent 50%, rgba(122, 158, 126, 0.15));
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask-composite: exclude;
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.login-card.card-hovered::before {
  opacity: 1;
}

/* Logo 区域 */
.logo-section {
  text-align: center;
  margin-bottom: 40px;
  animation: fadeInUp 0.6s ease 0.2s both;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.logo-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  color: #c47d5e;
  animation: logoFloat 3s ease-in-out infinite;
}

@keyframes logoFloat {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-8px) rotate(5deg); }
}

.logo-icon svg {
  width: 100%;
  height: 100%;
}

.login-title {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: 32px;
  font-weight: 600;
  color: #3d3632;
  margin: 0 0 8px;
  letter-spacing: -0.02em;
}

.login-subtitle {
  font-size: 14px;
  color: #6b5f57;
  margin: 0;
  font-weight: 400;
}

/* 表单 */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-group {
  position: relative;
  animation: fadeInUp 0.6s ease both;
}

.form-group:nth-child(1) { animation-delay: 0.3s; }
.form-group:nth-child(2) { animation-delay: 0.4s; }

.input-wrapper {
  position: relative;
}

.input-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  color: #9a8f85;
  transition: color 0.3s ease;
  z-index: 2;
}

.input-icon svg {
  width: 100%;
  height: 100%;
}

.form-group input {
  width: 100%;
  padding: 16px 48px;
  background: rgba(245, 241, 235, 0.6);
  border: 1px solid rgba(61, 54, 50, 0.1);
  border-radius: 12px;
  font-size: 15px;
  color: #3d3632;
  font-family: inherit;
  transition: all 0.3s ease;
}

.form-group input::placeholder {
  color: transparent;
}

.form-group label {
  position: absolute;
  left: 48px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 15px;
  color: #9a8f85;
  pointer-events: none;
  transition: opacity 0.2s ease;
}

.form-group input:focus,
.form-group.has-value input {
  background: rgba(255, 255, 255, 0.8);
  border-color: #c47d5e;
  box-shadow: 0 0 0 3px rgba(196, 125, 94, 0.1);
}

.form-group.focused .input-icon,
.form-group.has-value .input-icon {
  color: #c47d5e;
}

.form-group.focused label,
.form-group.has-value label {
  opacity: 0;
}

/* 输入框边框动画 */
.input-border {
  position: absolute;
  inset: 0;
  border-radius: 12px;
  pointer-events: none;
}

.input-border::after {
  content: '';
  position: absolute;
  inset: -1px;
  border-radius: 12px;
  border: 2px solid #c47d5e;
  opacity: 0;
  transform: scale(1.02);
  transition: all 0.3s ease;
}

.form-group.focused .input-border::after {
  opacity: 1;
  transform: scale(1);
}

/* 密码显示切换 */
.password-toggle {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  background: none;
  border: none;
  cursor: pointer;
  color: #9a8f85;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.3s ease;
}

.password-toggle:hover {
  color: #c47d5e;
}

.password-toggle svg {
  width: 100%;
  height: 100%;
}

/* 错误消息 */
.error-message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(196, 112, 112, 0.1);
  border: 1px solid rgba(196, 112, 112, 0.2);
  border-radius: 10px;
  color: #c47070;
  font-size: 14px;
  animation: shake 0.5s ease;
}

.error-message svg {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20%, 60% { transform: translateX(-5px); }
  40%, 80% { transform: translateX(5px); }
}

/* 登录按钮 */
.login-btn {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 16px;
  background: linear-gradient(135deg, #c47d5e 0%, #d4a574 100%);
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  color: white;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.3s ease;
  animation: fadeInUp 0.6s ease 0.5s both;
  box-shadow: 0 4px 16px rgba(196, 125, 94, 0.25);
}

.login-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #b06a4d 0%, #c47d5e 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.login-btn:hover:not(:disabled)::before {
  opacity: 1;
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(196, 125, 94, 0.35);
}

.login-btn:active:not(:disabled) {
  transform: translateY(0);
}

.login-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-text,
.btn-icon {
  position: relative;
  z-index: 1;
}

.btn-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
}

.btn-icon svg {
  width: 100%;
  height: 100%;
}

.spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 按钮波纹效果 */
.btn-ripple {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.login-btn:active:not(:disabled) .btn-ripple {
  background: radial-gradient(circle at center, rgba(255, 255, 255, 0.3) 0%, transparent 70%);
  animation: ripple 0.6s ease;
}

@keyframes ripple {
  from {
    transform: scale(0);
    opacity: 1;
  }
  to {
    transform: scale(2);
    opacity: 0;
  }
}

/* 底部链接 */
.login-footer {
  margin-top: 32px;
  text-align: center;
  animation: fadeInUp 0.6s ease 0.6s both;
}

.login-footer p {
  font-size: 14px;
  color: #6b5f57;
  margin: 0;
}

.login-footer a {
  color: #c47d5e;
  text-decoration: none;
  font-weight: 500;
  position: relative;
  transition: color 0.3s ease;
}

.login-footer a::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0;
  height: 1px;
  background: #c47d5e;
  transition: width 0.3s ease;
}

.login-footer a:hover {
  color: #9a5a42;
}

.login-footer a:hover::after {
  width: 100%;
  background: #9a5a42;
}

/* 版权信息 */
.copyright {
  position: absolute;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 12px;
  color: #9a8f85;
  opacity: 0.6;
}

/* 响应式 */
@media (max-width: 480px) {
  .login-card {
    margin: 16px;
    padding: 32px 24px;
    border-radius: 20px;
  }

  .login-title {
    font-size: 28px;
  }

  .logo-icon {
    width: 56px;
    height: 56px;
  }
}

/* 减少动画偏好 */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
</style>
