<template>
  <div class="landing">
    <!-- Nav -->
    <header class="nav" :class="{ 'nav-scrolled': scrolled }">
      <div class="nav-inner">
        <a class="nav-logo" href="#" @click.prevent="scrollToTop">
          <div class="logo-mark">
            <svg viewBox="0 0 32 32" fill="none">
              <rect x="2" y="2" width="28" height="28" rx="8" stroke="currentColor" stroke-width="2"/>
              <circle cx="12" cy="12" r="3" fill="currentColor" opacity="0.6"/>
              <circle cx="20" cy="12" r="3" fill="currentColor" opacity="0.6"/>
              <circle cx="16" cy="20" r="3" fill="currentColor"/>
              <path d="M12 12 L16 20 L20 12" stroke="currentColor" stroke-width="1.5" opacity="0.4"/>
            </svg>
          </div>
          <span class="logo-text">Easy RAG</span>
        </a>
        <nav class="nav-links">
          <a href="#features" @click.prevent="scrollTo('features')">核心能力</a>
          <a href="#how-it-works" @click.prevent="scrollTo('how-it-works')">工作流程</a>
        </nav>
        <div class="nav-actions">
          <button class="btn-ghost" @click="goLogin">登录</button>
          <button class="btn-primary-sm" @click="goRegister">免费注册</button>
        </div>
      </div>
    </header>

    <!-- Hero -->
    <section class="hero" ref="heroRef">
      <div class="hero-bg">
        <div class="hero-glow hero-glow-1"></div>
        <div class="hero-glow hero-glow-2"></div>
        <div class="hero-grid"></div>
      </div>
      <div class="hero-inner">
        <div class="hero-content">
          <div class="hero-badge">
            <span class="badge-dot"></span>
            RAG + Agent + Multi-Agent 一站式工作台
          </div>
          <h1 class="hero-title">
            让大模型
            <span class="hero-highlight">真正读懂</span>
            你的知识库
          </h1>
          <p class="hero-desc">
            从文档上传、智能检索到多智能体协同执行，Easy RAG 将知识管理、检索增强生成和 Agent 协作整合为一条完整工作流，让 AI 回答有据可依、任务可被自动执行。
          </p>
          <div class="hero-actions">
            <button class="btn-primary-lg" @click="goLogin">
              开始使用
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
            </button>
            <button class="btn-outline-lg" @click="scrollTo('features')">
              了解更多
            </button>
          </div>
          <div class="hero-metrics">
            <div class="metric">
              <span class="metric-num">3</span>
              <span class="metric-label">对话模式</span>
            </div>
            <div class="metric-div"></div>
            <div class="metric">
              <span class="metric-num">∞</span>
              <span class="metric-label">知识库容量</span>
            </div>
            <div class="metric-div"></div>
            <div class="metric">
              <span class="metric-num">100%</span>
              <span class="metric-label">私有化部署</span>
            </div>
          </div>
        </div>
        <div class="hero-visual">
          <div class="visual-stage">
            <!-- Animated pipeline illustration -->
            <div class="pipeline">
              <div class="pipe-node pipe-docs">
                <div class="node-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
                </div>
                <span>Docs</span>
              </div>
              <div class="pipe-connector">
                <div class="connector-line"></div>
                <div class="connector-pulse"></div>
              </div>
              <div class="pipe-node pipe-search">
                <div class="node-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                </div>
                <span>Retrieve</span>
              </div>
              <div class="pipe-connector">
                <div class="connector-line"></div>
                <div class="connector-pulse"></div>
              </div>
              <div class="pipe-node pipe-ai">
                <div class="node-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
                </div>
                <span>Agent</span>
              </div>
              <div class="pipe-connector">
                <div class="connector-line"></div>
                <div class="connector-pulse"></div>
              </div>
              <div class="pipe-node pipe-answer">
                <div class="node-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                </div>
                <span>Answer</span>
              </div>
            </div>
            <!-- Floating cards -->
            <div class="float-card fc-1">
              <div class="fc-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
              </div>
              <div>
                <strong>知识库管理</strong>
                <small>文档 · 分块 · 索引</small>
              </div>
            </div>
            <div class="float-card fc-2">
              <div class="fc-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
              </div>
              <div>
                <strong>实时检索</strong>
                <small>毫秒级语义召回</small>
              </div>
            </div>
            <div class="float-card fc-3">
              <div class="fc-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2z"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
              </div>
              <div>
                <strong>多智能体协同</strong>
                <small>编排 · 分工 · 执行</small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Bento -->
    <section id="features" class="section" ref="featuresRef">
      <div class="section-inner">
        <div class="section-header">
          <span class="section-kicker">核心能力</span>
          <h2>四个维度构建知识工作流</h2>
          <p>从内容沉淀到智能执行，每一步都有明确的能力边界和设计意图</p>
        </div>
        <div class="bento">
          <article class="bento-card bento-knowledge" data-reveal>
            <div class="bento-icon" style="--icon-color: #c47d5e">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
            </div>
            <h3>知识底座</h3>
            <p>知识库 → 文档 → 分块，三层结构管理内容。支持 PDF、Word、Markdown 等多种格式，分块策略可调，检索质量可控。</p>
            <ul class="bento-features">
              <li>多格式文档解析</li>
              <li>Chunk 粒度可视化</li>
              <li>启用/禁用精细控制</li>
            </ul>
          </article>
          <article class="bento-card bento-rag" data-reveal>
            <div class="bento-icon" style="--icon-color: #7a9e7e">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            </div>
            <h3>检索增强生成</h3>
            <p>先检索、再生成的稳定问答模式。回答绑定上下文来源，每一句结论都能追溯到原始文档片段。</p>
            <ul class="bento-features">
              <li>语义检索 + 重排序</li>
              <li>来源片段高亮引用</li>
              <li>多知识库联合召回</li>
            </ul>
          </article>
          <article class="bento-card bento-agentic" data-reveal>
            <div class="bento-icon" style="--icon-color: #d4a574">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
            </div>
            <h3>单智能体执行</h3>
            <p>Agent 模式自主规划任务路径，调用知识库检索、网络搜索等工具，适合需要多步骤推理的复杂问题。</p>
            <ul class="bento-features">
              <li>工具自主调用</li>
              <li>ReAct 推理链路</li>
              <li>执行轨迹可回放</li>
            </ul>
          </article>
          <article class="bento-card bento-multi" data-reveal>
            <div class="bento-icon" style="--icon-color: #b0887a">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
            </div>
            <h3>多智能体协同</h3>
            <p>Coordinator 统一调度，Retrieval → Analysis → Writing 三 Agent 分工协作，应对大规模复杂任务编排。</p>
            <ul class="bento-features">
              <li>角色专业化分工</li>
              <li>串并行灵活编排</li>
              <li>全链路过程记录</li>
            </ul>
          </article>
        </div>
      </div>
    </section>

    <!-- How It Works -->
    <section id="how-it-works" class="section section-alt" ref="howRef">
      <div class="section-inner">
        <div class="section-header">
          <span class="section-kicker">工作流程</span>
          <h2>三步构建你的 AI 知识助手</h2>
          <p>从上传文档到获得智能回答，最快只需几分钟</p>
        </div>
        <div class="steps">
          <div class="step" data-reveal>
            <div class="step-num">01</div>
            <div class="step-card">
              <div class="step-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
              </div>
              <h4>创建知识库并上传文档</h4>
              <p>新建知识库，上传 PDF / Word / Markdown 文件，系统自动解析、分块并建立向量索引</p>
            </div>
          </div>
          <div class="step-arrow">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          </div>
          <div class="step" data-reveal>
            <div class="step-num">02</div>
            <div class="step-card">
              <div class="step-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
              </div>
              <h4>选择对话模式开始提问</h4>
              <p>根据任务复杂度选择 RAG / Agentic / Multi-Agent 三种模式，系统自动匹配最优策略</p>
            </div>
          </div>
          <div class="step-arrow">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          </div>
          <div class="step" data-reveal>
            <div class="step-num">03</div>
            <div class="step-card">
              <div class="step-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
              </div>
              <h4>获得可溯源的准确回答</h4>
              <p>每次回答附带引用来源，支持查看原始文档片段，确保结论有据可依</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="section" ref="ctaRef">
      <div class="section-inner">
        <div class="cta-card" data-reveal>
          <div class="cta-bg-glow"></div>
          <h2>准备好构建你的知识工作台了吗？</h2>
          <p>登录后即可创建知识库、体验三种对话模式，探索 AI 驱动的知识管理新方式。</p>
          <div class="cta-actions">
            <button class="btn-primary-lg" @click="goLogin">
              立即开始
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
            </button>
            <button class="btn-outline-lg" @click="goRegister">注册账号</button>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
      <div class="footer-inner">
        <div class="footer-brand">
          <span class="logo-text">Easy RAG</span>
          <small>智能知识库管理系统</small>
        </div>
        <div class="footer-links">
          <a href="#features" @click.prevent="scrollTo('features')">核心能力</a>
          <a href="#how-it-works" @click.prevent="scrollTo('how-it-works')">工作流程</a>
          <a @click="goLogin">登录</a>
          <a @click="goRegister">注册</a>
        </div>
      </div>
      <div class="footer-bottom">
        <span>Powered by Easy RAG</span>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const scrolled = ref(false)

