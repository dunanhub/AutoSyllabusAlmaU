export default defineNuxtPlugin((nuxtApp) => {
  const initialize = async () => {
    const auth = useAuthStore()
    await auth.initialize()
    if (auth.isAuthenticated) {
      await useSyllabusStore().initialize()
    }
  }

  if (nuxtApp.isHydrating) {
    nuxtApp.hook('app:mounted', () => { void initialize() })
  } else {
    void initialize()
  }
})
