// Vitest 셋업: jest-dom 매처 등록 + localStorage 정리
import '@testing-library/jest-dom'
import { afterEach } from 'vitest'

afterEach(() => {
  localStorage.clear()
})
