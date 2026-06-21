<script setup lang="ts">
import {
  mdiArrowLeft,
  mdiBookOpenPageVariantOutline,
  mdiCheckCircleOutline,
  mdiDownloadOutline,
  mdiEyeOffOutline,
  mdiEyeOutline,
  mdiFileCogOutline,
  mdiFilePdfBox,
  mdiPencilOutline,
  mdiQrcode,
  mdiSchoolOutline,
  mdiTextBoxCheckOutline
} from '@mdi/js'
import type { CourseDetails } from '~/utils/courseSyllabus'
import type { DocumentFormat, DocumentLanguage, Syllabus } from '~/types/syllabus'
import { applyCourseDetailsToSyllabus, splitCodeAndName } from '~/utils/courseSyllabus'
import { renderTemplateWithSyllabus } from '~/utils/templateMarkers'

definePageMeta({ middleware: 'auth' })

const route = useRoute()
const store = useSyllabusStore()
const templatesStore = useTemplatesStore()
const { show } = useAppToast()

const syllabus = ref<Syllabus | null>(null)
const loading = ref(true)
const actionLoading = ref(false)
const editDialog = ref(false)
const editSubmitting = ref(false)
const qrDialog = ref(false)
const previewDrawer = ref(false)
const previewDialog = ref(false)
const previewHtml = ref('')
const previewMessage = ref('')
const pdfGenerating = ref(false)
const pdfDownloading = ref(false)
const downloadDialog = ref(false)
const selectedDownloadLanguage = ref<DocumentLanguage>('ru')
const selectedDownloadFormat = ref<DocumentFormat>('pdf')
const pdfPollInFlight = ref(false)
let pdfPollTimer: ReturnType<typeof setInterval> | null = null

const downloadLanguages = [
  { title: 'Русский', value: 'ru' },
  { title: 'Қазақша', value: 'kz' },
  { title: 'English', value: 'en' }
]

const documentFileFields: Record<DocumentFormat, Record<DocumentLanguage, keyof Syllabus>> = {
  pdf: {
    ru: 'pdfFileRu',
    kz: 'pdfFileKz',
    en: 'pdfFileEn'
  },
  docx: {
    ru: 'docxFileRu',
    kz: 'docxFileKz',
    en: 'docxFileEn'
  }
}

const names = computed(() => splitCodeAndName(syllabus.value?.titleInfo.codeAndName || ''))
const title = computed(() => syllabus.value?.titleInfo.codeAndName || 'Без названия')
const code = computed(() => names.value.courseCode || 'Код не указан')
const canPreview = computed(() => Boolean(syllabus.value?.constructorSavedAt))
const selectedTemplate = computed(() => {
  if (!syllabus.value) return null
  const id = syllabus.value.titleInfo.templateId
  return templatesStore.templates.find(item => item.id === id)
    || templatesStore.templates.find(item => item.isDefault)
    || templatesStore.templates.find(item => item.validationStatus === 'valid')
    || null
})
const templateStatus = computed(() => {
  if (!canPreview.value) return { label: 'Preview заблокирован', color: 'warning', icon: mdiEyeOffOutline }
  if (!selectedTemplate.value) return { label: 'Шаблон не выбран', color: 'error', icon: mdiEyeOffOutline }
  if (selectedTemplate.value.validationStatus !== 'valid') return { label: 'Шаблон Draft', color: 'warning', icon: mdiEyeOffOutline }
  return { label: selectedTemplate.value.isDefault ? 'Default template' : selectedTemplate.value.title, color: 'primary', icon: mdiTextBoxCheckOutline }
})
const qrValue = computed(() => {
  if (!syllabus.value) return ''
  if (syllabus.value.titleInfo.qrUrl) return syllabus.value.titleInfo.qrUrl
  if (!import.meta.client) return `/syllabuses/${syllabus.value.id}`
  return `${window.location.origin}/syllabuses/${syllabus.value.id}`
})

const pdfState = computed(() => {
  const status = syllabus.value?.pdfStatus || 'not_generated'
  if (status === 'processing') return { label: 'Документы формируются', color: 'info' }
  if (status === 'generated') return { label: 'Документы готовы', color: 'success' }
  if (status === 'failed') return { label: 'Ошибка документов', color: 'error' }
  return { label: 'Документы не созданы', color: 'default' }
})

