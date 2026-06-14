import { useTheme } from 'vuetify'

export function useAppTheme() {
  const theme = useTheme()
  const isDark = computed(() => theme.global.name.value === 'almauDark')

  function setTheme(value: 'almauDark' | 'almauLight') {
    theme.global.name.value = value
    if (import.meta.client) localStorage.setItem('sgs-theme', value)
  }

  function toggleTheme() {
    setTheme(isDark.value ? 'almauLight' : 'almauDark')
  }

  onMounted(() => {
    const saved = localStorage.getItem('sgs-theme')
    if (saved === 'almauLight' || saved === 'almauDark') setTheme(saved)
  })

  return { isDark, toggleTheme, setTheme }
}
