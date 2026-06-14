<script setup lang="ts">
import {
  mdiAccountEditOutline,
  mdiArrowLeft,
  mdiArrowRight,
  mdiBookOpenPageVariantOutline,
  mdiCheck,
  mdiClipboardCheckOutline,
  mdiCloudCheckOutline,
  mdiCloudSyncOutline,
  mdiFileDocumentEditOutline,
  mdiFileEyeOutline,
  mdiFormatListChecks,
  mdiFountainPenTip,
  mdiLibraryOutline,
  mdiSchoolOutline,
  mdiShieldCheckOutline,
  mdiTable,
  mdiTrayArrowDown
} from '@mdi/js'
import type { Syllabus } from '~/types/syllabus'
import { calculateCompletion } from '~/utils/mockSyllabuses'

const props = defineProps<{ modelValue: Syllabus; mode: 'create' | 'edit'; submitting?: boolean }>()
const emit = defineEmits<{
  'update:modelValue': [value: Syllabus]
  autosave: [value: Syllabus]
  saveDraft: [value: Syllabus]
  finish: [value: Syllabus]
  cancel: []
}>()

function clone(value: Syllabus): Syllabus {
  return JSON.parse(JSON.stringify(toRaw(value))) as Syllabus
}

const form = reactive<Syllabus>(clone(props.modelValue))
const currentStep = ref(0)
const saveState = ref<'idle' | 'saving' | 'saved'>('idle')
let timer: ReturnType<typeof setTimeout> | undefined
let ready = false

const sections = [
  { id: 'title', number: '01', title: 'Титульная информация', description: 'Таблица реквизитов дисциплины и преподавателя', icon: mdiBookOpenPageVariantOutline },
  { id: 'schedule', number: '02', title: 'График занятий и задания', description: 'Недели, темы, формат и задания', icon: mdiTable },
  { id: 'description', number: '03', title: 'Описание курса', description: 'Описание и цель обучения', icon: mdiFileDocumentEditOutline },
  { id: 'outcomes', number: '04', title: 'Результаты обучения', description: 'Связь результатов курса и ОП', icon: mdiSchoolOutline },
  { id: 'plan', number: '05', title: 'Тематический план', description: 'Большая таблица по неделям', icon: mdiFormatListChecks },
  { id: 'assessment', number: '06', title: 'Система оценивания курса', description: 'Проценты, веса и итоговые баллы', icon: mdiClipboardCheckOutline },
  { id: 'literature', number: '07', title: 'Список литературы', description: 'Обязательные, дополнительные и интернет-источники', icon: mdiLibraryOutline },
  { id: 'philosophy', number: '08', title: 'Философия преподавания и обучения', description: 'Подход к обучению и взаимодействию', icon: mdiFountainPenTip },
  { id: 'policy', number: '09', title: 'Политика курса', description: 'Допустимо, недопустимо, экзамен и коммуникации', icon: mdiShieldCheckOutline },
  { id: 'signatures', number: '10', title: 'Подписи', description: 'Составитель, подпись и печать', icon: mdiAccountEditOutline }
]

watch(() => props.modelValue, value => {
  if (value.id !== form.id) Object.assign(form, clone(value))
}, { deep: true })

watch(form, () => {
  if (!ready) return
  form.completion = calculateCompletion(form)
  emit('update:modelValue', clone(form))
  saveState.value = 'saving'
  clearTimeout(timer)
  timer = setTimeout(() => {
    emit('autosave', clone(form))
    saveState.value = 'saved'
  }, 700)
}, { deep: true })

onMounted(() => { ready = true })
onBeforeUnmount(() => clearTimeout(timer))

const canPreview = computed(() => Boolean(form.titleInfo.codeAndName.trim() || form.titleInfo.instructorName.trim() || form.courseDescription.trim()))
const completedSections = computed(() => new Set([
  form.titleInfo.codeAndName && form.titleInfo.instructorName ? 'title' : '',
  form.classSchedule.some(item => item.topic || item.task) ? 'schedule' : '',
  form.courseDescription || form.courseGoal ? 'description' : '',
  form.learningOutcomes.some(item => item.courseLearningOutcome || item.programLearningOutcome) ? 'outcomes' : '',
  form.thematicPlan.some(item => item.topicModule || item.tasks) ? 'plan' : '',
  form.assessmentSystem.some(item => item.topicModule) ? 'assessment' : '',
  form.literature.required.some(Boolean) || form.literature.additional.some(Boolean) || form.literature.internetResources.some(Boolean) ? 'literature' : '',
  form.teachingPhilosophy ? 'philosophy' : '',
  form.coursePolicy.masteringDiscipline || form.coursePolicy.allowed || form.coursePolicy.notAllowed ? 'policy' : '',
  form.signatures.preparedByName ? 'signatures' : ''
].filter(Boolean)))
const progress = computed(() => Math.round(completedSections.value.size / sections.length * 100))
const activeSection = computed(() => sections[currentStep.value])

