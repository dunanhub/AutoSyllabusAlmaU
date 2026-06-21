<script setup lang="ts">
import {
  mdiArrowLeft,
  mdiCheckCircleOutline,
  mdiContentSaveOutline,
  mdiFileDocumentEditOutline,
  mdiPlus,
  mdiTrashCanOutline,
  mdiTranslate
} from '@mdi/js'
import { ALMAU_SCHOOLS, APPROVAL_PLACEHOLDER, findAlmaUSchool } from '~/constants/schools'
import type { Syllabus } from '~/types/syllabus'
import { calculateAssessmentPoints, calculateCompletion } from '~/utils/mockSyllabuses'
import { renderTemplateWithSyllabus } from '~/utils/templateMarkers'

definePageMeta({ middleware: 'auth' })

const route = useRoute()
const syllabusStore = useSyllabusStore()
const templatesStore = useTemplatesStore()
const authStore = useAuthStore()
const { show } = useAppToast()

const syllabus = ref<Syllabus | null>(null)
const loading = ref(true)
const submitting = ref(false)
const loadError = ref('')
let pollTimer: ReturnType<typeof setInterval> | undefined
let polling = false
let aiPollTimer: ReturnType<typeof setInterval> | undefined
let aiPolling = false
let aiFillCompletionToastShown = false

const EDITABLE_CONSTRUCTOR_MARKERS = new Set([
  'manual.course_goal',
  'table.learning_outcomes',
  'manual.teaching_methods',
  'approval.director_name',
  'approval.program_leader',
  'table.weekly_plan',
  'manual.teaching_philosophy',
  'list.required_literature',
  'list.additional_literature',
  'list.internet_resources',
  'table.rubric'
])

const validTemplates = computed(() => templatesStore.templates.filter(template => template.validationStatus === 'valid'))
const templateItems = computed(() => validTemplates.value.map(template => ({
  title: template.isDefault ? `${template.title} · Default` : template.title,
  subtitle: template.description,
  value: template.id
})))
const schoolItems = computed(() => ALMAU_SCHOOLS.map(school => ({
  title: school.nameRu,
  subtitle: school.nameEn,
  value: school.id
})))
const selectedTemplate = computed(() => {
  if (!syllabus.value) return null
  return validTemplates.value.find(template => template.id === syllabus.value?.titleInfo.templateId)
    || validTemplates.value.find(template => template.isDefault)
    || validTemplates.value[0]
    || null
})
const selectedSchool = computed(() => syllabus.value?.titleInfo.schoolId ? findAlmaUSchool(syllabus.value.titleInfo.schoolId) : null)
const schoolNeedsManualApproval = computed(() => {
  const school = selectedSchool.value
  return Boolean(school && (school.deanName === APPROVAL_PLACEHOLDER || school.programLeaderName === APPROVAL_PLACEHOLDER))
})
const translationCompleted = computed(() => syllabus.value?.renderTranslationStatus === 'completed')
const hasEmptyAiFillTargets = computed(() => hasEmptyAiFillBlocks())
const aiFillButtonDisabled = computed(() => (
  aiFillRunning.value
  || (syllabus.value?.aiFillStatus === 'completed' && !hasEmptyAiFillTargets.value)
))
const aiFillStatusText = computed(() => {
  const status = syllabus.value?.aiFillStatus || 'not_started'
  return {
    not_started: 'ИИ ещё не запускался',
    processing: 'ИИ заполняет пустые блоки',
    completed: 'ИИ-дозаполнение завершено',
    failed: 'Ошибка ИИ-дозаполнения'
  }[status]
})
const aiFillRunning = computed(() => syllabus.value?.aiFillStatus === 'processing')
const translationStatusText = computed(() => {
  const status = syllabus.value?.renderTranslationStatus || 'not_translated'
  return {
    not_translated: 'Не переведено',
    translating: 'Перевод выполняется',
    completed: 'Переведено',
    failed: 'Ошибка перевода'
  }[status]
})
const templateMarkerKeys = computed(() => {
  const content = selectedTemplate.value?.content || ''
  const keys = new Set<string>()
  for (const match of content.matchAll(/data-marker-key=["']([^"']+)["']/g)) keys.add(match[1])
  for (const match of content.matchAll(/\{\{\s*([a-zA-Z0-9_.]+)\s*\}\}/g)) keys.add(match[1])
  return keys
})
const missingMarkerCount = computed(() => Array.from(templateMarkerKeys.value).filter(key => shouldShowMarker(key)).length)
const translationSourceHtml = computed(() => {
  if (!syllabus.value) return ''
  if (!selectedTemplate.value) return emptyTemplateHtml()
  return renderTemplateWithSyllabus(selectedTemplate.value.contentRu || selectedTemplate.value.content, syllabus.value, {
    showPlaceholders: true,
    editableKeys: EDITABLE_CONSTRUCTOR_MARKERS
  })
})
const showCourseSection = computed(() => false)
const showTeacherSection = computed(() => false)
const showManualSection = computed(() => [
  'manual.course_goal',
  'manual.teaching_methods',
  'manual.teaching_philosophy'
].some(shouldShowMarker))
const showApprovalSection = computed(() => ['approval.director_name', 'approval.program_leader'].some(shouldShowMarker))
const showLearningOutcomes = computed(() => shouldShowMarker('table.learning_outcomes'))
const showWeeklyPlan = computed(() => shouldShowMarker('table.weekly_plan'))
const showRubric = computed(() => shouldShowMarker('table.rubric'))
const showLiteratureSection = computed(() => [
  'list.required_literature',
  'list.additional_literature',
  'list.internet_resources'
].some(shouldShowMarker))

