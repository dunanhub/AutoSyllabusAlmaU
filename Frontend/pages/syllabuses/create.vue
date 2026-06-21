<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

onMounted(() => {
  void navigateTo('/syllabuses?create=1', { replace: true })
})
</script>

<template>
  <div class="flex min-h-[60vh] items-center justify-center">
    <v-progress-circular indeterminate color="primary" />
  </div>
</template>
