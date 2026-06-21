<script setup lang="ts">
import {
  mdiAccountTieOutline,
  mdiBookOpenPageVariantOutline,
  mdiContentCopy,
  mdiDotsVertical,
  mdiEyeOutline,
  mdiFileCogOutline,
  mdiFilePdfBox,
  mdiMagnify,
  mdiPlus,
  mdiQrcode,
  mdiSchoolOutline,
  mdiTrashCanOutline,
  mdiTuneVariant
} from '@mdi/js'
import { ALMAU_SCHOOLS } from '~/constants/schools'
import type { CourseDetails } from '~/utils/courseSyllabus'
import type { Syllabus, SyllabusLanguage, SyllabusPdfStatus, SyllabusStatus } from '~/types/syllabus'
import { createCourseSyllabusInput, splitCodeAndName } from '~/utils/courseSyllabus'

definePageMeta({ middleware: 'auth' })

const store = useSyllabusStore()
const { show } = useAppToast()
const route = useRoute()
const router = useRouter()
const loading = ref(true)
const search = ref('')
const language = ref<'all' | SyllabusLanguage>('all')
const status = ref<'all' | SyllabusStatus>('all')
const school = ref('all')
const program = ref('all')
const pdfStatus = ref<'all' | SyllabusPdfStatus>('all')
const createDialog = ref(false)
const qrDialog = ref(false)
const qrValue = ref('')
const previewDrawer = ref(false)
const previewSyllabus = ref<Syllabus | null>(null)
const pendingDelete = ref<Syllabus | null>(null)
const actionLoadingId = ref('')
const createSubmitting = ref(false)

const languageItems = [
  { title: 'Все языки', value: 'all' },
  { title: 'KZ · Қазақша', value: 'KZ' },
  { title: 'RU · Русский', value: 'RU' },
  { title: 'EN · English', value: 'EN' }
]

const statusItems = [
  { title: 'Все статусы', value: 'all' },
  { title: 'Черновик', value: 'draft' },
  { title: 'Готов', value: 'ready' }
]

const schoolItems = computed(() => [
  { title: 'Все школы', value: 'all' },
  ...ALMAU_SCHOOLS.map(item => ({ title: item.nameRu, value: item.id }))
])

const programItems = computed(() => {
  const values = Array.from(new Set(store.syllabuses.map(item => item.titleInfo.educationalProgram).filter(Boolean)))
  return [
    { title: 'Все программы', value: 'all' },
    ...values.map(value => ({ title: value, value }))
  ]
})

const pdfStatusItems = [
  { title: 'Все PDF', value: 'all' },
  { title: 'Не создан', value: 'not_generated' },
  { title: 'Формируется', value: 'processing' },
  { title: 'Готов', value: 'generated' },
  { title: 'Ошибка', value: 'failed' }
]

const filtered = computed(() => {
  const query = search.value.trim().toLowerCase()
  return store.syllabuses.filter((item) => {
    const names = splitCodeAndName(item.titleInfo.codeAndName)
    const matches = !query || [
      item.titleInfo.codeAndName,
      names.courseCode,
      names.courseName,
      item.titleInfo.instructorName,
      item.titleInfo.educationalProgram,
      item.titleInfo.schoolName
    ].some(value => value.toLowerCase().includes(query))

    return matches
      && (language.value === 'all' || item.titleInfo.languageOfEducation === language.value || item.titleInfo.languageOfEducation === 'MULTI')
      && (status.value === 'all' || item.status === status.value)
      && (school.value === 'all' || item.titleInfo.schoolId === school.value)
      && (program.value === 'all' || item.titleInfo.educationalProgram === program.value)
      && (pdfStatus.value === 'all' || (item.pdfStatus || 'not_generated') === pdfStatus.value)
  })
})

const hasFilters = computed(() => Boolean(
  search.value
  || language.value !== 'all'
  || status.value !== 'all'
  || school.value !== 'all'
  || program.value !== 'all'
  || pdfStatus.value !== 'all'
))
const formatDate = (date: string) => new Intl.DateTimeFormat('ru-RU', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(date))

