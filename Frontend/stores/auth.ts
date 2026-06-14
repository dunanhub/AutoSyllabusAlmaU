import { defineStore } from 'pinia'

const ACCESS_KEY = 'sgs-auth-access'
const REFRESH_KEY = 'sgs-auth-refresh'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<{ id?: number | string; email: string; first_name?: string; last_name?: string; is_staff?: boolean } | null>(null)
  const accessToken = ref('')
  const refreshToken = ref('')
  const initialized = ref(false)
  const isAuthenticated = computed(() => Boolean(accessToken.value))

  function persistTokens() {
    if (!import.meta.client) return
    if (accessToken.value) localStorage.setItem(ACCESS_KEY, accessToken.value)
    else localStorage.removeItem(ACCESS_KEY)
    if (refreshToken.value) localStorage.setItem(REFRESH_KEY, refreshToken.value)
    else localStorage.removeItem(REFRESH_KEY)
  }

  async function initialize() {
    if (initialized.value || !import.meta.client) return
    accessToken.value = localStorage.getItem(ACCESS_KEY) || ''
    refreshToken.value = localStorage.getItem(REFRESH_KEY) || ''

    if (refreshToken.value && !accessToken.value) {
      await refreshAccessToken()
    }

    if (accessToken.value) {
      try {
        await fetchCurrentUser()
      } catch {
        logout()
      }
    }
    initialized.value = true
  }

  function setTokens(access: string, refresh: string) {
    accessToken.value = access
    refreshToken.value = refresh
    persistTokens()
  }

  async function login(email: string, password: string) {
    const authApi = useAuthApi()
    const tokens = await authApi.login({ email, password })
    setTokens(tokens.access, tokens.refresh)
    await fetchCurrentUser()
    return user.value
  }

  async function fetchCurrentUser() {
    if (!accessToken.value) return null
    const authApi = useAuthApi()
    user.value = await authApi.me()
    return user.value
  }

  async function refreshAccessToken() {
    if (!refreshToken.value) return false
    try {
      const authApi = useAuthApi()
      const response = await authApi.refresh({ refresh: refreshToken.value })
      accessToken.value = response.access
      persistTokens()
      return true
    } catch {
      logout()
      return false
    }
  }

  function logout() {
    user.value = null
    accessToken.value = ''
    refreshToken.value = ''

    try {
      const syllabusStore = useSyllabusStore()
      syllabusStore.reset()
    } catch {
      // store may be unavailable during early initialization
    }

    if (import.meta.client) {
      localStorage.removeItem(ACCESS_KEY)
      localStorage.removeItem(REFRESH_KEY)
    }
  }

  return { user, accessToken, refreshToken, initialized, isAuthenticated, initialize, login, logout, fetchCurrentUser, refreshAccessToken }
})
