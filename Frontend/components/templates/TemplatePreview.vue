<script setup lang="ts">
defineProps<{
  title: string
  content: string
}>()
</script>

<template>
  <v-card class="template-preview">
    <div class="border-b border-white/10 px-5 py-4">
      <p class="text-xs font-black uppercase tracking-[.16em] text-primary">Preview</p>
      <h2 class="mt-1 text-lg font-black">{{ title }}</h2>
    </div>
    <div class="preview-paper">
      <!-- eslint-disable-next-line vue/no-v-html -->
      <div class="template-prose" v-html="content" />
    </div>
  </v-card>
</template>

<style scoped>
.template-preview {
  overflow: hidden;
}
.preview-paper {
  background: #f8fafc;
  padding: 20px;
}
.preview-paper :deep(.template-prose) {
  min-height: 520px;
  border: 1px solid #d8dee8;
  background: white;
  color: #111827;
  box-shadow: 0 16px 42px rgba(15, 23, 42, .1);
}
</style>
