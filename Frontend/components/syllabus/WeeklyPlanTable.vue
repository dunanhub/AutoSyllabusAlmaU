<script setup lang="ts">
import { mdiMinusCircleOutline, mdiPlus } from '@mdi/js'
import type { ThematicPlanRow } from '~/types/syllabus'
import { createId } from '~/utils/mockSyllabuses'

const model = defineModel<ThematicPlanRow[]>({ required: true })
const { show } = useAppToast()

function renumberWeeks() {
  model.value.forEach((item, index) => {
    item.week = String(index + 1)
  })
}

function addRow() {
  model.value.push({
    id: createId('topic'),
    week: String(model.value.length + 1),
    topicModule: '',
    courseOutcome: '',
    questions: '',
    tasks: '',
    literature: '',
    gradeStructure: ''
  })
  renumberWeeks()
  show('Неделя добавлена', 'success')
}

function removeRow(index: number) {
  if (model.value.length <= 1) return
  model.value.splice(index, 1)
  renumberWeeks()
  show('Неделя удалена', 'info')
}
</script>

<template>
  <div>
    <div class="mb-3 flex items-center justify-between gap-3">
      <p class="text-xs text-medium-emphasis">Тематический план поддерживает многострочный текст и дополнительные недели.</p>
      <v-btn color="primary" variant="tonal" size="small" :prepend-icon="mdiPlus" class="text-none" @click="addRow">Добавить неделю</v-btn>
    </div>
    <div class="table-wrap max-h-[720px] rounded-lg border border-white/10">
      <table class="data-table min-w-[1600px]">
        <thead><tr><th class="w-12">№</th><th class="w-24">Неделя</th><th>Тема / модуль</th><th>PO курса / PO ОП</th><th>Вопросы</th><th>Задания</th><th>Литература</th><th>Структура оценок</th><th class="w-16" /></tr></thead>
        <tbody>
          <tr v-for="(item, index) in model" :key="item.id">
            <td class="text-center font-bold">{{ index + 1 }}</td>
            <td><input v-model="item.week" class="form-input"></td>
            <td><textarea v-model="item.topicModule" class="form-input min-h-28 resize-y" /></td>
            <td><textarea v-model="item.courseOutcome" class="form-input min-h-28 resize-y" /></td>
            <td><textarea v-model="item.questions" class="form-input min-h-28 resize-y" /></td>
            <td><textarea v-model="item.tasks" class="form-input min-h-28 resize-y" /></td>
            <td><textarea v-model="item.literature" class="form-input min-h-28 resize-y" /></td>
            <td><textarea v-model="item.gradeStructure" class="form-input min-h-28 resize-y" /></td>
            <td><v-btn :icon="mdiMinusCircleOutline" variant="text" size="small" color="error" :disabled="model.length === 1" aria-label="Удалить неделю" @click="removeRow(index)" /></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
