<script setup lang="ts">
definePageMeta({ layout: 'auth' })

const auth = useAuthStore()

onMounted(async () => {
  await auth.initialize()
  await navigateTo(auth.isAuthenticated ? '/dashboard' : '/login', { replace: true })
})
</script>

<template>
  <div class="grid min-h-screen place-items-center bg-background">
    <v-progress-circular indeterminate color="primary" />
  </div>
</template>
