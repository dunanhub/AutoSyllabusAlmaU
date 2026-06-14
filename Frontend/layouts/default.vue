<script setup lang="ts">
const drawerOpen = ref(false)
</script>

<template>
  <div>
    <AppSidebar v-model="drawerOpen" />
    <AppHeader @toggle-drawer="drawerOpen = !drawerOpen" />
    <v-main>
      <div class="mx-auto w-full max-w-[1540px] px-4 py-5 sm:px-6 lg:px-8 lg:py-7">
        <slot />
      </div>
    </v-main>
  </div>
</template>