function clonePlain<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T
}

function setSyllabusValue(value: Syllabus) {
  syllabus.value = clonePlain(value)
}

function stripRowIds<T extends Record<string, unknown>>(rows: T[]) {
  return rows.map((row) => {
    const item = { ...row }
    delete item.id
    return item
  })
}

async function load() {
  loading.value = true
  loadError.value = ''
  try {
    await templatesStore.initialize()
    const found = await syllabusStore.getSyllabusById(String(route.params.id), true)
    syllabus.value = found ? clonePlain(found) : null
    applyDefaultTemplate()
    ensureMinimumWeeklyPlan()
    if (syllabus.value?.aiFillStatus === 'failed' || syllabus.value?.aiFillStatus === 'processing') {
      await pollAiFillStatus(false)
    }
    await maybeStartAiFill()
    if (syllabus.value?.aiFillStatus === 'processing') startAiPolling()
    if (syllabus.value?.renderTranslationStatus === 'translating') startPolling()
  } catch (error) {
    const status = (error as { status?: number; statusCode?: number })?.status || (error as { statusCode?: number })?.statusCode
    loadError.value = status === 404 || status === 403
      ? 'Документ не найден или у вас нет доступа к нему.'
      : 'Не удалось загрузить конструктор. Проверьте backend API и авторизацию.'
    syllabus.value = null
  } finally {
    loading.value = false
  }
}

onMounted(load)
onBeforeUnmount(() => {
  stopPolling()
  stopAiPolling()
})

function applyDefaultTemplate() {
  if (!syllabus.value || syllabus.value.titleInfo.templateId) return
  const fallback = validTemplates.value.find(template => template.isDefault) || validTemplates.value[0]
  if (fallback) syllabus.value.titleInfo.templateId = fallback.id
}

function shouldShowMarker(key: string) {
  return templateMarkerKeys.value.has(key) && EDITABLE_CONSTRUCTOR_MARKERS.has(key)
}

function onSchoolSelected(value: string | null) {
  if (!syllabus.value || !value) return
  const school = findAlmaUSchool(value)
  if (!school) return
  syllabus.value.titleInfo.schoolId = school.id
  syllabus.value.titleInfo.schoolName = school.nameRu
  syllabus.value.signatures.preparedByName = school.deanName === APPROVAL_PLACEHOLDER ? '' : school.deanName
  syllabus.value.signatures.preparedByPosition = school.programLeaderName === APPROVAL_PLACEHOLDER ? '' : school.programLeaderName
}

function addLearningOutcome() {
  syllabus.value?.learningOutcomes.push({
    id: `lo-${Date.now()}`,
    code: `LO${(syllabus.value.learningOutcomes.length || 0) + 1}`,
    courseLearningOutcome: '',
    programLearningOutcome: '',
    description: ''
  })
}

function addWeeklyPlan() {
  syllabus.value?.thematicPlan.push({
    id: `week-${Date.now()}`,
    week: String((syllabus.value.thematicPlan.length || 0) + 1),
    topicModule: '',
    courseOutcome: '',
    questions: '',
    tasks: '',
    literature: '',
    gradeStructure: ''
  })
}

function addRubricRow() {
  syllabus.value?.assessmentSystem.push({
    id: `rubric-${Date.now()}`,
    topicModule: '',
    maxPercent: '',
    maxWeight: '',
    finalPoints: ''
  })
}

function removeRow<T>(items: T[], index: number, min = 1) {
  if (items.length <= min) return
  items.splice(index, 1)
}

function ensureMinimumWeeklyPlan() {
  if (!syllabus.value) return
  while (syllabus.value.thematicPlan.length < 16) {
    addWeeklyPlan()
  }
}

