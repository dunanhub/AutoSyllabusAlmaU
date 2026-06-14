<script setup lang="ts">
import {
  mdiContentCopy, mdiDotsVertical, mdiEyeOutline, mdiFileDocumentPlusOutline,
  mdiMagnify, mdiPencilOutline, mdiPlus, mdiTrashCanOutline, mdiTuneVariant
} from '@mdi/js'
import type { Syllabus, SyllabusLanguage, SyllabusStatus } from '~/types/syllabus'

definePageMeta({ middleware: 'auth' })
const store = useSyllabusStore()
const { show } = useAppToast()
const loading = ref(true)
const search = ref('')
const language = ref<'all' | SyllabusLanguage>('all')
const status = ref<'all' | SyllabusStatus>('all')
const pendingDelete = ref<Syllabus | null>(null)
const actionLoadingId = ref('')

const languageItems = [
  { title: 'Все языки', value: 'all' },
  { title: 'KZ · Қазақша', value: 'KZ' },
  { title: 'RU · Русский', value: 'RU' },
  { title: 'EN · English', value: 'EN' }
]
const statusItems = [
  { title: 'Все статусы', value: 'all' },
  { title: 'Черновик', value: 'draft' },
  { title: 'Готов', value: 'ready' }
]
const headers = [
  { title: 'Дисциплина', key: 'codeAndName', minWidth: '300px' },
  { title: 'Язык', key: 'language', width: '90px' },
  { title: 'Преподаватель', key: 'instructor', minWidth: '180px' },
  { title: 'Готовность', key: 'completion', width: '160px', sortable: false },
  { title: 'Статус', key: 'status', width: '120px' },
  { title: 'Обновлён', key: 'updatedAt', width: '130px' },
  { title: '', key: 'actions', width: '64px', sortable: false, align: 'end' as const }
]

const filtered = computed(() => {
  const query = search.value.trim().toLowerCase()
  return store.syllabuses.filter(item => {
    const matches = !query || [item.titleInfo.codeAndName, item.titleInfo.instructorName, item.titleInfo.educationalProgram].some(value => value.toLowerCase().includes(query))
    return matches && (language.value === 'all' || item.titleInfo.languageOfEducation === language.value) && (status.value === 'all' || item.status === status.value)
  })
})
const hasFilters = computed(() => Boolean(search.value || language.value !== 'all' || status.value !== 'all'))
const formatDate = (date: string) => new Intl.DateTimeFormat('ru-RU', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(date))

onMounted(async () => {
  try {
    await store.initialize()
  } finally {
    loading.value = false
  }
})

function completion(item: Syllabus) {
  return item.completion
}
function resetFilters() {
  search.value = ''
  language.value = 'all'
  status.value = 'all'
}
async function confirmDelete() {
  if (!pendingDelete.value) return
  actionLoadingId.value = pendingDelete.value.id
  try {
    await store.deleteSyllabus(pendingDelete.value.id)
    pendingDelete.value = null
    show('Силлабус удалён', 'success')
  } finally {
    actionLoadingId.value = ''
  }
}
async function duplicate(id: string) {
  actionLoadingId.value = id
  try {
    const copy = await store.duplicateSyllabus(id)
    show('Копия силлабуса создана', 'success')
    await navigateTo(`/syllabuses/${copy.id}/edit`)
  } finally {
    actionLoadingId.value = ''
  }
}
function openRow(_event: Event, row: { item: Syllabus }) {
  navigateTo(`/syllabuses/${row.item.id}`)
}
</script>

