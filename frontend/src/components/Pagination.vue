<template>
  <div class="pagination-container">
    <div class="pagination-info">
      共 <span class="total">{{ total }}</span> 条
    </div>
    <div class="pagination-controls">
      <button
        class="btn btn-ghost btn-sm"
        :disabled="currentPage <= 1"
        @click="goToPage(currentPage - 1)"
      >
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/>
        </svg>
        上一页
      </button>

      <div class="page-numbers">
        <button
          v-for="page in displayedPages"
          :key="page"
          :class="['page-btn', { active: page === currentPage }]"
          @click="goToPage(page)"
        >
          {{ page }}
        </button>
      </div>

      <button
        class="btn btn-ghost btn-sm"
        :disabled="currentPage >= totalPages"
        @click="goToPage(currentPage + 1)"
      >
        下一页
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  total: number
  page: number
  pageSize: number
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'update:page', page: number): void
}>()

const currentPage = computed(() => props.page)
const totalPages = computed(() => Math.ceil(props.total / props.pageSize) || 1)

const displayedPages = computed(() => {
  const pages: number[] = []
  const total = totalPages.value
  const current = currentPage.value

  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    if (current <= 4) {
      for (let i = 1; i <= 5; i++) pages.push(i)
      pages.push(-1) // -1 表示省略号
      pages.push(total)
    } else if (current >= total - 3) {
      pages.push(1)
      pages.push(-1)
      for (let i = total - 4; i <= total; i++) pages.push(i)
    } else {
      pages.push(1)
      pages.push(-1)
      for (let i = current - 1; i <= current + 1; i++) pages.push(i)
      pages.push(-1)
      pages.push(total)
    }
  }

  return pages
})

const goToPage = (page: number) => {
  if (page >= 1 && page <= totalPages.value && page !== currentPage.value) {
    emit('update:page', page)
  }
}
</script>

<style scoped>
.pagination-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4) 0;
  border-top: 1px solid var(--border-subtle);
}

.pagination-info {
  font-size: var(--text-sm);
  color: var(--text-muted);
}

.pagination-info .total {
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.pagination-controls .btn svg {
  width: 16px;
  height: 16px;
  fill: currentColor;
}

.page-numbers {
  display: flex;
  align-items: center;
  gap: var(--space-1);
}

.page-btn {
  min-width: 32px;
  height: 32px;
  padding: 0 var(--space-2);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--duration-fast);
}

.page-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.page-btn.active {
  background: var(--color-primary);
  color: white;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
