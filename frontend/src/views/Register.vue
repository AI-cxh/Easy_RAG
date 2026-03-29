<template>
  <div class="register-container" @mousemove="handleMouseMove" ref="containerRef">
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

    <!-- 注册卡片 -->
    <div class="register-card" :class="{ 'card-hovered': isCardHovered }"
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
        <h1 class="register-title">Easy RAG</h1>
        <p class="register-subtitle">创建您的账号</p>
      </div>

      <!-- 表单区域 -->
      <form @submit.prevent="handleRegister" class="register-form">
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
              placeholder=" "
              required
              minlength="3"
              maxlength="50"
              :disabled="loading"
              @focus="focusedField = 'username'"
              @blur="focusedField = ''"
              autocomplete="username"
            />
            <label for="username">用户名</label>
            <div class="input-border"></div>
          </div>
        </div>

        <div class="form-group" :class="{ 'focused': focusedField === 'email', 'has-value': email }">
          <div class="input-wrapper">
            <div class="input-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                <polyline points="22,6 12,13 2,6"/>
              </svg>
            </div>
            <input
              id="email"
              v-model="email"
              type="email"
              placeholder=" "
              required
              :disabled="loading"
              @focus="focusedField = 'email'"
              @blur="focusedField = ''"
              autocomplete="email"
            />
            <label for="email">邮箱</label>
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
              placeholder=" "
              required
              minlength="6"
              :disabled="loading"
              @focus="focusedField = 'password'"
              @blur="focusedField = ''"
              autocomplete="new-password"
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

        <div class="form-group" :class="{ 'focused': focusedField === 'confirmPassword', 'has-value': confirmPassword }">
          <div class="input-wrapper">
            <div class="input-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
              </svg>
            </div>
            <input
              id="confirmPassword"
              v-model="confirmPassword"
              :type="showConfirmPassword ? 'text' : 'password'"
              placeholder=" "
              required
              :disabled="loading"
              @focus="focusedField = 'confirmPassword'"
              @blur="focusedField = ''"
              autocomplete="new-password"
            />
            <label for="confirmPassword">确认密码</label>
            <div class="input-border"></div>
            <button type="button" class="password-toggle" @click="showConfirmPassword = !showConfirmPassword" tabindex="-1">
              <svg v-if="!showConfirmPassword" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
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

        <div v-if="success" class="success-message">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
          <span>{{ success }}</span>
        </div>

        <button type="submit" class="register-btn" :disabled="loading || !isFormValid">
          <span class="btn-text">{{ loading ? '注册中...' : '创建账号' }}</span>
          <span class="btn-icon">
            <svg v-if="loading" class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10" stroke-dasharray="60" stroke-dashoffset="20"/>
            </svg>
          </span>
          <div class="btn-ripple"></div>
        </button>
      </form>

      <!-- 底部链接 -->
      <div class="register-footer">
        <p>已有账号？<router-link to="/login">立即登录</router-link></p>
      </div>
    </div>

    <!-- 底部版权 -->
    <div class="copyright">
      <p>Powered by Easy RAG</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const { register } = useAuth()

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')
const success = ref('')
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const focusedField = ref('')
const isCardHovered = ref(false)
const containerRef = ref<HTMLElement | null>(null)

const mouseGlow = reactive({ x: -200, y: -200 })

const isFormValid = computed(() => {
  return username.value.length >= 3 &&
         email.value.includes('@') &&
         password.value.length >= 6 &&
         confirmPassword.value.length >= 6
})

function handleMouseMove(e: MouseEvent) {
  if (containerRef.value) {
    const rect = containerRef.value.getBoundingClientRect()
    mouseGlow.x = e.clientX - rect.left - 150
    mouseGlow.y = e.clientY - rect.top - 150
  }
}

