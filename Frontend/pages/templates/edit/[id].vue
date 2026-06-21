<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

const route = useRoute()
const id = String(route.params.id || '')

await navigateTo(`/templates?edit=${encodeURIComponent(id)}`, { replace: true })
</script>

<template>
  <div />
</template>
