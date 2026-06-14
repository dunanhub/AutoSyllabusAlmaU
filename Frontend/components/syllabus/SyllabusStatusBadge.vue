<script setup lang="ts">
import type { SyllabusStatus } from '~/types/syllabus'

defineProps<{ status: SyllabusStatus }>()
</script>

<template>
  <v-chip :color="status === 'ready' ? 'success' : 'warning'" size="small" variant="tonal" class="font-weight-bold">
    {{ status === 'ready' ? 'Готов' : 'Черновик' }}
  </v-chip>
</template>
