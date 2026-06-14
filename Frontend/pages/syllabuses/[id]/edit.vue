<script setup lang="ts">
import { mdiArrowLeft } from '@mdi/js'
import type { Syllabus } from '~/types/syllabus'

definePageMeta({ middleware: 'auth' })
const route = useRoute()
const store = useSyllabusStore()
const { show } = useAppToast()
const syllabus = ref<Syllabus | null>(null)
const loading = ref(true)
const submitting = ref(false)

async function load() {
  loading.value = true
  try {
    await store.initialize()
    const found = await store.getSyllabusById(String(route.params.id))
    syllabus.value = found ? structuredClone(found) : null
  } finally {
    loading.value = false
  }
}

onMounted(load)

async function save(value: Syllabus, status?: 'draft' | 'ready') {
  const updated = await store.updateSyllabus(value.id, status ? { ...value, status } : value)
  syllabus.value = structuredClone(updated)
  return updated
}
async function saveDraft(value: Syllabus) {
  submitting.value = true
  try {
    const updated = await save(value, 'draft')
    show('Черновик сохранён', 'success')
    await navigateTo(`/syllabuses/${updated.id}`)
  } finally {
    submitting.value = false
  }
}
async function finish(value: Syllabus) {
  submitting.value = true
  try {
    const updated = await save(value)
    show('Силлабус сохранён', 'success')
    await navigateTo(`/syllabuses/${updated.id}`)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div>
    <div v-if="loading" class="py-20 text-center"><v-progress-circular indeterminate color="primary" /><p class="mt-3 text-sm text-medium-emphasis">Загрузка силлабуса...</p></div>
    <template v-else-if="syllabus">
      <div class="mb-6 space-y-4">
        <v-btn variant="text" :prepend-icon="mdiArrowLeft" class="text-none" @click="navigateTo(`/syllabuses/${syllabus.id}`)">Вернуться к просмотру</v-btn>
        <PageHeader eyebrow="Редактирование документа" :title="syllabus.titleInfo.codeAndName || 'Без названия'" description="Изменения автоматически сохраняются в локальном хранилище." />
      </div>
      <SyllabusForm v-model="syllabus" mode="edit" :submitting="submitting" @autosave="save" @save-draft="saveDraft" @finish="finish" @cancel="navigateTo(`/syllabuses/${syllabus.id}`)" />
    </template>
    <v-card v-else class="app-surface"><EmptyState title="Силлабус не найден" description="Документ был удалён или ссылка устарела."><v-btn color="primary" @click="navigateTo('/syllabuses')">Вернуться к списку</v-btn></EmptyState></v-card>
  </div>
</template>
