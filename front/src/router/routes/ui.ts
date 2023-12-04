import type { RouteRecordRaw } from 'vue-router'

export default [
  {
    path: '/ui',
    name: 'ui',
    component: () => import('~/ui/layouts/constrained.vue'),
    children: [
      {
        path: 'upload',
        name: 'ui.upload',
        component: () => import('~/ui/pages/upload.vue'),
      }
    ]
  }
] as RouteRecordRaw[]
