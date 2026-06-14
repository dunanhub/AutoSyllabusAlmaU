<script setup lang="ts">
import { mdiMinusCircleOutline, mdiPlus } from '@mdi/js'
import type { LiteratureBlock } from '~/types/syllabus'

const model = defineModel<LiteratureBlock>({ required: true })
const { show } = useAppToast()

const sections = [
  { key: 'required' as const, title: 'A. Обязательная литература' },
  { key: 'additional' as const, title: 'B. Дополнительная литература' },
  { key: 'internetResources' as const, title: 'C. Интернет-ресурсы' }
]

function add(key: keyof LiteratureBlock) {
  model.value[key].push('')
  show('Источник добавлен', 'success')
}

function remove(key: keyof LiteratureBlock, index: number) {
  if (model.value[key].length <= 1) {
    model.value[key][0] = ''
    return
  }
  model.value[key].splice(index, 1)
  show('Источник удалён', 'info')
}
</script>

<template>
  <div class="space-y-4">
    <v-card v-for="section in sections" :key="section.key" class="soft-surface pa-4">
      <div class="mb-3 flex items-center justify-between gap-3">
        <h3 class="text-sm font-bold">{{ section.title }}</h3>
        <v-btn color="primary" variant="tonal" size="small" :prepend-icon="mdiPlus" class="text-none" @click="add(section.key)">Добавить</v-btn>
      </div>
      <div class="space-y-3">
        <div v-for="(_item, index) in model[section.key]" :key="`${section.key}-${index}`" class="grid gap-3 md:grid-cols-[1fr_auto]">
          <BaseTextarea v-model="model[section.key][index]" :label="`Источник ${index + 1}`" :rows="2" />
          <div class="flex items-end">
            <v-btn :icon="mdiMinusCircleOutline" variant="text" size="small" color="error" :disabled="model[section.key].length === 1" aria-label="Удалить источник" @click="remove(section.key, index)" />
          </div>
        </div>
      </div>
    </v-card>
  </div>
</template>
