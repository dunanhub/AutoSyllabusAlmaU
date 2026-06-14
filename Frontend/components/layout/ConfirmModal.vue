<script setup lang="ts">
import { mdiAlertOutline } from '@mdi/js'

withDefaults(defineProps<{
  open: boolean
  title?: string
  message?: string
  confirmText?: string
}>(), {
  title: 'Подтвердите действие',
  message: 'Это действие нельзя отменить.',
  confirmText: 'Удалить'
})

const emit = defineEmits<{ confirm: []; cancel: [] }>()
</script>

<template>
  <v-dialog :model-value="open" max-width="460" @update:model-value="value => !value && emit('cancel')">
    <v-card class="pa-2">
      <v-card-title class="flex items-center gap-3 text-base font-weight-bold">
        <v-avatar color="error" variant="tonal" size="40"><v-icon :icon="mdiAlertOutline" /></v-avatar>
        {{ title }}
      </v-card-title>
      <v-card-text class="text-medium-emphasis">{{ message }}</v-card-text>
      <v-card-actions class="px-4 pb-4">
        <v-spacer />
        <v-btn variant="text" @click="emit('cancel')">Отмена</v-btn>
        <v-btn color="error" variant="flat" @click="emit('confirm')">{{ confirmText }}</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
