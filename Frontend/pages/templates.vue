<script setup lang="ts">
import {
  mdiAlertCircleOutline,
  mdiArrowLeft,
  mdiContentSaveOutline,
  mdiFileDocumentPlusOutline,
  mdiPlus,
  mdiRefresh,
  mdiTranslate,
  mdiEyeOutline
} from '@mdi/js'
import TemplateEditor from '~/components/templates/TemplateEditor.vue'
import TemplatePreviewDialog from '~/components/templates/TemplatePreviewDialog.vue'
import { TEMPLATE_MARKER_BY_KEY } from '~/constants/templateMarkers'
import { createTemplateMarkerHtml, validateTemplatePayload } from '~/utils/templateMarkers'
import type { TemplateRecord } from '~/stores/templates'

definePageMeta({ middleware: 'auth' })

const route = useRoute()
const templates = useTemplatesStore()
const { show } = useAppToast()

const isCreateRoute = computed(() => route.path === '/templates/create')
const editTemplateId = computed(() => String(route.query.edit || ''))
const isEditRoute = computed(() => route.path === '/templates' && Boolean(editTemplateId.value))
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
const previewDialog = ref(false)
const previewTemplate = ref<TemplateRecord | null>(null)
const previewLoading = ref(false)
const retryingTranslationId = ref('')
const editingTemplate = computed(() => templates.templates.find(item => item.id === editTemplateId.value) || null)
let pollingTimer: ReturnType<typeof setInterval> | null = null

onMounted(async () => {
  await templates.initialize()
  loadDefaultTemplateForCreate()
  loadEditableTemplate()
  startTranslationPolling()
})

watch(editTemplateId, () => loadEditableTemplate())
watch(() => route.path, () => loadDefaultTemplateForCreate())
watch(() => templates.templates.map(item => `${item.id}:${item.translationStatus}`).join('|'), () => startTranslationPolling())
onBeforeUnmount(() => stopTranslationPolling())

function loadDefaultTemplateForCreate() {
  if (!isCreateRoute.value || savedTemplateId.value || editTemplateId.value) return
  void templates.getDefaultTemplate().then((template) => {
    if (!template) return
    content.value = template.content
    sourceLanguage.value = template.sourceLanguage || 'ru'
  })
}

function loadEditableTemplate() {
  if (!editTemplateId.value) {
    return
  }

  const template = templates.templates.find(item => item.id === editTemplateId.value)
  if (!template) {
    return
  }

  savedTemplateId.value = template.id
  title.value = template.title
  description.value = template.description
  content.value = template.content
  sourceLanguage.value = template.sourceLanguage || 'ru'
}

function validate() {
  const result = validateTemplatePayload(title.value, description.value, content.value)
  validationErrors.value = result.errors
  return result
}

async function saveTemplate() {
  return persistTemplate()
}

async function persistTemplate(options: { allowDraft?: boolean } = {}) {
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
      const existing = await templates.updateTemplate(savedTemplateId.value, {
        title: payload.title,
        description: payload.description,
        content: payload.content,
        sourceLanguage: payload.sourceLanguage
      })
      show(options.allowDraft ? 'Черновик шаблона сохранен' : 'Шаблон обновлен', 'success')
      startTranslationPolling()
      return existing
    }

    const created = await templates.createTemplate(payload)
    savedTemplateId.value = created.id
    show(options.allowDraft ? 'Черновик шаблона сохранен' : 'Шаблон сохранен', 'success')
    startTranslationPolling()
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
  const saved = await persistTemplate({ allowDraft: true })
  if (!saved) return
  validationDialog.value = false
  await navigateTo('/templates')
}

function setCurrentTemplateActive() {
  void persistTemplate().then(async (saved) => {
    if (!saved) return
    const activated = await templates.setActive(saved.id)
    show(activated ? 'Шаблон назначен Default' : 'Draft шаблон нельзя сделать Default.', activated ? 'success' : 'error')
  })
}

function templateStatus(template: { id: string, validationStatus: 'valid' | 'invalid' }) {
  if (templates.activeTemplateId === template.id) return 'Default'
  return template.validationStatus === 'valid' ? 'Готов' : 'Draft'
}

function templateStatusColor(template: { id: string, validationStatus: 'valid' | 'invalid' }) {
  const status = templateStatus(template)
  if (status === 'Default') return 'primary'
  if (status === 'Готов') return 'info'
  return 'warning'
}

