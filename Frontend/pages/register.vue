<script setup lang="ts">
import {
  mdiAccountOutline,
  mdiArrowRight,
  mdiCheckCircle,
  mdiCheckCircleOutline,
  mdiEmailOutline,
  mdiEyeOffOutline,
  mdiEyeOutline,
  mdiLockOutline,
  mdiShieldCheckOutline
} from '@mdi/js'

definePageMeta({ layout: 'auth' })

const auth = useAuthStore()
const { show } = useAppToast()
const { isDark } = useAppTheme()

const firstName = ref('')
const lastName = ref('')
const email = ref('')
const password = ref('')
const passwordConfirm = ref('')
const showPassword = ref(false)
const showPasswordConfirm = ref(false)
const error = ref('')
const loading = ref(false)
const booting = ref(true)

const passwordChecks = computed(() => [
  { label: 'Не менее 8 символов', valid: password.value.length >= 8 },
  { label: 'Содержит буквы', valid: /[A-Za-zА-Яа-я]/.test(password.value) },
  { label: 'Содержит цифры', valid: /\d/.test(password.value) }
])

onMounted(async () => {
  try {
    await auth.initialize()
    if (auth.isAuthenticated) await navigateTo('/dashboard')
  } finally {
    booting.value = false
  }
})

function apiValidationMessage(errorValue: any) {
  const data = errorValue?.data ?? errorValue?.response?._data
  if (!data || typeof data !== 'object') return ''

  const fieldOrder = ['email', 'passwordConfirm', 'password', 'firstName', 'lastName', 'non_field_errors']
  for (const field of fieldOrder) {
    const value = data[field]
    if (Array.isArray(value) && value.length) return String(value[0])
    if (typeof value === 'string') return value
  }
  return ''
}

