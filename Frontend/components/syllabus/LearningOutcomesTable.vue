<script setup lang="ts">
import { mdiMinusCircleOutline, mdiPlus } from '@mdi/js'
import type { LearningOutcomeRow } from '~/types/syllabus'
import { createId } from '~/utils/mockSyllabuses'

const model = defineModel<LearningOutcomeRow[]>({ required: true })
const { show } = useAppToast()

function addRow() {
  model.value.push({
    id: createId('lo'),
    code: `PO${model.value.length + 1}`,
    courseLearningOutcome: '',
    programLearningOutcome: '',
    description: ''
  })
  show('Результат обучения добавлен', 'success')
}

function removeRow(index: number) {
  if (model.value.length <= 1) return
  model.value.splice(index, 1)
  show('Результат обучения удалён', 'info')
}
</script>

<template>
  <div>
    <div class="mb-3 flex items-center justify-between gap-3">
      <p class="text-xs text-medium-emphasis">Таблица соответствия результатов обучения курса и образовательной программы.</p>
      <v-btn color="primary" variant="tonal" size="small" :prepend-icon="mdiPlus" class="text-none" @click="addRow">Добавить результат</v-btn>
    </div>
    <div class="table-wrap rounded-lg border border-white/10">
      <table class="data-table min-w-[980px]">
        <thead><tr><th class="w-12">№</th><th class="w-24">Код</th><th>Результаты обучения курса</th><th>Результаты обучения ОП</th><th>Описание</th><th class="w-16" /></tr></thead>
        <tbody>
          <tr v-for="(item, index) in model" :key="item.id">
            <td class="text-center font-bold">{{ index + 1 }}</td>
            <td><input v-model="item.code" class="form-input" placeholder="PO1"></td>
            <td><textarea v-model="item.courseLearningOutcome" class="form-input min-h-24 resize-y" /></td>
            <td><textarea v-model="item.programLearningOutcome" class="form-input min-h-24 resize-y" /></td>
            <td><textarea v-model="item.description" class="form-input min-h-24 resize-y" /></td>
            <td><v-btn :icon="mdiMinusCircleOutline" variant="text" size="small" color="error" :disabled="model.length === 1" aria-label="Удалить результат" @click="removeRow(index)" /></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
