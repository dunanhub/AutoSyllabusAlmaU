import vuetify, { transformAssetUrls } from 'vite-plugin-vuetify'

export default defineNuxtConfig({
  compatibilityDate: '2025-05-15',
  devtools: { enabled: true },
  experimental: {
    appManifest: false
  },
  modules: ['@pinia/nuxt', '@nuxtjs/tailwindcss', '@nuxt/eslint'],
  runtimeConfig: {
    public: {
      apiUrl: 'http://localhost:8000/api'
    }
  },
  css: ['vuetify/styles', '~/assets/css/main.css'],
  build: {
    transpile: ['vuetify']
  },
  vite: {
    server: {
      watch: {
        usePolling: true,
        interval: 1000
      }
    },
    vue: {
      template: { transformAssetUrls }
    }
  },
  hooks: {
    'vite:extendConfig': (config) => {
      config.plugins?.push(vuetify({ autoImport: true }))
    }
  },
  components: [
    { path: '~/components/ui', pathPrefix: false },
    { path: '~/components/layout', pathPrefix: false },
    { path: '~/components/syllabus', pathPrefix: false },
    { path: '~/components/templates', pathPrefix: false }
  ],
  app: {
    head: {
      title: 'Syllabus Generator System',
      meta: [
        { name: 'description', content: 'Корпоративная система управления силлабусами AlmaU' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' }
      ]
    }
  },
  typescript: {
    strict: true,
    typeCheck: true
  }
})
