<script setup lang="ts">
import {
  mdiAccountCircleOutline,
  mdiAlertCircleOutline,
  mdiApi,
  mdiBrain,
  mdiBrushVariant,
  mdiCloudSyncOutline,
  mdiContentSaveOutline,
  mdiDatabaseRefreshOutline,
  mdiFileDocumentMultipleOutline,
  mdiLogout,
  mdiRefresh,
  mdiShieldCheckOutline,
  mdiTrashCanOutline,
  mdiTuneVariant,
  mdiViewDashboardOutline,
} from '@mdi/js'

definePageMeta({ middleware: 'auth' })

const auth = useAuthStore()
const templates = useTemplatesStore()
const syllabuses = useSyllabusStore()
const analytics = useAnalyticsStore()
const settings = useSettingsStore()
const appTheme = useAppTheme()
const { show } = useAppToast()

const profileLoading = ref(false)
const profileSaving = ref(false)
const dataLoading = ref(false)
const apiChecking = ref(false)
const apiStatus = ref<'unknown' | 'ok' | 'error'>('unknown')
const resetDialog = ref(false)
const profileForm = reactive({
  firstName: '',
  lastName: '',
})

const languageOptions = [
  { title: 'Русский', value: 'ru' },
  { title: 'Қазақша', value: 'kz' },
  { title: 'English', value: 'en' },
]

const themeMode = computed({
  get: () => appTheme.isDark.value ? 'dark' : 'light',
  set: (value: string) => {
    appTheme.setTheme(value === 'light' ? 'almauLight' : 'almauDark')
    show('Тема сохранена', 'success')
  },
})

const displayName = computed(() => {
  const first = auth.user?.first_name || ''
  const last = auth.user?.last_name || ''
  const full = `${first} ${last}`.trim()
  return full || auth.user?.email || 'Пользователь'
})

