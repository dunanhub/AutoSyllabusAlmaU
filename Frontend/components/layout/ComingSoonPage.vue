<script setup lang="ts">
import { mdiArrowLeft, mdiClockOutline } from '@mdi/js'

defineProps<{ eyebrow: string; title: string; description: string }>()
</script>

<template>
  <div class="space-y-6">
    <PageHeader :eyebrow="eyebrow" :title="title" :description="description" />
    <v-card class="app-surface overflow-hidden pa-8 text-center sm:pa-14">
      <div class="mx-auto max-w-xl">
        <v-avatar color="primary" variant="tonal" size="64"><v-icon :icon="mdiClockOutline" size="32" /></v-avatar>
        <h2 class="mt-6 text-2xl font-black">Раздел готовится к запуску</h2>
        <p class="mt-3 text-sm leading-7 text-medium-emphasis">Интерфейс уже включён в рабочее пространство. Бизнес-функции будут подключены на следующем этапе вместе с backend API.</p>
        <v-btn color="primary" variant="tonal" :prepend-icon="mdiArrowLeft" class="mt-7 text-none" @click="navigateTo('/dashboard')">Вернуться к обзору</v-btn>
      </div>
    </v-card>
  </div>
</template>
