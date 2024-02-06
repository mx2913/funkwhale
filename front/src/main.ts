import type { InitModule, InitModuleContext } from '~/types'

import store, { key } from '~/store'
import router from '~/router'

import { createApp, defineAsyncComponent, h } from 'vue'
import { createPinia } from 'pinia'

import useLogger from '~/composables/useLogger'
import useTheme from '~/composables/useTheme'

import Funkwhale from '@funkwhale/ui'
import '@funkwhale/ui/style.css'

import '~/style/_main.scss'

import '~/api'

import 'virtual:uno.css'

// NOTE: Set the theme as fast as possible
useTheme()

const logger = useLogger()
logger.info('Loading environment:', import.meta.env.MODE)
logger.debug('Environment variables:', import.meta.env)

const app = createApp({
  name: 'Root',
  data: () => ({ ready: false }),
  mounted () {
    this.ready = true
    logger.info('Everything loaded!')
  },
  render () {
    if (this.ready) {
      return h(defineAsyncComponent(() => import('~/App.vue')))
    }

    return null
  }
})

const pinia = createPinia()

app.use(router)
app.use(pinia)
app.use(store, key)
app.use(Funkwhale)

const modules: Record<string | 'axios', { install?: InitModule }> = import.meta.glob('./init/*.ts', { eager: true })
const moduleContext: InitModuleContext = {
  app,
  router,
  store
}

// NOTE: Other modules may depend on network requests and we need to ensure
//       that all axios interceptors are set before any requests are made
//       and that the instance url is set before any requests are made
const IMPORTANT_MODULES_QUEUE = ['axios', 'instance']
const waitForImportantModules = async () => {
  logger.debug('Loading important modules')
  for (const moduleName of IMPORTANT_MODULES_QUEUE) {
    const path = `./init/${moduleName}.ts`
    if (!(path in modules)) {
      logger.error(`Failed to load important module: ${path}`)
      continue
    }

    await modules[path].install?.(moduleContext)?.catch((error: Error) => {
      logger.error(`Failed to load important module: ${path}`, error)
      throw error
    })

    delete modules[path]
  }
}

waitForImportantModules()
  .then(() => logger.debug('Loading rest of the modules'))
  // NOTE: We load the modules in parallel
  .then(() => Promise.all(Object.values(modules).map(module => module.install?.(moduleContext))))
  .catch(error => logger.error('Failed to load modules:', error))
  // NOTE: We need to mount the app after all modules are loaded
  .finally(() => {
    logger.debug('Mounting app')
    app.mount('#app')
  })

// TODO (wvffle): Rename filters from useSharedLabels to filters from backend
