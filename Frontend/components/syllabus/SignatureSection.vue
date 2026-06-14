<script setup lang="ts">
import { mdiImagePlusOutline } from '@mdi/js'
import type { SignatureBlock } from '~/types/syllabus'

const model = defineModel<SignatureBlock>({ required: true })
const signatureInput = ref<HTMLInputElement | null>(null)
const stampInput = ref<HTMLInputElement | null>(null)

function readFile(event: Event, key: 'signatureImage' | 'stampImage') {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => {
    model.value[key] = String(reader.result || '')
  }
  reader.readAsDataURL(file)
}
</script>

<template>
  <div class="space-y-5">
    <div class="grid gap-4 md:grid-cols-3">
      <BaseInput v-model="model.preparedByName" label="ФИО составителя" />
      <BaseInput v-model="model.preparedByPosition" label="Должность" />
      <BaseInput v-model="model.preparedByDate" type="date" label="Дата" />
    </div>
    <div class="grid gap-4 md:grid-cols-2">
      <v-card class="soft-surface pa-4">
        <p class="mb-3 text-sm font-bold">Подпись</p>
        <v-btn :prepend-icon="mdiImagePlusOutline" variant="tonal" color="primary" class="text-none" @click="signatureInput?.click()">Загрузить подпись</v-btn>
        <input ref="signatureInput" type="file" accept="image/*" class="hidden" @change="readFile($event, 'signatureImage')">
        <img v-if="model.signatureImage" :src="model.signatureImage" alt="Подпись" class="mt-4 max-h-28 rounded-lg bg-white p-2">
      </v-card>
      <v-card class="soft-surface pa-4">
        <p class="mb-3 text-sm font-bold">Печать</p>
        <v-btn :prepend-icon="mdiImagePlusOutline" variant="tonal" color="primary" class="text-none" @click="stampInput?.click()">Загрузить печать</v-btn>
        <input ref="stampInput" type="file" accept="image/*" class="hidden" @change="readFile($event, 'stampImage')">
        <img v-if="model.stampImage" :src="model.stampImage" alt="Печать" class="mt-4 max-h-28 rounded-lg bg-white p-2">
      </v-card>
    </div>
  </div>
</template>