function snapshot() {
  form.completion = calculateCompletion(form)
  return clone(form)
}
function next() { if (currentStep.value < sections.length - 1) currentStep.value++ }
function previous() { if (currentStep.value > 0) currentStep.value-- }
</script>

<template>
  <div class="mx-auto max-w-[1450px]">
    <v-card class="app-surface mb-5 pa-4 sm:pa-5">
      <div class="flex flex-wrap items-center justify-between gap-4">
        <div class="flex items-center gap-4">
          <v-progress-circular :model-value="progress" color="primary" :size="50" :width="5"><span class="text-[11px] font-black">{{ progress }}%</span></v-progress-circular>
          <div><p class="text-sm font-bold">Готовность книжного силлабуса</p><p class="mt-1 text-xs text-medium-emphasis">{{ completedSections.size }} из {{ sections.length }} разделов содержат данные</p></div>
        </div>
        <div class="flex items-center gap-2 text-xs" :class="saveState === 'saving' ? 'text-primary' : 'text-medium-emphasis'">
          <v-icon :icon="saveState === 'saving' ? mdiCloudSyncOutline : mdiCloudCheckOutline" size="18" :class="{ 'animate-spin': saveState === 'saving' }" />
          {{ saveState === 'saving' ? 'Сохранение...' : saveState === 'saved' ? 'Все изменения сохранены' : 'Автосохранение включено' }}
        </div>
      </div>
      <v-progress-linear :model-value="progress" color="primary" height="5" rounded class="mt-4" />
    </v-card>

    <div class="grid gap-5 xl:grid-cols-[300px_minmax(0,1fr)]">
      <aside>
        <v-card class="app-surface pa-2 xl:sticky xl:top-24">
          <div class="flex gap-1 overflow-x-auto xl:block">
            <button
              v-for="(section, index) in sections"
              :key="section.id"
              class="step-item flex min-w-[240px] items-center gap-3 rounded-xl p-3 text-left xl:w-full"
              :class="{ active: currentStep === index }"
              @click="currentStep = index"
            >
              <span class="step-number grid size-8 shrink-0 place-items-center rounded-lg border text-[10px] font-black" :class="{ completed: completedSections.has(section.id) }">
                <v-icon v-if="completedSections.has(section.id)" :icon="mdiCheck" size="16" />
                <span v-else>{{ section.number }}</span>
              </span>
              <span class="min-w-0">
                <strong class="block truncate text-xs">{{ section.title }}</strong>
                <span class="mt-1 hidden truncate text-[10px] text-medium-emphasis xl:block">{{ section.description }}</span>
              </span>
            </button>
          </div>
        </v-card>
      </aside>

      <v-card class="app-surface min-w-0 overflow-hidden">
        <div class="flex items-start gap-4 border-b border-white/10 bg-surface-bright px-5 py-5 sm:px-7">
          <v-avatar color="primary" variant="tonal" size="44"><v-icon :icon="activeSection.icon" /></v-avatar>
          <div><p class="page-eyebrow">Раздел {{ activeSection.number }}</p><h2 class="mt-1 text-xl font-black">{{ activeSection.title }}</h2><p class="mt-1 text-xs text-medium-emphasis">{{ activeSection.description }}</p></div>
        </div>

        <div class="p-5 sm:p-7">
          <div v-if="currentStep === 0" class="space-y-5">
            <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              <BaseInput v-model="form.titleInfo.codeAndName" label="Код и название дисциплины" required class="xl:col-span-2" placeholder="HIS 1101 — История Казахстана" />
              <BaseSelect v-model="form.status" label="Статус"><option value="draft">Черновик</option><option value="ready">Готов</option></BaseSelect>
              <BaseInput v-model="form.titleInfo.credits" type="number" label="Кредиты" />
              <BaseInput v-model="form.titleInfo.totalHours" type="number" label="Всего часов" />
              <BaseInput v-model="form.titleInfo.classroomHours" type="number" label="Аудиторные часы" />
              <BaseInput v-model="form.titleInfo.independentWorkHours" type="number" label="Самостоятельная работа" />
              <BaseInput v-model="form.titleInfo.levelOfTraining" label="Уровень обучения" />
              <BaseInput v-model="form.titleInfo.semester" label="Семестр" />
              <BaseInput v-model="form.titleInfo.educationalProgram" label="Образовательная программа" class="xl:col-span-2" />
              <BaseSelect v-model="form.titleInfo.languageOfEducation" label="Язык обучения"><option value="KZ">KZ · Қазақша</option><option value="RU">RU · Русский</option><option value="EN">EN · English</option></BaseSelect>
              <BaseInput v-model="form.titleInfo.proficiencyLevel" label="Уровень владения языком" />
              <BaseInput v-model="form.titleInfo.formatOfTraining" label="Формат обучения" />
              <BaseInput v-model="form.titleInfo.timeAndPlace" label="Время и место проведения занятий" class="xl:col-span-2" />
              <BaseInput v-model="form.titleInfo.instructorName" label="Преподаватель" required />
              <BaseInput v-model="form.titleInfo.instructorDegree" label="Ученая степень / должность" />
              <BaseInput v-model="form.titleInfo.instructorEmail" type="email" label="Email" />
              <BaseTextarea v-model="form.titleInfo.instructorContacts" label="Контакты преподавателя" class="xl:col-span-2" />
            </div>
            <BaseTextarea v-model="form.titleInfo.prerequisites" label="Пререквизиты" />
          </div>

          <ClassScheduleTable v-else-if="currentStep === 1" v-model="form.classSchedule" />

          <div v-else-if="currentStep === 2" class="grid gap-5">
            <BaseTextarea v-model="form.courseDescription" label="Описание курса" :rows="8" />
            <BaseTextarea v-model="form.courseGoal" label="Цель обучения" :rows="5" />
          </div>

          <LearningOutcomesTable v-else-if="currentStep === 3" v-model="form.learningOutcomes" />
          <WeeklyPlanTable v-else-if="currentStep === 4" v-model="form.thematicPlan" />
          <AssessmentTable v-else-if="currentStep === 5" v-model="form.assessmentSystem" />
          <LiteratureSection v-else-if="currentStep === 6" v-model="form.literature" />
          <BaseTextarea v-else-if="currentStep === 7" v-model="form.teachingPhilosophy" label="Философия преподавания и обучения" :rows="12" />
          <PolicySection v-else-if="currentStep === 8" v-model="form.coursePolicy" />
          <SignatureSection v-else v-model="form.signatures" />
        </div>

        <div class="flex flex-wrap items-center justify-between gap-3 border-t border-white/10 bg-surface-bright px-5 py-4 sm:px-7">
          <v-btn :prepend-icon="mdiArrowLeft" variant="text" :disabled="currentStep === 0" class="text-none" @click="previous">Назад</v-btn>
          <span class="text-xs text-medium-emphasis">Шаг {{ currentStep + 1 }} из {{ sections.length }}</span>
          <v-btn v-if="currentStep < sections.length - 1" color="primary" :append-icon="mdiArrowRight" class="text-none font-weight-bold" @click="next">Следующий раздел</v-btn>
          <v-btn v-else color="primary" :prepend-icon="mdiFileEyeOutline" :loading="props.submitting" :disabled="(!canPreview && mode === 'create') || props.submitting" class="text-none font-weight-bold" @click="emit('finish', snapshot())">Сохранить и открыть</v-btn>
        </div>
      </v-card>
    </div>

    <v-card class="sticky bottom-3 z-20 mt-5 app-surface pa-3">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <p class="hidden text-xs text-medium-emphasis md:block">{{ mode === 'create' ? 'Новый документ' : 'Редактирование' }} · автосохранение активно</p>
        <div class="ml-auto flex flex-wrap gap-2">
          <v-btn variant="text" class="text-none" @click="emit('cancel')">Отмена</v-btn>
          <v-btn variant="outlined" :prepend-icon="mdiTrayArrowDown" :loading="props.submitting" :disabled="props.submitting" class="text-none" @click="emit('saveDraft', snapshot())">Сохранить черновик</v-btn>
          <v-btn color="primary" :prepend-icon="mdiFileEyeOutline" :loading="props.submitting" :disabled="(!canPreview && mode === 'create') || props.submitting" class="text-none font-weight-bold" @click="emit('finish', snapshot())">Сохранить и открыть preview</v-btn>
        </div>
      </div>
    </v-card>
  </div>
</template>

<style scoped>
.step-item { color: rgba(var(--v-theme-on-surface), .62); transition: background .18s, color .18s; }
.step-item:hover { background: rgba(var(--v-theme-primary), .06); color: rgb(var(--v-theme-on-surface)); }
.step-item.active { background: rgba(var(--v-theme-primary), .13); color: rgb(var(--v-theme-primary)); }
.step-number { border-color: rgba(var(--v-border-color), .14); }
.step-item.active .step-number, .step-number.completed { border-color: rgb(var(--v-theme-primary)); background: rgb(var(--v-theme-primary)); color: #032d23; }
</style>