function activateTemplate(id: string) {
  void templates.setActive(id).then((activated) => {
    show(activated ? 'Шаблон назначен Default' : 'Draft шаблон нельзя сделать Default. Сначала заполните название, описание и исправьте маркеры.', activated ? 'success' : 'error')
  })
}

function translationStatusText(status: TemplateRecord['translationStatus']) {
  return {
    not_translated: 'Not translated',
    translating: 'Translating',
    completed: 'Completed',
    failed: 'Failed'
  }[status]
}

function translationStatusColor(status: TemplateRecord['translationStatus']) {
  return {
    not_translated: 'default',
    translating: 'warning',
    completed: 'success',
    failed: 'error'
  }[status]
}

async function retryTranslation(template: TemplateRecord) {
  retryingTranslationId.value = template.id
  try {
    const response = await templates.translateTemplate(template.id)
    if (response?.status === 'translating') {
      show('Повторный перевод запущен', 'success')
      startTranslationPolling()
      return
    }
    show('Перевод уже обрабатывается', 'info')
  } catch (error) {
    show(error instanceof Error ? error.message : 'Не удалось повторить перевод', 'error')
  } finally {
    retryingTranslationId.value = ''
  }
}

async function openPreview(template: TemplateRecord) {
  previewLoading.value = true
  previewTemplate.value = template
  try {
    await templates.refreshTranslations(template.id)
    previewTemplate.value = templates.templates.find(item => item.id === template.id) || template
  } finally {
    previewLoading.value = false
  }
  previewDialog.value = true
  if (previewTemplate.value?.translationStatus === 'translating') startTranslationPolling()
}

function startTranslationPolling() {
  if (pollingTimer || !templates.templates.some(item => item.translationStatus === 'translating')) return
  pollingTimer = setInterval(async () => {
    const translating = templates.templates.filter(item => item.translationStatus === 'translating')
    if (!translating.length) {
      stopTranslationPolling()
      return
    }
    await Promise.allSettled(translating.map(item => templates.refreshTranslations(item.id)))
    if (!templates.templates.some(item => item.translationStatus === 'translating')) stopTranslationPolling()
  }, 3000)
}

function stopTranslationPolling() {
  if (!pollingTimer) return
  clearInterval(pollingTimer)
  pollingTimer = null
}
</script>

