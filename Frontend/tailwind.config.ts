import type { Config } from 'tailwindcss'

export default <Partial<Config>>{
  content: [],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eef8f3',
          100: '#d9efe5',
          200: '#b5dfcc',
          300: '#84c8aa',
          400: '#4cab83',
          500: '#248c65',
          600: '#126f50',
          700: '#0c5942',
          800: '#0a4736',
          900: '#07392c',
          950: '#032219'
        }
      },
      boxShadow: {
        card: '0 1px 2px rgb(15 23 42 / 0.04)',
        panel: '0 8px 30px rgb(15 23 42 / 0.08)'
      }
    }
  }
}