const featuresRef = ref<HTMLElement | null>(null)
const howRef = ref<HTMLElement | null>(null)
const ctaRef = ref<HTMLElement | null>(null)

const sectionMap: Record<string, HTMLElement | null> = {}

function scrollTo(id: string) {
  sectionMap[id]?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function goLogin() {
  router.push('/login')
}

function goRegister() {
  router.push('/register')
}

let revealObserver: IntersectionObserver | null = null

onMounted(() => {
  sectionMap['features'] = featuresRef.value
  sectionMap['how-it-works'] = howRef.value
  sectionMap['cta'] = ctaRef.value

  const handleScroll = () => {
    scrolled.value = window.scrollY > 60
  }
  window.addEventListener('scroll', handleScroll, { passive: true })

  revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('revealed')
        }
      })
    },
    { threshold: 0.15, rootMargin: '0px 0px -40px 0px' }
  )

  document.querySelectorAll('[data-reveal]').forEach((el) => {
    revealObserver?.observe(el)
  })
})

onBeforeUnmount(() => {
  revealObserver?.disconnect()
  revealObserver = null
})
</script>

<style scoped>
/* ========== Base ========== */
.landing {
  min-height: 100vh;
  background: #fafaf9;
  color: var(--text-primary);
  font-family: var(--font-sans);
  overflow-x: hidden;
}

