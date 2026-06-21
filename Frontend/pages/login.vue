<script setup lang="ts">
import {
  mdiArrowRight,
  mdiCheckCircleOutline,
  mdiEmailOutline,
  mdiEyeOffOutline,
  mdiEyeOutline,
  mdiLockOutline,
  mdiShieldCheckOutline
} from '@mdi/js'

definePageMeta({ layout: 'auth' })

const REMEMBERED_EMAIL_KEY = 'sgs-remembered-email'

const auth = useAuthStore()
const { show } = useAppToast()
const { isDark } = useAppTheme()
const email = ref('')
const password = ref('')
const rememberEmail = ref(false)
const showPassword = ref(false)
const error = ref('')
const loading = ref(false)
const booting = ref(true)

onMounted(async () => {
  const rememberedEmail = localStorage.getItem(REMEMBERED_EMAIL_KEY)
  if (rememberedEmail) {
    email.value = rememberedEmail
    rememberEmail.value = true
  }

  try {
    await auth.initialize()
    if (auth.isAuthenticated) await navigateTo('/dashboard')
  } finally {
    booting.value = false
  }
})

function persistRememberedEmail() {
  if (!import.meta.client) return
  if (rememberEmail.value) localStorage.setItem(REMEMBERED_EMAIL_KEY, email.value.trim())
  else localStorage.removeItem(REMEMBERED_EMAIL_KEY)
}