const selectedDocumentReady = computed(() => {
  if (!syllabus.value || syllabus.value.pdfStatus !== 'generated') return false
  return isDocumentReady(syllabus.value, selectedDownloadLanguage.value, selectedDownloadFormat.value)
})

const formattedPdfDate = computed(() => {
  if (!syllabus.value?.pdfGeneratedAt) return ''
  return new Intl.DateTimeFormat('ru-RU', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(syllabus.value.pdfGeneratedAt))
})

const formattedConstructorDate = computed(() => {
  if (!syllabus.value?.constructorSavedAt) return ''
  return new Intl.DateTimeFormat('ru-RU', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(syllabus.value.constructorSavedAt))
})

function displayLanguage(value: string) {
  return value === 'MULTI' ? 'RU / KZ / EN' : value || 'RU'
}

function compactRows(rows: Array<[string, string | number | undefined | null]>) {
  return rows.filter(([, value]) => value !== undefined && value !== null && String(value).trim() !== '')
}

const courseRows = computed(() => {
  const item = syllabus.value
  if (!item) return []
  return compactRows([
    ['Код и название', item.titleInfo.codeAndName],
    ['Кредиты ECTS', item.titleInfo.credits],
    ['Всего часов', item.titleInfo.totalHours],
    ['Аудиторные часы', item.titleInfo.classroomHours],
    ['Самостоятельная работа', item.titleInfo.independentWorkHours],
    ['Пререквизиты', item.titleInfo.prerequisites],
    ['Уровень обучения', item.titleInfo.levelOfTraining],
    ['Семестр', item.titleInfo.semester],
    ['Образовательная программа', item.titleInfo.educationalProgram],
    ['Формат обучения', item.titleInfo.formatOfTraining],
    ['Время и место', item.titleInfo.timeAndPlace]
  ])
})

const teacherRows = computed(() => {
  const item = syllabus.value
  if (!item) return []
  return compactRows([
    ['ФИО', item.titleInfo.instructorName],
    ['Email', item.titleInfo.instructorEmail],
    ['Контакты', item.titleInfo.instructorContacts]
  ])
})

async function load() {
  loading.value = true
  try {
    await Promise.all([store.initialize(), templatesStore.initialize()])
    syllabus.value = await store.getSyllabusById(String(route.params.id)) || null
    if (syllabus.value?.pdfStatus === 'processing') startPdfPolling()
  } finally {
    loading.value = false
  }
}

onMounted(load)
onBeforeUnmount(stopPdfPolling)

function stopPdfPolling() {
  if (pdfPollTimer) {
    clearInterval(pdfPollTimer)
    pdfPollTimer = null
  }
  pdfGenerating.value = false
}

async function pollPdfStatus() {
  if (!syllabus.value || pdfPollInFlight.value) return
  pdfPollInFlight.value = true
  try {
    const updated = await store.getPdfStatus(syllabus.value.id)
    if (updated) syllabus.value = updated
    if (syllabus.value?.pdfStatus === 'generated') {
      stopPdfPolling()
      show('Документы RU / KZ / EN готовы', 'success')
    } else if (syllabus.value?.pdfStatus === 'failed') {
      stopPdfPolling()
      show('Ошибка генерации документов', 'error')
    }
  } catch {
    // Keep polling after temporary network errors.
  } finally {
    pdfPollInFlight.value = false
  }
}

function startPdfPolling() {
  if (pdfPollTimer) return
  pdfGenerating.value = true
  void pollPdfStatus()
  pdfPollTimer = setInterval(() => void pollPdfStatus(), 3000)
}

function isDocumentReady(item: Syllabus, language: DocumentLanguage, format: DocumentFormat) {
  if (item.documents?.[language]?.[format]) return true
  const field = documentFileFields[format][language]
  if (item[field]) return true
  return format === 'pdf' && language === 'ru' && Boolean(item.pdfFile)
}