onMounted(async () => {
  try {
    await store.initialize()
    if (route.query.create === '1') {
      createDialog.value = true
      const query = { ...route.query }
      delete query.create
      void router.replace({ query })
    }
  } finally {
    loading.value = false
  }
})

function resetFilters() {
  search.value = ''
  language.value = 'all'
  status.value = 'all'
  school.value = 'all'
  program.value = 'all'
  pdfStatus.value = 'all'
}

function courseName(item: Syllabus) {
  return splitCodeAndName(item.titleInfo.codeAndName).courseName || item.titleInfo.codeAndName || 'Без названия'
}

function courseCode(item: Syllabus) {
  return splitCodeAndName(item.titleInfo.codeAndName).courseCode || 'Код не указан'
}

function pdfState(item: Syllabus) {
  const value = item.pdfStatus || 'not_generated'
  if (value === 'processing') return { label: 'PDF формируется', color: 'info' }
  if (value === 'generated') return { label: 'PDF готов', color: 'success' }
  if (value === 'failed') return { label: 'Ошибка PDF', color: 'error' }
  return { label: 'PDF не создан', color: 'default' }
}

function displayLanguage(value: string) {
  return value === 'MULTI' ? 'RU / KZ / EN' : value || 'RU'
}

function openQr(item: Syllabus) {
  qrValue.value = item.titleInfo.qrUrl || `${window.location.origin}/syllabuses/${item.id}`
  qrDialog.value = true
}

function openPreview(item: Syllabus) {
  previewSyllabus.value = item
  previewDrawer.value = true
}

async function createCourse(details: CourseDetails) {
  createSubmitting.value = true
  try {
    const created = await store.createSyllabus(createCourseSyllabusInput(details))
    const qrUrl = import.meta.client ? `${window.location.origin}/syllabuses/${created.id}` : `/syllabuses/${created.id}`
    const updated = await store.updateSyllabus(created.id, {
      ...created,
      titleInfo: {
        ...created.titleInfo,
        qrUrl
      }
    })
    createDialog.value = false
    show('Дисциплина создана', 'success')
    await navigateTo(`/syllabuses/${updated.id}`)
  } finally {
    createSubmitting.value = false
  }
}

async function confirmDelete() {
  if (!pendingDelete.value) return
  actionLoadingId.value = pendingDelete.value.id
  try {
    await store.deleteSyllabus(pendingDelete.value.id)
    show('Дисциплина удалена', 'success')
    pendingDelete.value = null
  } finally {
    actionLoadingId.value = ''
  }
}

async function duplicate(id: string) {
  actionLoadingId.value = id
  try {
    const copy = await store.duplicateSyllabus(id)
    show('Копия дисциплины создана', 'success')
    await navigateTo(`/syllabuses/${copy.id}`)
  } finally {
    actionLoadingId.value = ''
  }
}

async function generatePdf(item = previewSyllabus.value) {
  if (!item) return
  actionLoadingId.value = item.id
  try {
    await store.generatePdf(item.id)
    previewSyllabus.value = await store.getSyllabusById(item.id) || item
    show('Генерация PDF запущена', 'success')
  } catch {
    show('Ошибка запуска PDF', 'error')
  } finally {
    actionLoadingId.value = ''
  }
}

async function downloadPdf(item = previewSyllabus.value) {
  if (!item || item.pdfStatus !== 'generated') return
  actionLoadingId.value = item.id
  try {
    await store.downloadPdf(item.id)
  } catch {
    show('Ошибка скачивания PDF', 'error')
  } finally {
    actionLoadingId.value = ''
  }
}
</script>