function forgotPassword() {
  show('Восстановление пароля будет подключено позже.', 'info')
}

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
    await auth.login(email.value.trim(), password.value)
    persistRememberedEmail()
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
  <main class="login-page" :class="{ 'login-page--light': !isDark }">
    <div class="background-glow background-glow--green" aria-hidden="true" />
    <div class="background-glow background-glow--blue" aria-hidden="true" />
    <div class="background-grid" aria-hidden="true" />

    <section class="login-shell">
      <aside class="brand-panel">
        <div class="brand-header">
          <img
            src="/images/almau-logo-white.png"
            alt="AlmaU — Almaty Management University"
            class="brand-logo"
          >
        </div>

        <div class="brand-content">
          <p class="brand-kicker">Academic management platform</p>
          <h1>Syllabus<br>Generator System</h1>
          <p class="brand-description">
            Единое пространство для подготовки, согласования и публикации
            академических силлабусов AlmaU.
          </p>

          <ul class="brand-benefits">
            <li>
              <v-icon :icon="mdiCheckCircleOutline" size="19" />
              Стандартизированная структура документов
            </li>
            <li>
              <v-icon :icon="mdiCheckCircleOutline" size="19" />
              Автосохранение и контроль статуса
            </li>
            <li>
              <v-icon :icon="mdiCheckCircleOutline" size="19" />
              Подготовка официального PDF
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
            <p class="form-kicker">Вход в систему</p>
            <h2>Добро пожаловать</h2>
            <p>Используйте корпоративную учётную запись AlmaU.</p>
          </header>

          <div v-if="booting" class="login-skeleton" aria-label="Загрузка авторизации">
            <v-skeleton-loader color="transparent" type="text, text, button" />
          </div>

          <form v-else class="login-form" novalidate @submit.prevent="submit">
            <label class="field-label" for="login-email">Корпоративный email</label>
            <div class="field-shell">
              <v-icon :icon="mdiEmailOutline" size="21" class="field-icon" />
              <input
                id="login-email"
                v-model="email"
                type="email"
                inputmode="email"
                autocomplete="email"
                placeholder="name@almau.edu.kz"
                aria-describedby="demo-credentials"
              >
            </div>

            <label class="field-label field-label--password" for="login-password">Пароль</label>
            <div class="field-shell">
              <v-icon :icon="mdiLockOutline" size="21" class="field-icon" />
              <input
                id="login-password"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                autocomplete="current-password"
                placeholder="Введите пароль"
              >
              <button
                type="button"
                class="password-toggle"
                :aria-label="showPassword ? 'Скрыть пароль' : 'Показать пароль'"
                @click="showPassword = !showPassword"
              >
                <v-icon :icon="showPassword ? mdiEyeOffOutline : mdiEyeOutline" size="21" />
              </button>
            </div>

            <div class="form-options">
              <label class="remember-control">
                <input v-model="rememberEmail" type="checkbox">
                <span class="custom-checkbox" aria-hidden="true" />
                <span>Запомнить email</span>
              </label>
              <button type="button" class="forgot-link" @click="forgotPassword">
                Забыли пароль?
              </button>
            </div>

            <v-alert
              v-if="error"
              type="error"
              variant="tonal"
              density="compact"
              class="login-error"
            >
              {{ error }}
            </v-alert>

            <button type="submit" class="login-submit" :disabled="loading">
              <v-progress-circular v-if="loading" indeterminate size="21" width="2" />
              <template v-else>
                <span>Войти в систему</span>
                <v-icon :icon="mdiArrowRight" size="22" />
              </template>
            </button>
          </form>

          <div id="demo-credentials" class="demo-credentials auth-switch">
            Нет аккаунта?
            <NuxtLink to="/register">Зарегистрироваться</NuxtLink>
            <!-- <span>Демонстрационный доступ</span>
            <strong>teacher@almau.edu.kz</strong>
            <span class="demo-separator">/</span>
            <strong>Demo12345</strong> -->
          </div>
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
.login-page {
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

.login-page--light {
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
  mask-image: linear-gradient(to bottom, transparent, #000 20%, #000 80%, transparent);
  pointer-events: none;
}

.login-shell {
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
  box-shadow:
    0 0 0 54px rgba(94, 234, 212, .04),
    0 0 0 108px rgba(94, 234, 212, .025);
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
  object-fit: contain;
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
  letter-spacing: .025em;
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
  padding: 36px 0;
}

.brand-kicker,
.form-kicker {
  margin: 0 0 14px;
  color: #5eead4;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: .16em;
  text-transform: uppercase;
}

.brand-content h1 {
  margin: 0;
  font-size: clamp(34px, 4vw, 52px);
  font-weight: 750;
  letter-spacing: -.045em;
  line-height: .98;
}

.brand-description {
  max-width: 390px;
  margin: 24px 0 0;
  color: #b6c6d7;
  font-size: 15px;
  line-height: 1.65;
}

.brand-benefits {
  display: grid;
  gap: 12px;
  margin: 28px 0 0;
  padding: 0;
  color: #d9e5ef;
  font-size: 13px;
  list-style: none;
}

.brand-benefits li {
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand-benefits :deep(.v-icon) {
  color: #34d399;
}

.brand-footer {
  display: flex;
  align-items: center;
  gap: 9px;
  color: #8eafc1;
  font-size: 11px;
}

.form-panel {
  display: flex;
  min-width: 0;
  flex-direction: column;
  justify-content: space-between;
  background: var(--panel-bg);
  padding: clamp(30px, 5vw, 58px) clamp(32px, 5vw, 64px) 24px;
}

.form-container {
  width: min(100%, 420px);
  margin: auto;
}

.form-header {
  margin-bottom: 30px;
}

.form-kicker {
  margin-bottom: 8px;
  color: #10b981;
}

.form-header h2 {
  margin: 0;
  color: var(--text);
  font-size: clamp(28px, 3vw, 36px);
  font-weight: 750;
  letter-spacing: -.035em;
}

.form-header p:last-child {
  margin: 8px 0 0;
  color: var(--muted);
  font-size: 14px;
}

.login-skeleton {
  min-height: 260px;
}

.field-label {
  display: block;
  margin-bottom: 7px;
  color: var(--text);
  font-size: 13px;
  font-weight: 650;
}

.field-label--password {
  margin-top: 18px;
}

.field-shell {
  display: flex;
  min-height: 52px;
  align-items: center;
  overflow: hidden;
  border: 1px solid var(--field-border);
  border-radius: 10px;
  background: var(--field-bg);
  transition: border-color .18s, box-shadow .18s, background .18s;
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
  margin-left: 15px;
  color: var(--subtle);
}

.field-shell input {
  min-width: 0;
  flex: 1;
  border: 0;
  outline: 0;
  background: transparent;
  padding: 0 13px;
  color: var(--text);
  font-size: 14px;
}

.field-shell input::placeholder {
  color: var(--subtle);
}

.password-toggle {
  display: grid;
  width: 48px;
  align-self: stretch;
  flex: 0 0 48px;
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
.forgot-link:focus-visible,
.login-submit:focus-visible {
  outline: 3px solid rgba(16, 185, 129, .24);
  outline-offset: 2px;
}

.form-options {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-top: 16px;
  color: var(--muted);
  font-size: 12px;
}

.remember-control {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  cursor: pointer;
}

.remember-control input {
  position: absolute;
  width: 1px;
  height: 1px;
  opacity: 0;
}

.custom-checkbox {
  display: grid;
  width: 17px;
  height: 17px;
  place-items: center;
  border: 1px solid var(--field-border);
  border-radius: 4px;
  background: var(--field-bg);
}

.remember-control input:checked + .custom-checkbox {
  border-color: #10b981;
  background: #10b981;
}

.remember-control input:checked + .custom-checkbox::after {
  width: 8px;
  height: 4px;
  border-bottom: 2px solid #fff;
  border-left: 2px solid #fff;
  content: "";
  transform: translateY(-1px) rotate(-45deg);
}

.remember-control input:focus-visible + .custom-checkbox {
  box-shadow: 0 0 0 3px rgba(16, 185, 129, .2);
}

.forgot-link {
  border: 0;
  background: transparent;
  color: #10b981;
  font: inherit;
  font-weight: 650;
  cursor: pointer;
}

.forgot-link:hover {
  color: #34d399;
}

.login-error {
  margin-top: 14px;
}

.login-submit {
  display: flex;
  width: 100%;
  min-height: 52px;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: 22px;
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

.login-submit:hover:not(:disabled) {
  box-shadow: 0 15px 30px rgba(16, 185, 129, .26);
  filter: brightness(1.06);
  transform: translateY(-1px);
}

.login-submit:disabled {
  cursor: wait;
  opacity: .7;
}

.demo-credentials {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 5px;
  margin-top: 24px;
  border-top: 1px solid var(--panel-border);
  padding-top: 18px;
  color: var(--subtle);
  font-size: 10px;
}

.auth-switch {
  margin: 18px 0 0;
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

.auth-switch a:focus-visible {
  border-radius: 3px;
  outline: 3px solid rgba(16, 185, 129, .22);
  outline-offset: 2px;
}

.demo-credentials span:first-child {
  width: 100%;
  margin-bottom: 2px;
  text-align: center;
  text-transform: uppercase;
  letter-spacing: .08em;
}

.demo-credentials strong {
  color: var(--muted);
  font-weight: 650;
}

.demo-separator {
  color: var(--field-border);
}

.form-footer {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-top: 24px;
  color: var(--subtle);
  font-size: 9px;
}

@media (max-width: 900px) {
  .brand-header {
    display: block;
  }

  .workspace-badge {
    margin-top: 22px;
  }

  .brand-content h1 {
    font-size: 40px;
  }

  .form-panel {
    padding-inline: 32px;
  }
}

@media (max-width: 767px) {
  .login-page {
    display: block;
    overflow-y: auto;
  }

  .login-shell {
    min-height: 100svh;
    grid-template-columns: 1fr;
  }

  .brand-panel {
    min-height: 190px;
    padding: 25px 26px;
  }

  .brand-header {
    display: flex;
    align-items: center;
  }

  .brand-logo {
    width: 190px;
  }

  .workspace-badge {
    margin-top: 0;
  }

  .brand-content {
    margin: 28px 0 0;
    padding: 0;
  }

  .brand-kicker,
  .brand-description,
  .brand-benefits,
  .brand-footer {
    display: none;
  }

  .brand-content h1 {
    font-size: 29px;
    line-height: 1.05;
  }

  .brand-content h1 br {
    display: none;
  }

  .form-panel {
    min-height: 460px;
    padding: 30px 26px 18px;
  }

  .form-header {
    margin-bottom: 24px;
  }
}

@media (max-width: 480px) {
  .workspace-badge {
    display: none;
  }

  .brand-panel {
    min-height: 164px;
  }

  .brand-logo {
    width: 170px;
  }

  .brand-content {
    margin-top: 22px;
  }

  .brand-content h1 {
    font-size: 25px;
  }

  .form-panel {
    padding: 26px 20px 16px;
  }

  .form-options {
    align-items: flex-start;
  }

  .form-footer {
    display: block;
    text-align: center;
  }

  .form-footer span:last-child {
    display: none;
  }
}

@media (max-height: 740px) and (min-width: 768px) {
  .login-shell {
    min-height: 100svh;
  }

  .brand-panel {
    padding-block: 28px;
  }

  .brand-content {
    padding-block: 20px;
  }

  .brand-description {
    margin-top: 16px;
  }

  .brand-benefits {
    gap: 8px;
    margin-top: 18px;
  }

  .form-panel {
    padding-block: 26px 16px;
  }

  .form-header {
    margin-bottom: 20px;
  }

  .field-label--password {
    margin-top: 12px;
  }

  .login-submit {
    margin-top: 16px;
  }

  .demo-credentials {
    margin-top: 16px;
    padding-top: 12px;
  }

  .form-footer {
    margin-top: 14px;
  }
}
</style>
