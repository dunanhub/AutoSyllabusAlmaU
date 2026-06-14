<script setup lang="ts">
defineOptions({ inheritAttrs: false })

withDefaults(defineProps<{
  label?: string
  hint?: string
  rows?: number
}>(), {
  label: '',
  hint: '',
  rows: 4
})

const model = defineModel<string>()
</script>

<template>
  <label class="block">
    <span v-if="label" class="form-label">{{ label }}</span>
    <textarea v-model="model" v-bind="$attrs" :rows="rows" class="form-textarea" />
    <span v-if="hint" class="mt-1.5 block text-xs text-slate-400">{{ hint }}</span>
  </label>
</template>
