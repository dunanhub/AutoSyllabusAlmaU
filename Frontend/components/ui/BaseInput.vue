<script setup lang="ts">
defineOptions({ inheritAttrs: false })

withDefaults(defineProps<{
  label?: string
  hint?: string
  error?: string
  required?: boolean
}>(), {
  label: '',
  hint: '',
  error: '',
  required: false
})

const model = defineModel<string | number | null>()

const value = computed({
  get: () => model.value ?? '',
  set: (next: string | number | null) => {
    const inputType = String((useAttrs().type ?? '')).toLowerCase()
    if (inputType === 'number') {
      model.value = next === '' || next === null ? '' : Number(next)
      return
    }
    model.value = next ?? ''
  }
})
</script>

<template>
  <label class="block">
    <span v-if="label" class="form-label">{{ label }} <span v-if="required" class="text-red-500">*</span></span>
    <input v-model="value" v-bind="$attrs" class="form-input">
    <span v-if="error" class="mt-1.5 block text-xs text-red-600">{{ error }}</span>
    <span v-else-if="hint" class="mt-1.5 block text-xs text-slate-400">{{ hint }}</span>
  </label>
</template>
