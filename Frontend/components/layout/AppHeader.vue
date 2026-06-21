<script setup lang="ts">
import { mdiChevronDown, mdiMagnify, mdiMenu, mdiMoonWaningCrescent, mdiWhiteBalanceSunny } from '@mdi/js'

const emit = defineEmits<{ toggleDrawer: [] }>()
const route = useRoute()
const auth = useAuthStore()
const { isDark, toggleTheme } = useAppTheme()
const search = ref('')
const isMounted = ref(false)

const sectionName = computed(() => {
  if (route.path === '/dashboard') return 'Обзор'
  if (route.path === '/templates') return 'Шаблоны'
  if (route.path === '/analytics') return 'Аналитика'
  if (route.path === '/settings') return 'Настройки'
  if (route.path.includes('/create')) return 'Новый силлабус'
  if (route.path.includes('/edit')) return 'Редактирование'
  if (/\/syllabuses\/[^/]+$/.test(route.path)) return 'Предпросмотр'
  return 'Силлабусы'
})

const profileEmail = computed(() => (isMounted.value ? auth.user?.email || '' : ''))
const profileInitials = computed(() => profileEmail.value.slice(0, 2).toUpperCase() || 'SG')

onMounted(() => {
  isMounted.value = true
})
</script>

<template>
  <v-app-bar flat height="72" class="app-header" border="b">
    <v-app-bar-nav-icon :icon="mdiMenu" aria-label="Открыть меню" @click="emit('toggleDrawer')" />
    <div class="ml-1 hidden sm:block">
      <p class="text-[10px] font-extrabold uppercase tracking-[0.16em] text-primary">Syllabus Generator</p>
      <p class="text-sm font-bold">{{ sectionName }}</p>
    </div>

    <v-spacer />
    <v-text-field
      v-model="search"
      :prepend-inner-icon="mdiMagnify"
      placeholder="Поиск по workspace"
      density="compact"
      variant="solo-filled"
      flat
      hide-details
      class="mr-3 hidden max-w-[300px] lg:block"
    />
    <!-- <v-chip size="small" variant="tonal" color="primary" class="mr-2 hidden md:inline-flex">Demo workspace</v-chip> -->
    <v-btn
      :icon="isDark ? mdiWhiteBalanceSunny : mdiMoonWaningCrescent"
      variant="text"
      :aria-label="isDark ? 'Включить светлую тему' : 'Включить темную тему'"
      @click="toggleTheme"
    />
    <!-- <v-btn :icon="mdiBellOutline" variant="text" aria-label="Уведомления">
      <v-badge color="primary" dot />
    </v-btn> -->
    <v-menu>
      <template #activator="{ props }">
        <v-btn v-bind="props" variant="text" class="ml-1 px-2">
          <v-avatar color="primary" size="34" class="mr-2 font-weight-bold">
            {{ profileInitials }}
          </v-avatar>
          <span class="hidden max-w-40 truncate text-xs font-bold xl:inline">{{ profileEmail }}</span>
          <v-icon :icon="mdiChevronDown" size="16" class="ml-1" />
        </v-btn>
      </template>
      <v-list density="compact">
        <v-list-item title="Профиль преподавателя" subtitle="Demo workspace" />
      </v-list>
    </v-menu>
  </v-app-bar>
</template>

<style scoped>
.app-header {
  background: rgba(var(--v-theme-surface), .92) !important;
  backdrop-filter: blur(18px);
}
</style>