async function saveCourse(details: CourseDetails) {
  if (!syllabus.value) return
  editSubmitting.value = true
  try {
    const payload = applyCourseDetailsToSyllabus(syllabus.value, details)
    const updated = await store.updateSyllabus(syllabus.value.id, payload)
    syllabus.value = updated
    editDialog.value = false
    show('Данные дисциплины обновлены', 'success')
  } finally {
    editSubmitting.value = false
  }
}

async function toggleStatus() {
  if (!syllabus.value) return
  const status = syllabus.value.status === 'ready' ? 'draft' : 'ready'
  actionLoading.value = true
  try {
    syllabus.value = await store.updateStatus(syllabus.value.id, status)
    show(status === 'ready' ? 'Силлабус отмечен как готовый' : 'Силлабус возвращён в черновики', 'success')
  } finally {
    actionLoading.value = false
  }
}

function buildPreviewHtml() {
  if (!syllabus.value) return false
  if (!canPreview.value) {
    previewMessage.value = 'Сначала сохраните силлабус в конструкторе.'
    previewHtml.value = ''
    return false
  }
  const template = selectedTemplate.value
  if (!template || template.validationStatus !== 'valid') {
    previewMessage.value = 'Выбранный шаблон не найден или находится в статусе Draft.'
    previewHtml.value = ''
    return false
  }
  if (syllabus.value.renderTranslationStatus === 'completed' && syllabus.value.renderedContentRu) {
    previewHtml.value = syllabus.value.renderedContentRu
  } else {
    const content = template.contentRu || template.content || template.contentKz || template.contentEn
    previewHtml.value = renderTemplateWithSyllabus(content, syllabus.value)
  }
  previewMessage.value = ''
  return true
}

function openPreview() {
  if (!buildPreviewHtml()) {
    show(previewMessage.value, 'info')
    return
  }
  previewDrawer.value = true
}

function openFullPreview() {
  if (!buildPreviewHtml()) return
  previewDialog.value = true
}

async function generatePdf() {
  if (!syllabus.value || pdfGenerating.value) return
  pdfGenerating.value = true
  try {
    const updated = await store.generatePdf(syllabus.value.id)
    if (updated) syllabus.value = updated
    startPdfPolling()
  } catch {
    show('Ошибка генерации документов', 'error')
  } finally {
    if (syllabus.value?.pdfStatus !== 'processing') pdfGenerating.value = false
  }
}

async function openDownloadDialog() {
  if (!syllabus.value || syllabus.value.pdfStatus !== 'generated' || pdfGenerating.value) return
  try {
    const updated = await store.getPdfStatus(syllabus.value.id)
    if (updated) syllabus.value = updated
  } catch {
    show('Не удалось обновить статус документов', 'error')
    return
  }
  downloadDialog.value = true
}

async function downloadSelectedDocument() {
  if (!syllabus.value || syllabus.value.pdfStatus !== 'generated' || pdfDownloading.value) return
  const updated = await store.getPdfStatus(syllabus.value.id)
  if (updated) syllabus.value = updated
  if (!selectedDocumentReady.value) {
    show('Эта версия документа ещё не готова. Нажмите «Сгенерировать документы» заново.', 'info')
    return
  }
  pdfDownloading.value = true
  try {
    await store.downloadDocument(syllabus.value.id, {
      language: selectedDownloadLanguage.value,
      format: selectedDownloadFormat.value
    })
    downloadDialog.value = false
  } catch (error) {
    console.error('Document download failed', error)
    show('Не удалось скачать документ. Проверьте, что документы сгенерированы заново.', 'error')
  } finally {
    pdfDownloading.value = false
  }
}
</script>

