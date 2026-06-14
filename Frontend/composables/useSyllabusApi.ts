import type {
  PdfGenerationResponse,
  PdfStatusResponse,
  Syllabus,
  SyllabusInput,
  SyllabusStatus
} from '~/types/syllabus'

export interface SyllabusesListResponse {
  results?: Syllabus[]
}

export function useSyllabusApi() {
  const { request } = useApi()

  return {
    list() {
      return request<Syllabus[] | SyllabusesListResponse>('/syllabuses/')
    },
    get(id: string) {
      return request<Syllabus>(`/syllabuses/${id}/`)
    },
    create(payload: SyllabusInput) {
      return request<Syllabus, SyllabusInput>('/syllabuses/', { method: 'POST', body: payload })
    },
    update(id: string, payload: Partial<SyllabusInput>) {
      return request<Syllabus, Partial<SyllabusInput>>(`/syllabuses/${id}/`, { method: 'PUT', body: payload })
    },
    patch(id: string, payload: Partial<SyllabusInput>) {
      return request<Syllabus, Partial<SyllabusInput>>(`/syllabuses/${id}/`, { method: 'PATCH', body: payload })
    },
    remove(id: string) {
      return request<unknown>(`/syllabuses/${id}/`, { method: 'DELETE' })
    },
    duplicate(id: string) {
      return request<Syllabus>(`/syllabuses/${id}/duplicate/`, { method: 'POST' })
    },
    setStatus(id: string, status: SyllabusStatus) {
      return request<Syllabus, { status: SyllabusStatus }>(`/syllabuses/${id}/set-status/`, { method: 'POST', body: { status } })
    },
    generatePdf(id: string) {
      return request<PdfGenerationResponse>(`/syllabuses/${id}/generate-pdf/`, {
        method: 'POST',
        showErrorToast: false
      })
    },
    getPdfStatus(id: string) {
      return request<PdfStatusResponse>(`/syllabuses/${id}/pdf-status/`, {
        showErrorToast: false
      })
    },
    downloadPdf(id: string) {
      return request<Blob>(`/syllabuses/${id}/download-pdf/`, {
        responseType: 'blob',
        showErrorToast: false
      })
    }
  }
}
