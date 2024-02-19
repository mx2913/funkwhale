import { useLocalStorage } from '@vueuse/core'
import { createRouter, createWebHistory } from 'vue-router'

import routesV1 from './routes'
import routesV2 from '~/ui/routes'

const isUIv2 = useLocalStorage('ui-v2', false)
const routes = isUIv2.value ? routesV2 : routesV1

export default createRouter({
  history: createWebHistory(import.meta.env.VUE_APP_ROUTER_BASE_URL as string ?? '/'),
  linkActiveClass: 'active',
  routes,

  scrollBehavior (to, from, savedPosition) {
    if (to.meta.preserveScrollPosition) {
      return savedPosition ?? { left: 0, top: 0 }
    }

    return new Promise(resolve => {
      setTimeout(() => {
        if (to.hash) {
          resolve({ el: to.hash, behavior: 'smooth' })
        }

        resolve(savedPosition ?? { left: 0, top: 0 })
      }, 100)
    })
  }
})
