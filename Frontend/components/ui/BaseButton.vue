<script setup lang="ts">
import type { Component } from 'vue'

withDefaults(defineProps<{
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  type?: 'button' | 'submit'
  disabled?: boolean
  loading?: boolean
  icon?: Component | string
}>(), {
  variant: 'primary',
  size: 'md',
  type: 'button',
  disabled: false,
  loading: false,
  icon: undefined
})
</script>

<template>
  <v-btn
    :type="type"
    :disabled="disabled || loading"
    :loading="loading"
    :color="variant === 'danger' ? 'error' : variant === 'primary' ? 'primary' : undefined"
    :variant="variant === 'primary' ? 'flat' : variant === 'ghost' ? 'text' : 'outlined'"
    :size="size === 'md' ? 'default' : size"
    class="text-none font-weight-bold"
  >
    <v-icon v-if="typeof icon === 'string'" :icon="icon" size="18" class="mr-2" />
    <component :is="icon" v-else-if="icon" class="mr-2 size-4 shrink-0" />
    <slot />
  </v-btn>
</template>
