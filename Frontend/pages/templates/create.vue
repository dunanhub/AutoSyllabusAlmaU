<script setup lang="ts">
import {
  mdiAlertCircleOutline,
  mdiArrowLeft,
  mdiContentSaveOutline,
} from '@mdi/js'
import TemplateEditor from '~/components/templates/TemplateEditor.vue'
import { TEMPLATE_MARKER_BY_KEY } from '~/constants/templateMarkers'
import { createTemplateMarkerHtml, validateTemplatePayload } from '~/utils/templateMarkers'

definePageMeta({ middleware: 'auth' })

const store = useTemplatesStore()
const { show } = useAppToast()

const title = ref('Новый шаблон силлабуса')
const description = ref('')
const sourceLanguage = ref<'kz' | 'ru' | 'en'>('ru')
function marker(key: string) {
  const definition = TEMPLATE_MARKER_BY_KEY[key]
  return definition ? createTemplateMarkerHtml(definition) : ''
}

const content = ref(`
  <h1 style="text-align: center">СИЛЛАБУС ДИСЦИПЛИНЫ</h1>
  <p style="text-align: center">Шаблон для курса AlmaU</p>
  <h2>1. Титульная информация</h2>
  <table>
    <tbody>
      <tr><th>Код и название дисциплины</th><td>${marker('course.code_and_name')}</td></tr>
      <tr><th>Кредиты / часы</th><td>${marker('course.credits')} ECTS / ${marker('course.total_hours')} часов</td></tr>
      <tr><th>Преподаватель</th><td>${marker('teacher.full_name')}</td></tr>
    </tbody>
  </table>
  <h2>2. Описание курса</h2>
  <p>${marker('manual.course_description')}</p>
  <h2>3. Тематический план</h2>
  <p>${marker('table.weekly_plan')}</p>
`)
const saving = ref(false)
const savedTemplateId = ref('')
const validationDialog = ref(false)
const validationErrors = ref<string[]>([])

onMounted(async () => {
  await store.initialize()
  const template = await store.getDefaultTemplate()
  if (template) {
    content.value = template.content
    sourceLanguage.value = template.sourceLanguage || 'ru'
  }
})

function validate() {
  const result = validateTemplatePayload(title.value, description.value, content.value)
  validationErrors.value = result.errors
  return result
}

async function saveTemplate(options: { allowDraft?: boolean } = {}) {
  const validation = validate()
  if (!validation.valid && !options.allowDraft) {
    validationDialog.value = true
    show('Проверьте параметры шаблона и маркеры.', 'error')
    return null
  }

  saving.value = true
  try {
    const payload = {
      title: options.allowDraft ? title.value.trim() : title.value.trim() || 'Без названия',
      description: options.allowDraft ? description.value.trim() : description.value.trim() || 'Описание не заполнено',
      content: content.value,
      sourceLanguage: sourceLanguage.value
    }

    if (savedTemplateId.value) {
      const existing = await store.updateTemplate(savedTemplateId.value, {
        title: payload.title,
        description: payload.description,
        content: payload.content,
        sourceLanguage: payload.sourceLanguage
      })
      show(options.allowDraft ? 'Черновик шаблона сохранен' : 'Шаблон обновлен', 'success')
      return existing
    }

    const created = await store.createTemplate(payload)
    savedTemplateId.value = created.id
    show(options.allowDraft ? 'Черновик шаблона сохранен' : 'Шаблон сохранен', 'success')
    return created
  } finally {
    saving.value = false
  }
}

async function saveAndReturn() {
  const saved = await saveTemplate()
  if (!saved) return
  await navigateTo('/templates')
}

async function saveDraftAndReturn() {
  const saved = await saveTemplate({ allowDraft: true })
  if (!saved) return
  validationDialog.value = false
  await navigateTo('/templates')
}
</script>

<template>
  <div class="template-create space-y-6">
    <v-btn
      variant="text"
      :prepend-icon="mdiArrowLeft"
      class="text-none"
      @click="navigateTo('/templates')"
    >
      Назад к шаблонам
    </v-btn>

    <PageHeader
      title="Создание шаблона"
      description="Создайте Word‑подобный шаблон силлабуса с таблицами, изображениями и форматированием."
    />

    <v-card class="app-surface pa-4 sm:pa-5">
      <TemplateEditor
        v-model="content"
        v-model:title="title"
        v-model:description="description"
        v-model:source-language="sourceLanguage"
      />
    </v-card>

    <div class="sticky-actions">
      <v-btn variant="text" class="text-none" @click="navigateTo('/templates')">Отмена</v-btn>
      <v-spacer />
      <v-btn variant="tonal" :prepend-icon="mdiContentSaveOutline" class="text-none" :loading="saving" @click="saveTemplate">
        Сохранить
      </v-btn>
      <v-btn color="primary" :prepend-icon="mdiContentSaveOutline" class="text-none font-weight-bold" :loading="saving" @click="saveAndReturn">
        Сохранить и вернуться
      </v-btn>
    </div>

    <v-dialog v-model="validationDialog" max-width="620">
      <v-card class="pa-2">
        <v-card-title class="d-flex align-center ga-2 font-weight-black">
          <v-icon color="error" :icon="mdiAlertCircleOutline" />
          Шаблон не сохранён
        </v-card-title>
        <v-card-text>
          <p class="mb-3 text-medium-emphasis">
            Шаблон содержит незаполненные параметры или некорректные маркеры. Можно продолжить редактирование или сохранить текущую версию как Draft.
          </p>
          <v-list density="compact">
            <v-list-item
              v-for="error in validationErrors"
              :key="error"
              :title="error"
            />
          </v-list>
        </v-card-text>
        <v-card-actions>
          <v-btn variant="text" class="text-none" @click="validationDialog = false">Продолжить</v-btn>
          <v-spacer />
          <v-btn color="primary" class="text-none font-weight-bold" :loading="saving" @click="saveDraftAndReturn">
            Сохранить как Draft
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<style scoped>
.sticky-actions {
  position: sticky;
  bottom: 16px;
  z-index: 5;
  display: flex;
  align-items: center;
  gap: 10px;
  border: 1px solid rgba(var(--v-border-color), .12);
  border-radius: 18px;
  background: rgba(var(--v-theme-surface), .92);
  padding: 12px;
  backdrop-filter: blur(16px);
  box-shadow: 0 18px 50px rgba(0, 0, 0, .22);
}
@media (max-width: 640px) {
  .sticky-actions {
    flex-wrap: wrap;
  }
}
</style>
