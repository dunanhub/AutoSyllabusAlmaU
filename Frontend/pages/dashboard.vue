<script setup lang="ts">
import {
  mdiArrowRight, mdiCalendarClock, mdiCheckCircleOutline, mdiClockOutline,
  mdiFileDocumentMultipleOutline, mdiFileEditOutline, mdiPlus, mdiTrendingUp
} from '@mdi/js'
import type { Syllabus } from '~/types/syllabus'

definePageMeta({ middleware: 'auth' })
const store = useSyllabusStore()
const auth = useAuthStore()
const loading = ref(true)
const recent = computed(() => [...store.syllabuses].sort((a, b) => Date.parse(b.updatedAt) - Date.parse(a.updatedAt)).slice(0, 5))
const firstName = computed(() => auth.user?.email.split('@')[0] || 'преподаватель')

function completion(item: Syllabus) {
  return item.completion
}

const averageCompletion = computed(() => store.syllabuses.length
  ? Math.round(store.syllabuses.reduce((sum, item) => sum + completion(item), 0) / store.syllabuses.length)
  : 0)
const readyCount = computed(() => store.syllabuses.filter(item => item.status === 'ready').length)
const draftCount = computed(() => store.syllabuses.filter(item => item.status === 'draft').length)
const recentCount = computed(() => store.syllabuses.filter(item => Date.now() - Date.parse(item.updatedAt) < 604800000).length)
const readyPercent = computed(() => store.syllabuses.length ? Math.round(readyCount.value / store.syllabuses.length * 100) : 0)

const stats = computed(() => [
  { label: 'Все документы', value: store.syllabuses.length, icon: mdiFileDocumentMultipleOutline, color: 'primary', note: 'в рабочем пространстве' },
  { label: 'Черновики', value: draftCount.value, icon: mdiFileEditOutline, color: 'warning', note: 'требуют заполнения' },
  { label: 'Готовы', value: readyCount.value, icon: mdiCheckCircleOutline, color: 'secondary', note: `${readyPercent.value}% от общего числа` },
  { label: 'Изменены за 7 дней', value: recentCount.value, icon: mdiTrendingUp, color: 'info', note: 'активность команды' }
])

const formatDate = (date: string) => new Intl.DateTimeFormat('ru-RU', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }).format(new Date(date))

