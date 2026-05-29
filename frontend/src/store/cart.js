// 장바구니 저장소 (localStorage 기반) - US-C3, FE-NFR-S1
const CART_KEY = 'tableorder.cart'

// 순수 함수: 장바구니 총액 계산 (단위 테스트 대상, 백엔드 calc_total과 일관)
export function calcCartTotal(items) {
  return items.reduce((sum, it) => sum + it.price * it.quantity, 0)
}

function read() {
  const raw = localStorage.getItem(CART_KEY)
  return raw ? JSON.parse(raw) : []
}

function write(items) {
  localStorage.setItem(CART_KEY, JSON.stringify(items))
}

export const cartStore = {
  getItems() {
    return read()
  },

  addItem(menuItem) {
    const items = read()
    const existing = items.find((it) => it.menu_item_id === menuItem.id)
    if (existing) {
      existing.quantity += 1
    } else {
      items.push({
        menu_item_id: menuItem.id,
        name: menuItem.name,
        price: menuItem.price,
        quantity: 1,
      })
    }
    write(items)
    return items
  },

  setQty(menuItemId, quantity) {
    let items = read()
    if (quantity <= 0) {
      items = items.filter((it) => it.menu_item_id !== menuItemId)
    } else {
      const target = items.find((it) => it.menu_item_id === menuItemId)
      if (target) target.quantity = quantity
    }
    write(items)
    return items
  },

  removeItem(menuItemId) {
    const items = read().filter((it) => it.menu_item_id !== menuItemId)
    write(items)
    return items
  },

  clear() {
    localStorage.removeItem(CART_KEY)
  },

  getTotal() {
    return calcCartTotal(read())
  },
}