function addListItem(type: 'required' | 'additional' | 'internetResources') {
  syllabus.value?.literature[type].push('')
}

function updateAssessmentPoints() {
  if (!syllabus.value) return
  syllabus.value.assessmentSystem = syllabus.value.assessmentSystem.map(row => ({
    ...row,
    finalPoints: calculateAssessmentPoints(row.maxPercent, row.maxWeight)
  }))
}

async function save() {
  if (!syllabus.value) return
  if (!selectedTemplate.value) {
    show('Выберите валидный шаблон перед сохранением', 'error')
    return
  }

  submitting.value = true
  let savedId = ''
  try {
    const payload = buildConstructorPayload()
    const updated = await syllabusStore.patchSyllabus(syllabus.value.id, payload)
    setSyllabusValue(updated)
    savedId = updated.id
    show('Силлабус сохранён', 'success')
  } catch (error) {
    show(errorMessage(error, 'Не удалось сохранить силлабус'), 'error')
    submitting.value = false
    return
  }

  try {
    const taskRecord = await syllabusStore.translateRendered(savedId)
    if (taskRecord) setSyllabusValue(taskRecord)
    show('Перевод RU / KZ / EN запущен', 'info')
  } catch {
    show('Силлабус сохранён, но перевод не запустился', 'info')
  } finally {
    submitting.value = false
  }
  await navigateTo(`/syllabuses/${savedId}`)
}

function buildConstructorPayload(): Partial<Syllabus> {
  if (!syllabus.value || !selectedTemplate.value) return {}
  const payload = clonePlain(syllabus.value)
  payload.titleInfo.templateId = selectedTemplate.value.id
  payload.constructorSavedAt = payload.constructorSavedAt || new Date().toISOString()
  payload.completion = calculateCompletion(payload)

  return {
    titleInfo: payload.titleInfo,
    courseGoal: payload.courseGoal,
    teachingPhilosophy: payload.teachingPhilosophy,
    learningOutcomes: stripRowIds(payload.learningOutcomes) as Syllabus['learningOutcomes'],
    thematicPlan: stripRowIds(payload.thematicPlan) as Syllabus['thematicPlan'],
    assessmentSystem: stripRowIds(payload.assessmentSystem) as Syllabus['assessmentSystem'],
    literature: payload.literature,
    coursePolicy: payload.coursePolicy,
    signatures: payload.signatures,
    constructorSavedAt: payload.constructorSavedAt,
    completion: payload.completion
  }
}

async function maybeStartAiFill() {
  if (!syllabus.value) return
  if (syllabus.value.aiFillStatus === 'processing') return
  if (syllabus.value.aiFillStatus === 'completed') return
  if (syllabus.value.aiFillStatus === 'failed') return
  if (!hasEmptyAiFillBlocks()) return
  await runAiFill(false)
}

async function runAiFill(showToast = true) {
  if (!syllabus.value || aiFillRunning.value) return
  aiFillCompletionToastShown = false
  const current = await pollAiFillStatus(false)
  if (current?.aiFillStatus === 'processing') {
    if (showToast) show('ИИ уже заполняет пустые блоки', 'info')
    startAiPolling()
    return
  }
  if (!hasEmptyAiFillBlocks()) {
    if (showToast) show('Пустых блоков для ИИ-дозаполнения нет', 'info')
    return
  }

  try {
    if (!authStore.initialized) await authStore.initialize()
    const updated = await syllabusStore.aiFill(syllabus.value.id)
    if (updated) setSyllabusValue(updated)
    if (showToast) show('ИИ запущен', 'info')
  } catch (error) {
    if (showToast) show(errorMessage(error, 'Не удалось запустить ИИ-дозаполнение'), 'error')
    return
  }

  const status = await pollAiFillStatus(false)
  if (status?.aiFillStatus === 'processing') startAiPolling()
}

function hasEmptyAiFillBlocks() {
  if (!syllabus.value) return false
  return [
    !String(syllabus.value.courseGoal || '').trim(),
    !String(syllabus.value.coursePolicy.masteringDiscipline || '').trim(),
    !String(syllabus.value.teachingPhilosophy || '').trim(),
    rowsEmpty(syllabus.value.learningOutcomes, ['code', 'courseLearningOutcome', 'programLearningOutcome', 'description']),
    syllabus.value.thematicPlan.length < 16 || rowsEmpty(syllabus.value.thematicPlan, ['topicModule', 'courseOutcome', 'questions', 'tasks', 'literature', 'gradeStructure']),
    rowsEmpty(syllabus.value.assessmentSystem, ['topicModule', 'maxPercent', 'maxWeight', 'finalPoints']),
    !syllabus.value.literature.required.some(item => item.trim()),
    !syllabus.value.literature.additional.some(item => item.trim()),
    !syllabus.value.literature.internetResources.some(item => item.trim())
  ].some(Boolean)
}

