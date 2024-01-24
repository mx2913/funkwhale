import type { RouteRecordRaw } from 'vue-router'
import { useUploadsStore } from '~/ui/stores/upload'

export default [
  {
    path: '/ui',
    name: 'ui',
    component: () => import('~/ui/layouts/constrained.vue'),
    children: [
      {
        path: 'upload',
        name: 'upload',
        component: () => import('~/ui/pages/upload.vue'),
        children: [
          {
            path: '',
            name: 'upload.index',
            component: () => import('~/ui/pages/upload/index.vue')
          },

          {
            path: 'running',
            name: 'upload.running',
            component: () => import('~/ui/pages/upload/running.vue'),
            beforeEnter: (_to, _from, next) => {
              const uploads = useUploadsStore()
              if (uploads.uploadGroups.length === 0) {
                next('/ui/upload')
              } else {
                next()
              }
            }
          },

          {
            path: 'history',
            name: 'upload.history',
            component: () => import('~/ui/pages/upload/history.vue')
          },

          {
            path: 'all',
            name: 'upload.all',
            component: () => import('~/ui/pages/upload/all.vue')
          }
        ]
      }
    ]
  }
] as RouteRecordRaw[]