/* ========== Nav ========== */
.nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: var(--z-sticky);
  padding: 16px 0;
  transition: all 0.3s ease;
}

.nav-scrolled {
  background: rgba(250, 250, 249, 0.85);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  padding: 10px 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.nav-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.nav-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: inherit;
  cursor: pointer;
}

.logo-mark {
  width: 34px;
  height: 34px;
  color: var(--color-primary);
}

.logo-mark svg {
  width: 100%;
  height: 100%;
}

.logo-text {
  font-family: var(--font-display);
  font-size: 1.25rem;
  font-weight: 600;
  letter-spacing: -0.02em;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 32px;
}

.nav-links a {
  font-size: 0.9rem;
  color: var(--text-secondary);
  text-decoration: none;
  transition: color 0.2s;
  cursor: pointer;
}

.nav-links a:hover {
  color: var(--text-primary);
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.btn-ghost {
  padding: 8px 18px;
  border: none;
  background: transparent;
  color: var(--text-primary);
  font-family: var(--font-sans);
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  border-radius: var(--radius-full);
  transition: background 0.2s;
}

.btn-ghost:hover {
  background: rgba(0, 0, 0, 0.04);
}

.btn-primary-sm {
  padding: 8px 20px;
  border: none;
  background: var(--gradient-accent);
  color: white;
  font-family: var(--font-sans);
  font-size: 0.9rem;
  font-weight: 600;
  border-radius: var(--radius-full);
  cursor: pointer;
  transition: all 0.25s var(--ease-out);
  box-shadow: 0 2px 8px rgba(196, 125, 94, 0.25);
}

.btn-primary-sm:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(196, 125, 94, 0.35);
}

/* ========== Hero ========== */
.hero {
  min-height: 100vh;
  display: flex;
  align-items: center;
  position: relative;
  padding: 120px 32px 80px;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.hero-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(120px);
  opacity: 0.35;
}

.hero-glow-1 {
  width: 600px;
  height: 600px;
  top: -200px;
  right: -100px;
  background: rgba(196, 125, 94, 0.12);
  animation: heroDrift 20s ease-in-out infinite;
}

.hero-glow-2 {
  width: 500px;
  height: 500px;
  bottom: -150px;
  left: -150px;
  background: rgba(122, 158, 126, 0.1);
  animation: heroDrift 24s ease-in-out infinite reverse;
}

@keyframes heroDrift {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -30px) scale(1.05); }
  66% { transform: translate(-20px, 20px) scale(0.96); }
}

.hero-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(0, 0, 0, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 0, 0, 0.03) 1px, transparent 1px);
  background-size: 60px 60px;
  mask-image: radial-gradient(ellipse at center, black 30%, transparent 70%);
}

