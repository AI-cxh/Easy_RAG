<template>
  <nav class="breadcrumb">
    <template v-for="(item, index) in items" :key="index">
      <router-link
        v-if="item.to"
        :to="item.to"
        class="breadcrumb-item"
      >
        {{ item.label }}
      </router-link>
      <span v-else class="breadcrumb-item current">
        {{ item.label }}
      </span>
      <span v-if="index < items.length - 1" class="separator">
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/>
        </svg>
      </span>
    </template>
  </nav>
</template>

<script setup lang="ts">
interface BreadcrumbItem {
  label: string
  to?: string
}

defineProps<{
  items: BreadcrumbItem[]
}>()
</script>

<style scoped>
.breadcrumb {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--text-sm);
  margin-bottom: var(--space-4);
}

.breadcrumb-item {
  color: var(--text-secondary);
  text-decoration: none;
  transition: color var(--duration-fast);
}

.breadcrumb-item:hover {
  color: var(--color-primary);
}

.breadcrumb-item.current {
  color: var(--text-primary);
  font-weight: var(--font-medium);
}

.separator {
  display: flex;
  align-items: center;
  color: var(--text-muted);
}

.separator svg {
  width: 16px;
  height: 16px;
  fill: currentColor;
}
</style>
