/// <reference types="semantic-ui" />

import type { MaybeElement } from '@vueuse/core'
import $ from 'jquery'

export const setupDropdown = (selector: string | HTMLElement = '.ui.dropdown', el: MaybeElement = document.body) => {
  if (!(el instanceof Element)) return null

  const $dropdown = typeof selector === 'string'
    ? $(el).find(selector)
    : $(selector)

  $dropdown.dropdown({
    selectOnKeydown: false,
    action (text: unknown, value: unknown, $el: JQuery) {
      // used to ensure focusing the dropdown and clicking via keyboard
      // works as expected
      $el[0]?.click()

      $dropdown.dropdown('hide')
    }
  })

  return $dropdown
}