.hero-inner {
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 64px;
  align-items: center;
  position: relative;
  z-index: 1;
}

.hero-content {
  max-width: 560px;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 16px;
  background: rgba(196, 125, 94, 0.08);
  border: 1px solid rgba(196, 125, 94, 0.15);
  border-radius: var(--radius-full);
  font-size: 0.82rem;
  color: var(--color-primary-dark);
  margin-bottom: 28px;
}

.badge-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-primary);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.hero-title {
  font-family: var(--font-display);
  font-size: clamp(2.8rem, 5.5vw, 4rem);
  font-weight: 600;
  line-height: 1.1;
  letter-spacing: -0.03em;
  margin: 0 0 24px;
  color: #1a1a1a;
}

.hero-highlight {
  background: linear-gradient(135deg, #c47d5e 0%, #d4a574 50%, #7a9e7e 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-desc {
  font-size: 1.08rem;
  line-height: 1.75;
  color: var(--text-secondary);
  margin: 0 0 36px;
  max-width: 480px;
}

.hero-actions {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 48px;
}

.btn-primary-lg {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 28px;
  border: none;
  background: var(--gradient-accent);
  color: white;
  font-family: var(--font-sans);
  font-size: 1rem;
  font-weight: 600;
  border-radius: var(--radius-full);
  cursor: pointer;
  transition: all 0.25s var(--ease-out);
  box-shadow: 0 4px 20px rgba(196, 125, 94, 0.3);
}

.btn-primary-lg:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(196, 125, 94, 0.4);
}

.btn-outline-lg {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 28px;
  border: 1px solid rgba(0, 0, 0, 0.12);
  background: white;
  color: var(--text-primary);
  font-family: var(--font-sans);
  font-size: 1rem;
  font-weight: 500;
  border-radius: var(--radius-full);
  cursor: pointer;
  transition: all 0.25s var(--ease-out);
}

.btn-outline-lg:hover {
  border-color: rgba(0, 0, 0, 0.2);
  background: #fafaf9;
  transform: translateY(-1px);
}

.hero-metrics {
  display: flex;
  align-items: center;
  gap: 24px;
}

.metric {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.metric-num {
  font-family: var(--font-display);
  font-size: 1.6rem;
  font-weight: 600;
  color: #1a1a1a;
}

.metric-label {
  font-size: 0.82rem;
  color: var(--text-muted);
}

.metric-div {
  width: 1px;
  height: 36px;
  background: rgba(0, 0, 0, 0.08);
}

/* ========== Hero Visual ========== */
.hero-visual {
  position: relative;
  min-height: 520px;
  display: flex;
  align-items: center;
}

.visual-stage {
  position: relative;
  width: 100%;
  padding: 48px 36px;
}

.pipeline {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  padding: 40px 24px;
  background: white;
  border-radius: 24px;
  border: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.06);
}

.pipe-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 20px;
  border-radius: 16px;
  background: #fafaf9;
  min-width: 90px;
  position: relative;
  z-index: 1;
}

.pipe-node .node-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
}

