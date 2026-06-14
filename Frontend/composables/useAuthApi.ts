export interface LoginPayload {
  email: string
  password: string
}

export interface TokenPair {
  access: string
  refresh: string
}

export interface CurrentUserResponse {
  id: number | string
  email: string
  first_name?: string
  last_name?: string
  is_staff?: boolean
}

export function useAuthApi() {
  const { request } = useApi()

  return {
    login(payload: LoginPayload) {
      return request<TokenPair, LoginPayload>('/auth/login/', { method: 'POST', body: payload, requiresAuth: false, retryOnUnauthorized: false })
    },
    refresh(payload: { refresh: string }) {
      return request<{ access: string }, { refresh: string }>('/auth/refresh/', { method: 'POST', body: payload, requiresAuth: false, retryOnUnauthorized: false })
    },
    me() {
      return request<CurrentUserResponse>('/auth/me/')
    }
  }
}