function rowsEmpty<T extends object>(rows: T[], fields: string[]) {
  return !rows.some(row => fields.some(field => String((row as Record<string, unknown>)[field] || '').trim()))
}

function startAiPolling() {
  stopAiPolling()
  aiPollTimer = setInterval(async () => {
    void pollAiFillStatus(true)
  }, 3000)
  void pollAiFillStatus(true)
}

async function pollAiFillStatus(showMessages = true) {
  if (!syllabus.value || aiPolling) return syllabus.value
  aiPolling = true
  try {
    const updated = await syllabusStore.getAiFillStatus(syllabus.value.id)
    if (updated) {
      setSyllabusValue(updated)
      ensureMinimumWeeklyPlan()
    }
    if (updated?.aiFillStatus === 'completed') {
      if (showMessages && !aiFillCompletionToastShown) {
        show('ИИ заполнил пустые блоки', 'success')
        aiFillCompletionToastShown = true
      }
      stopAiPolling()
    }
    if (updated?.aiFillStatus === 'failed') {
      if (showMessages) show('ИИ-дозаполнение завершилось ошибкой', 'error')
      stopAiPolling()
    }
    return updated || syllabus.value
  } catch {
    // Keep polling on temporary network errors.
    return syllabus.value
  } finally {
    aiPolling = false
  }
}

function errorMessage(error: unknown, fallback: string) {
  const data = (error as { data?: unknown })?.data
  return extractErrorText(data) || fallback
}

function extractErrorText(value: unknown): string {
  if (!value) return ''
  if (typeof value === 'string') return value
  if (Array.isArray(value)) return value.map(extractErrorText).filter(Boolean).join(', ')
  if (typeof value === 'object') {
    const record = value as Record<string, unknown>
    for (const key of ['detail', 'message', 'error', 'nonFieldErrors', 'non_field_errors']) {
      const text = extractErrorText(record[key])
      if (text) return text
    }
    return Object.entries(record)
      .map(([key, item]) => {
        const text = extractErrorText(item)
        return text ? `${key}: ${text}` : ''
      })
      .filter(Boolean)
      .join('; ')
  }
  return ''
}

function stopAiPolling() {
  if (aiPollTimer) clearInterval(aiPollTimer)
  aiPollTimer = undefined
}

function startPolling() {
  stopPolling()
  pollTimer = setInterval(async () => {
    if (!syllabus.value || polling) return
    polling = true
    try {
      const updated = await syllabusStore.getRenderTranslationStatus(syllabus.value.id)
      if (updated) setSyllabusValue(updated)
      if (updated?.renderTranslationStatus === 'completed') {
        show('Перевод на RU / KZ / EN завершён', 'success')
        stopPolling()
      }
      if (updated?.renderTranslationStatus === 'failed') {
        show('Перевод завершился ошибкой', 'error')
        stopPolling()
      }
    } catch {
      // Keep polling on temporary network errors.
    } finally {
      polling = false
    }
  }, 3000)
}

function stopPolling() {
  if (pollTimer) clearInterval(pollTimer)
  pollTimer = undefined
}

function emptyTemplateHtml() {
  return '<div class="template-empty-value">Выберите валидный шаблон силлабуса.</div>'
}
</script>