<template>
  <div class="space-y-6">
    <PageHeader
      eyebrow="Реестр дисциплин"
      title="Силлабусы"
      description="Сначала создайте дисциплину с базовыми данными, затем заполните полный силлабус в конструкторе."
    >
      <template #actions>
        <v-btn color="primary" :prepend-icon="mdiPlus" class="text-none font-weight-bold" @click="createDialog = true">
          Создать дисциплину
        </v-btn>
      </template>
    </PageHeader>

    <v-card class="app-surface overflow-hidden">
      <div class="grid gap-3 border-b border-white/10 bg-surface-bright p-4 xl:grid-cols-[minmax(260px,1fr)_150px_150px_210px_210px_150px_auto]">
        <v-text-field v-model="search" :prepend-inner-icon="mdiMagnify" label="Поиск" placeholder="Название, код, преподаватель или программа" clearable />
        <v-select v-model="language" :items="languageItems" label="Язык" />
        <v-select v-model="status" :items="statusItems" label="Статус" />
        <v-select v-model="school" :items="schoolItems" label="Школа" />
        <v-select v-model="program" :items="programItems" label="Программа" />
        <v-select v-model="pdfStatus" :items="pdfStatusItems" label="PDF" />
        <v-btn v-if="hasFilters" variant="text" :prepend-icon="mdiTuneVariant" class="text-none self-center" @click="resetFilters">
          Сбросить
        </v-btn>
      </div>

      <div v-if="loading" class="p-12 text-center">
        <v-progress-circular indeterminate color="primary" />
        <p class="mt-3 text-sm text-medium-emphasis">Загрузка дисциплин...</p>
      </div>

      <div v-else class="course-grid p-4 sm:p-5">
        <button class="create-card" type="button" @click="createDialog = true">
          <span class="create-icon"><v-icon :icon="mdiPlus" size="34" /></span>
          <strong>Создать дисциплину</strong>
          <span>Заполните только базовые данные, а силлабус дополните позже.</span>
        </button>

        <article v-for="item in filtered" :key="item.id" class="course-card">
          <button class="course-main" type="button" @click="navigateTo(`/syllabuses/${item.id}`)">
            <div class="flex items-start justify-between gap-3">
              <v-avatar color="primary" variant="tonal" size="44"><v-icon :icon="mdiSchoolOutline" /></v-avatar>
              <div class="flex gap-2">
                <v-chip size="x-small" variant="outlined">{{ displayLanguage(item.titleInfo.languageOfEducation) }}</v-chip>
                <SyllabusStatusBadge :status="item.status" />
              </div>
            </div>

            <div class="mt-5 min-w-0">
              <p class="text-xs font-bold uppercase tracking-[.16em] text-primary">{{ courseCode(item) }}</p>
              <h3 class="mt-2 line-clamp-2 text-lg font-black">{{ courseName(item) }}</h3>
            </div>

            <div class="mt-5 grid gap-3 text-left text-xs text-medium-emphasis">
              <p class="flex items-center gap-2"><v-icon :icon="mdiAccountTieOutline" size="16" />{{ item.titleInfo.instructorName || 'Преподаватель не указан' }}</p>
              <p class="line-clamp-1">{{ item.titleInfo.schoolName || item.titleInfo.educationalProgram || 'Школа не указана' }}</p>
              <p>{{ item.titleInfo.semester || 'Семестр не указан' }}</p>
            </div>

            <div class="mt-5">
              <div class="mb-1 flex justify-between text-[10px] text-medium-emphasis">
                <span>Заполнение силлабуса</span>
                <strong>{{ item.completion }}%</strong>
              </div>
              <v-progress-linear :model-value="item.completion" color="primary" height="6" rounded />
            </div>
          </button>

          <div class="course-footer">
            <div>
              <v-chip size="x-small" variant="tonal" :color="pdfState(item).color" :prepend-icon="mdiFilePdfBox">
                {{ pdfState(item).label }}
              </v-chip>
              <p class="mt-2 text-[10px] text-medium-emphasis">Обновлено: {{ formatDate(item.updatedAt) }}</p>
            </div>
            <div class="flex items-center gap-1">
              <v-btn :icon="mdiEyeOutline" size="small" variant="text" aria-label="Открыть" @click="navigateTo(`/syllabuses/${item.id}`)" />
              <v-btn :icon="mdiBookOpenPageVariantOutline" size="small" variant="text" aria-label="Preview" @click="openPreview(item)" />
              <v-btn :icon="mdiQrcode" size="small" variant="text" aria-label="QR код" @click="openQr(item)" />
              <v-menu>
                <template #activator="{ props }">
                  <v-btn v-bind="props" :icon="mdiDotsVertical" size="small" variant="text" aria-label="Действия" />
                </template>
                <v-list density="compact">
                  <v-list-item :prepend-icon="mdiFileCogOutline" title="Сгенерировать PDF" :disabled="actionLoadingId === item.id" @click="generatePdf(item)" />
                  <v-list-item :prepend-icon="mdiContentCopy" title="Дублировать" :disabled="actionLoadingId === item.id" @click="duplicate(item.id)" />
                  <v-divider />
                  <v-list-item :prepend-icon="mdiTrashCanOutline" title="Удалить" base-color="error" :disabled="actionLoadingId === item.id" @click="pendingDelete = item" />
                </v-list>
              </v-menu>
            </div>
          </div>
        </article>
      </div>

      <EmptyState
        v-if="!loading && !filtered.length && hasFilters"
        :icon="mdiMagnify"
        title="Дисциплины не найдены"
        description="Измените параметры поиска или создайте новую дисциплину."
      >
        <v-btn variant="outlined" @click="resetFilters">Сбросить фильтры</v-btn>
      </EmptyState>
    </v-card>

    <CourseCreateDialog v-model="createDialog" :submitting="createSubmitting" @submit="createCourse" />
    <QrCodeDialog v-model="qrDialog" :value="qrValue" />
    <SyllabusPreviewDrawer
      v-model="previewDrawer"
      :syllabus="previewSyllabus"
      :generating="Boolean(previewSyllabus && actionLoadingId === previewSyllabus.id)"
      :downloading="Boolean(previewSyllabus && actionLoadingId === previewSyllabus.id)"
      @generate="generatePdf()"
      @download="downloadPdf()"
      @full="previewSyllabus && navigateTo(`/syllabuses/${previewSyllabus.id}`)"
    />

    <ConfirmModal
      :open="Boolean(pendingDelete)"
      title="Удалить дисциплину?"
      :message="`Дисциплина «${pendingDelete ? courseName(pendingDelete) : 'Без названия'}» будет удалена вместе с силлабусом.`"
      @confirm="confirmDelete"
      @cancel="pendingDelete = null"
    />
  </div>
