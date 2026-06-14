type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'
type FetchBody = Record<string, any> | BodyInit | null | undefined

interface ApiFetchOptions<T extends FetchBody> {
  method?: HttpMethod
  body?: T
  query?: Record<string, string | number | boolean | undefined>
  requiresAuth?: boolean
  retryOnUnauthorized?: boolean
  responseType?: 'json' | 'blob'
  showErrorToast?: boolean
}

function normalizeBaseUrl(value: string) {
  return value.replace(/\/+$/, '')
}

export function useApi() {
  const config = useRuntimeConfig()
  const auth = useAuthStore()
  const apiError = useApiError()

  const baseURL = normalizeBaseUrl(config.public.apiUrl || 'http://localhost:8000/api')

  async function request<TResponse, TBody extends FetchBody = FetchBody>(path: string, options: ApiFetchOptions<TBody> = {} as ApiFetchOptions<TBody>, retried = false): Promise<TResponse> {
    try {
      const response = await $fetch<TResponse>(path, {
        baseURL,
        method: options.method ?? 'GET',
        body: options.body,
        query: options.query,
        responseType: options.responseType,
        headers: options.requiresAuth === false || !auth.accessToken
          ? undefined
          : { Authorization: `Bearer ${auth.accessToken}` }
      })
      return response
    } catch (error) {
      const status = (error as { status?: number })?.status
      if (status === 401 && options.requiresAuth !== false && !retried && auth.refreshToken && options.retryOnUnauthorized !== false) {
        const refreshed = await auth.refreshAccessToken()
        if (refreshed) return request<TResponse, TBody>(path, options, true)
      }
      if (options.showErrorToast !== false) apiError.handle(error)
      throw error
    }
  }

  return { baseURL, request }
}