<template>
  <div>
    <div v-if="loading" class="py-20 text-center">
      <v-progress-circular indeterminate color="primary" />
      <p class="mt-3 text-sm text-medium-emphasis">Загрузка конструктора...</p>
    </div>

    <template v-else-if="syllabus">
      <div class="constructor-header mb-5">
        <div class="constructor-title">
          <v-btn variant="text" :prepend-icon="mdiArrowLeft" class="mb-3 text-none" @click="navigateTo(`/syllabuses/${syllabus.id}`)">
            Назад к дисциплине
          </v-btn>
          <p class="page-eyebrow">Конструктор силлабуса</p>
          <h1 class="mt-1 text-3xl font-black">{{ syllabus.titleInfo.codeAndName || 'Без названия' }}</h1>
          <p class="mt-2 max-w-3xl text-sm text-medium-emphasis">
            Слева показаны только незаполненные маркеры выбранного шаблона. Справа всегда отображается русская A4-версия.
          </p>
        </div>
        <div class="constructor-actions">
          <div class="status-chip-row">
            <v-chip size="small" :color="aiFillRunning ? 'warning' : syllabus.aiFillStatus === 'failed' ? 'error' : 'info'" variant="tonal">
              {{ aiFillStatusText }}
            </v-chip>
            <v-chip size="small" :color="translationCompleted ? 'success' : syllabus.renderTranslationStatus === 'failed' ? 'error' : 'primary'" variant="tonal">
              <v-icon :icon="translationCompleted ? mdiCheckCircleOutline : mdiTranslate" start />
              {{ translationStatusText }}
            </v-chip>
          </div>
          <div class="action-button-row">
            <v-btn
              variant="tonal"
              color="primary"
              :loading="aiFillRunning"
              :disabled="aiFillButtonDisabled"
              class="text-none font-weight-bold"
              @click="runAiFill(true)"
            >
              Заполнить пустые блоки ИИ
            </v-btn>
            <v-btn color="primary" :loading="submitting" :prepend-icon="mdiContentSaveOutline" class="text-none font-weight-bold" @click="save">
              Сохранить
            </v-btn>
          </div>
        </div>
      </div>

      <div class="constructor-grid">
        <aside class="constructor-panel">
          <v-card class="app-surface overflow-hidden">
            <div class="fields-card-head border-b border-white/10 bg-surface-bright">
              <div class="flex items-center gap-3">
                <v-avatar size="40" color="primary" variant="tonal"><v-icon :icon="mdiFileDocumentEditOutline" /></v-avatar>
                <div>
                  <h2 class="text-sm font-black">Оставшиеся поля</h2>
                  <p class="text-xs text-medium-emphasis">Draft-шаблоны скрыты из списка</p>
                </div>
              </div>
            </div>

            <div class="space-y-4 p-4">
              <v-select
                v-model="syllabus.titleInfo.templateId"
                :items="templateItems"
                item-title="title"
                item-value="value"
                label="Шаблон силлабуса"
                :loading="templatesStore.loading"
                variant="outlined"
                density="comfortable"
                hide-details="auto"
              />

              <v-alert v-if="missingMarkerCount === 0" type="success" variant="tonal" density="comfortable">
                В этом шаблоне нет ручных полей для заполнения. Данные отображаются в A4-preview.
              </v-alert>

              <v-alert v-if="syllabus.aiFillStatus === 'failed'" type="error" variant="tonal" density="comfortable">
                {{ syllabus.aiFillError || 'ИИ-дозаполнение завершилось ошибкой. Проверьте Gemini API key и backend logs.' }}
              </v-alert>

              <section v-if="showCourseSection" class="form-section">
                <h3>Курс</h3>
                <BaseInput v-if="shouldShowMarker('course.code_and_name')" v-model="syllabus.titleInfo.codeAndName" label="Код и название" />
                <div class="grid gap-3 sm:grid-cols-2">
                  <BaseInput v-if="shouldShowMarker('course.credits')" v-model="syllabus.titleInfo.credits" label="ECTS" />
                  <BaseInput v-if="shouldShowMarker('course.total_hours')" v-model="syllabus.titleInfo.totalHours" label="Всего часов" />
                  <BaseInput v-if="shouldShowMarker('course.classroom_hours')" v-model="syllabus.titleInfo.classroomHours" label="Аудиторные часы" />
                  <BaseInput v-if="shouldShowMarker('course.independent_hours')" v-model="syllabus.titleInfo.independentWorkHours" label="Самостоятельные часы" />
                </div>
                <BaseTextarea v-if="shouldShowMarker('course.prerequisites')" v-model="syllabus.titleInfo.prerequisites" label="Пререквизиты" />
                <div class="grid gap-3 sm:grid-cols-2">
                  <BaseInput v-if="shouldShowMarker('course.level')" v-model="syllabus.titleInfo.levelOfTraining" label="Уровень" />
                  <BaseInput v-if="shouldShowMarker('course.semester')" v-model="syllabus.titleInfo.semester" label="Семестр" />
                </div>
                <BaseInput v-if="shouldShowMarker('course.program')" v-model="syllabus.titleInfo.educationalProgram" label="Программа" />
                <BaseInput v-if="shouldShowMarker('course.format')" v-model="syllabus.titleInfo.formatOfTraining" label="Формат обучения" />
                <BaseTextarea v-if="shouldShowMarker('course.time_place')" v-model="syllabus.titleInfo.timeAndPlace" label="Время и место" />
              </section>

              <section v-if="showTeacherSection" class="form-section">
                <h3>Преподаватель</h3>
                <BaseInput v-if="shouldShowMarker('teacher.full_name')" v-model="syllabus.titleInfo.instructorName" label="ФИО" />
                <BaseInput v-if="shouldShowMarker('teacher.email')" v-model="syllabus.titleInfo.instructorEmail" type="email" label="Email" />
              </section>

              <section v-if="showManualSection" class="form-section">
                <h3>Ручной ввод</h3>
                <BaseTextarea v-if="shouldShowMarker('manual.course_description')" v-model="syllabus.courseDescription" label="Описание курса" :rows="5" />
                <BaseTextarea v-if="shouldShowMarker('manual.course_goal')" v-model="syllabus.courseGoal" label="Цель курса" :rows="4" />
                <BaseTextarea v-if="shouldShowMarker('manual.teaching_methods')" v-model="syllabus.coursePolicy.masteringDiscipline" label="Методы обучения" :rows="4" />
                <BaseTextarea v-if="shouldShowMarker('manual.teaching_philosophy')" v-model="syllabus.teachingPhilosophy" label="Философия преподавания" :rows="4" />
              </section>

              <section v-if="showApprovalSection" class="form-section">
                <h3>Утверждение</h3>
                <v-select
                  v-model="syllabus.titleInfo.schoolId"
                  :items="schoolItems"
                  item-title="title"
                  item-value="value"
                  label="Школа AlmaU"
                  variant="outlined"
                  density="comfortable"
                  hide-details="auto"
                  @update:model-value="onSchoolSelected"
                />
                <v-alert v-if="schoolNeedsManualApproval" type="warning" variant="tonal" density="comfortable">
                  На официальных страницах AlmaU не удалось надёжно подтвердить ФИО директора и program leader для выбранной школы.
                  Заполните эти два поля вручную, чтобы они попали в A4-документ.
                </v-alert>
                <BaseInput v-if="schoolNeedsManualApproval && shouldShowMarker('approval.director_name')" v-model="syllabus.signatures.preparedByName" label="Директор / декан" />
                <BaseInput v-if="schoolNeedsManualApproval && shouldShowMarker('approval.program_leader')" v-model="syllabus.signatures.preparedByPosition" label="Руководитель программы" />
              </section>

              <section v-if="showLearningOutcomes" class="form-section">
                <h3>Результаты обучения</h3>
                <div v-for="(row, index) in syllabus.learningOutcomes" :key="row.id || index" class="mini-row">
                  <BaseInput v-model="row.code" label="Код" />
                  <BaseTextarea v-model="row.courseLearningOutcome" label="Результат курса" :rows="2" />
                  <BaseTextarea v-model="row.programLearningOutcome" label="Результат программы" :rows="2" />
                  <BaseTextarea v-model="row.description" label="Описание" :rows="2" />
                  <v-btn icon size="small" variant="text" color="error" class="row-delete" :disabled="syllabus.learningOutcomes.length <= 1" @click="removeRow(syllabus.learningOutcomes, index)">
                    <v-icon :icon="mdiTrashCanOutline" />
                  </v-btn>
                </div>
                <v-btn block size="small" variant="tonal" color="primary" :prepend-icon="mdiPlus" class="text-none add-row-button" @click="addLearningOutcome">Добавить</v-btn>
              </section>

              <section v-if="showWeeklyPlan" class="form-section">
                <h3>Недельный план</h3>
                <div v-for="(row, index) in syllabus.thematicPlan" :key="row.id || index" class="mini-row">
                  <div class="grid gap-3 sm:grid-cols-[90px_1fr]">
                    <BaseInput v-model="row.week" label="Неделя" />
                    <BaseTextarea v-model="row.topicModule" label="Тема / модуль" :rows="2" />
                  </div>
                  <BaseTextarea v-model="row.courseOutcome" label="Результат" :rows="2" />
                  <BaseTextarea v-model="row.questions" label="Вопросы" :rows="2" />
                  <BaseTextarea v-model="row.tasks" label="Задания" :rows="2" />
                  <v-btn icon size="small" variant="text" color="error" class="row-delete" :disabled="syllabus.thematicPlan.length <= 1" @click="removeRow(syllabus.thematicPlan, index)">
                    <v-icon :icon="mdiTrashCanOutline" />
                  </v-btn>
                </div>
                <v-btn block size="small" variant="tonal" color="primary" :prepend-icon="mdiPlus" class="text-none add-row-button" @click="addWeeklyPlan">Добавить</v-btn>
              </section>

              <section v-if="showRubric" class="form-section">
                <h3>Рубрика / оценивание</h3>
                <div v-for="(row, index) in syllabus.assessmentSystem" :key="row.id || index" class="mini-row">
                  <BaseTextarea v-model="row.topicModule" label="Компонент" :rows="2" />
                  <div class="grid gap-3 sm:grid-cols-3">
                    <BaseInput v-model="row.maxPercent" label="Макс. %" @input="updateAssessmentPoints" />
                    <BaseInput v-model="row.maxWeight" label="Вес" @input="updateAssessmentPoints" />
                    <BaseInput v-model="row.finalPoints" label="Баллы" />
                  </div>
                  <v-btn icon size="small" variant="text" color="error" class="row-delete" :disabled="syllabus.assessmentSystem.length <= 1" @click="removeRow(syllabus.assessmentSystem, index)">
                    <v-icon :icon="mdiTrashCanOutline" />
                  </v-btn>
                </div>
                <v-btn block size="small" variant="tonal" color="primary" :prepend-icon="mdiPlus" class="text-none add-row-button" @click="addRubricRow">Добавить</v-btn>
              </section>

              <section v-if="showLiteratureSection" class="form-section">
                <h3>Литература</h3>
                <div v-for="type in ['required', 'additional', 'internetResources']" :key="type" class="space-y-2">
                  <template v-if="shouldShowMarker(type === 'required' ? 'list.required_literature' : type === 'additional' ? 'list.additional_literature' : 'list.internet_resources')">
                    <div class="literature-subhead">
                      <p class="text-xs font-black uppercase tracking-[.12em] text-medium-emphasis">
                        {{ type === 'required' ? 'Обязательная' : type === 'additional' ? 'Дополнительная' : 'Интернет-ресурсы' }}
                      </p>
                    </div>
                    <div v-for="(_, index) in syllabus.literature[type as 'required' | 'additional' | 'internetResources']" :key="`${type}-${index}`" class="mini-row literature-row">
                      <BaseTextarea v-model="syllabus.literature[type as 'required' | 'additional' | 'internetResources'][index]" label="Источник" :rows="2" />
                      <v-btn icon size="small" variant="text" color="error" class="row-delete" :disabled="syllabus.literature[type as 'required' | 'additional' | 'internetResources'].length <= 1" @click="removeRow(syllabus.literature[type as 'required' | 'additional' | 'internetResources'], index)">
                        <v-icon :icon="mdiTrashCanOutline" />
                      </v-btn>
                    </div>
                    <v-btn block size="small" variant="tonal" color="primary" :prepend-icon="mdiPlus" class="text-none add-row-button" @click="addListItem(type as 'required' | 'additional' | 'internetResources')">Добавить</v-btn>
                  </template>
                </div>
              </section>
            </div>
          </v-card>
        </aside>

        <section class="preview-panel">
          <v-card class="app-surface sticky-preview overflow-hidden" style="border: 1px solid rgb(255 255 255 / 14%)">
            <div class="flex flex-wrap items-center justify-between gap-3 border-b border-white/10 bg-surface-bright px-4 py-3">
              <div>
                <h2 class="text-sm font-black">A4 Preview · Русская версия</h2>
                <p class="text-xs text-medium-emphasis">{{ selectedTemplate?.title || 'Шаблон не выбран' }}</p>
              </div>
              <v-chip size="small" color="primary" variant="tonal">RU</v-chip>
            </div>
            <div class="preview-scroll">
              <article class="template-preview-paper template-prose" v-html="translationSourceHtml" />
            </div>
            <div v-if="syllabus.renderTranslationStatus === 'failed'" class="border-t border-error/30 px-4 py-3 text-sm text-error">
              {{ syllabus.renderTranslationError || 'Не удалось выполнить перевод.' }}
            </div>
          </v-card>
        </section>
      </div>
    </template>

    <v-card v-else class="app-surface">
      <EmptyState title="Силлабус не найден" :description="loadError || 'Документ был удалён или ссылка устарела.'">
        <v-btn color="primary" @click="navigateTo('/syllabuses')">Вернуться к списку</v-btn>
      </EmptyState>
    </v-card>
  </div>
