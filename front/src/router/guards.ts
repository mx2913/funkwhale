import type { NavigationGuardNext, RouteLocationNamedRaw, RouteLocationNormalized } from 'vue-router'
import type { Permission } from '~/store/auth'

import store from '~/store'

export const hasPermissions = (permission: Permission) => (to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) => {
  if (store.state.auth.authenticated && store.state.auth.availablePermissions[permission]) {
    return next()
  }

  console.log('Not authenticated. Redirecting to library.')
  next({ name: 'library.index' })
}

export const requireLoggedIn = (fallbackLocation?: RouteLocationNamedRaw) => (to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) => {
  if (store.state.auth.authenticated) return next()
  console.log('!', to)
  return next(fallbackLocation ?? { name: 'login', query: { next: to.fullPath } })
}

export const requireLoggedOut = (fallbackLocation: RouteLocationNamedRaw) => (to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) => {
  if (!store.state.auth.authenticated) return next()
  return next(fallbackLocation)
}
