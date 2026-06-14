<script setup lang="ts">
withDefaults(defineProps<{ padded?: boolean }>(), { padded: true })
</script>

<template>
  <v-card class="app-surface" :class="{ 'pa-5 sm:pa-6': padded }">
    <slot />
  </v-card>
</template>
