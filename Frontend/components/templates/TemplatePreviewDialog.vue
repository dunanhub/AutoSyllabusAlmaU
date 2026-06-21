<script setup lang="ts">
import { mdiAlertCircleOutline, mdiCheckCircleOutline, mdiClockOutline } from '@mdi/js'
import type { TemplateRecord } from '~/stores/templates'

const props = defineProps<{
  modelValue: boolean
  template: TemplateRecord | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const activeTab = ref('kz')
const opened = computed({
  get: () => props.modelValue,
  set: value => emit('update:modelValue', value)
})

const statusIcon = computed(() => {
  if (props.template?.translationStatus === 'completed') return mdiCheckCircleOutline
  if (props.template?.translationStatus === 'failed') return mdiAlertCircleOutline
  return mdiClockOutline
})

function contentFor(language: 'kz' | 'ru' | 'en') {
  if (!props.template) return ''
  if (language === 'kz') return props.template.contentKz || fallbackContent()
  if (language === 'ru') return props.template.contentRu || fallbackContent()
  return props.template.contentEn || fallbackContent()
}

function fallbackContent() {
  const status = props.template?.translationStatus
  if (status === 'failed') return `<p class="template-empty-value">${props.template?.translationError || 'Перевод завершился ошибкой.'}</p>`
  if (status === 'translating') return '<p class="template-empty-value">Перевод выполняется. Обновление появится автоматически.</p>'
  return '<p class="template-empty-value">Перевод пока не создан.</p>'
}
</script>

<template>
  <v-dialog v-model="opened" fullscreen transition="dialog-bottom-transition">
    <v-card class="template-preview-dialog">
      <v-toolbar color="surface" density="comfortable">
        <v-toolbar-title class="font-weight-black">
          {{ template?.title || 'Просмотр шаблона' }}
        </v-toolbar-title>
        <v-btn-toggle
          v-model="activeTab"
          mandatory
          density="comfortable"
          variant="outlined"
          divided
          class="mr-3 language-toggle"
        >
          <v-btn value="kz" class="text-none">Қазақша</v-btn>
          <v-btn value="ru" class="text-none">Русский</v-btn>
          <v-btn value="en" class="text-none">English</v-btn>
        </v-btn-toggle>
        <v-chip
          v-if="template"
          class="mr-3"
          size="small"
          :prepend-icon="statusIcon"
          :color="template.translationStatus === 'completed' ? 'success' : template.translationStatus === 'failed' ? 'error' : 'warning'"
          variant="tonal"
        >
          {{ template.translationStatus }}
        </v-chip>
        <v-btn variant="text" class="text-none" @click="opened = false">Закрыть</v-btn>
      </v-toolbar>

      <v-window v-model="activeTab" class="template-preview-window">
        <v-window-item value="kz">
          <div class="template-preview-paper template-prose" v-html="contentFor('kz')" />
        </v-window-item>
        <v-window-item value="ru">
          <div class="template-preview-paper template-prose" v-html="contentFor('ru')" />
        </v-window-item>
        <v-window-item value="en">
          <div class="template-preview-paper template-prose" v-html="contentFor('en')" />
        </v-window-item>
      </v-window>
    </v-card>
  </v-dialog>
</template>

<style scoped>
.template-preview-dialog {
  background: rgb(var(--v-theme-background));
}
.template-preview-window {
  overflow: auto;
  padding: 24px;
}
.language-toggle {
  flex: 0 0 auto;
}
.template-preview-paper {
  width: 794px;
  min-height: 1123px;
  max-width: 100%;
  margin: 0 auto 24px;
  background: #fff;
  color: #111827;
  padding: 64px 72px;
  box-shadow: 0 24px 70px rgba(0, 0, 0, .25);
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
.template-preview-paper :deep(.template-marker) {
  display: inline-flex;
  border: 1px solid rgba(16, 185, 129, .42);
  border-radius: 999px;
  background: rgba(16, 185, 129, .12);
  color: #047857;
  font-size: .88em;
  font-weight: 800;
  padding: 3px 9px;
}
.template-preview-paper :deep(.template-empty-value) {
  color: #64748b;
  font-style: italic;
}
</style>
