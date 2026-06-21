<script setup lang="ts">
import {
  mdiArrowLeft,
  mdiCheck,
  mdiContentSaveOutline,
  mdiEyeOutline
} from '@mdi/js'

definePageMeta({ middleware: 'auth' })

const route = useRoute()
const store = useTemplatesStore()
const { show } = useAppToast()
const content = ref('')
const templateId = computed(() => String(route.query.template || 'default-almau-syllabus'))
const preview = ref(true)
const template = ref<Awaited<ReturnType<typeof store.getTemplateById>> | null>(null)

onMounted(async () => {
  await loadTemplate()
})

watch(templateId, async () => {
  await loadTemplate()
})

async function loadTemplate() {
  template.value = await store.getTemplateById(templateId.value)
  content.value = template.value?.content || ''
}

async function save() {
  if (!template.value) return
  await store.updateTemplate(template.value.id, content.value)
  show('Шаблон сохранен', 'success')
}

async function setActive() {
  if (!template.value) return
  const activated = await store.setActive(template.value.id)
  show(activated ? 'Шаблон назначен активным' : 'Draft шаблон нельзя активировать.', activated ? 'success' : 'error')
}
</script>

<template>
  <div class="space-y-6">
    <div>
      <v-btn variant="text" :prepend-icon="mdiArrowLeft" class="mb-3 text-none" @click="navigateTo('/templates')">
        Назад к шаблонам
      </v-btn>
      <PageHeader
        eyebrow="Template Builder v1"
        :title="template?.title || 'Template'"
        :description="template?.description || 'Frontend-only шаблон'"
      >
        <template #actions>
          <v-btn variant="tonal" :prepend-icon="mdiEyeOutline" class="text-none" @click="preview = !preview">
            {{ preview ? 'Hide preview' : 'Show preview' }}
          </v-btn>
          <v-btn variant="outlined" :prepend-icon="mdiCheck" class="text-none" @click="setActive">Set active</v-btn>
          <v-btn color="primary" :prepend-icon="mdiContentSaveOutline" class="text-none font-weight-bold" @click="save">Save</v-btn>
        </template>
      </PageHeader>
    </div>

    <v-alert type="info" variant="tonal" density="comfortable">
      Этот legacy-экран редактирует шаблон через общий store. Backend PDF-шаблон WeasyPrint пока не меняется.
    </v-alert>

    <div class="grid gap-5" :class="preview ? 'xl:grid-cols-[minmax(0,1fr)_520px]' : ''">
      <TemplateEditor v-model="content" />
      <TemplatePreview v-if="preview && template" :title="template.title" :content="content" />
    </div>
  </div>
</template>
