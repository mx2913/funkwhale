import { useColorMode, usePreferredDark } from '@vueuse/core'
import { computed } from 'vue'

const theme = useColorMode({
  selector: 'html',
  modes: {
    auto: '',
    light: 'theme-light light',
    dark: 'theme-dark dark'
  },
  emitAuto: true
})

const preferredDark = usePreferredDark({ window })
const selectedTheme = computed(() => theme.value === 'auto'
  ? preferredDark.value ? 'dark' : 'light'
  : theme.value
)

export default () => ({
  theme,
  selectedTheme
})
