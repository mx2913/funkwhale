import { visualizer } from 'rollup-plugin-visualizer'
import { defineConfig, type PluginOption } from 'vite'
import { VitePWA } from 'vite-plugin-pwa'
import { resolve } from 'path'

import manifest from './pwa-manifest.json'

import VueI18n from '@intlify/unplugin-vue-i18n/vite'
import Vue from '@vitejs/plugin-vue'
import VueMacros from 'unplugin-vue-macros/vite'
import VueDevTools from 'vite-plugin-vue-devtools'

import { fileURLToPath, URL } from "url"

const port = +(process.env.VUE_PORT ?? 8080)

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  envPrefix: ['VUE_', 'FUNKWHALE_SENTRY_'],
  plugins: [
    // https://github.com/webfansplz/vite-plugin-vue-devtools
    VueDevTools(),

    // https://vue-macros.sxzz.moe/
    VueMacros({
      plugins: {
        // https://github.com/vitejs/vite/tree/main/packages/plugin-vue
        vue: Vue(),
      }
    }),

    // https://github.com/intlify/bundle-tools/tree/main/packages/vite-plugin-vue-i18n
    VueI18n({
      include: resolve(__dirname, './src/locales/**')
    }),

    // https://github.com/btd/rollup-plugin-visualizer
    visualizer() as unknown as PluginOption,

    // https://github.com/antfu/vite-plugin-pwa
    VitePWA({
      strategies: 'injectManifest',
      srcDir: 'src',
      filename: 'serviceWorker.ts',
      manifestFilename: 'manifest.json',
      devOptions: {
        enabled: true,
        type: 'module',
        navigateFallback: 'index.html'
      },
      manifest
    })
  ],
  server: {
    port
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `
          @use "./src/style/global-vars" as *;
        `
      }
    }
  },
  resolve: {
    alias: [
      { find: '#', replacement: fileURLToPath(new URL('./src/worker', import.meta.url)) },
      { find: '?', replacement: fileURLToPath(new URL('./test', import.meta.url)) },
      { find: '~', replacement: fileURLToPath(new URL('./src', import.meta.url)) }
    ]
  },
  build: {
    sourcemap: true,
    // https://rollupjs.org/configuration-options/
    rollupOptions: {
      output: {
        manualChunks: {
          'axios': ['axios', 'axios-auth-refresh'],
          'dompurify': ['dompurify'],
          'jquery': ['jquery'],
          'lodash': ['lodash-es'],
          'moment': ['moment'],
          'sentry': ['@sentry/vue', '@sentry/tracing'],
          'standardized-audio-context': ['standardized-audio-context'],
          'vue-router': ['vue-router'],
        }
      }
    }
  },
  test: {
    environment: 'jsdom',
    globals: true,
    reporters: ['default', 'junit'],
    outputFile: "./test_results.xml",
    coverage: {
      src: './src',
      all: true,
      reporter: ['text', 'cobertura']
    },
    setupFiles: [
      './test/setup/mock-audio-context.ts',
      './test/setup/mock-vue-i18n.ts'
    ]
  }
}))
