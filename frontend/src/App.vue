<template>
  <div id="app">
    <header class="app-header">
      <div class="app-header-content">
        <h1 class="app-logo">Easy RAG</h1>
        <nav class="app-nav">
          <router-link to="/chat" class="app-nav-link" active-class="active">聊天</router-link>
          <router-link to="/knowledge" class="app-nav-link" active-class="active">知识库管理</router-link>
        </nav>
      </div>
    </header>
    <main class="app-main">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { RouterView, RouterLink } from 'vue-router'
</script>
