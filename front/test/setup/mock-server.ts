import { handlers } from '../msw-server'
import { setupServer } from 'msw/node'

import.meta.env.VUE_APP_INSTANCE_URL = 'http://localhost:3000/'

const server = setupServer(
  ...handlers.map((handler) => {
    if (typeof handler.info.path === 'string') {
      handler.info.path = handler.info.path.replace('/api/v1', '')
    }

    handler.info.header = handler.info.header.replace('/api/v1', '')
    return handler
  })
)

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())
