import { describe, it, expect } from 'vitest'

import { normalizeQuery, parseTokens, compileTokens } from '@/search'

describe('search', () => {
  it('normalizeQuery returns correct tokens', () => {
    const input = 'this is a "search query" yeah'
    const output = normalizeQuery(input)
    expect(output).to.deep.equal(['this', 'is', 'a', 'search query', 'yeah'])
  })
  it('parseTokens can extract fields and values from tokens', () => {
    const input = ['unhandled', 'key:value', 'status:pending', 'title:"some title"', 'anotherunhandled']
    const output = parseTokens(input)
    const expected = [
      {
        field: null,
        value: 'unhandled'
      },
      {
        field: 'key',
        value: 'value'
      },
      {
        field: 'status',
        value: 'pending'
      },
      {
        field: 'title',
        value: 'some title'
      },
      {
        field: null,
        value: 'anotherunhandled'
      }
    ]
    expect(output).to.deep.equal(expected)
  })
  it('compileTokens returns proper query string', () => {
    const input = [
      {
        field: null,
        value: 'unhandled'
      },
      {
        field: 'key',
        value: 'value'
      },
      {
        field: 'status',
        value: 'pending'
      },
      {
        field: 'title',
        value: 'some title'
      },
      {
        field: null,
        value: 'anotherunhandled'
      }
    ]
    const expected = 'unhandled key:value status:pending title:"some title" anotherunhandled'
    const output = compileTokens(input)
    expect(output).to.deep.equal(expected)
  })
})
