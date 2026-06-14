<script setup lang="ts">
import { mdiAlertCircleOutline, mdiCheckCircleOutline, mdiClose, mdiInformationOutline } from '@mdi/js'

const { messages, dismiss } = useAppToast()
const icons = {
  success: mdiCheckCircleOutline,
  info: mdiInformationOutline,
  error: mdiAlertCircleOutline
}
</script>

<template>
  <div class="pointer-events-none fixed right-4 top-4 z-[2500] flex w-[calc(100%-2rem)] max-w-sm flex-col gap-2">
    <v-alert
      v-for="message in messages"
      :key="message.id"
      :type="message.kind"
      :icon="icons[message.kind]"
      variant="elevated"
      border="start"
      class="pointer-events-auto"
    >
      <div class="flex items-center justify-between gap-3">
        <span class="text-sm font-semibold">{{ message.text }}</span>
        <v-btn :icon="mdiClose" size="x-small" variant="text" aria-label="Закрыть" @click="dismiss(message.id)" />
      </div>
    </v-alert>
  </div>
</template>