</template>

<style scoped>
.constructor-grid {
  display: grid;
  gap: 20px;
  grid-template-columns: minmax(320px, 440px) minmax(0, 1fr);
}

.constructor-header {
  display: grid;
  align-items: start;
  gap: 20px;
  grid-template-columns: minmax(0, 1fr) auto;
}

.constructor-title {
  min-width: 0;
}

.constructor-panel,
.preview-panel {
  min-width: 0;
}

.constructor-actions {
  display: grid;
  justify-items: end;
  gap: 10px;
  width: max-content;
  max-width: min(100%, 560px);
  margin-left: auto;
}

.status-chip-row,
.action-button-row {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.status-chip-row {
  border: 1px solid rgba(var(--v-border-color), .12);
  border-radius: 999px;
  background: rgba(var(--v-theme-surface-bright), .48);
  padding: 5px;
}

.fields-card-head {
  padding: 14px 16px;
}

@media (max-width: 1700px) and (min-width: 1181px) {
  .constructor-grid {
    gap: 24px;
    grid-template-columns: minmax(280px, 360px) minmax(0, 1fr);
  }

  .fields-card-head {
    padding: 12px 14px;
  }

  .fields-card-head :deep(.v-avatar) {
    width: 36px !important;
    height: 36px !important;
  }

  .constructor-panel :deep(.v-field) {
    font-size: 14px;
  }

  .constructor-panel :deep(.form-label) {
    font-size: 11px;
  }

  .form-section {
    border-radius: 16px;
    padding: 14px;
  }

  .mini-row {
    border-radius: 14px;
    padding: 12px 46px 12px 12px;
  }
}

.sticky-preview {
  position: sticky;
  top: 88px;
}

.preview-scroll {
  max-height: calc(100vh - 210px);
  overflow: auto;
  background: rgb(var(--v-theme-background));
  padding: 28px;
}

.template-preview-paper {
  width: min(100%, 794px);
  min-height: 1123px;
  margin: 0 auto;
  padding: 72px;
  background: #fff;
  color: #111827;
  box-shadow: 0 22px 70px rgba(0, 0, 0, .34);
}

.template-prose :deep(table) {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

.template-prose :deep(th),
.template-prose :deep(td) {
  border: 1px solid #cbd5e1;
  padding: 8px;
  vertical-align: top;
  word-break: break-word;
}

.template-prose :deep(img) {
  max-width: 100%;
  height: auto;
}

.template-prose :deep(.template-empty-value) {
  color: #64748b;
  font-style: italic;
}

.template-prose :deep(.template-preview-marker) {
  display: inline-flex;
  max-width: 100%;
  align-items: center;
  border: 1px dashed #10b981;
  border-radius: 999px;
  background: #ecfdf5;
  color: #047857;
  font-size: 12px;
  font-weight: 800;
  line-height: 1.25;
  padding: 4px 10px;
  vertical-align: baseline;
  white-space: normal;
}

.template-prose :deep(.template-preview-marker--table) {
  border-color: #3b82f6;
  background: #eff6ff;
  color: #1d4ed8;
}

.template-prose :deep(.template-preview-marker--list) {
  border-color: #14b8a6;
  background: #f0fdfa;
  color: #0f766e;
}

.template-prose :deep(.template-preview-marker--image) {
  border-color: #8b5cf6;
  background: #f5f3ff;
  color: #6d28d9;
}

.form-section {
  display: grid;
  gap: 12px;
  border: 1px solid rgba(var(--v-border-color), .14);
  border-radius: 18px;
  background:
    linear-gradient(180deg, rgba(var(--v-theme-surface-bright), .72), rgba(var(--v-theme-surface-bright), .38));
  padding: 16px;
}

.form-section h3 {
  margin-bottom: 2px;
  color: rgb(var(--v-theme-on-surface));
  font-size: 13px;
  font-weight: 900;
  letter-spacing: .08em;
  text-transform: uppercase;
}

.constructor-panel :deep(.form-label) {
  margin-bottom: 8px;
  color: rgba(var(--v-theme-on-surface), .68);
  font-size: 12px;
  font-weight: 800;
}

.constructor-panel :deep(.form-textarea) {
  width: 100%;
  min-height: 118px;
  max-height: 260px;
  resize: vertical;
}

.mini-row {
  position: relative;
  display: grid;
  gap: 10px;
  border: 1px solid rgba(var(--v-border-color), .12);
  border-radius: 16px;
  padding: 14px 52px 14px 14px;
  background: rgba(var(--v-theme-surface-bright), .42);
}

.literature-row {
  margin-top: 8px;
}

.row-delete {
  position: absolute;
  right: 10px;
  top: 10px;
}

.add-row-button {
  margin-top: 4px;
  border: 1px dashed rgba(var(--v-theme-primary), .45);
}

.literature-subhead {
  display: flex;
  align-items: center;
  min-height: 28px;
}

@media (max-width: 1180px) {
  .constructor-header {
    grid-template-columns: 1fr;
  }

  .constructor-grid {
    grid-template-columns: 1fr;
  }

  .sticky-preview {
    position: static;
  }

  .preview-scroll {
    max-height: none;
  }

  .constructor-actions {
    justify-items: stretch;
    width: 100%;
    margin-left: 0;
  }

  .status-chip-row,
  .action-button-row {
    justify-content: flex-start;
  }
}

@media (max-width: 640px) {
  .template-preview-paper {
    min-height: 900px;
    padding: 32px 24px;
  }

  .preview-scroll {
    padding: 12px;
  }
}
</style>
