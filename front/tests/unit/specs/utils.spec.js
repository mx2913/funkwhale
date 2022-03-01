import { describe, it, expect } from 'vitest'

import { parseAPIErrors } from '@/utils'

describe('utils', () => {
  describe('parseAPIErrors', () => {
    it('handles flat structure', () => {
      const input = { old_password: ['Invalid password'] }
      const expected = ['Invalid password']
      const output = parseAPIErrors(input)
      expect(output).to.deep.equal(expected)
    })
    it('handles flat structure with multiple errors per field', () => {
      const input = { old_password: ['Invalid password', 'Too short'] }
      const expected = ['Invalid password', 'Too short']
      const output = parseAPIErrors(input)
      expect(output).to.deep.equal(expected)
    })
    it('translate field name', () => {
      const input = { old_password: ['This field is required'] }
      const expected = ['Old Password: This field is required']
      const output = parseAPIErrors(input)
      expect(output).to.deep.equal(expected)
    })
    it('handle nested fields', () => {
      const input = { summary: { text: ['Ensure this field has no more than 5000 characters.'] } }
      const expected = ['Summary - Text: Ensure this field has no more than 5000 characters.']
      const output = parseAPIErrors(input)
      expect(output).to.deep.equal(expected)
    })
  })
})
