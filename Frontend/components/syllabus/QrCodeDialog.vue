<script setup lang="ts">
import { mdiClose, mdiContentCopy, mdiOpenInNew, mdiQrcode } from '@mdi/js'
import QrcodeVue from 'qrcode.vue'

const props = defineProps<{
  modelValue: boolean
  value: string
  title?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const { show } = useAppToast()

async function copy() {
  if (!import.meta.client || !props.value) return
  await navigator.clipboard.writeText(props.value)
  show('Ссылка скопирована', 'success')
}

function openLink() {
  if (!import.meta.client || !props.value) return
  window.open(props.value, '_blank', 'noopener,noreferrer')
}
</script>

<template>
  <v-dialog
    :model-value="modelValue"
    max-width="600"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <v-card class="qr-card">
      <div class="qr-header">
        <div class="flex items-center gap-3">
          <v-avatar color="primary" variant="tonal"><v-icon :icon="mdiQrcode" /></v-avatar>
          <div>
            <h2 class="text-lg font-black">{{ title || 'QR код дисциплины' }}</h2>
            <p class="mt-1 text-xs text-medium-emphasis">Откройте дисциплину по ссылке</p>
          </div>
        </div>
        <v-btn :icon="mdiClose" variant="text" size="small" aria-label="Закрыть" @click="emit('update:modelValue', false)" />
      </div>

      <div class="qr-body">
        <div class="qr-box">
          <QrcodeVue :value="value || ' '" :size="240" level="M" render-as="svg" />
        </div>
        <div class="qr-url">
          <p>{{ value }}</p>
        </div>
      </div>

      <div class="qr-actions">
        <div class="flex flex-wrap gap-2">
          <v-btn variant="tonal" :prepend-icon="mdiOpenInNew" class="text-none" @click="openLink">Открыть ссылку</v-btn>
          <v-btn color="primary" :prepend-icon="mdiContentCopy" class="text-none font-weight-bold" @click="copy">Скопировать ссылку</v-btn>
        </div>
        <v-btn variant="text" class="text-none" @click="emit('update:modelValue', false)">Закрыть</v-btn>
      </div>
    </v-card>
  </v-dialog>
</template>

<style scoped>
.qr-card {
  border: 1px solid rgba(var(--v-border-color), .1);
  overflow: hidden;
}
.qr-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  border-bottom: 1px solid rgba(var(--v-border-color), .1);
  padding: 20px;
}
.qr-body {
  display: grid;
  gap: 16px;
  padding: 20px;
}
.qr-box {
  display: grid;
  place-items: center;
  border-radius: 22px;
  background: #fff;
  padding: 22px;
}
.qr-url {
  border: 1px solid rgba(var(--v-border-color), .1);
  border-radius: 14px;
  background: rgb(var(--v-theme-surface-bright));
  padding: 10px 12px;
}
.qr-url p {
  overflow-wrap: anywhere;
  color: rgba(var(--v-theme-on-surface), .66);
  font-size: 12px;
  line-height: 1.55;
}
.qr-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 8px;
  border-top: 1px solid rgba(var(--v-border-color), .1);
  padding: 16px 20px;
}
@media (max-width: 520px) {
  .qr-actions :deep(.v-btn) {
    flex: 1 1 100%;
  }
}
</style>
