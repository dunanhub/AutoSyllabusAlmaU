<script setup lang="ts">
defineOptions({ inheritAttrs: false })

withDefaults(defineProps<{
  label?: string
  required?: boolean
}>(), {
  label: '',
  required: false
})

const model = defineModel<string | number>()
</script>

<template>
  <label class="block">
    <span v-if="label" class="form-label">{{ label }} <span v-if="required" class="text-red-500">*</span></span>
    <select v-model="model" v-bind="$attrs" class="form-input">
      <slot />
    </select>
  </label>
</template>
