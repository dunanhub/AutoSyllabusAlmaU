<script setup lang="ts">
import { mdiArrowLeft, mdiDownloadOutline, mdiFileCogOutline, mdiPencilOutline } from '@mdi/js'
import type { Syllabus } from '~/types/syllabus'

definePageMeta({ middleware: 'auth' })
const route = useRoute()
const store = useSyllabusStore()
const { show } = useAppToast()
const syllabus = ref<Syllabus | null>(null)
const loading = ref(true)
const actionLoading = ref(false)
const pdfGenerating = ref(false)
const pdfDownloading = ref(false)
const pdfPollInFlight = ref(false)
let pdfPollTimer: ReturnType<typeof setInterval> | null = null

const pdfState = computed(() => {
  const status = syllabus.value?.pdfStatus || 'not_generated'
  if (status === 'processing') return { label: 'PDF формируется', color: 'info' }
  if (status === 'generated') return { label: 'PDF готов', color: 'success' }
  if (status === 'failed') return { label: 'Ошибка PDF', color: 'error' }
  return { label: 'PDF не создан', color: 'default' }
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

async function load() {
  loading.value = true
  try {
    await store.initialize()
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
      show('PDF успешно сгенерирован', 'success')
    } else if (syllabus.value?.pdfStatus === 'failed') {
      stopPdfPolling()
      show('Ошибка генерации PDF', 'error')
    }
  } catch {
    // A temporary network error should not cancel an active background job.
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

async function generatePdf() {
  if (!syllabus.value || pdfGenerating.value) return
  pdfGenerating.value = true
  try {
    const updated = await store.generatePdf(syllabus.value.id)
    if (updated) syllabus.value = updated
    startPdfPolling()
  } catch {
    try {
      await store.refresh()
      syllabus.value = await store.getSyllabusById(syllabus.value.id)
    } catch {
      // Keep the current document visible when refreshing the failed status is unavailable.
    }
    show('Ошибка генерации PDF', 'error')
  } finally {
    if (syllabus.value?.pdfStatus !== 'processing') pdfGenerating.value = false
  }
}

async function downloadPdf() {
  if (!syllabus.value || syllabus.value.pdfStatus !== 'generated' || pdfDownloading.value) return
  pdfDownloading.value = true
  try {
    await store.downloadPdf(syllabus.value.id)
  } catch {
    show('Ошибка скачивания PDF', 'error')
  } finally {
    pdfDownloading.value = false
  }
}
</script>

<template>
  <div>
    <div v-if="loading" class="py-20 text-center"><v-progress-circular indeterminate color="primary" /><p class="mt-3 text-sm text-medium-emphasis">Загрузка документа...</p></div>
    <template v-else-if="syllabus">
      <div class="print-hidden mb-5 space-y-4">
        <v-btn variant="text" :prepend-icon="mdiArrowLeft" class="text-none" @click="navigateTo('/syllabuses')">Реестр силлабусов</v-btn>
        <v-card class="app-surface pa-4 sm:pa-5">
          <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div class="min-w-0">
              <div class="flex flex-wrap items-center gap-2">
                <h1 class="truncate text-xl font-black">{{ syllabus.titleInfo.codeAndName || 'Без названия' }}</h1>
                <SyllabusStatusBadge :status="syllabus.status" />
                <v-chip size="x-small" variant="tonal" :color="pdfState.color">{{ pdfState.label }}</v-chip>
              </div>
              <p class="mt-2 text-xs text-medium-emphasis">{{ syllabus.titleInfo.educationalProgram || 'Программа не указана' }} · {{ syllabus.titleInfo.semester || 'Семестр не указан' }} · {{ syllabus.titleInfo.languageOfEducation }}</p>
              <p v-if="formattedPdfDate" class="mt-1 text-[11px] text-medium-emphasis">PDF создан: {{ formattedPdfDate }}</p>
              <p v-if="syllabus.pdfError" class="mt-1 max-w-3xl text-[11px] text-error">{{ syllabus.pdfError }}</p>
            </div>
            <div class="flex flex-wrap gap-2">
              <v-btn size="small" variant="tonal" :color="syllabus.status === 'ready' ? 'warning' : 'success'" :loading="actionLoading" class="text-none" @click="toggleStatus">{{ syllabus.status === 'ready' ? 'Вернуть в черновики' : 'Отметить готовым' }}</v-btn>
              <v-btn size="small" variant="outlined" :prepend-icon="mdiPencilOutline" class="text-none" @click="navigateTo(`/syllabuses/${syllabus.id}/edit`)">Редактировать</v-btn>
              <v-btn size="small" color="primary" :prepend-icon="mdiFileCogOutline" :loading="pdfGenerating" :disabled="pdfDownloading" class="text-none font-weight-bold" @click="generatePdf">Сгенерировать PDF</v-btn>
              <v-btn size="small" variant="outlined" :prepend-icon="mdiDownloadOutline" :loading="pdfDownloading" :disabled="syllabus.pdfStatus !== 'generated' || pdfGenerating" class="text-none" @click="downloadPdf">Скачать PDF</v-btn>
            </div>
          </div>
        </v-card>
      </div>
      <div class="a4-shell overflow-x-auto rounded-2xl border border-white/10 bg-[#050b14] p-3 sm:p-8"><SyllabusPreview :syllabus="syllabus" /></div>
    </template>
    <v-card v-else class="app-surface"><EmptyState title="Силлабус не найден" description="Документ был удалён или ссылка устарела."><v-btn color="primary" @click="navigateTo('/syllabuses')">Вернуться к реестру</v-btn></EmptyState></v-card>
  </div>
</template>