</template>

<style scoped>
.course-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}
.create-card,
.course-card {
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(var(--v-border-color), .1);
  border-radius: 22px;
  background: linear-gradient(rgb(var(--v-theme-surface)), rgb(var(--v-theme-surface))) padding-box,
    linear-gradient(135deg, rgba(var(--v-theme-primary), .65), rgba(56, 189, 248, .24), rgba(139, 92, 246, .35)) border-box;
  transition: transform .18s ease, border-color .18s ease, box-shadow .18s ease;
}
.create-card {
  display: grid;
  min-height: 315px;
  place-items: center;
  padding: 28px;
  text-align: center;
}
.create-card:hover,
.course-card:hover {
  box-shadow: 0 22px 60px rgba(0, 0, 0, .22);
  transform: translateY(-3px);
}
.create-icon {
  display: grid;
  width: 72px;
  height: 72px;
  place-items: center;
  border-radius: 22px;
  background: rgba(var(--v-theme-primary), .12);
  color: rgb(var(--v-theme-primary));
}
.create-card strong {
  margin-top: 18px;
  font-size: 18px;
}
.create-card span:last-child {
  max-width: 230px;
  color: rgba(var(--v-theme-on-surface), .62);
  font-size: 13px;
}
.course-main {
  display: block;
  width: 100%;
  min-height: 255px;
  padding: 18px;
  text-align: left;
}
.course-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  border-top: 1px solid rgba(var(--v-border-color), .08);
  padding: 14px 16px;
}
</style>
