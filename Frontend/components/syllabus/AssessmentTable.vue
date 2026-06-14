<script setup lang="ts">
import { mdiMinusCircleOutline, mdiPlus } from '@mdi/js'
import type { AssessmentRow } from '~/types/syllabus'
import { calculateAssessmentPoints, createId } from '~/utils/mockSyllabuses'

const model = defineModel<AssessmentRow[]>({ required: true })
const { show } = useAppToast()

function isSummaryRow(topicModule: string) {
  const value = topicModule.toLowerCase()
  return value.includes('всего за теоретическое обучение') || value.includes('государственный экзамен') || value.includes('всего за курс')
}

const componentRows = computed(() => model.value.filter(row => !isSummaryRow(row.topicModule)))
const summaryRows = computed(() => model.value.filter(row => isSummaryRow(row.topicModule)))
const totalWeight = computed(() => summaryRows.value.find(row => row.topicModule.toLowerCase().includes('всего за курс'))?.maxWeight ?? componentRows.value.reduce((sum, item) => sum + Number(item.maxWeight || 0), 0))
const totalPoints = computed(() => summaryRows.value.find(row => row.topicModule.toLowerCase().includes('всего за курс'))?.finalPoints ?? componentRows.value.reduce((sum, item) => sum + Number(item.finalPoints || 0), 0))
const theoryTotal = computed(() => summaryRows.value.find(row => row.topicModule.toLowerCase().includes('теорет'))?.finalPoints || totalPoints.value)
const stateExam = computed(() => summaryRows.value.find(row => row.topicModule.toLowerCase().includes('государ'))?.finalPoints || 0)

watch(model, (items) => {
  items.forEach((item) => {
    item.finalPoints = calculateAssessmentPoints(item.maxPercent, item.maxWeight)
  })
}, { deep: true, immediate: true })

function addRow() {
  const insertIndex = model.value.findIndex(row => isSummaryRow(row.topicModule))
  const row = { id: createId('assessment'), topicModule: '', maxPercent: 100, maxWeight: 0, finalPoints: 0 }
  if (insertIndex === -1) model.value.push(row)
  else model.value.splice(insertIndex, 0, row)
  show('Компонент оценивания добавлен', 'success')
}

function removeRow(index: number) {
  if (model.value.length <= 1) return
  model.value.splice(index, 1)
  show('Компонент оценивания удалён', 'info')
}
</script>

<template>
  <div>
    <div class="mb-3 flex flex-wrap items-center justify-between gap-3">
      <p class="text-xs" :class="totalWeight === 100 ? 'text-medium-emphasis' : 'font-medium text-warning'">
        Текущая сумма весов: {{ totalWeight }}%. Итоговые баллы: {{ totalPoints }}.
      </p>
      <v-btn color="primary" variant="tonal" size="small" :prepend-icon="mdiPlus" class="text-none" @click="addRow">Добавить компонент</v-btn>
    </div>
    <div class="table-wrap rounded-lg border border-white/10">
      <table class="data-table min-w-[880px]">
        <thead><tr><th>Тема / модуль</th><th class="w-44">Максимальный процент (%)</th><th class="w-44">Максимальный вес (%)</th><th class="w-40">Итоговые баллы</th><th class="w-16" /></tr></thead>
        <tbody>
          <tr v-for="(item, index) in model" :key="item.id">
            <td><textarea v-model="item.topicModule" class="form-input min-h-16 resize-y" placeholder="Рубежный контроль 1" /></td>
            <td><input v-model="item.maxPercent" type="number" min="0" class="form-input"></td>
            <td><input v-model="item.maxWeight" type="number" min="0" class="form-input"></td>
            <td><input :value="item.finalPoints" readonly class="form-input font-bold text-primary"></td>
            <td><v-btn :icon="mdiMinusCircleOutline" variant="text" size="small" color="error" :disabled="model.length === 1" aria-label="Удалить компонент" @click="removeRow(index)" /></td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="mt-4 grid gap-3 md:grid-cols-3">
      <div class="soft-surface rounded-xl p-4"><p class="text-xs text-medium-emphasis">Всего за теоретическое обучение</p><p class="mt-2 text-xl font-black">{{ theoryTotal }}</p></div>
      <div class="soft-surface rounded-xl p-4"><p class="text-xs text-medium-emphasis">Государственный экзамен</p><p class="mt-2 text-xl font-black">{{ stateExam }}</p></div>
      <div class="soft-surface rounded-xl p-4"><p class="text-xs text-medium-emphasis">Всего за курс</p><p class="mt-2 text-xl font-black text-primary">{{ totalPoints }}</p></div>
    </div>
  </div>
</template>
