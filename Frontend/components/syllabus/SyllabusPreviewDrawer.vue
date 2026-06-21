<script setup lang="ts">
import {
  mdiClose,
  mdiDownloadOutline,
  mdiFileCogOutline,
  mdiOpenInNew
} from '@mdi/js'
import type { Syllabus } from '~/types/syllabus'

const props = withDefaults(defineProps<{
  modelValue?: boolean
  syllabus: Syllabus | null
  previewHtml?: string
  previewBlocked?: boolean
  blockedMessage?: string
  inline?: boolean
  generating?: boolean
  downloading?: boolean
}>(), {
  modelValue: false,
  inline: false,
  previewHtml: '',
  previewBlocked: false,
  blockedMessage: 'Предпросмотр недоступен.',
  generating: false,
  downloading: false
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  generate: []
  download: []
  full: []
}>()

const canDownload = computed(() => props.syllabus?.pdfStatus === 'generated')
</script>

<template>
  <div v-if="inline" class="preview-panel">
    <div class="preview-toolbar">
      <div>
        <p class="text-sm font-black">Preview</p>
        <p class="text-xs text-medium-emphasis">{{ syllabus?.titleInfo.codeAndName || 'Документ не выбран' }}</p>
      </div>
      <div class="flex flex-wrap justify-end gap-2">
        <v-btn size="small" variant="tonal" :prepend-icon="mdiOpenInNew" class="text-none" @click="emit('full')">Full</v-btn>
        <v-btn size="small" variant="tonal" :loading="generating" :prepend-icon="mdiFileCogOutline" class="text-none" @click="emit('generate')">Документы</v-btn>
        <v-btn size="small" variant="outlined" :loading="downloading" :disabled="!canDownload || generating" :prepend-icon="mdiDownloadOutline" class="text-none" @click="emit('download')">Скачать</v-btn>
      </div>
    </div>
    <div class="preview-body">
      <div v-if="previewBlocked" class="preview-empty">
        <p class="text-base font-black">Предпросмотр недоступен</p>
        <p class="mt-2 text-sm text-medium-emphasis">{{ blockedMessage }}</p>
      </div>
      <div v-else-if="previewHtml" class="template-preview-paper template-prose" v-html="previewHtml" />
      <SyllabusPreview v-else-if="syllabus" :syllabus="syllabus" />
    </div>
  </div>

  <v-navigation-drawer
    v-else
    :model-value="modelValue"
    location="right"
    temporary
    width="760"
    class="preview-drawer"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <div class="preview-toolbar sticky top-0 z-10">
      <div>
        <p class="text-sm font-black">Предпросмотр силлабуса</p>
        <p class="text-xs text-medium-emphasis">{{ syllabus?.titleInfo.codeAndName || 'Документ не выбран' }}</p>
      </div>
      <div class="flex flex-wrap justify-end gap-2">
        <v-btn size="small" variant="tonal" :prepend-icon="mdiOpenInNew" class="text-none" @click="emit('full')">Full</v-btn>
        <v-btn size="small" variant="tonal" :loading="generating" :prepend-icon="mdiFileCogOutline" class="text-none" @click="emit('generate')">Документы</v-btn>
        <v-btn size="small" variant="outlined" :loading="downloading" :disabled="!canDownload || generating" :prepend-icon="mdiDownloadOutline" class="text-none" @click="emit('download')">Скачать</v-btn>
        <v-btn size="small" variant="text" :icon="mdiClose" aria-label="Закрыть" @click="emit('update:modelValue', false)" />
      </div>
    </div>
    <div class="preview-body">
      <div v-if="previewBlocked" class="preview-empty">
        <p class="text-base font-black">Предпросмотр недоступен</p>
        <p class="mt-2 text-sm text-medium-emphasis">{{ blockedMessage }}</p>
      </div>
      <div v-else-if="previewHtml" class="template-preview-paper template-prose" v-html="previewHtml" />
      <SyllabusPreview v-else-if="syllabus" :syllabus="syllabus" />
    </div>
  </v-navigation-drawer>
</template>

<style scoped>
.preview-drawer {
  border-left: 1px solid rgba(var(--v-border-color), .14);
}
.preview-panel {
  overflow: hidden;
  border: 1px solid rgba(var(--v-border-color), .1);
  border-radius: 24px;
  background: rgb(var(--v-theme-surface));
}
.preview-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  border-bottom: 1px solid rgba(var(--v-border-color), .1);
  background: rgb(var(--v-theme-surface));
  padding: 14px 16px;
}
.preview-body {
  overflow-x: auto;
  background: #050b14;
  padding: 18px;
}
.preview-panel .preview-body {
  max-height: calc(100vh - 210px);
  overflow: auto;
}
.preview-empty {
  display: grid;
  min-height: 360px;
  place-items: center;
  border: 1px dashed rgba(var(--v-border-color), .24);
  border-radius: 18px;
  background: rgb(var(--v-theme-surface));
  padding: 32px;
  text-align: center;
}
.template-preview-paper {
  width: 794px;
  min-height: 1123px;
  max-width: 100%;
  margin: 0 auto;
  background: #fff;
  color: #111827;
  padding: 64px 72px;
  box-shadow: 0 18px 48px rgba(0, 0, 0, .35);
}
.template-preview-paper :deep(table) {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}
.template-preview-paper :deep(th),
.template-preview-paper :deep(td) {
  border: 1px solid #cbd5e1;
  overflow-wrap: anywhere;
  padding: 8px;
  vertical-align: top;
}
.template-preview-paper :deep(.template-empty-value) {
  color: #64748b;
  font-style: italic;
}
</style>
