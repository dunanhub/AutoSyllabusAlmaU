<script setup lang="ts">
import { mdiMinusCircleOutline, mdiPlus } from '@mdi/js'
import type { ClassScheduleRow } from '~/types/syllabus'
import { createId } from '~/utils/mockSyllabuses'

const model = defineModel<ClassScheduleRow[]>({ required: true })
const { show } = useAppToast()

function renumberWeeks() {
  model.value.forEach((item, index) => {
    item.week = String(index + 1)
  })
}

function addRow() {
  model.value.push({ id: createId('schedule'), week: String(model.value.length + 1), topic: '', format: '', task: '' })
  renumberWeeks()
  show('Строка графика добавлена', 'success')
}

function removeRow(index: number) {
  if (model.value.length <= 1) return
  model.value.splice(index, 1)
  renumberWeeks()
  show('Строка графика удалена', 'info')
}
</script>

<template>
  <div>
    <div class="mb-3 flex items-center justify-between gap-3">
      <p class="text-xs text-medium-emphasis">Минимум 15 недель по умолчанию; можно добавлять больше строк.</p>
      <v-btn color="primary" variant="tonal" size="small" :prepend-icon="mdiPlus" class="text-none" @click="addRow">Добавить строку</v-btn>
    </div>
    <div class="table-wrap max-h-[680px] rounded-lg border border-white/10">
      <table class="data-table min-w-[980px]">
        <thead><tr><th class="w-12">№</th><th class="w-24">Неделя</th><th>Тема / модуль</th><th>Формат проведения занятий</th><th>Задание</th><th class="w-16" /></tr></thead>
        <tbody>
          <tr v-for="(item, index) in model" :key="item.id">
            <td class="text-center font-bold">{{ index + 1 }}</td>
            <td><input v-model="item.week" class="form-input"></td>
            <td><textarea v-model="item.topic" class="form-input min-h-20 resize-y" /></td>
            <td><textarea v-model="item.format" class="form-input min-h-20 resize-y" /></td>
            <td><textarea v-model="item.task" class="form-input min-h-20 resize-y" /></td>
            <td><v-btn :icon="mdiMinusCircleOutline" variant="text" size="small" color="error" :disabled="model.length === 1" aria-label="Удалить строку" @click="removeRow(index)" /></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