async function handleRegister() {
  if (!username.value || !email.value || !password.value || !confirmPassword.value) {
    error.value = '请填写所有字段'
    return
  }

  if (password.value !== confirmPassword.value) {
    error.value = '两次输入的密码不一致'
    return
  }

  loading.value = true
  error.value = ''
  success.value = ''

  try {
    await register(username.value, email.value, password.value)
    success.value = '注册成功！请等待管理员审核后登录'

    // 清空表单
    username.value = ''
    email.value = ''
    password.value = ''
    confirmPassword.value = ''

    // 3秒后跳转到登录页
    setTimeout(() => {
      router.push('/login')
    }, 3000)
  } catch (e: any) {
    error.value = e.message || '注册失败'
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

/* 使用与全局一致的温暖色调 */
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
  background: #faf8f5;
  padding: 40px 20px;
}

/* 背景渐变 */
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

/* 注册卡片 */
.register-card {
  position: relative;
  width: 100%;
  max-width: 420px;
  margin: 20px;
  padding: 40px;
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

.register-card::before {
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

.register-card.card-hovered::before {
  opacity: 1;
}

/* Logo 区域 */
.logo-section {
  text-align: center;
  margin-bottom: 32px;
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
  width: 56px;
  height: 56px;
  margin: 0 auto 12px;
  color: #c47d5e;
  animation: logoFloat 3s ease-in-out infinite;
}

@keyframes logoFloat {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-6px) rotate(5deg); }
}

.logo-icon svg {
  width: 100%;
  height: 100%;
}

.register-title {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: 28px;
  font-weight: 600;
  color: #3d3632;
  margin: 0 0 6px;
  letter-spacing: -0.02em;
}

.register-subtitle {
  font-size: 14px;
  color: #6b5f57;
  margin: 0;
  font-weight: 400;
}

/* 表单 */
.register-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.form-group {
  position: relative;
  animation: fadeInUp 0.6s ease both;
}

.form-group:nth-child(1) { animation-delay: 0.25s; }
.form-group:nth-child(2) { animation-delay: 0.3s; }
.form-group:nth-child(3) { animation-delay: 0.35s; }
.form-group:nth-child(4) { animation-delay: 0.4s; }

.input-wrapper {
  position: relative;
}

.input-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
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
  padding: 14px 44px;
  background: rgba(245, 241, 235, 0.6);
  border: 1px solid rgba(61, 54, 50, 0.1);
  border-radius: 12px;
  font-size: 14px;
  color: #3d3632;
  font-family: inherit;
  transition: all 0.3s ease;
}

.form-group input::placeholder {
  color: transparent;
}

.form-group label {
  position: absolute;
  left: 44px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 14px;
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
  right: 14px;
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
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
  font-size: 13px;
  animation: shake 0.5s ease;
}

.error-message svg {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20%, 60% { transform: translateX(-5px); }
  40%, 80% { transform: translateX(5px); }
}

/* 成功消息 */
.success-message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(122, 158, 126, 0.1);
  border: 1px solid rgba(122, 158, 126, 0.2);
  border-radius: 10px;
  color: #5d7a60;
  font-size: 13px;
  animation: fadeInUp 0.3s ease;
}

.success-message svg {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

/* 注册按钮 */
.register-btn {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #c47d5e 0%, #d4a574 100%);
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  color: white;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.3s ease;
  animation: fadeInUp 0.6s ease 0.5s both;
  margin-top: 4px;
  box-shadow: 0 4px 16px rgba(196, 125, 94, 0.25);
}

.register-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #b06a4d 0%, #c47d5e 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.register-btn:hover:not(:disabled)::before {
  opacity: 1;
}

.register-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(196, 125, 94, 0.35);
}

.register-btn:active:not(:disabled) {
  transform: translateY(0);
}

.register-btn:disabled {
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
  width: 18px;
  height: 18px;
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

.register-btn:active:not(:disabled) .btn-ripple {
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
.register-footer {
  margin-top: 24px;
  text-align: center;
  animation: fadeInUp 0.6s ease 0.6s both;
}

.register-footer p {
  font-size: 14px;
  color: #6b5f57;
  margin: 0;
}

.register-footer a {
  color: #c47d5e;
  text-decoration: none;
  font-weight: 500;
  position: relative;
  transition: color 0.3s ease;
}

.register-footer a::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0;
  height: 1px;
  background: #c47d5e;
  transition: width 0.3s ease;
}

.register-footer a:hover {
  color: #9a5a42;
}

.register-footer a:hover::after {
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
  .register-container {
    padding: 20px 16px;
  }

  .register-card {
    margin: 16px;
    padding: 28px 20px;
    border-radius: 20px;
  }

  .register-title {
    font-size: 24px;
  }

  .logo-icon {
    width: 48px;
    height: 48px;
  }

  .form-group input {
    padding: 12px 40px;
    font-size: 13px;
  }

  .input-icon {
    width: 16px;
    height: 16px;
    left: 14px;
  }

  .form-group label {
    left: 40px;
    font-size: 13px;
  }

  .form-group.focused label,
  .form-group.has-value label {
    left: 14px;
    font-size: 10px;
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
