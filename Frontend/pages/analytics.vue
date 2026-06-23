<script setup lang="ts">
import {
  mdiAlertCircleOutline,
  mdiBrain,
  mdiChartDonut,
  mdiCheckCircleOutline,
  mdiFileDocumentMultipleOutline,
  mdiRefresh,
  mdiTableClock,
  mdiTranslate,
  mdiTune,
} from '@mdi/js'
import type { AnalyticsTask, AnalyticsTaskFilters, AnalyticsTaskStatus, AnalyticsTaskType } from '~/composables/useAnalyticsApi'

definePageMeta({ middleware: 'auth' })

const analytics = useAnalyticsStore()
const { show } = useAppToast()
const filters = reactive<AnalyticsTaskFilters>({
  status: '',
  type: '',
  search: '',
  period: 'all',
})
let pollingTimer: ReturnType<typeof setInterval> | null = null

const statusOptions = [
  { title: 'Все статусы', value: '' },
  { title: 'В очереди', value: 'queued' },
  { title: 'Выполняется', value: 'processing' },
  { title: 'Завершено', value: 'completed' },
  { title: 'Ошибка', value: 'failed' },
]

const typeOptions = [
  { title: 'Все типы', value: '' },
  { title: 'Перевод шаблона', value: 'template_translation' },
  { title: 'ИИ-дозаполнение', value: 'syllabus_ai_fill' },
  { title: 'Перевод силлабуса', value: 'render_translation' },
  { title: 'Генерация документов', value: 'document_generation' },
]

const periodOptions = [
  { title: 'За всё время', value: 'all' },
  { title: 'Сегодня', value: 'today' },
  { title: '7 дней', value: '7d' },
  { title: '30 дней', value: '30d' },
]

const summaryCards = computed(() => {
  const summary = analytics.summary
  return [
    {
      label: 'Дисциплины',
      value: summary?.syllabuses.total ?? 0,
      note: `${summary?.syllabuses.ready ?? 0} готовы · ${summary?.syllabuses.draft ?? 0} черновики`,
      icon: mdiFileDocumentMultipleOutline,
      color: 'primary',
    },
    {
      label: 'Шаблоны',
      value: summary?.templates.total ?? 0,
      note: `${summary?.templates.valid ?? 0} готовые · ${summary?.templates.default ?? 0} default`,
      icon: mdiChartDonut,
      color: 'info',
    },
    {
      label: 'Документы',
      value: summary?.documents.generated ?? 0,
      note: `${summary?.documents.processing ?? 0} в обработке · ${summary?.documents.failed ?? 0} ошибок`,
      icon: mdiCheckCircleOutline,
      color: summary?.documents.failed ? 'warning' : 'success',
    },
    {
      label: 'Ошибки автоматизации',
      value: summary?.automation.failedTotal ?? 0,
      note: `${summary?.automation.processingTotal ?? 0} активные задачи`,
      icon: mdiAlertCircleOutline,
      color: summary?.automation.failedTotal ? 'error' : 'success',
    },
  ]
})

const hasActiveTasks = computed(() => analytics.hasProcessingTasks || Boolean(analytics.summary?.automation.processingTotal))

watch(filters, () => {
  void analytics.fetchTasks(cleanFilters())
}, { deep: true })

watch(hasActiveTasks, (active) => {
  if (active) startPolling()
  else stopPolling()
})

onMounted(async () => {
  await analytics.refresh(cleanFilters())
  if (hasActiveTasks.value) startPolling()
})

onBeforeUnmount(() => stopPolling())

function cleanFilters() {
  return {
    status: filters.status || undefined,
    type: filters.type || undefined,
    search: filters.search || undefined,
    period: filters.period || 'all',
  }
}

function startPolling() {
  if (pollingTimer) return
  pollingTimer = setInterval(() => {
    void analytics.refresh(cleanFilters())
  }, 5000)
}

function stopPolling() {
  if (!pollingTimer) return
  clearInterval(pollingTimer)
  pollingTimer = null
}

async function refresh() {
  await analytics.refresh(cleanFilters())
  show('Аналитика обновлена', 'success')
}

async function retryTask(task: AnalyticsTask) {
  try {
    await analytics.retryTask(task.id, cleanFilters())
    show('Задача повторно запущена', 'success')
    startPolling()
  } catch (error) {
    const message = (error as { data?: { detail?: string }, message?: string })?.data?.detail
      || (error as Error)?.message
      || 'Не удалось повторить задачу'
    show(message, 'error')
  }
}

function taskTypeText(type: AnalyticsTaskType) {
  return {
    template_translation: 'Перевод шаблона',
    syllabus_ai_fill: 'ИИ-дозаполнение',
    render_translation: 'Перевод силлабуса',
    document_generation: 'Генерация документов',
  }[type]
}

