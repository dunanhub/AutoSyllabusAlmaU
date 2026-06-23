import type { AnalyticsSummary, AnalyticsTask, AnalyticsTaskFilters } from '~/composables/useAnalyticsApi'

export const useAnalyticsStore = defineStore('analytics', () => {
  const summary = ref<AnalyticsSummary | null>(null)
  const tasks = ref<AnalyticsTask[]>([])
  const loadingSummary = ref(false)
  const loadingTasks = ref(false)
  const retryingTaskId = ref('')

  const hasProcessingTasks = computed(() => tasks.value.some(task => ['queued', 'processing'].includes(task.status)))

  async function fetchSummary() {
    loadingSummary.value = true
    try {
      summary.value = await useAnalyticsApi().summary()
    } finally {
      loadingSummary.value = false
    }
  }

  async function fetchTasks(filters: AnalyticsTaskFilters = {}) {
    loadingTasks.value = true
    try {
      tasks.value = await useAnalyticsApi().tasks(filters)
    } finally {
      loadingTasks.value = false
    }
  }

  async function refresh(filters: AnalyticsTaskFilters = {}) {
    await Promise.all([fetchSummary(), fetchTasks(filters)])
  }

  async function retryTask(id: string, filters: AnalyticsTaskFilters = {}) {
    retryingTaskId.value = id
    try {
      const retried = await useAnalyticsApi().retryTask(id)
      tasks.value = [retried, ...tasks.value]
      await fetchSummary()
      await fetchTasks(filters)
      return retried
    } finally {
      retryingTaskId.value = ''
    }
  }

  return {
    summary,
    tasks,
    loadingSummary,
    loadingTasks,
    retryingTaskId,
    hasProcessingTasks,
    fetchSummary,
    fetchTasks,
    refresh,
    retryTask
  }
})