async function submit() {
  error.value = ''
  if (!firstName.value.trim() || !lastName.value.trim()) {
    error.value = 'Введите имя и фамилию.'
    return
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
    error.value = 'Введите корректный email.'
    return
  }
  if (password.value.length < 8 || !/[A-Za-zА-Яа-я]/.test(password.value) || !/\d/.test(password.value)) {
    error.value = 'Пароль должен соответствовать указанным требованиям.'
    return
  }
  if (password.value !== passwordConfirm.value) {
    error.value = 'Пароли не совпадают.'
    return
  }

  loading.value = true
  try {
    await auth.register({
      firstName: firstName.value.trim(),
      lastName: lastName.value.trim(),
      email: email.value.trim(),
      password: password.value,
      passwordConfirm: passwordConfirm.value
    })
    show('Аккаунт успешно создан.', 'success')
    await navigateTo('/dashboard')
  } catch (errorValue: any) {
    error.value = apiValidationMessage(errorValue)
      || (errorValue?.status ? 'Не удалось создать аккаунт.' : 'Сервер недоступен или ошибка сети.')
    show(error.value, 'error')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="register-page" :class="{ 'register-page--light': !isDark }">
    <div class="background-glow background-glow--green" aria-hidden="true" />
    <div class="background-glow background-glow--blue" aria-hidden="true" />
    <div class="background-grid" aria-hidden="true" />

    <section class="register-shell">
      <aside class="brand-panel">
        <div class="brand-header">
          <img
            src="/images/almau-logo-white.png"
            alt="AlmaU — Almaty Management University"
            class="brand-logo"
          >
          <span class="workspace-badge">
            <span class="workspace-dot" />
            AlmaU Digital Workspace
          </span>
        </div>

        <div class="brand-content">
          <p class="brand-kicker">Academic management platform</p>
          <h1>Начните работу<br>с AlmaU</h1>
          <p class="brand-description">
            Создайте персональный аккаунт преподавателя для управления
            академическими силлабусами в единой системе.
          </p>

          <ul class="brand-benefits">
            <li>
              <v-icon :icon="mdiCheckCircleOutline" size="19" />
              Персональное рабочее пространство
            </li>
            <li>
              <v-icon :icon="mdiCheckCircleOutline" size="19" />
              Защищённый доступ по JWT
            </li>
            <li>
              <v-icon :icon="mdiCheckCircleOutline" size="19" />
              Сохранение и подготовка PDF
            </li>
          </ul>
        </div>

        <div class="brand-footer">
          <v-icon :icon="mdiShieldCheckOutline" size="20" />
          <span>Защищённая корпоративная система</span>
        </div>
      </aside>

      <div class="form-panel">
        <div class="form-container">
          <header class="form-header">
            <p class="form-kicker">Новый аккаунт</p>
            <h2>Регистрация</h2>
            <p>Заполните данные для создания рабочего пространства.</p>
          </header>

          <div v-if="booting" class="register-skeleton" aria-label="Загрузка авторизации">
            <v-skeleton-loader color="transparent" type="text, text, text, button" />
          </div>

          <form v-else class="register-form" novalidate @submit.prevent="submit">
            <div class="name-grid">
              <div>
                <label class="field-label" for="register-first-name">Имя</label>
                <div class="field-shell">
                  <v-icon :icon="mdiAccountOutline" size="20" class="field-icon" />
                  <input
                    id="register-first-name"
                    v-model="firstName"
                    type="text"
                    autocomplete="given-name"
                    placeholder="Имя"
                  >
                </div>
              </div>
              <div>
                <label class="field-label" for="register-last-name">Фамилия</label>
                <div class="field-shell">
                  <v-icon :icon="mdiAccountOutline" size="20" class="field-icon" />
                  <input
                    id="register-last-name"
                    v-model="lastName"
                    type="text"
                    autocomplete="family-name"
                    placeholder="Фамилия"
                  >
                </div>
              </div>
            </div>

            <label class="field-label field-label--spaced" for="register-email">Email</label>
            <div class="field-shell">
              <v-icon :icon="mdiEmailOutline" size="20" class="field-icon" />
              <input
                id="register-email"
                v-model="email"
                type="email"
                inputmode="email"
                autocomplete="email"
                placeholder="name@example.com"
              >
            </div>

            <div class="password-grid">
              <div>
                <label class="field-label field-label--spaced" for="register-password">Пароль</label>
                <div class="field-shell">
                  <v-icon :icon="mdiLockOutline" size="20" class="field-icon" />
                  <input
                    id="register-password"
                    v-model="password"
                    :type="showPassword ? 'text' : 'password'"
                    autocomplete="new-password"
                    placeholder="Пароль"
                  >
                  <button
                    type="button"
                    class="password-toggle"
                    :aria-label="showPassword ? 'Скрыть пароль' : 'Показать пароль'"
                    @click="showPassword = !showPassword"
                  >
                    <v-icon :icon="showPassword ? mdiEyeOffOutline : mdiEyeOutline" size="20" />
                  </button>
                </div>
              </div>
              <div>
                <label class="field-label field-label--spaced" for="register-password-confirm">Повторите пароль</label>
                <div class="field-shell">
                  <v-icon :icon="mdiLockOutline" size="20" class="field-icon" />
                  <input
                    id="register-password-confirm"
                    v-model="passwordConfirm"
                    :type="showPasswordConfirm ? 'text' : 'password'"
                    autocomplete="new-password"
                    placeholder="Ещё раз"
                  >
                  <button
                    type="button"
                    class="password-toggle"
                    :aria-label="showPasswordConfirm ? 'Скрыть пароль' : 'Показать пароль'"
                    @click="showPasswordConfirm = !showPasswordConfirm"
                  >
                    <v-icon :icon="showPasswordConfirm ? mdiEyeOffOutline : mdiEyeOutline" size="20" />
                  </button>
                </div>
              </div>
            </div>

            <div class="password-requirements" aria-live="polite">
              <span
                v-for="check in passwordChecks"
                :key="check.label"
                :class="{ valid: check.valid }"
              >
                <v-icon :icon="mdiCheckCircle" size="14" />
                {{ check.label }}
              </span>
            </div>

            <v-alert
              v-if="error"
              type="error"
              variant="tonal"
              density="compact"
              class="register-error"
            >
              {{ error }}
            </v-alert>

            <button type="submit" class="register-submit" :disabled="loading">
              <v-progress-circular v-if="loading" indeterminate size="21" width="2" />
              <template v-else>
                <span>Создать аккаунт</span>
                <v-icon :icon="mdiArrowRight" size="22" />
              </template>
            </button>
          </form>

          <p class="auth-switch">
            Уже есть аккаунт?
            <NuxtLink to="/login">Войти в систему</NuxtLink>
          </p>
        </div>

        <footer class="form-footer">
          <span>© 2026 Almaty Management University</span>
          <span>Internal Academic System</span>
        </footer>
      </div>
    </section>
  </main>
</template>

<style scoped>
.register-page {
  --page-bg: #06101d;
  --panel-bg: #0d1726;
  --panel-border: rgba(148, 163, 184, .18);
  --field-bg: #111e30;
  --field-border: #2b3b50;
  --text: #f5f7fa;
  --muted: #94a3b8;
  --subtle: #64748b;
  position: relative;
  display: grid;
  min-height: 100svh;
  place-items: stretch;
  overflow: hidden;
  background: var(--page-bg);
  color: var(--text);
}

.register-page--light {
  --page-bg: #e9eef2;
  --panel-bg: #fff;
  --panel-border: rgba(15, 23, 42, .1);
  --field-bg: #f7f9fb;
  --field-border: #d9e0e7;
  --text: #172033;
  --muted: #64748b;
  --subtle: #8491a3;
}

.background-glow {
  position: absolute;
  width: 460px;
  height: 460px;
  border-radius: 50%;
  filter: blur(110px);
  opacity: .18;
  pointer-events: none;
}

.background-glow--green {
  top: -230px;
  left: -130px;
  background: #10b981;
}

.background-glow--blue {
  right: -180px;
  bottom: -260px;
  background: #2563eb;
}

.background-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(148, 163, 184, .035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(148, 163, 184, .035) 1px, transparent 1px);
  background-size: 44px 44px;
  pointer-events: none;
}

.register-shell {
  position: relative;
  z-index: 1;
  display: grid;
  width: 100%;
  min-height: 100svh;
  grid-template-columns: minmax(0, .88fr) minmax(0, 1.12fr);
  overflow: hidden;
  background: var(--panel-bg);
}

.brand-panel {
  position: relative;
  display: flex;
  min-width: 0;
  flex-direction: column;
  overflow: hidden;
  background:
    radial-gradient(circle at 10% 90%, rgba(16, 185, 129, .24), transparent 34%),
    radial-gradient(circle at 100% 5%, rgba(37, 99, 235, .22), transparent 32%),
    linear-gradient(145deg, #071c2d 0%, #072238 52%, #063348 100%);
  padding: clamp(30px, 4vw, 50px);
  color: #fff;
}

.brand-panel::after {
  position: absolute;
  right: -140px;
  bottom: -150px;
  width: 360px;
  height: 360px;
  border: 1px solid rgba(94, 234, 212, .14);
  border-radius: 50%;
  box-shadow: 0 0 0 54px rgba(94, 234, 212, .04), 0 0 0 108px rgba(94, 234, 212, .025);
  content: "";
}

.brand-header,
.brand-content,
.brand-footer {
  position: relative;
  z-index: 1;
}

.brand-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
}

.brand-logo {
  width: min(100%, 235px);
  height: auto;
}

.workspace-badge {
  display: inline-flex;
  flex: 0 0 auto;
  align-items: center;
  gap: 7px;
  border: 1px solid rgba(167, 243, 208, .22);
  border-radius: 999px;
  background: rgba(3, 31, 45, .48);
  padding: 7px 10px;
  color: #c7f9e9;
  font-size: 10px;
  font-weight: 700;
}

.workspace-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #34d399;
  box-shadow: 0 0 0 4px rgba(52, 211, 153, .12);
}

