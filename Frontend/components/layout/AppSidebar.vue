<script setup lang="ts">
import {
  mdiBookEducationOutline,
  mdiChartBoxOutline,
  mdiCogOutline,
  mdiFileDocumentMultipleOutline,
  mdiLogout,
  mdiViewDashboardOutline
} from '@mdi/js'
import { useDisplay } from 'vuetify'

const model = defineModel<boolean>({ default: false })
const route = useRoute()
const auth = useAuthStore()
const { lgAndUp } = useDisplay()

const navigation = [
  { label: 'Обзор', to: '/dashboard', icon: mdiViewDashboardOutline },
  { label: 'Силлабусы', to: '/syllabuses', icon: mdiFileDocumentMultipleOutline },
  { label: 'Шаблоны', to: '/templates', icon: mdiBookEducationOutline },
  { label: 'Аналитика', to: '/analytics', icon: mdiChartBoxOutline },
  { label: 'Настройки', to: '/settings', icon: mdiCogOutline }
]

function isActive(to: string) {
  return to === '/dashboard' ? route.path === to : route.path.startsWith(to)
}

async function logout() {
  auth.logout()
  await navigateTo('/login')
}
</script>

<template>
  <v-navigation-drawer
    v-model="model"
    :width="270"
    :permanent="lgAndUp"
    color="#071A16"
    class="app-sidebar"
  >
    <div class="flex h-full flex-col">
      <NuxtLink to="/dashboard" class="flex h-[72px] items-center gap-3 border-b border-white/10 px-5 text-white">
        <span class="grid size-10 place-items-center rounded-xl bg-primary text-xl font-black text-[#032d23]">A</span>
        <span>
          <strong class="block text-sm tracking-wide">AlmaU</strong>
          <span class="text-[11px] text-white/45">Syllabus Generator</span>
        </span>
      </NuxtLink>

      <div class="px-5 pb-2 pt-6 text-[10px] font-extrabold uppercase tracking-[0.18em] text-white/30">
        Demo workspace
      </div>
      <v-list class="flex-1 bg-transparent px-3" nav density="comfortable">
        <v-list-item
          v-for="item in navigation"
          :key="item.to"
          :active="isActive(item.to)"
          :prepend-icon="item.icon"
          :title="item.label"
          :to="item.to"
          color="primary"
          rounded="lg"
          class="mb-1"
        />
      </v-list>

      <div class="border-t border-white/10 p-3">
        <div class="mb-2 flex items-center gap-3 rounded-xl bg-white/5 p-3">
          <v-avatar color="primary" size="34" class="font-weight-bold text-[#032d23]">
            {{ auth.user?.email.slice(0, 2).toUpperCase() || 'SG' }}
          </v-avatar>
          <div class="min-w-0">
            <p class="truncate text-xs font-bold text-white">{{ auth.user?.email }}</p>
            <p class="mt-0.5 text-[10px] text-white/35">Преподаватель AlmaU</p>
          </div>
        </div>
        <v-btn :prepend-icon="mdiLogout" variant="text" color="white" block class="justify-start opacity-70" @click="logout">
          Выйти
        </v-btn>
      </div>
    </div>
  </v-navigation-drawer>
</template>

<style scoped>
.app-sidebar :deep(.v-list-item--active) {
  background: rgba(16, 185, 129, .16);
}
.app-sidebar :deep(.v-list-item-title) {
  font-size: 13px;
  font-weight: 700;
}
</style>
