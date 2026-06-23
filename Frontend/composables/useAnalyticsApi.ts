export type AnalyticsTaskStatus = 'queued' | 'processing' | 'completed' | 'failed'
export type AnalyticsTaskType = 'template_translation' | 'syllabus_ai_fill' | 'render_translation' | 'document_generation'
export type AnalyticsPeriod = 'all' | 'today' | '7d' | '30d'

export interface AnalyticsTask {
  id: string
  taskId: string
  taskType: AnalyticsTaskType
  objectType: 'template' | 'syllabus'
  objectId: string
  objectTitle: string
  status: AnalyticsTaskStatus
  retryAction: string
  error: string
  startedAt: string | null
  finishedAt: string | null
  createdAt: string
  updatedAt: string
}

export interface AnalyticsSummary {
  syllabuses: {
    total: number
    draft: number
    ready: number
  }
  templates: {
    total: number
    valid: number
    draft: number
    default: number
    translation: Record<string, number>
  }
  documents: {
    generated: number
    processing: number
    failed: number
    notGenerated: number
  }
  automation: {
    ai: Record<string, number>
    renderTranslation: Record<string, number>
    tasks: Record<string, number>
    failedTotal: number
    processingTotal: number
  }
  recentErrors: AnalyticsTask[]
  activeTasks: AnalyticsTask[]
}

export interface AnalyticsTaskFilters {
  status?: AnalyticsTaskStatus | ''
  type?: AnalyticsTaskType | ''
  search?: string
  period?: AnalyticsPeriod
}

export function useAnalyticsApi() {
  const { request } = useApi()

  return {
    summary() {
      return request<AnalyticsSummary>('/analytics/summary/')
    },
    tasks(filters: AnalyticsTaskFilters = {}) {
      return request<AnalyticsTask[]>('/analytics/tasks/', {
        query: {
          status: filters.status || undefined,
          type: filters.type || undefined,
          search: filters.search || undefined,
          period: filters.period || undefined,
        },
      })
    },
    retryTask(id: string) {
      return request<AnalyticsTask>(`/analytics/tasks/${id}/retry/`, {
        method: 'POST',
        showErrorToast: false
      })
    }
  }
}
