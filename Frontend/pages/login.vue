<script setup lang="ts">
import { mdiArrowRight, mdiCheckCircleOutline, mdiEyeOffOutline, mdiEyeOutline, mdiLockOutline, mdiShieldCheckOutline } from '@mdi/js'

definePageMeta({ layout: 'auth' })
const auth = useAuthStore()
const { show } = useAppToast()
const email = ref('')
const password = ref('')
const showPassword = ref(false)
const error = ref('')
const loading = ref(false)
const booting = ref(true)

onMounted(async () => {
  try {
    await auth.initialize()
    if (auth.isAuthenticated) await navigateTo('/dashboard')
  } finally {
    booting.value = false
  }
})

async function submit() {
  error.value = ''
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
    error.value = 'Введите корректный email.'
    return
  }
  if (!password.value.trim()) {
    error.value = 'Введите пароль.'
    return
  }
  loading.value = true
  try {
    await auth.login(email.value, password.value)
    await navigateTo('/dashboard')
  } catch (errorValue: any) {
    if (errorValue?.status === 401) {
      error.value = 'Неверный email или пароль.'
      show('Неверный email или пароль.', 'error')
    } else if (!errorValue?.status) {
      error.value = 'Сервер недоступен или ошибка сети.'
      show('Сервер недоступен или ошибка сети.', 'error')
    } else {
      error.value = 'Не удалось войти в систему.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page grid min-h-screen lg:grid-cols-[1.15fr_.85fr]">
    <section class="relative hidden overflow-hidden bg-[#061b17] p-12 text-white lg:flex lg:flex-col lg:justify-between xl:p-16">
      <div class="login-glow login-glow-one" />
      <div class="login-glow login-glow-two" />
      <div class="relative flex items-center gap-3">
        <span class="grid size-11 place-items-center rounded-xl bg-primary text-xl font-black text-[#032d23]">A</span>
        <div><strong class="block text-sm tracking-wide">AlmaU</strong><span class="text-xs text-white/45">Almaty Management University</span></div>
      </div>

      <div class="relative max-w-xl">
        <v-chip color="primary" variant="tonal" size="small" class="mb-6 font-weight-bold">ACADEMIC WORKSPACE</v-chip>
        <h1 class="text-4xl font-black leading-[1.12] tracking-[-0.04em] xl:text-6xl">
          Силлабусы в едином цифровом пространстве
        </h1>
        <p class="mt-6 max-w-lg text-base leading-7 text-white/55">
          Создавайте, согласовывайте и готовьте академические документы в структурированном формате AlmaU.
        </p>
        <div class="mt-10 grid gap-4 sm:grid-cols-3">
          <div v-for="item in ['Единая структура', 'Автосохранение', 'PDF-ready preview']" :key="item" class="rounded-xl border border-white/10 bg-white/5 p-4 backdrop-blur">
            <v-icon :icon="mdiCheckCircleOutline" color="primary" size="20" />
            <p class="mt-3 text-xs font-bold text-white/75">{{ item }}</p>
          </div>
        </div>
      </div>
      <p class="relative text-xs text-white/30">© 2026 AlmaU. Внутренняя информационная система.</p>
    </section>

    <section class="flex items-center justify-center bg-background p-5 sm:p-10">
      <div class="w-full max-w-[440px]">
        <div class="mb-8 flex items-center gap-3 lg:hidden">
          <span class="grid size-10 place-items-center rounded-xl bg-primary text-lg font-black text-[#032d23]">A</span>
          <div><strong class="block text-sm">AlmaU</strong><span class="text-xs text-medium-emphasis">Syllabus Generator</span></div>
        </div>
        <v-card class="app-surface pa-6 sm:pa-9">
          <v-avatar color="primary" variant="tonal" size="46"><v-icon :icon="mdiShieldCheckOutline" /></v-avatar>
          <p class="page-eyebrow mt-6">Вход в систему</p>
          <h2 class="mt-2 text-2xl font-black tracking-tight">Рабочее пространство преподавателя</h2>
          <p class="mt-2 text-sm leading-6 text-medium-emphasis">Используйте корпоративную учётную запись AlmaU.</p>

          <div v-if="booting" class="mt-7 space-y-4">
            <v-skeleton-loader type="text, text, button" />
          </div>
          <v-form v-else class="mt-7" @submit.prevent="submit">
            <v-text-field v-model="email" label="Email" placeholder="name@almau.edu.kz" type="email" autocomplete="email" />
            <v-text-field
              v-model="password"
              class="mt-4"
              label="Пароль"
              placeholder="Введите пароль"
              :type="showPassword ? 'text' : 'password'"
              :prepend-inner-icon="mdiLockOutline"
              :append-inner-icon="showPassword ? mdiEyeOffOutline : mdiEyeOutline"
              autocomplete="current-password"
              @click:append-inner="showPassword = !showPassword"
            />
            <v-alert v-if="error" type="error" variant="tonal" density="compact" class="mt-4">{{ error }}</v-alert>
            <v-btn type="submit" color="primary" size="large" block :loading="loading" :prepend-icon="mdiArrowRight" class="mt-6 text-none font-weight-bold">
              Войти
            </v-btn>
          </v-form>
          <p class="mt-6 border-t border-white/10 pt-5 text-center text-xs text-medium-emphasis">
            Демо-режим: любой корректный email и непустой пароль.
          </p>
        </v-card>
      </div>
    </section>
  </div>
</template>

<style scoped>
.login-glow { position: absolute; border-radius: 999px; filter: blur(20px); opacity: .24; }
.login-glow-one { width: 420px; height: 420px; right: -120px; top: -120px; background: #10b981; }
.login-glow-two { width: 360px; height: 360px; left: 12%; bottom: -190px; background: #8b5cf6; opacity: .12; }
</style>