<template>
  <div v-if="isCreateRoute || isEditRoute" class="template-create space-y-6">
    <v-btn
      variant="text"
      :prepend-icon="mdiArrowLeft"
      class="text-none"
      @click="navigateTo('/templates')"
    >
      Назад к шаблонам
    </v-btn>

    <v-alert v-if="isEditRoute && !editingTemplate" type="warning" variant="tonal">
      Шаблон не найден. Вернитесь к списку и выберите существующий шаблон.
    </v-alert>

    <template v-else>
      <PageHeader
        :title="isEditRoute ? 'Редактирование шаблона' : 'Создание шаблона'"
        :description="isEditRoute ? 'Измените документ, маркеры автозаполнения, название и описание шаблона.' : 'Создайте Word‑подобный шаблон силлабуса с таблицами, изображениями и форматированием.'"
      >
        <template v-if="isEditRoute" #actions>
          <v-tooltip
            :disabled="editingTemplate?.validationStatus === 'valid'"
            text="Draft нельзя сделать Default. Сначала сохраните шаблон без ошибок."
          >
            <template #activator="{ props }">
              <span v-bind="props">
                <v-btn
                  variant="outlined"
                  class="text-none"
                  :disabled="editingTemplate?.validationStatus !== 'valid'"
                  @click="setCurrentTemplateActive"
                >
                  Сделать Default
                </v-btn>
              </span>
            </template>
          </v-tooltip>
        </template>
      </PageHeader>

      <v-alert
        v-if="isEditRoute && editingTemplate?.validationStatus !== 'valid'"
        type="warning"
        variant="tonal"
        density="comfortable"
      >
        Этот шаблон сейчас Draft. Его нельзя сделать Default, пока название, описание и маркеры не пройдут проверку.
      </v-alert>

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
    </template>

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

  <div v-else class="space-y-6">
    <PageHeader
      title="Шаблоны"
      description="Создавайте и редактируйте шаблоны силлабусов для дальнейшего использования в учебных дисциплинах."
    >
      <template #actions>
        <v-btn
          color="primary"
          :prepend-icon="mdiPlus"
          class="text-none font-weight-bold"
          @click="navigateTo('/templates/create')"
        >
          Создать шаблон
        </v-btn>
      </template>
    </PageHeader>

    <v-card v-if="!templates.templates.length" class="app-surface">
      <EmptyState
        title="Шаблонов пока нет"
        description="Список очищен. Создайте новый шаблон силлабуса и сохраните его как Draft или готовый шаблон."
        :icon="mdiFileDocumentPlusOutline"
      >
        <v-btn
          color="primary"
          :prepend-icon="mdiPlus"
          class="text-none font-weight-bold"
          @click="navigateTo('/templates/create')"
        >
          Создать шаблон
        </v-btn>
      </EmptyState>
    </v-card>

    <div v-else class="template-grid">
      <v-card
        v-for="template in templates.templates"
        :key="template.id"
        class="template-card"
      >
        <div class="template-card__top">
          <v-chip
            size="small"
            :color="templateStatusColor(template)"
            variant="tonal"
          >
            {{ templateStatus(template) }}
          </v-chip>
          <v-chip size="small" variant="tonal">
            {{ template.markers.length }} марк.
          </v-chip>
          <v-chip
            size="small"
            :color="translationStatusColor(template.translationStatus)"
            variant="tonal"
            :prepend-icon="mdiTranslate"
          >
            {{ translationStatusText(template.translationStatus) }}
          </v-chip>
        </div>
        <h3>{{ template.title || 'Без названия' }}</h3>
        <p>{{ template.description || 'Описание не заполнено' }}</p>
        <v-alert
          v-if="template.translationStatus === 'failed'"
          type="error"
          variant="tonal"
          density="compact"
          class="mt-3 template-card__error"
        >
          {{ template.translationError || 'Перевод не выполнен. Можно повторить попытку.' }}
        </v-alert>
        <div class="template-card__actions">
          <v-btn
            variant="tonal"
            class="text-none"
            @click="navigateTo(`/templates?edit=${encodeURIComponent(template.id)}`)"
          >
            Редактировать
          </v-btn>
          <v-btn
            variant="tonal"
            class="text-none"
            :prepend-icon="mdiEyeOutline"
            :loading="previewLoading && previewTemplate?.id === template.id"
            @click="openPreview(template)"
          >
            Просмотр
          </v-btn>
          <v-btn
            v-if="template.translationStatus === 'failed'"
            color="primary"
            variant="tonal"
            class="text-none"
            :prepend-icon="mdiRefresh"
            :loading="retryingTranslationId === template.id"
            :disabled="template.validationStatus !== 'valid'"
            @click="retryTranslation(template)"
          >
            Повторить перевод
          </v-btn>
          <v-tooltip
            :disabled="template.validationStatus === 'valid'"
            text="Draft нельзя сделать Default. Заполните название, описание и исправьте маркеры."
          >
            <template #activator="{ props }">
              <span v-bind="props">
                <v-btn
                  v-if="templates.activeTemplateId !== template.id"
                  variant="text"
                  class="text-none"
                  :disabled="template.validationStatus !== 'valid'"
                  @click="activateTemplate(template.id)"
                >
                  Сделать Default
                </v-btn>
              </span>
            </template>
          </v-tooltip>
        </div>
      </v-card>
    </div>

    <TemplatePreviewDialog
      v-model="previewDialog"
      :template="previewTemplate"
    />
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
.template-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
}
.template-card {
  border: 1px solid rgba(var(--v-border-color), .12);
  background: rgb(var(--v-theme-surface));
  padding: 18px;
}
.template-card__top {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  justify-content: flex-start;
  gap: 8px;
  margin-bottom: 14px;
}
.template-card h3 {
  color: rgb(var(--v-theme-on-surface));
  font-size: 18px;
  font-weight: 900;
}
.template-card p {
  min-height: 44px;
  margin-top: 8px;
  color: rgba(var(--v-theme-on-surface), .62);
  font-size: 13px;
  line-height: 1.55;
}
.template-card__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 18px;
}
@media (max-width: 640px) {
  .sticky-actions {
    flex-wrap: wrap;
  }
}
</style>