.brand-content {
  margin: auto 0;
  padding: 34px 0;
}

.brand-kicker,
.form-kicker {
  margin: 0 0 12px;
  color: #5eead4;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: .16em;
  text-transform: uppercase;
}

.brand-content h1 {
  margin: 0;
  font-size: clamp(34px, 4vw, 50px);
  font-weight: 750;
  letter-spacing: -.045em;
  line-height: 1;
}

.brand-description {
  max-width: 390px;
  margin: 22px 0 0;
  color: #b6c6d7;
  font-size: 15px;
  line-height: 1.65;
}

.brand-benefits {
  display: grid;
  gap: 11px;
  margin: 26px 0 0;
  padding: 0;
  color: #d9e5ef;
  font-size: 13px;
  list-style: none;
}

.brand-benefits li,
.brand-footer {
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand-benefits :deep(.v-icon) {
  color: #34d399;
}

.brand-footer {
  color: #8eafc1;
  font-size: 11px;
}

.form-panel {
  display: flex;
  min-width: 0;
  flex-direction: column;
  justify-content: space-between;
  background: var(--panel-bg);
  padding: clamp(24px, 3.5vw, 42px) clamp(32px, 5vw, 64px) 20px;
}

.form-container {
  width: min(100%, 540px);
  margin: auto;
}

.form-header {
  margin-bottom: 22px;
}

.form-kicker {
  margin-bottom: 6px;
  color: #10b981;
}

.form-header h2 {
  margin: 0;
  color: var(--text);
  font-size: clamp(27px, 3vw, 34px);
  font-weight: 750;
  letter-spacing: -.035em;
}

.form-header p:last-child {
  margin: 6px 0 0;
  color: var(--muted);
  font-size: 13px;
}

.register-skeleton {
  min-height: 320px;
}

.name-grid,
.password-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.field-label {
  display: block;
  margin-bottom: 6px;
  color: var(--text);
  font-size: 12px;
  font-weight: 650;
}

.field-label--spaced {
  margin-top: 13px;
}

.field-shell {
  display: flex;
  min-height: 48px;
  align-items: center;
  overflow: hidden;
  border: 1px solid var(--field-border);
  border-radius: 9px;
  background: var(--field-bg);
  transition: border-color .18s, box-shadow .18s;
}

.field-shell:hover {
  border-color: color-mix(in srgb, #10b981 45%, var(--field-border));
}

.field-shell:focus-within {
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, .12);
}

.field-icon {
  flex: 0 0 auto;
  margin-left: 13px;
  color: var(--subtle);
}

.field-shell input {
  min-width: 0;
  flex: 1;
  border: 0;
  outline: 0;
  background: transparent;
  padding: 0 11px;
  color: var(--text);
  font-size: 13px;
}

.field-shell input::placeholder {
  color: var(--subtle);
}

.password-toggle {
  display: grid;
  width: 42px;
  align-self: stretch;
  flex: 0 0 42px;
  place-items: center;
  border: 0;
  background: transparent;
  color: var(--subtle);
  cursor: pointer;
}

.password-toggle:hover {
  color: #10b981;
}

.password-toggle:focus-visible,
.register-submit:focus-visible,
.auth-switch a:focus-visible {
  border-radius: 3px;
  outline: 3px solid rgba(16, 185, 129, .22);
  outline-offset: 2px;
}

.password-requirements {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 14px;
  margin-top: 12px;
  color: var(--subtle);
  font-size: 10px;
}

.password-requirements span {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.password-requirements .valid {
  color: #10b981;
}

.register-error {
  margin-top: 12px;
}

.register-submit {
  display: flex;
  width: 100%;
  min-height: 50px;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: 18px;
  border: 1px solid #20c997;
  border-radius: 10px;
  background: linear-gradient(135deg, #0fad7f, #0a8d70);
  box-shadow: 0 12px 24px rgba(16, 185, 129, .18);
  color: #fff;
  font-size: 14px;
  font-weight: 750;
  cursor: pointer;
  transition: transform .18s, box-shadow .18s, filter .18s;
}

.register-submit:hover:not(:disabled) {
  box-shadow: 0 15px 30px rgba(16, 185, 129, .26);
  filter: brightness(1.06);
  transform: translateY(-1px);
}

.register-submit:disabled {
  cursor: wait;
  opacity: .7;
}

.auth-switch {
  margin: 17px 0 0;
  color: var(--muted);
  font-size: 12px;
  text-align: center;
}

.auth-switch a {
  margin-left: 4px;
  color: #10b981;
  font-weight: 700;
  text-decoration: none;
}

.auth-switch a:hover {
  color: #34d399;
  text-decoration: underline;
}

.form-footer {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-top: 16px;
  color: var(--subtle);
  font-size: 9px;
}

@media (max-width: 900px) {
  .brand-header {
    display: block;
  }

  .workspace-badge {
    margin-top: 20px;
  }

  .form-panel {
    padding-inline: 28px;
  }

  .name-grid,
  .password-grid {
    grid-template-columns: 1fr;
    gap: 0;
  }
}

@media (max-width: 767px) {
  .register-page {
    display: block;
    overflow-y: auto;
  }

  .register-shell {
    min-height: 100svh;
    grid-template-columns: 1fr;
  }

  .brand-panel {
    min-height: 170px;
    padding: 24px 26px;
  }

  .brand-header {
    display: flex;
    align-items: center;
  }

  .brand-logo {
    width: 185px;
  }

  .workspace-badge {
    margin-top: 0;
  }

  .brand-content {
    margin: 24px 0 0;
    padding: 0;
  }

  .brand-kicker,
  .brand-description,
  .brand-benefits,
  .brand-footer {
    display: none;
  }

  .brand-content h1 {
    font-size: 27px;
  }

  .brand-content h1 br {
    display: none;
  }

  .form-panel {
    padding: 28px 24px 16px;
  }
}

@media (max-width: 480px) {
  .workspace-badge {
    display: none;
  }

  .brand-panel {
    min-height: 150px;
  }

  .brand-logo {
    width: 165px;
  }

  .brand-content h1 {
    font-size: 23px;
  }

  .form-panel {
    padding-inline: 20px;
  }

  .form-footer {
    display: block;
    text-align: center;
  }

  .form-footer span:last-child {
    display: none;
  }
}

@media (max-height: 740px) and (min-width: 901px) {
  .brand-panel {
    padding-block: 26px;
  }

  .brand-content {
    padding-block: 18px;
  }

  .brand-description {
    margin-top: 14px;
  }

  .brand-benefits {
    gap: 7px;
    margin-top: 16px;
  }

  .form-panel {
    padding-block: 18px 12px;
  }

  .form-header {
    margin-bottom: 14px;
  }

  .field-shell {
    min-height: 44px;
  }

  .field-label--spaced {
    margin-top: 9px;
  }

  .password-requirements {
    margin-top: 8px;
  }

  .register-submit {
    min-height: 46px;
    margin-top: 12px;
  }
}
</style>
