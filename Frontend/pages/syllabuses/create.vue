<script setup lang="ts">
import { mdiArrowLeft } from '@mdi/js'
import type { Syllabus } from '~/types/syllabus'
import { createEmptySyllabus } from '~/utils/mockSyllabuses'

definePageMeta({ middleware: 'auth' })
const store = useSyllabusStore()
const { show } = useAppToast()
const form = ref<Syllabus>(createEmptySyllabus())
const submitting = ref(false)
const createdId = ref('')

function applyCreated(record: Syllabus) {
  createdId.value = record.id
  form.value = structuredClone(record)
}

function buildPayload(value: Syllabus, status?: 'draft' | 'ready') {
  return status ? { ...value, status } : value
}

async function autosave(value: Syllabus) {
  if (submitting.value) return
  if (!createdId.value) {
    const created = await store.createSyllabus(buildPayload(value))
    applyCreated(created)
    show('Черновик создан', 'success')
    return
  }
  const updated = await store.updateSyllabus(createdId.value, buildPayload({ ...value, id: createdId.value }))
  applyCreated(updated)
}
async function saveDraft(value: Syllabus) {
  submitting.value = true
  try {
    const saved = createdId.value
      ? await store.updateSyllabus(createdId.value, buildPayload({ ...value, id: createdId.value }, 'draft'))
      : await store.createSyllabus(buildPayload(value, 'draft'))
    applyCreated(saved)
    show('Черновик сохранён', 'success')
    await navigateTo(`/syllabuses/${saved.id}`)
  } finally {
    submitting.value = false
  }
}
async function finish(value: Syllabus) {
  submitting.value = true
  try {
    const saved = createdId.value
      ? await store.updateSyllabus(createdId.value, buildPayload({ ...value, id: createdId.value }))
      : await store.createSyllabus(buildPayload(value))
    applyCreated(saved)
    show('Силлабус сохранён', 'success')
    await navigateTo(`/syllabuses/${saved.id}`)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="space-y-6">
    <v-btn variant="text" :prepend-icon="mdiArrowLeft" class="text-none" @click="navigateTo('/syllabuses')">Реестр силлабусов</v-btn>
    <PageHeader eyebrow="Новый документ" title="Создание силлабуса" description="Заполните разделы документа. Изменения автоматически сохраняются в mock store." />
    <SyllabusForm v-model="form" mode="create" :submitting="submitting" @autosave="autosave" @save-draft="saveDraft" @finish="finish" @cancel="navigateTo('/syllabuses')" />
  </div>
</template>
