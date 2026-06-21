import type {
  AiFillResponse,
  AiFillStatusResponse,
  DocumentFormat,
  DocumentLanguage,
  PdfGenerationResponse,
  RenderTranslationResponse,
  RenderTranslationStatusResponse,
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
    },
    downloadDocument(id: string, language: DocumentLanguage, format: DocumentFormat) {
      return request<Blob>(`/syllabuses/${id}/download-document/?language=${language}&format=${format}`, {
        responseType: 'blob',
        showErrorToast: false
      })
    },
    translateRendered(id: string) {
      return request<RenderTranslationResponse>(`/syllabuses/${id}/translate-rendered/`, {
        method: 'POST',
        showErrorToast: false
      })
    },
    getRenderTranslationStatus(id: string) {
      return request<RenderTranslationStatusResponse>(`/syllabuses/${id}/render-translation-status/`, {
        showErrorToast: false
      })
    },
    aiFill(id: string) {
      return request<AiFillResponse>(`/syllabuses/${id}/ai-fill/`, {
        method: 'POST',
        showErrorToast: false
      })
    },
    getAiFillStatus(id: string) {
      return request<AiFillStatusResponse>(`/syllabuses/${id}/ai-fill-status/`, {
        showErrorToast: false
      })
    }
  }
}