.pipe-docs .node-icon { color: #c47d5e; background: rgba(196, 125, 94, 0.1); }
.pipe-search .node-icon { color: #7a9e7e; background: rgba(122, 158, 126, 0.1); }
.pipe-ai .node-icon { color: #d4a574; background: rgba(212, 165, 116, 0.15); }
.pipe-answer .node-icon { color: #5d7a60; background: rgba(122, 158, 126, 0.12); }

.pipe-node .node-icon svg {
  width: 20px;
  height: 20px;
}

.pipe-node span {
  font-size: 0.78rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.pipe-connector {
  position: relative;
  width: 48px;
  height: 2px;
  flex-shrink: 0;
}

.connector-line {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 2px;
}

.connector-pulse {
  position: absolute;
  top: 50%;
  left: 0;
  width: 12px;
  height: 2px;
  background: var(--color-primary);
  border-radius: 2px;
  transform: translateY(-50%);
  animation: pipeFlow 2s ease-in-out infinite;
}

@keyframes pipeFlow {
  0% { left: 0; opacity: 0; }
  30% { opacity: 1; }
  70% { opacity: 1; }
  100% { left: calc(100% - 12px); opacity: 0; }
}

.pipe-connector:nth-child(2) .connector-pulse { animation-delay: 0.5s; }
.pipe-connector:nth-child(4) .connector-pulse { animation-delay: 1s; }
.pipe-connector:nth-child(6) .connector-pulse { animation-delay: 1.5s; }

/* Floating cards */
.float-card {
  position: absolute;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: white;
  border-radius: 14px;
  border: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  animation: floatCard 6s ease-in-out infinite;
}

.fc-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
}

.fc-1 {
  top: -14px;
  left: 12px;
  animation-delay: 0s;
}

.fc-1 .fc-icon { color: #c47d5e; background: rgba(196, 125, 94, 0.1); }

.fc-2 {
  bottom: -14px;
  left: 12px;
  animation-delay: 2s;
}

.fc-2 .fc-icon { color: #7a9e7e; background: rgba(122, 158, 126, 0.1); }

.fc-3 {
  top: -14px;
  right: 12px;
  animation-delay: 4s;
}

.fc-3 .fc-icon { color: #d4a574; background: rgba(212, 165, 116, 0.12); }

.float-card .fc-icon svg {
  width: 18px;
  height: 18px;
}

.float-card strong {
  display: block;
  font-size: 0.82rem;
  font-weight: 600;
  line-height: 1.3;
}

.float-card small {
  font-size: 0.72rem;
  color: var(--text-muted);
}

@keyframes floatCard {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

/* ========== Sections ========== */
.section {
  padding: 100px 32px;
}

.section-alt {
  background: #f7f6f4;
}

.section-inner {
  max-width: 1200px;
  margin: 0 auto;
}

.section-header {
  text-align: center;
  max-width: 600px;
  margin: 0 auto 64px;
}

.section-kicker {
  display: inline-block;
  font-family: var(--font-mono);
  font-size: 0.76rem;
  font-weight: 500;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--color-primary);
  margin-bottom: 16px;
}

.section-header h2 {
  font-family: var(--font-display);
  font-size: clamp(2rem, 4vw, 2.8rem);
  font-weight: 600;
  letter-spacing: -0.02em;
  color: #1a1a1a;
  margin: 0 0 14px;
}

.section-header p {
  font-size: 1.05rem;
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0;
}

/* ========== Bento Grid ========== */
.bento {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto auto;
  gap: 20px;
}

.bento-card {
  padding: 36px 32px;
  background: white;
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 24px;
  transition: all 0.35s var(--ease-out);
  position: relative;
  overflow: hidden;
}

.bento-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  opacity: 0;
  transition: opacity 0.35s;
}

.bento-knowledge::before { background: linear-gradient(90deg, #c47d5e, #d4a574); }
.bento-rag::before { background: linear-gradient(90deg, #7a9e7e, #8db091); }
.bento-agentic::before { background: linear-gradient(90deg, #d4a574, #e0bc90); }
.bento-multi::before { background: linear-gradient(90deg, #b0887a, #c47d5e); }

.bento-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.08);
  border-color: rgba(0, 0, 0, 0.08);
}

.bento-card:hover::before {
  opacity: 1;
}

.bento-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 14px;
  background: color-mix(in srgb, var(--icon-color) 10%, transparent);
  color: var(--icon-color);
  margin-bottom: 20px;
}

.bento-icon svg {
  width: 22px;
  height: 22px;
}

.bento-card h3 {
  font-family: var(--font-display);
  font-size: 1.35rem;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: #1a1a1a;
  margin: 0 0 10px;
}

.bento-card > p {
  font-size: 0.92rem;
  line-height: 1.65;
  color: var(--text-secondary);
  margin: 0 0 20px;
}

.bento-features {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.bento-features li {
  font-size: 0.8rem;
  color: var(--text-secondary);
  padding: 5px 12px;
  background: #f7f6f4;
  border-radius: var(--radius-full);
}

/* ========== Steps ========== */
.steps {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  gap: 24px;
}

.step {
  flex: 1;
  max-width: 320px;
  position: relative;
}

.step-num {
  font-family: var(--font-display);
  font-size: 3.5rem;
  font-weight: 600;
  color: rgba(0, 0, 0, 0.04);
  line-height: 1;
  margin-bottom: -20px;
  margin-left: -4px;
  pointer-events: none;
}

.step-card {
  padding: 28px 24px;
  background: white;
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 20px;
  transition: all 0.3s var(--ease-out);
}

.step-card:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.06);
  transform: translateY(-2px);
}

.step-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: rgba(196, 125, 94, 0.08);
  color: var(--color-primary);
  margin-bottom: 16px;
}

.step-icon svg {
  width: 20px;
  height: 20px;
}

.step-card h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 8px;
}

.step-card p {
  font-size: 0.88rem;
  line-height: 1.6;
  color: var(--text-secondary);
  margin: 0;
}

.step-arrow {
  display: flex;
  align-items: center;
  justify-content: center;
  padding-top: 60px;
  color: rgba(0, 0, 0, 0.15);
  flex-shrink: 0;
}

.step-arrow svg {
  width: 24px;
  height: 24px;
}

/* ========== CTA ========== */
.cta-card {
  position: relative;
  text-align: center;
  padding: 72px 48px;
  background: #1a1a1a;
  border-radius: 32px;
  overflow: hidden;
}

.cta-bg-glow {
  position: absolute;
  top: -50%;
  left: 50%;
  transform: translateX(-50%);
  width: 600px;
  height: 600px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(196, 125, 94, 0.15), transparent 70%);
  pointer-events: none;
}

.cta-card h2 {
  position: relative;
  font-family: var(--font-display);
  font-size: clamp(2rem, 4vw, 2.6rem);
  font-weight: 600;
  letter-spacing: -0.02em;
  color: white;
  margin: 0 0 16px;
}

.cta-card > p {
  position: relative;
  font-size: 1.05rem;
  color: rgba(255, 255, 255, 0.6);
  max-width: 480px;
  margin: 0 auto 36px;
  line-height: 1.6;
}

.cta-actions {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
}

.cta-card .btn-outline-lg {
  background: transparent;
  color: white;
  border-color: rgba(255, 255, 255, 0.2);
}

.cta-card .btn-outline-lg:hover {
  border-color: rgba(255, 255, 255, 0.4);
  background: rgba(255, 255, 255, 0.05);
}

/* ========== Footer ========== */
.footer {
  padding: 40px 32px 28px;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.footer-inner {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.footer-brand {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.footer-brand .logo-text {
  font-size: 1.1rem;
}

.footer-brand small {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.footer-links {
  display: flex;
  align-items: center;
  gap: 24px;
}

.footer-links a {
  font-size: 0.88rem;
  color: var(--text-secondary);
  text-decoration: none;
  cursor: pointer;
  transition: color 0.2s;
}

.footer-links a:hover {
  color: var(--text-primary);
}

.footer-bottom {
  max-width: 1200px;
  margin: 0 auto;
  padding-top: 20px;
  border-top: 1px solid rgba(0, 0, 0, 0.04);
  font-size: 0.78rem;
  color: var(--text-muted);
}

/* ========== Reveal animation ========== */
[data-reveal] {
  opacity: 0;
  transform: translateY(32px);
  transition: opacity 0.7s var(--ease-out), transform 0.7s var(--ease-out);
}

[data-reveal].revealed {
  opacity: 1;
  transform: translateY(0);
}

/* ========== Responsive ========== */
@media (max-width: 960px) {
  .nav-links {
    display: none;
  }

  .hero-inner {
    grid-template-columns: 1fr;
    gap: 48px;
  }

  .hero-visual {
    min-height: 360px;
  }

  .pipeline {
    flex-wrap: wrap;
    gap: 8px;
    padding: 24px 16px;
  }

  .pipe-connector {
    display: none;
  }

  .pipe-node {
    min-width: 70px;
    padding: 12px 14px;
  }

  .float-card {
    display: none;
  }

  .bento {
    grid-template-columns: 1fr;
  }

  .steps {
    flex-direction: column;
    align-items: stretch;
  }

  .step {
    max-width: none;
  }

  .step-arrow {
    padding-top: 0;
    transform: rotate(90deg);
  }

  .hero-metrics {
    gap: 16px;
  }

  .section {
    padding: 64px 20px;
  }

  .cta-card {
    padding: 48px 24px;
  }

  .footer-inner {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }

  .footer-links {
    flex-wrap: wrap;
    justify-content: center;
  }
}

@media (max-width: 540px) {
  .hero {
    padding: 100px 16px 48px;
  }

  .hero-title {
    font-size: 2.2rem;
  }

  .hero-actions {
    flex-direction: column;
  }

  .hero-actions button {
    width: 100%;
    justify-content: center;
  }

  .hero-metrics {
    flex-wrap: wrap;
  }

  .cta-actions {
    flex-direction: column;
  }

  .cta-actions button {
    width: 100%;
    justify-content: center;
  }

  .nav-inner {
    padding: 0 16px;
  }

  .bento-card {
    padding: 24px 20px;
  }
}
</style>