<template>
  <div>
    <div v-if="loading" class="py-20 text-center">
      <v-progress-circular indeterminate color="primary" />
      <p class="mt-3 text-sm text-medium-emphasis">Загрузка дисциплины...</p>
    </div>

    <template v-else-if="syllabus">
      <div class="space-y-5">
        <v-card class="course-header overflow-hidden pa-5 sm:pa-7">
          <div class="relative z-10 flex flex-col gap-6">
            <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
              <div class="min-w-0">
                <v-btn variant="text" :prepend-icon="mdiArrowLeft" class="mb-3 text-none text-white/70" @click="navigateTo('/syllabuses')">
                  Реестр дисциплин
                </v-btn>
                <h1 class="max-w-5xl text-3xl font-black tracking-[-0.04em] text-white sm:text-4xl">
                  {{ title }}
                </h1>
                <p class="mt-3 max-w-3xl text-sm leading-6 text-white/62">
                  {{ syllabus.titleInfo.educationalProgram || 'Образовательная программа не указана' }}
                  <span v-if="syllabus.titleInfo.semester"> · {{ syllabus.titleInfo.semester }}</span>
                  <span> · {{ displayLanguage(syllabus.titleInfo.languageOfEducation) }}</span>
                </p>
              </div>

              <div class="header-actions">
                <v-btn variant="tonal" :prepend-icon="mdiPencilOutline" class="text-none" @click="editDialog = true">Редактировать</v-btn>
                <v-btn color="primary" :prepend-icon="mdiBookOpenPageVariantOutline" class="text-none font-weight-bold" @click="navigateTo(`/syllabuses/${syllabus.id}/edit`)">Конструктор</v-btn>
                <v-btn variant="tonal" :prepend-icon="mdiQrcode" class="text-none" @click="qrDialog = true">QR</v-btn>
                <v-tooltip :text="canPreview ? 'Открыть предпросмотр' : 'Сначала сохраните силлабус в конструкторе'">
                  <template #activator="{ props }">
                    <span v-bind="props">
                      <v-btn variant="tonal" :prepend-icon="mdiEyeOutline" class="text-none" :disabled="!canPreview" @click="openPreview">Предпросмотр</v-btn>
                    </span>
                  </template>
                </v-tooltip>
                <v-btn variant="tonal" :loading="pdfGenerating" :disabled="pdfDownloading" :prepend-icon="mdiFileCogOutline" class="text-none" @click="generatePdf">Сгенерировать документы</v-btn>
                <v-btn variant="outlined" :loading="pdfDownloading" :disabled="syllabus.pdfStatus !== 'generated' || pdfGenerating" :prepend-icon="mdiDownloadOutline" class="text-none" @click="openDownloadDialog">Скачать</v-btn>
              </div>
            </div>

            <div class="flex flex-wrap gap-2">
              <v-chip size="small" variant="flat" color="primary">{{ code }}</v-chip>
              <SyllabusStatusBadge :status="syllabus.status" />
              <v-chip size="small" variant="tonal" :color="pdfState.color" :prepend-icon="mdiFilePdfBox">{{ pdfState.label }}</v-chip>
              <v-chip size="small" variant="tonal">{{ displayLanguage(syllabus.titleInfo.languageOfEducation) }}</v-chip>
              <v-chip size="small" variant="tonal" :color="templateStatus.color" :prepend-icon="templateStatus.icon">{{ templateStatus.label }}</v-chip>
            </div>
          </div>
        </v-card>

        <section class="grid gap-5 xl:grid-cols-[1.15fr_.85fr]">
          <div class="space-y-5">
            <v-card class="app-surface overflow-hidden">
              <div class="card-title-row">
                <v-avatar color="primary" variant="tonal"><v-icon :icon="mdiSchoolOutline" /></v-avatar>
                <div>
                  <h2>Данные курса</h2>
                  <p>Поля, которые попадут в маркеры шаблона.</p>
                </div>
              </div>
              <div class="overflow-x-auto p-4 sm:p-6">
                <table class="info-table">
                  <tbody>
                    <tr v-for="[label, value] in courseRows" :key="label">
                      <th>{{ label }}</th>
                      <td>{{ value }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </v-card>

            <v-card v-if="syllabus.courseDescription" class="app-surface pa-5 sm:pa-6">
              <div class="card-title-row compact">
                <v-avatar color="primary" variant="tonal"><v-icon :icon="mdiTextBoxCheckOutline" /></v-avatar>
                <div>
                  <h2>Описание курса</h2>
                  <p>Маркер manual.course_description</p>
                </div>
              </div>
              <p class="mt-5 whitespace-pre-line text-sm leading-7 text-medium-emphasis">{{ syllabus.courseDescription }}</p>
            </v-card>
          </div>

          <div class="space-y-5">
            <v-card v-if="teacherRows.length" class="app-surface pa-5 sm:pa-6">
              <div class="card-title-row compact">
                <v-avatar color="primary" variant="tonal"><v-icon :icon="mdiCheckCircleOutline" /></v-avatar>
                <div>
                  <h2>Преподаватель</h2>
                  <p>Автоматически берётся из пользователя системы.</p>
                </div>
              </div>
              <dl class="mt-4 grid gap-3">
                <div v-for="[label, value] in teacherRows" :key="label" class="meta-row">
                  <dt>{{ label }}</dt>
                  <dd>{{ value }}</dd>
                </div>
              </dl>
            </v-card>

            <v-card class="app-surface pa-5 sm:pa-6">
              <div class="card-title-row compact">
                <v-avatar color="primary" variant="tonal"><v-icon :icon="mdiBookOpenPageVariantOutline" /></v-avatar>
                <div>
                  <h2>Шаблон и предпросмотр</h2>
                  <p>Preview станет доступен после первого сохранения конструктора.</p>
                </div>
              </div>
              <div class="mt-4 space-y-3">
                <div class="meta-row">
                  <dt>Шаблон</dt>
                  <dd>{{ selectedTemplate?.title || 'Не выбран' }}</dd>
                </div>
                <div class="meta-row">
                  <dt>Сохранение конструктора</dt>
                  <dd>{{ formattedConstructorDate || 'Ещё не сохранялся' }}</dd>
                </div>
                <v-progress-linear :model-value="syllabus.completion" color="primary" height="8" rounded />
              </div>
              <div class="mt-5 flex flex-wrap gap-2">
                <v-btn color="primary" class="text-none" @click="navigateTo(`/syllabuses/${syllabus.id}/edit`)">Открыть конструктор</v-btn>
                <v-btn variant="outlined" class="text-none" :disabled="!canPreview" @click="openPreview">Предпросмотр</v-btn>
              </div>
            </v-card>

            <v-card class="app-surface pa-5 sm:pa-6">
              <div class="card-title-row compact">
                <v-avatar color="info" variant="tonal"><v-icon :icon="mdiQrcode" /></v-avatar>
                <div>
                  <h2>QR код</h2>
                  <p>Ссылка на страницу дисциплины.</p>
                </div>
              </div>
              <p class="mt-4 break-all rounded-xl bg-surface-bright px-3 py-2 text-[11px] text-medium-emphasis">{{ qrValue }}</p>
              <v-btn color="primary" variant="tonal" :prepend-icon="mdiQrcode" class="mt-4 text-none" @click="qrDialog = true">Показать QR</v-btn>
            </v-card>

            <v-card class="app-surface pa-5 sm:pa-6">
              <div class="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h2 class="text-base font-black">Статус документа</h2>
                  <p class="mt-1 text-xs text-medium-emphasis">PDF: {{ pdfState.label }}<span v-if="formattedPdfDate"> · {{ formattedPdfDate }}</span></p>
                  <p v-if="syllabus.pdfError" class="mt-2 text-xs text-error">{{ syllabus.pdfError }}</p>
                </div>
                <v-btn
                  size="small"
                  variant="tonal"
                  :color="syllabus.status === 'ready' ? 'warning' : 'success'"
                  :loading="actionLoading"
                  class="text-none"
                  @click="toggleStatus"
                >
                  {{ syllabus.status === 'ready' ? 'Вернуть в черновики' : 'Отметить готовым' }}
                </v-btn>
              </div>
            </v-card>
          </div>
        </section>
      </div>

      <CourseEditDialog v-model="editDialog" :syllabus="syllabus" :submitting="editSubmitting" @submit="saveCourse" />
      <QrCodeDialog v-model="qrDialog" :value="qrValue" :title="title" />
      <SyllabusPreviewDrawer
        v-model="previewDrawer"
        :syllabus="syllabus"
        :preview-html="previewHtml"
        :preview-blocked="!canPreview"
        blocked-message="Сначала сохраните силлабус в конструкторе."
        :generating="pdfGenerating"
        :downloading="pdfDownloading"
        @generate="generatePdf"
        @download="openDownloadDialog"
        @full="openFullPreview"
      />

      <v-dialog v-model="downloadDialog" max-width="520">
        <v-card class="app-surface">
          <v-card-title class="text-lg font-black">Скачать документ</v-card-title>
          <v-card-text class="space-y-4">
            <p class="text-sm text-medium-emphasis">
              Выберите язык готового PDF-документа.
            </p>
            <v-select
              v-model="selectedDownloadLanguage"
              :items="downloadLanguages"
              item-title="title"
              item-value="value"
              label="Язык"
              variant="outlined"
              density="comfortable"
            />
            <v-alert
              v-if="!selectedDocumentReady"
              type="info"
              variant="tonal"
              density="compact"
              text="Выбранная версия ещё не создана. Нажмите «Сгенерировать документы» и дождитесь статуса «Документы готовы»."
            />
          </v-card-text>
          <v-card-actions class="justify-end">
            <v-btn variant="text" class="text-none" @click="downloadDialog = false">Отмена</v-btn>
            <v-btn
              color="primary"
              :loading="pdfDownloading"
              :disabled="!selectedDocumentReady"
              :prepend-icon="mdiDownloadOutline"
              class="text-none"
              @click="downloadSelectedDocument"
            >
              Скачать
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <v-dialog v-model="previewDialog" fullscreen scrollable>
        <v-card>
          <div class="print-hidden flex items-center justify-between border-b border-white/10 bg-surface px-4 py-3">
            <div>
              <p class="text-sm font-bold">Предпросмотр силлабуса</p>
              <p class="text-xs text-medium-emphasis">{{ syllabus.titleInfo.codeAndName }}</p>
            </div>
            <v-btn variant="text" class="text-none" @click="previewDialog = false">Закрыть</v-btn>
          </div>
          <div class="a4-shell overflow-x-auto bg-[#050b14] p-3 sm:p-8">
            <div class="template-preview-paper template-prose" v-html="previewHtml" />
          </div>
        </v-card>
      </v-dialog>
    </template>

    <v-card v-else class="app-surface">
      <EmptyState title="Дисциплина не найдена" description="Документ был удалён или ссылка устарела.">
        <v-btn color="primary" @click="navigateTo('/syllabuses')">Вернуться к реестру</v-btn>
      </EmptyState>
    </v-card>
  </div>
</template>

<style scoped>
.course-header {
  position: relative;
  border: 1px solid rgba(var(--v-theme-primary), .22);
  background: radial-gradient(circle at 82% 10%, rgba(16,185,129,.24), transparent 26%),
    linear-gradient(135deg, #071a16 0%, #0b2d27 55%, #111827 100%);
}
.header-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-start;
  gap: 8px;
}
@media (min-width: 1024px) {
  .header-actions {
    max-width: 560px;
    justify-content: flex-end;
  }
}
.card-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid rgba(var(--v-border-color), .1);
  padding: 18px 20px;
}
.card-title-row.compact {
  border-bottom: 0;
  padding: 0;
}
.card-title-row h2 {
  font-size: 16px;
  font-weight: 900;
}
.card-title-row p {
  margin-top: 2px;
  color: rgba(var(--v-theme-on-surface), .62);
  font-size: 12px;
}
.info-table {
  width: 100%;
  min-width: 560px;
  border-collapse: collapse;
  font-size: 13px;
}
.info-table th,
.info-table td {
  border: 1px solid rgba(var(--v-border-color), .1);
  padding: 11px 13px;
  vertical-align: top;
}
.info-table th {
  width: 230px;
  background: rgba(var(--v-theme-primary), .06);
  color: rgba(var(--v-theme-on-surface), .78);
  font-weight: 800;
  text-align: left;
}
.meta-row {
  border: 1px solid rgba(var(--v-border-color), .08);
  border-radius: 14px;
  background: rgba(var(--v-theme-surface-bright), .62);
  padding: 10px 12px;
}
.meta-row dt {
  color: rgb(var(--v-theme-primary));
  font-size: 10px;
  font-weight: 900;
  letter-spacing: .12em;
  text-transform: uppercase;
}
.meta-row dd {
  margin-top: 4px;
  overflow-wrap: anywhere;
  color: rgba(var(--v-theme-on-surface), .78);
  font-size: 13px;
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
</style>
