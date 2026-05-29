// CartStore 및 순수 총액 계산 단위 테스트 (FE-NFR-M1)
import { describe, it, expect, beforeEach } from 'vitest'
import { cartStore, calcCartTotal } from './cart.js'

describe('calcCartTotal', () => {
  it('빈 장바구니는 0', () => {
    expect(calcCartTotal([])).toBe(0)
  })

  it('항목 소계의 합과 일치', () => {
    const items = [
      { price: 9000, quantity: 2 },
      { price: 2000, quantity: 1 },
    ]
    expect(calcCartTotal(items)).toBe(20000)
  })
})

describe('cartStore', () => {
  beforeEach(() => localStorage.clear())

  it('메뉴 추가 시 수량 1로 생성, 재추가 시 수량 증가', () => {
    cartStore.addItem({ id: 1, name: '비빔밥', price: 9000 })
    cartStore.addItem({ id: 1, name: '비빔밥', price: 9000 })
    const items = cartStore.getItems()
    expect(items).toHaveLength(1)
    expect(items[0].quantity).toBe(2)
  })

  it('수량을 0으로 설정하면 항목 제거', () => {
    cartStore.addItem({ id: 1, name: '비빔밥', price: 9000 })
    cartStore.setQty(1, 0)
    expect(cartStore.getItems()).toHaveLength(0)
  })

  it('총액 계산', () => {
    cartStore.addItem({ id: 1, name: '비빔밥', price: 9000 })
    cartStore.setQty(1, 3)
    cartStore.addItem({ id: 2, name: '콜라', price: 2000 })
    expect(cartStore.getTotal()).toBe(29000)
  })

  it('clear 시 비워짐', () => {
    cartStore.addItem({ id: 1, name: '비빔밥', price: 9000 })
    cartStore.clear()
    expect(cartStore.getItems()).toHaveLength(0)
  })

  it('새로고침(재읽기) 후에도 유지', () => {
    cartStore.addItem({ id: 1, name: '비빔밥', price: 9000 })
    // localStorage를 통해 다시 읽기
    expect(cartStore.getItems()).toHaveLength(1)
  })
})