onMounted(async () => {
  try {
    await auth.initialize()
    await store.initialize()
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="space-y-6">
    <section class="hero-panel relative overflow-hidden rounded-2xl border border-white/10 p-6 text-white sm:p-8">
      <div class="relative z-10 grid gap-8 lg:grid-cols-[1fr_auto] lg:items-end">
        <div>
          <v-chip color="primary" variant="tonal" size="small" class="mb-4 font-weight-bold">DEMO WORKSPACE</v-chip>
          <h1 class="text-3xl font-black tracking-[-0.04em] sm:text-4xl">Добро пожаловать, {{ firstName }}</h1>
          <p class="mt-3 max-w-2xl text-sm leading-6 text-white/55">Контролируйте готовность документов, продолжайте редактирование и создавайте новые силлабусы в единой академической системе.</p>
        </div>
        <v-btn color="primary" size="large" :prepend-icon="mdiPlus" class="text-none font-weight-bold" @click="navigateTo('/syllabuses/create')">
          Создать силлабус
        </v-btn>
      </div>
    </section>

    <section v-if="loading" class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <v-card v-for="index in 4" :key="index" class="app-surface pa-5">
        <v-skeleton-loader type="heading, text, text" />
      </v-card>
    </section>

    <section v-else class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <v-card v-for="item in stats" :key="item.label" class="app-surface pa-5">
        <div class="flex items-start justify-between">
          <v-avatar :color="item.color" variant="tonal" size="42"><v-icon :icon="item.icon" /></v-avatar>
          <v-chip size="x-small" variant="text" color="success">LIVE</v-chip>
        </div>
        <p class="mt-5 text-3xl font-black">{{ item.value }}</p>
        <p class="mt-1 text-sm font-bold">{{ item.label }}</p>
        <p class="mt-1 text-xs text-medium-emphasis">{{ item.note }}</p>
      </v-card>
    </section>

    <section v-if="!loading" class="grid gap-4 xl:grid-cols-[1.3fr_.7fr]">
      <v-card class="app-surface pa-5 sm:pa-6">
        <div class="flex items-center justify-between">
          <div><h2 class="text-base font-bold">Готовность workspace</h2><p class="mt-1 text-xs text-medium-emphasis">Среднее заполнение всех документов</p></div>
          <span class="text-2xl font-black text-primary">{{ averageCompletion }}%</span>
        </div>
        <v-progress-linear :model-value="averageCompletion" color="primary" height="10" rounded class="mt-6" />
        <div class="mt-6 grid grid-cols-2 gap-3">
          <div class="soft-surface rounded-xl p-4"><p class="text-xs text-medium-emphasis">Готовые документы</p><p class="mt-2 text-xl font-black text-success">{{ readyCount }}</p></div>
          <div class="soft-surface rounded-xl p-4"><p class="text-xs text-medium-emphasis">В работе</p><p class="mt-2 text-xl font-black text-warning">{{ draftCount }}</p></div>
        </div>
      </v-card>

      <v-card class="app-surface pa-5 sm:pa-6">
        <h2 class="text-base font-bold">Распределение статусов</h2>
        <p class="mt-1 text-xs text-medium-emphasis">Текущее состояние реестра</p>
        <div class="mt-6 flex items-center justify-center">
          <v-progress-circular :model-value="readyPercent" :size="140" :width="14" color="primary">
            <div class="text-center"><strong class="block text-2xl">{{ readyPercent }}%</strong><span class="text-[10px] text-medium-emphasis">готовы</span></div>
          </v-progress-circular>
        </div>
      </v-card>
    </section>

    <section v-if="!loading" class="grid gap-4 xl:grid-cols-[1.45fr_.55fr]">
      <v-card class="app-surface overflow-hidden">
        <div class="flex items-center justify-between border-b border-white/10 px-5 py-4 sm:px-6">
          <div><h2 class="text-base font-bold">Последние силлабусы</h2><p class="mt-1 text-xs text-medium-emphasis">Недавно созданные и обновлённые документы</p></div>
          <v-btn variant="text" color="primary" :append-icon="mdiArrowRight" class="text-none" @click="navigateTo('/syllabuses')">Все силлабусы</v-btn>
        </div>
        <div v-if="recent.length">
          <button v-for="item in recent" :key="item.id" class="recent-row grid w-full gap-3 px-5 py-4 text-left sm:grid-cols-[minmax(0,1fr)_170px_120px_auto] sm:items-center sm:px-6" @click="navigateTo(`/syllabuses/${item.id}`)">
            <div class="flex min-w-0 items-center gap-3">
              <v-avatar color="primary" variant="tonal" size="38" class="font-weight-black">A</v-avatar>
              <div class="min-w-0"><p class="truncate text-sm font-bold">{{ item.titleInfo.codeAndName || 'Без названия' }}</p><p class="mt-1 truncate text-xs text-medium-emphasis">{{ item.titleInfo.educationalProgram || 'Программа не указана' }} · {{ item.titleInfo.instructorName || 'Преподаватель не указан' }}</p></div>
            </div>
            <div>
              <div class="mb-2 flex justify-between text-[10px] text-medium-emphasis"><span>Заполнение</span><strong>{{ completion(item) }}%</strong></div>
              <v-progress-linear :model-value="completion(item)" color="primary" height="5" rounded />
            </div>
            <SyllabusStatusBadge :status="item.status" />
            <span class="text-[11px] text-medium-emphasis">{{ formatDate(item.updatedAt) }}</span>
          </button>
        </div>
        <EmptyState v-else title="Силлабусы пока не созданы" description="Создайте первый документ, чтобы начать работу." />
      </v-card>

      <v-card class="app-surface pa-5 sm:pa-6">
        <div class="flex items-center gap-3"><v-avatar color="info" variant="tonal"><v-icon :icon="mdiCalendarClock" /></v-avatar><div><h2 class="text-base font-bold">Активность</h2><p class="text-xs text-medium-emphasis">Последние изменения</p></div></div>
        <v-timeline density="compact" side="end" class="mt-4">
          <v-timeline-item v-for="item in recent.slice(0, 4)" :key="item.id" dot-color="primary" size="x-small">
            <p class="line-clamp-1 text-xs font-bold">{{ item.titleInfo.codeAndName }}</p>
            <p class="mt-1 flex items-center gap-1 text-[10px] text-medium-emphasis"><v-icon :icon="mdiClockOutline" size="12" />{{ formatDate(item.updatedAt) }}</p>
          </v-timeline-item>
        </v-timeline>
      </v-card>
    </section>
  </div>
</template>

<style scoped>
.hero-panel { background: radial-gradient(circle at 80% 15%, rgba(16,185,129,.24), transparent 28%), linear-gradient(135deg, #071a16 0%, #0b2d27 55%, #111827 100%); }
.recent-row { border-bottom: 1px solid rgba(var(--v-border-color), .07); transition: background .16s; }
.recent-row:hover { background: rgba(var(--v-theme-primary), .05); }
</style>
