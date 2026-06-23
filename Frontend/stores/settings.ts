export type WorkspaceLanguage = 'ru' | 'kz' | 'en'

export interface WorkspaceSettings {
  preferredLanguage: WorkspaceLanguage
  autoOpenPreview: boolean
  showAiHelper: boolean
  compactMode: boolean
}

const SETTINGS_KEY = 'sgs-settings-v1'

const defaults: WorkspaceSettings = {
  preferredLanguage: 'ru',
  autoOpenPreview: true,
  showAiHelper: true,
  compactMode: false,
}

function normalizeSettings(value: Partial<WorkspaceSettings> | null): WorkspaceSettings {
  return {
    preferredLanguage: ['ru', 'kz', 'en'].includes(String(value?.preferredLanguage))
      ? value?.preferredLanguage as WorkspaceLanguage
      : defaults.preferredLanguage,
    autoOpenPreview: typeof value?.autoOpenPreview === 'boolean' ? value.autoOpenPreview : defaults.autoOpenPreview,
    showAiHelper: typeof value?.showAiHelper === 'boolean' ? value.showAiHelper : defaults.showAiHelper,
    compactMode: typeof value?.compactMode === 'boolean' ? value.compactMode : defaults.compactMode,
  }
}

export const useSettingsStore = defineStore('settings', () => {
  const preferences = ref<WorkspaceSettings>({ ...defaults })
  const initialized = ref(false)

  function initialize() {
    if (initialized.value || !import.meta.client) return
    try {
      const saved = JSON.parse(localStorage.getItem(SETTINGS_KEY) || 'null') as Partial<WorkspaceSettings> | null
      preferences.value = normalizeSettings(saved)
    } catch {
      preferences.value = { ...defaults }
    }
    initialized.value = true
  }

  function save(next?: Partial<WorkspaceSettings>) {
    if (next) preferences.value = normalizeSettings({ ...preferences.value, ...next })
    if (import.meta.client) localStorage.setItem(SETTINGS_KEY, JSON.stringify(preferences.value))
  }

  function resetPreferences() {
    preferences.value = { ...defaults }
    if (import.meta.client) localStorage.removeItem(SETTINGS_KEY)
  }

  return {
    preferences,
    initialized,
    initialize,
    save,
    resetPreferences,
  }
})
