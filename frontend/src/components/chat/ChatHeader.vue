<template>
  <div class="chat-header">
    <h1 class="chat-title">{{ title }}</h1>
  </div>
</template>

<script setup lang="ts">
interface Props {
  title?: string
}

withDefaults(defineProps<Props>(), {
  title: '布妞 - 您的私人助手'
})
</script>

<style scoped>
.chat-header {
  padding: var(--spacing-lg) var(--spacing-2xl);
  background-color: var(--bg-card);
  border-bottom: 1px solid var(--border-base);
}

.chat-title {
  font-size: var(--font-size-xl);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

@media (max-width: 768px) {
  .chat-header {
    padding: var(--spacing-md) var(--spacing-lg);
  }
}
</style>