const initials = computed(() => {
  const source = displayName.value || 'A'
  return source
    .split(/\s+/)
    .map(part => part[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()
})

const templateStats = computed(() => ({
  total: templates.templates.length,
  valid: templates.templates.filter(item => item.validationStatus === 'valid').length,
  draft: templates.templates.filter(item => item.validationStatus !== 'valid').length,
  failed: templates.templates.filter(item => item.translationStatus === 'failed').length,
  translating: templates.templates.filter(item => item.translationStatus === 'translating').length,
  defaultTemplate: templates.templates.find(item => item.isDefault) || null,
}))

const syllabusStats = computed(() => ({
  total: syllabuses.syllabuses.length,
  generated: syllabuses.syllabuses.filter(item => item.pdfStatus === 'generated').length,
  failed: syllabuses.syllabuses.filter(item => item.pdfStatus === 'failed').length,
}))

const integrationItems = computed(() => [
  {
    title: 'Backend API',
    description: apiStatus.value === 'ok'
      ? 'JWT-сессия и API доступны.'
      : apiStatus.value === 'error'
        ? 'API сейчас не отвечает или токен недействителен.'
        : 'Нажмите “Проверить API”, чтобы обновить статус.',
    status: apiStatus.value,
    icon: mdiApi,
  },
  {
    title: 'Gemini AI',
    description: 'Проверяется через задачи перевода и AI-дозаполнения. Ошибки и retry доступны в аналитике.',
    status: (analytics.summary?.automation.failedTotal ?? 0) > 0 ? 'error' : 'unknown',
    icon: mdiBrain,
  },
  {
    title: 'Celery / Redis',
    description: `${analytics.summary?.automation.processingTotal ?? 0} активных фоновых задач. История доступна в аналитике.`,
    status: (analytics.summary?.automation.processingTotal ?? 0) > 0 ? 'ok' : 'unknown',
    icon: mdiCloudSyncOutline,
  },
])

onMounted(async () => {
  settings.initialize()
  await Promise.allSettled([
    auth.initialize(),
    templates.initialize(),
    syllabuses.initialize(),
    analytics.fetchSummary(),
  ])
  syncProfileForm()
})

watch(() => auth.user, syncProfileForm, { deep: true })

function syncProfileForm() {
  profileForm.firstName = auth.user?.first_name || ''
  profileForm.lastName = auth.user?.last_name || ''
}

function errorMessage(error: unknown, fallback: string) {
  const data = (error as { data?: unknown })?.data
  if (typeof data === 'string') return data
  if (data && typeof data === 'object') {
    const first = Object.values(data as Record<string, unknown>)[0]
    if (Array.isArray(first)) return String(first[0])
    if (typeof first === 'string') return first
  }
  return fallback
}

function savePreferences() {
  settings.save()
  show('Настройки сохранены', 'success')
}

async function saveProfile() {
  profileSaving.value = true
  try {
    await auth.updateProfile({
      firstName: profileForm.firstName.trim(),
      lastName: profileForm.lastName.trim(),
    })
    apiStatus.value = 'ok'
    show('Профиль сохранён', 'success')
  } catch (error) {
    show(errorMessage(error, 'Не удалось сохранить профиль'), 'error')
  } finally {
    profileSaving.value = false
  }
}

async function refreshProfile() {
  profileLoading.value = true
  try {
    await auth.fetchCurrentUser()
    syncProfileForm()
    apiStatus.value = 'ok'
    show('Профиль обновлён', 'success')
  } catch {
    apiStatus.value = 'error'
    show('Не удалось проверить API', 'error')
  } finally {
    profileLoading.value = false
  }
}

async function refreshWorkspaceData() {
  dataLoading.value = true
  try {
    await Promise.all([
      syllabuses.refresh(),
      templates.initialize(true),
      analytics.refresh(),
    ])
    show('Данные workspace обновлены', 'success')
  } catch {
    show('Не удалось обновить данные', 'error')
  } finally {
    dataLoading.value = false
  }
}

async function checkApi() {
  apiChecking.value = true
  try {
    await auth.fetchCurrentUser()
    await analytics.fetchSummary()
    apiStatus.value = 'ok'
    show('API доступен', 'success')
  } catch {
    apiStatus.value = 'error'
    show('Не удалось проверить API', 'error')
  } finally {
    apiChecking.value = false
  }
}

function resetLocalPreferences() {
  settings.resetPreferences()
  resetDialog.value = false
  show('Локальные настройки очищены', 'success')
}

function logout() {
  auth.logout()
  navigateTo('/login')
}

function statusColor(status: string) {
  return status === 'ok' ? 'success' : status === 'error' ? 'error' : 'info'
}

function statusText(status: string) {
  return status === 'ok' ? 'Работает' : status === 'error' ? 'Ошибка' : 'Инфо'
}
</script>

<template>
  <div class="space-y-6">
    <PageHeader
      eyebrow="Workspace"
      title="Настройки"
      description="Профиль, внешний вид, локальные предпочтения и диагностика проекта."
    >
      <template #actions>
        <v-tooltip text="Обновляет дисциплины, шаблоны и аналитику задач из backend.">
          <template #activator="{ props }">
            <v-btn
              v-bind="props"
              color="primary"
              variant="flat"
              class="text-none font-weight-bold"
              :prepend-icon="mdiRefresh"
              :loading="dataLoading"
              :disabled="dataLoading"
              @click="refreshWorkspaceData"
            >
              Обновить данные
            </v-btn>
          </template>
        </v-tooltip>
      </template>
    </PageHeader>

    <section class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <v-card class="app-surface pa-5">
        <v-avatar color="primary" variant="tonal" size="42"><v-icon :icon="mdiFileDocumentMultipleOutline" /></v-avatar>
        <p class="mt-5 text-3xl font-black">{{ syllabusStats.total }}</p>
        <p class="mt-1 text-sm font-bold">Дисциплины</p>
        <p class="mt-1 text-xs text-medium-emphasis">{{ syllabusStats.generated }} документов готовы · {{ syllabusStats.failed }} ошибок</p>
      </v-card>
      <v-card class="app-surface pa-5">
        <v-avatar color="info" variant="tonal" size="42"><v-icon :icon="mdiViewDashboardOutline" /></v-avatar>
        <p class="mt-5 text-3xl font-black">{{ templateStats.total }}</p>
        <p class="mt-1 text-sm font-bold">Шаблоны</p>
        <p class="mt-1 text-xs text-medium-emphasis">{{ templateStats.valid }} готовы · {{ templateStats.draft }} draft</p>
      </v-card>
      <v-card class="app-surface pa-5">
        <v-avatar color="warning" variant="tonal" size="42"><v-icon :icon="mdiBrain" /></v-avatar>
        <p class="mt-5 text-3xl font-black">{{ analytics.summary?.automation.failedTotal ?? 0 }}</p>
        <p class="mt-1 text-sm font-bold">Ошибки AI/Celery</p>
        <p class="mt-1 text-xs text-medium-emphasis">{{ analytics.summary?.automation.processingTotal ?? 0 }} задач в работе</p>
      </v-card>
      <v-card class="app-surface pa-5">
        <v-avatar color="success" variant="tonal" size="42"><v-icon :icon="mdiShieldCheckOutline" /></v-avatar>
        <p class="mt-5 text-3xl font-black">{{ auth.isAuthenticated ? 'ON' : 'OFF' }}</p>
        <p class="mt-1 text-sm font-bold">JWT session</p>
        <p class="mt-1 text-xs text-medium-emphasis">Токены хранятся отдельно от UI-настроек</p>
      </v-card>
    </section>

    <section class="grid gap-4 xl:grid-cols-[.9fr_1.1fr]">
      <v-card class="app-surface overflow-hidden">
        <div class="border-b border-white/10 p-5">
          <div class="flex items-center gap-3">
            <v-avatar color="primary" size="52" class="font-weight-black">{{ initials }}</v-avatar>
            <div class="min-w-0">
              <h2 class="truncate text-lg font-black">{{ displayName }}</h2>
              <p class="truncate text-sm text-medium-emphasis">{{ auth.user?.email || 'Email не загружен' }}</p>
            </div>
          </div>
        </div>
        <div class="space-y-4 p-5">
          <div class="grid gap-3 sm:grid-cols-2">
            <v-text-field
              v-model="profileForm.firstName"
              label="Имя"
              variant="outlined"
              density="comfortable"
              hide-details
              autocomplete="given-name"
            />
            <v-text-field
              v-model="profileForm.lastName"
              label="Фамилия"
              variant="outlined"
              density="comfortable"
              hide-details
              autocomplete="family-name"
            />
          </div>
          <div class="soft-surface rounded-xl p-4">
            <p class="text-xs text-medium-emphasis">Email</p>
            <p class="mt-1 font-bold">{{ auth.user?.email || 'Не загружен' }}</p>
          </div>
          <div class="soft-surface rounded-xl p-4">
            <p class="text-xs text-medium-emphasis">Роль</p>
            <p class="mt-1 font-bold">{{ auth.user?.is_staff ? 'Администратор' : 'Преподаватель AlmaU' }}</p>
          </div>
          <v-alert type="info" variant="tonal" density="comfortable">
            Email и пароль остаются read-only. Сейчас можно безопасно обновлять имя и фамилию.
          </v-alert>
          <div class="grid gap-2 sm:grid-cols-2">
            <v-tooltip text="Сохраняет имя и фамилию в backend-профиле текущего пользователя.">
              <template #activator="{ props }">
                <v-btn
                  v-bind="props"
                  block
                  color="primary"
                  variant="flat"
                  class="text-none font-weight-bold"
                  :prepend-icon="mdiContentSaveOutline"
                  :loading="profileSaving"
                  :disabled="profileSaving || profileLoading"
                  @click="saveProfile"
                >
                  Сохранить профиль
                </v-btn>
              </template>
            </v-tooltip>
            <v-tooltip text="Заново загружает профиль из /api/auth/me/ и сбрасывает несохранённые изменения.">
              <template #activator="{ props }">
                <v-btn
                  v-bind="props"
                  block
                  color="primary"
                  variant="tonal"
                  class="text-none font-weight-bold"
                  :prepend-icon="mdiAccountCircleOutline"
                  :loading="profileLoading"
                  :disabled="profileLoading || profileSaving"
                  @click="refreshProfile"
                >
                  Обновить профиль
                </v-btn>
              </template>
            </v-tooltip>
          </div>
        </div>
      </v-card>

      <v-card class="app-surface pa-5">
        <div class="mb-5 flex items-center gap-3">
          <v-avatar color="primary" variant="tonal"><v-icon :icon="mdiBrushVariant" /></v-avatar>
          <div>
            <h2 class="text-base font-bold">Внешний вид и workspace defaults</h2>
            <p class="text-xs text-medium-emphasis">Эти настройки хранятся только в браузере.</p>
          </div>
        </div>

        <div class="grid gap-5 lg:grid-cols-2">
          <v-tooltip text="Тема сохраняется в localStorage ключ sgs-theme и применяется после reload.">
            <template #activator="{ props }">
              <div v-bind="props">
                <p class="mb-2 text-xs font-bold uppercase tracking-[.14em] text-medium-emphasis">Тема</p>
                <v-btn-toggle v-model="themeMode" mandatory divided class="w-full">
                  <v-btn value="dark" class="flex-1 text-none">Dark</v-btn>
                  <v-btn value="light" class="flex-1 text-none">Light</v-btn>
                </v-btn-toggle>
              </div>
            </template>
          </v-tooltip>
          <v-tooltip text="Используется как предпочитаемый язык preview и будущих workspace-действий.">
            <template #activator="{ props }">
              <v-select
                v-bind="props"
                v-model="settings.preferences.preferredLanguage"
                :items="languageOptions"
                label="Язык preview по умолчанию"
                variant="outlined"
                density="comfortable"
                hide-details
                @update:model-value="savePreferences"
              />
            </template>
          </v-tooltip>
        </div>

        <div class="mt-6 grid gap-3 sm:grid-cols-2">
          <v-tooltip text="После открытия конструктора или дисциплины preview может открываться автоматически.">
            <template #activator="{ props }">
              <v-switch
                v-bind="props"
                v-model="settings.preferences.autoOpenPreview"
                color="primary"
                hide-details
                label="Автооткрытие preview"
                @update:model-value="savePreferences"
              />
            </template>
          </v-tooltip>
          <v-tooltip text="Показывает AI-помощник и кнопки дозаполнения там, где они поддерживаются.">
            <template #activator="{ props }">
              <v-switch
                v-bind="props"
                v-model="settings.preferences.showAiHelper"
                color="primary"
                hide-details
                label="Показывать AI-помощник"
                @update:model-value="savePreferences"
              />
            </template>
          </v-tooltip>
          <v-tooltip text="Включает более плотный workspace UI для небольших экранов и длинных форм.">
            <template #activator="{ props }">
              <v-switch
                v-bind="props"
                v-model="settings.preferences.compactMode"
                color="primary"
                hide-details
                label="Компактный режим"
                @update:model-value="savePreferences"
              />
            </template>
          </v-tooltip>
        </div>
      </v-card>
    </section>

    <section class="grid gap-4 xl:grid-cols-2">
      <v-card class="app-surface pa-5">
        <div class="mb-5 flex items-center justify-between gap-3">
          <div class="flex items-center gap-3">
            <v-avatar color="info" variant="tonal"><v-icon :icon="mdiViewDashboardOutline" /></v-avatar>
            <div>
              <h2 class="text-base font-bold">Шаблоны</h2>
              <p class="text-xs text-medium-emphasis">Default-шаблон и состояние переводов.</p>
            </div>
          </div>
          <v-tooltip text="Переходит на страницу Template Builder со списком шаблонов.">
            <template #activator="{ props }">
              <v-btn v-bind="props" variant="text" color="primary" class="text-none" @click="navigateTo('/templates')">Открыть</v-btn>
            </template>
          </v-tooltip>
        </div>
        <div class="grid gap-3 sm:grid-cols-3">
          <div class="soft-surface rounded-xl p-4">
            <p class="text-xs text-medium-emphasis">Готовые</p>
            <p class="mt-1 text-xl font-black text-success">{{ templateStats.valid }}</p>
          </div>
          <div class="soft-surface rounded-xl p-4">
            <p class="text-xs text-medium-emphasis">Draft</p>
            <p class="mt-1 text-xl font-black text-warning">{{ templateStats.draft }}</p>
          </div>
          <div class="soft-surface rounded-xl p-4">
            <p class="text-xs text-medium-emphasis">Failed</p>
            <p class="mt-1 text-xl font-black text-error">{{ templateStats.failed }}</p>
          </div>
        </div>
        <v-alert class="mt-4" type="success" variant="tonal" density="comfortable">
          Default: {{ templateStats.defaultTemplate?.title || 'Не выбран' }}
        </v-alert>
        <v-tooltip text="Принудительно перезагружает шаблоны из backend API.">
          <template #activator="{ props }">
            <v-btn
              v-bind="props"
              block
              color="primary"
              variant="tonal"
              class="mt-4 text-none font-weight-bold"
              :loading="templates.loading"
              :disabled="templates.loading"
              :prepend-icon="mdiRefresh"
              @click="templates.initialize(true).then(() => show('Шаблоны обновлены', 'success')).catch(() => show('Не удалось обновить шаблоны', 'error'))"
            >
              Обновить шаблоны
            </v-btn>
          </template>
        </v-tooltip>
      </v-card>

      <v-card class="app-surface pa-5">
        <div class="mb-5 flex items-center justify-between gap-3">
          <div class="flex items-center gap-3">
            <v-avatar color="primary" variant="tonal"><v-icon :icon="mdiTuneVariant" /></v-avatar>
            <div>
              <h2 class="text-base font-bold">Интеграции</h2>
              <p class="text-xs text-medium-emphasis">Проверка API и подсказки по фоновой обработке.</p>
            </div>
          </div>
          <v-tooltip text="Проверяет JWT-сессию, /auth/me/ и analytics summary.">
            <template #activator="{ props }">
              <v-btn
                v-bind="props"
                color="primary"
                variant="tonal"
                class="text-none"
                :loading="apiChecking"
                :disabled="apiChecking"
                :prepend-icon="mdiApi"
                @click="checkApi"
              >
                Проверить API
              </v-btn>
            </template>
          </v-tooltip>
        </div>
        <div class="space-y-3">
          <div v-for="item in integrationItems" :key="item.title" class="soft-surface rounded-xl p-4">
            <div class="flex items-start justify-between gap-3">
              <div class="flex gap-3">
                <v-avatar :color="statusColor(item.status)" variant="tonal" size="38"><v-icon :icon="item.icon" /></v-avatar>
                <div>
                  <p class="text-sm font-bold">{{ item.title }}</p>
                  <p class="mt-1 text-xs leading-5 text-medium-emphasis">{{ item.description }}</p>
                </div>
              </div>
              <v-chip :color="statusColor(item.status)" size="small" variant="tonal">{{ statusText(item.status) }}</v-chip>
            </div>
          </div>
        </div>
        <v-tooltip text="Открывает мониторинг фоновых задач Celery, ошибок Gemini и retry.">
          <template #activator="{ props }">
            <v-btn
              v-bind="props"
              block
              variant="text"
              color="primary"
              class="mt-4 text-none"
              @click="navigateTo('/analytics')"
            >
              Открыть аналитику задач
            </v-btn>
          </template>
        </v-tooltip>
      </v-card>
    </section>

    <v-card class="app-surface pa-5">
      <div class="grid gap-5 xl:grid-cols-[1fr_auto] xl:items-center">
        <div class="flex items-start gap-3">
          <v-avatar color="error" variant="tonal"><v-icon :icon="mdiAlertCircleOutline" /></v-avatar>
          <div>
            <h2 class="text-base font-bold">Данные и безопасность</h2>
            <p class="mt-1 text-sm text-medium-emphasis">
              Можно обновить данные workspace, очистить только локальные UI-настройки или выйти из аккаунта.
            </p>
          </div>
        </div>
        <div class="flex flex-wrap gap-2">
          <v-tooltip text="Обновляет все рабочие данные без выхода из аккаунта.">
            <template #activator="{ props }">
              <v-btn
                v-bind="props"
                color="primary"
                variant="tonal"
                class="text-none"
                :prepend-icon="mdiDatabaseRefreshOutline"
                :loading="dataLoading"
                :disabled="dataLoading"
                @click="refreshWorkspaceData"
              >
                Refresh workspace
              </v-btn>
            </template>
          </v-tooltip>
          <v-tooltip text="Удаляет только локальные UI-предпочтения. JWT, шаблоны и backend-данные не трогает.">
            <template #activator="{ props }">
              <v-btn
                v-bind="props"
                color="warning"
                variant="tonal"
                class="text-none"
                :prepend-icon="mdiTrashCanOutline"
                @click="resetDialog = true"
              >
                Очистить UI-настройки
              </v-btn>
            </template>
          </v-tooltip>
          <v-tooltip text="Очищает JWT-токены текущей сессии и возвращает на страницу входа.">
            <template #activator="{ props }">
              <v-btn v-bind="props" color="error" variant="tonal" class="text-none" :prepend-icon="mdiLogout" @click="logout">
                Выйти
              </v-btn>
            </template>
          </v-tooltip>
        </div>
      </div>
    </v-card>

    <ConfirmModal
      :open="resetDialog"
      title="Очистить локальные настройки?"
      message="Будут удалены только UI-предпочтения settings. JWT-токены, шаблоны, силлабусы и backend-данные останутся без изменений."
      confirm-text="Очистить"
      @cancel="resetDialog = false"
      @confirm="resetLocalPreferences"
    />
  </div>
</template>

<style scoped>
:global(.v-tooltip > .v-overlay__content) {
  max-width: 280px;
  border: 1px solid rgba(var(--v-theme-primary), 0.28);
  border-radius: 14px;
  background: rgb(var(--v-theme-surface)) !important;
  color: rgb(var(--v-theme-on-surface)) !important;
  box-shadow: 0 18px 48px rgba(0, 0, 0, 0.24);
  font-size: 0.78rem;
  font-weight: 700;
  line-height: 1.45;
  padding: 10px 12px;
}
</style>