function taskTypeIcon(type: AnalyticsTaskType) {
  return {
    template_translation: mdiTranslate,
    syllabus_ai_fill: mdiBrain,
    render_translation: mdiTranslate,
    document_generation: mdiFileDocumentMultipleOutline,
  }[type]
}

function statusText(status: AnalyticsTaskStatus) {
  return {
    queued: 'В очереди',
    processing: 'Выполняется',
    completed: 'Завершено',
    failed: 'Ошибка',
  }[status]
}

function statusColor(status: AnalyticsTaskStatus) {
  return {
    queued: 'info',
    processing: 'warning',
    completed: 'success',
    failed: 'error',
  }[status]
}

function formatDate(date: string | null) {
  if (!date) return '—'
  return new Intl.DateTimeFormat('ru-RU', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(date))
}

function friendlyError(error: string) {
  if (!error) return ''
  if (/(503|429|UNAVAILABLE|RESOURCE_EXHAUSTED|high demand|quota)/i.test(error)) {
    return 'Gemini временно недоступен или превышен лимит. Попробуйте позже.'
  }
  return error
}
</script>

<template>
  <div class="space-y-6">
    <PageHeader
      eyebrow="Данные"
      title="Аналитика"
      description="Мониторинг дисциплин, шаблонов, документов и фоновых Celery-задач."
    >
      <template #actions>
        <v-btn
          color="primary"
          :prepend-icon="mdiRefresh"
          class="text-none font-weight-bold"
          :loading="analytics.loadingSummary || analytics.loadingTasks"
          @click="refresh"
        >
          Обновить
        </v-btn>
      </template>
    </PageHeader>

    <section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <v-card v-for="card in summaryCards" :key="card.label" class="app-surface pa-5">
        <div class="flex items-start justify-between">
          <v-avatar :color="card.color" variant="tonal" size="42">
            <v-icon :icon="card.icon" />
          </v-avatar>
          <v-chip size="x-small" variant="text" color="success">LIVE</v-chip>
        </div>
        <p class="mt-5 text-3xl font-black">{{ card.value }}</p>
        <p class="mt-1 text-sm font-bold">{{ card.label }}</p>
        <p class="mt-1 text-xs text-medium-emphasis">{{ card.note }}</p>
      </v-card>
    </section>

    <section class="grid gap-4 xl:grid-cols-[1fr_1fr]">
      <v-card class="app-surface pa-5">
        <div class="flex items-center gap-3">
          <v-avatar color="warning" variant="tonal"><v-icon :icon="mdiTableClock" /></v-avatar>
          <div>
            <h2 class="text-base font-bold">Активные задачи</h2>
            <p class="text-xs text-medium-emphasis">Processing и queued задачи Celery</p>
          </div>
        </div>
        <div v-if="analytics.summary?.activeTasks.length" class="mt-4 space-y-3">
          <div v-for="task in analytics.summary.activeTasks" :key="task.id" class="soft-surface rounded-xl p-4">
            <div class="flex items-center justify-between gap-3">
              <p class="text-sm font-bold">{{ taskTypeText(task.taskType) }}</p>
              <v-chip :color="statusColor(task.status)" size="small" variant="tonal">{{ statusText(task.status) }}</v-chip>
            </div>
            <p class="mt-1 text-xs text-medium-emphasis">{{ task.objectTitle || task.taskId }}</p>
          </div>
        </div>
        <p v-else class="mt-5 text-sm text-medium-emphasis">Активных задач сейчас нет.</p>
      </v-card>

      <v-card class="app-surface pa-5">
        <div class="flex items-center gap-3">
          <v-avatar color="error" variant="tonal"><v-icon :icon="mdiAlertCircleOutline" /></v-avatar>
          <div>
            <h2 class="text-base font-bold">Последние ошибки</h2>
            <p class="text-xs text-medium-emphasis">Gemini, PDF, DOCX и AI-задачи</p>
          </div>
        </div>
        <div v-if="analytics.summary?.recentErrors.length" class="mt-4 space-y-3">
          <div v-for="task in analytics.summary.recentErrors" :key="task.id" class="rounded-xl border border-error/20 bg-error/10 p-4">
            <p class="text-sm font-bold">{{ task.objectTitle || taskTypeText(task.taskType) }}</p>
            <p class="mt-1 text-xs text-error">{{ friendlyError(task.error) }}</p>
          </div>
        </div>
        <p v-else class="mt-5 text-sm text-medium-emphasis">Ошибок фоновых задач нет.</p>
      </v-card>
    </section>

    <v-card class="app-surface overflow-hidden">
      <div class="border-b border-white/10 p-5">
        <div class="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
          <div>
            <div class="flex items-center gap-3">
              <v-avatar color="primary" variant="tonal"><v-icon :icon="mdiTune" /></v-avatar>
              <div>
                <h2 class="text-base font-bold">Фоновые задачи</h2>
                <p class="text-xs text-medium-emphasis">История переводов, AI-дозаполнения и генерации документов.</p>
              </div>
            </div>
          </div>
          <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4 xl:min-w-[820px]">
            <v-text-field
              v-model="filters.search"
              label="Поиск"
              density="comfortable"
              hide-details
              variant="outlined"
            />
            <v-select
              v-model="filters.status"
              :items="statusOptions"
              label="Статус"
              density="comfortable"
              hide-details
              variant="outlined"
            />
            <v-select
              v-model="filters.type"
              :items="typeOptions"
              label="Тип"
              density="comfortable"
              hide-details
              variant="outlined"
            />
            <v-select
              v-model="filters.period"
              :items="periodOptions"
              label="Период"
              density="comfortable"
              hide-details
              variant="outlined"
            />
          </div>
        </div>
      </div>

      <div v-if="analytics.loadingTasks" class="p-5">
        <v-skeleton-loader type="table" />
      </div>

      <EmptyState
        v-else-if="!analytics.tasks.length"
        title="Фоновых задач пока нет"
        description="Запустите перевод шаблона, AI-дозаполнение или генерацию документов, чтобы увидеть историю задач."
        :icon="mdiTableClock"
      />

      <div v-else>
        <div class="hidden overflow-x-auto lg:block">
          <table class="analytics-table">
            <thead>
              <tr>
                <th>Тип</th>
                <th>Объект</th>
                <th>Статус</th>
                <th>Task ID</th>
                <th>Старт</th>
                <th>Финиш</th>
                <th>Ошибка</th>
                <th />
              </tr>
            </thead>
            <tbody>
              <tr v-for="task in analytics.tasks" :key="task.id">
                <td>
                  <div class="flex items-center gap-2">
                    <v-icon :icon="taskTypeIcon(task.taskType)" size="18" color="primary" />
                    <span>{{ taskTypeText(task.taskType) }}</span>
                  </div>
                </td>
                <td class="max-w-[240px]">
                  <p class="truncate font-bold">{{ task.objectTitle || 'Без названия' }}</p>
                  <p class="truncate text-[11px] text-medium-emphasis">{{ task.objectType }} · {{ task.objectId }}</p>
                </td>
                <td><v-chip :color="statusColor(task.status)" size="small" variant="tonal">{{ statusText(task.status) }}</v-chip></td>
                <td class="max-w-[190px]"><code class="truncate-code">{{ task.taskId }}</code></td>
                <td>{{ formatDate(task.startedAt || task.createdAt) }}</td>
                <td>{{ formatDate(task.finishedAt) }}</td>
                <td class="max-w-[280px]"><p class="line-clamp-2 text-error">{{ friendlyError(task.error) }}</p></td>
                <td class="text-right">
                  <v-btn
                    size="small"
                    variant="tonal"
                    color="primary"
                    class="text-none"
                    :disabled="task.status !== 'failed'"
                    :loading="analytics.retryingTaskId === task.id"
                    @click="retryTask(task)"
                  >
                    Повторить
                  </v-btn>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="grid gap-3 p-4 lg:hidden">
          <v-card v-for="task in analytics.tasks" :key="task.id" class="soft-surface pa-4">
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0">
                <p class="text-sm font-bold">{{ taskTypeText(task.taskType) }}</p>
                <p class="mt-1 truncate text-xs text-medium-emphasis">{{ task.objectTitle || task.taskId }}</p>
              </div>
              <v-chip :color="statusColor(task.status)" size="small" variant="tonal">{{ statusText(task.status) }}</v-chip>
            </div>
            <p v-if="task.error" class="mt-3 text-xs text-error">{{ friendlyError(task.error) }}</p>
            <div class="mt-4 flex items-center justify-between gap-3">
              <span class="text-xs text-medium-emphasis">{{ formatDate(task.startedAt || task.createdAt) }}</span>
              <v-btn
                size="small"
                variant="tonal"
                color="primary"
                class="text-none"
                :disabled="task.status !== 'failed'"
                :loading="analytics.retryingTaskId === task.id"
                @click="retryTask(task)"
              >
                Повторить
              </v-btn>
            </div>
          </v-card>
        </div>
      </div>
    </v-card>
  </div>
</template>

<style scoped>
.analytics-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}
.analytics-table th {
  color: rgba(var(--v-theme-on-surface), .58);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: .08em;
  padding: 14px 16px;
  text-align: left;
  text-transform: uppercase;
}
.analytics-table td {
  border-top: 1px solid rgba(var(--v-border-color), .09);
  padding: 14px 16px;
  vertical-align: top;
}
.analytics-table tr:hover td {
  background: rgba(var(--v-theme-primary), .035);
}
.truncate-code {
  display: block;
  max-width: 170px;
  overflow: hidden;
  color: rgba(var(--v-theme-on-surface), .7);
  font-size: 11px;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
