<script setup lang="ts">
import { mdiFileDocumentOutline } from '@mdi/js'

withDefaults(defineProps<{
  title: string
  description?: string
  icon?: string
}>(), {
  description: '',
  icon: mdiFileDocumentOutline
})
</script>

<template>
  <div class="px-6 py-14 text-center">
    <v-avatar color="primary" variant="tonal" size="54"><v-icon :icon="icon" size="26" /></v-avatar>
    <h3 class="mt-4 text-base font-bold">{{ title }}</h3>
    <p v-if="description" class="mx-auto mt-2 max-w-md text-sm leading-6 text-medium-emphasis">{{ description }}</p>
    <div v-if="$slots.default" class="mt-5"><slot /></div>
  </div>
</template>