<template>
  <div class="space-y-6">
    <PageHeader eyebrow="Документы" title="Силлабусы" description="Рабочий реестр учебных документов, их статусов и степени готовности.">
      <template #actions>
        <v-btn color="primary" :prepend-icon="mdiPlus" class="text-none font-weight-bold" @click="navigateTo('/syllabuses/create')">Создать силлабус</v-btn>
      </template>
    </PageHeader>

    <v-card class="app-surface overflow-hidden">
      <div class="grid gap-3 border-b border-white/10 bg-surface-bright p-4 lg:grid-cols-[minmax(300px,1fr)_190px_190px_auto]">
        <v-text-field v-model="search" :prepend-inner-icon="mdiMagnify" label="Поиск" placeholder="Название, код или преподаватель" clearable />
        <v-select v-model="language" :items="languageItems" label="Язык" />
        <v-select v-model="status" :items="statusItems" label="Статус" />
        <v-btn v-if="hasFilters" variant="text" :prepend-icon="mdiTuneVariant" class="text-none self-center" @click="resetFilters">Сбросить</v-btn>
      </div>

      <div v-if="loading" class="p-12 text-center">
        <v-progress-circular indeterminate color="primary" />
        <p class="mt-3 text-sm text-medium-emphasis">Загрузка документов...</p>
      </div>

      <template v-else-if="filtered.length">
        <div class="hidden md:block">
          <v-data-table
            :headers="headers"
            :items="filtered"
            item-value="id"
            hover
            density="comfortable"
            :items-per-page="10"
            class="syllabus-table"
            @click:row="openRow"
          >
            <template #[`item.codeAndName`]="{ item }">
              <div class="py-2">
                <p class="max-w-80 truncate font-weight-bold">{{ item.titleInfo.codeAndName || 'Без названия' }}</p>
                <p class="mt-1 max-w-80 truncate text-xs text-medium-emphasis">{{ item.titleInfo.educationalProgram || 'Программа не указана' }}</p>
              </div>
            </template>
            <template #[`item.language`]="{ item }"><v-chip size="x-small" variant="outlined">{{ item.titleInfo.languageOfEducation }}</v-chip></template>
            <template #[`item.instructor`]="{ item }">{{ item.titleInfo.instructorName || '—' }}</template>
            <template #[`item.completion`]="{ item }">
              <div class="min-w-32">
                <div class="mb-1 flex justify-between text-[10px] text-medium-emphasis"><span>Заполнено</span><strong>{{ completion(item) }}%</strong></div>
                <v-progress-linear :model-value="completion(item)" color="primary" height="5" rounded />
              </div>
            </template>
            <template #[`item.status`]="{ item }"><SyllabusStatusBadge :status="item.status" /></template>
            <template #[`item.updatedAt`]="{ item }"><span class="whitespace-nowrap text-xs text-medium-emphasis">{{ formatDate(item.updatedAt) }}</span></template>
            <template #[`item.actions`]="{ item }">
              <v-menu>
                <template #activator="{ props }">
                  <v-btn v-bind="props" :icon="mdiDotsVertical" size="small" variant="text" aria-label="Действия" @click.stop />
                </template>
                <v-list density="compact">
                  <v-list-item :prepend-icon="mdiEyeOutline" title="Просмотреть" @click="navigateTo(`/syllabuses/${item.id}`)" />
                  <v-list-item :prepend-icon="mdiPencilOutline" title="Редактировать" @click="navigateTo(`/syllabuses/${item.id}/edit` )" />
                  <v-list-item :prepend-icon="mdiContentCopy" title="Дублировать" :disabled="actionLoadingId === item.id" @click="duplicate(item.id)" />
                  <v-divider />
                  <v-list-item :prepend-icon="mdiTrashCanOutline" title="Удалить" base-color="error" :disabled="actionLoadingId === item.id" @click="pendingDelete = item" />
                </v-list>
              </v-menu>
            </template>
          </v-data-table>
        </div>

        <div class="divide-y divide-white/10 md:hidden">
          <article v-for="item in filtered" :key="item.id" class="p-4" @click="navigateTo(`/syllabuses/${item.id}`)">
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0"><h3 class="truncate text-sm font-bold">{{ item.titleInfo.codeAndName || 'Без названия' }}</h3><p class="mt-1 text-xs text-medium-emphasis">{{ item.titleInfo.educationalProgram || 'Программа не указана' }} · {{ item.titleInfo.languageOfEducation }}</p></div>
              <SyllabusStatusBadge :status="item.status" />
            </div>
            <p class="mt-4 text-xs text-medium-emphasis">{{ item.titleInfo.instructorName || 'Преподаватель не указан' }}</p>
            <div class="mt-4"><div class="mb-1 flex justify-between text-[10px] text-medium-emphasis"><span>Готовность</span><strong>{{ completion(item) }}%</strong></div><v-progress-linear :model-value="completion(item)" color="primary" height="6" rounded /></div>
            <div class="mt-4 flex justify-end gap-1 border-t border-white/10 pt-3">
              <v-btn :icon="mdiPencilOutline" size="small" variant="text" aria-label="Редактировать" @click.stop="navigateTo(`/syllabuses/${item.id}/edit`)" />
              <v-btn :icon="mdiContentCopy" size="small" variant="text" aria-label="Дублировать" :loading="actionLoadingId === item.id" @click.stop="duplicate(item.id)" />
              <v-btn :icon="mdiTrashCanOutline" size="small" variant="text" color="error" aria-label="Удалить" :loading="actionLoadingId === item.id" @click.stop="pendingDelete = item" />
            </div>
          </article>
        </div>
      </template>

      <EmptyState v-else :icon="hasFilters ? mdiMagnify : mdiFileDocumentPlusOutline" title="Документы не найдены" description="Измените параметры поиска или создайте новый силлабус.">
        <v-btn v-if="hasFilters" variant="outlined" @click="resetFilters">Сбросить фильтры</v-btn>
      </EmptyState>
    </v-card>

    <ConfirmModal
      :open="Boolean(pendingDelete)"
      title="Удалить силлабус?"
      :message="`Документ «${pendingDelete?.titleInfo.codeAndName || 'Без названия'}» будет удалён без возможности восстановления.`"
      @confirm="confirmDelete"
      @cancel="pendingDelete = null"
    />
  </div>
</template>

<style scoped>
.syllabus-table :deep(tbody tr) { cursor: pointer; }
.syllabus-table :deep(.v-data-table-footer) { border-top: 1px solid rgba(var(--v-border-color), .08); }
</style>
