import { createVuetify } from 'vuetify'
import { aliases, mdi } from 'vuetify/iconsets/mdi-svg'

export default defineNuxtPlugin((nuxtApp) => {
  const vuetify = createVuetify({
    ssr: true,
    icons: {
      defaultSet: 'mdi',
      aliases,
      sets: { mdi }
    },
    theme: {
      defaultTheme: 'almauDark',
      themes: {
        almauDark: {
          dark: true,
          colors: {
            background: '#0B1220',
            surface: '#111827',
            'surface-bright': '#162033',
            'surface-variant': '#1E293B',
            primary: '#10B981',
            'primary-darken-1': '#059669',
            secondary: '#8B5CF6',
            info: '#38BDF8',
            warning: '#F59E0B',
            error: '#F87171',
            success: '#10B981',
            'on-background': '#F8FAFC',
            'on-surface': '#F8FAFC'
          },
          variables: {
            'border-color': '#FFFFFF',
            'border-opacity': 0.08,
            'high-emphasis-opacity': 0.96,
            'medium-emphasis-opacity': 0.62
          }
        },
        almauLight: {
          dark: false,
          colors: {
            background: '#F4F7F6',
            surface: '#FFFFFF',
            'surface-bright': '#F8FAFC',
            'surface-variant': '#E8EFEC',
            primary: '#087F5B',
            'primary-darken-1': '#064E3B',
            secondary: '#7C3AED',
            info: '#0284C7',
            warning: '#D97706',
            error: '#DC2626',
            success: '#059669',
            'on-background': '#10201A',
            'on-surface': '#10201A'
          },
          variables: {
            'border-color': '#0F172A',
            'border-opacity': 0.1,
            'high-emphasis-opacity': 0.94,
            'medium-emphasis-opacity': 0.64
          }
        }
      }
    },
    defaults: {
      VBtn: { rounded: 'lg', elevation: 0 },
      VCard: { rounded: 'xl', elevation: 0 },
      VTextField: { variant: 'outlined', density: 'comfortable', color: 'primary', hideDetails: 'auto' },
      VSelect: { variant: 'outlined', density: 'comfortable', color: 'primary', hideDetails: 'auto' },
      VTextarea: { variant: 'outlined', density: 'comfortable', color: 'primary', hideDetails: 'auto' }
    }
  })

  nuxtApp.vueApp.use(vuetify)
})
