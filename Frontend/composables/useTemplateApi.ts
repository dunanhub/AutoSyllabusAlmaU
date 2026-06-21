import type { TemplateRecord, TemplateTranslationResponse } from '~/stores/templates'

export interface TemplatesListResponse {
  results?: TemplateRecord[]
}

export interface TemplateTranslateResponse {
  taskId: string
  status: TemplateRecord['translationStatus']
}

export function useTemplateApi() {
  const { request } = useApi()

  return {
    list() {
      return request<TemplateRecord[] | TemplatesListResponse>('/templates/')
    },
    get(id: string) {
      return request<TemplateRecord>(`/templates/${id}/`)
    },
    create(payload: Partial<TemplateRecord>) {
      return request<TemplateRecord, Partial<TemplateRecord>>('/templates/', { method: 'POST', body: payload })
    },
    update(id: string, payload: Partial<TemplateRecord>) {
      return request<TemplateRecord, Partial<TemplateRecord>>(`/templates/${id}/`, { method: 'PATCH', body: payload })
    },
    remove(id: string) {
      return request<unknown>(`/templates/${id}/`, { method: 'DELETE' })
    },
    setDefault(id: string) {
      return request<TemplateRecord>(`/templates/${id}/set-default/`, { method: 'POST' })
    },
    translate(id: string) {
      return request<TemplateTranslateResponse>(`/templates/${id}/translate/`, {
        method: 'POST',
        showErrorToast: false
      })
    },
    translations(id: string) {
      return request<TemplateTranslationResponse>(`/templates/${id}/translations/`, {
        showErrorToast: false
      })
    }
  }
}
