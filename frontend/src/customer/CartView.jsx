// 고객용 장바구니 화면 (US-C3)
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { cartStore } from '../store/cart.js'

export default function CartView() {
  const navigate = useNavigate()
  const [items, setItems] = useState(cartStore.getItems())

  const total = items.reduce((s, it) => s + it.price * it.quantity, 0)

  const changeQty = (id, delta) => {
    const target = items.find((i) => i.menu_item_id === id)
    const next = cartStore.setQty(id, target.quantity + delta)
    setItems([...next])
  }
  const remove = (id) => setItems([...cartStore.removeItem(id)])
  const clearAll = () => {
    cartStore.clear()
    setItems([])
  }

  return (
    <div className="cart-page">
      <header className="page-header">
        <button className="back-btn" data-testid="cart-back"
                onClick={() => navigate('/customer')} aria-label="뒤로가기">‹</button>
        <h2>장바구니</h2>
      </header>

      {items.length === 0 ? (
        <div className="empty-state" data-testid="cart-empty">
          <div className="emoji">🛒</div>
          <div className="empty-title">장바구니가 비어 있어요</div>
          <p className="muted">메뉴를 담아 주문해 보세요.</p>
          <button className="btn primary" onClick={() => navigate('/customer')}>메뉴 보러가기</button>
        </div>
      ) : (
        <>
          <ul className="cart-list">
            {items.map((it) => (
              <li key={it.menu_item_id} className="cart-item">
                <div className="cart-item-top">
                  <div>
                    <div className="cart-item-name">{it.name}</div>
                    <div className="cart-item-unit">단가 {it.price.toLocaleString()}원</div>
                  </div>
                  <button className="cart-remove" data-testid={`cart-remove-${it.menu_item_id}`}
                          onClick={() => remove(it.menu_item_id)}>삭제</button>
                </div>
                <div className="cart-item-bottom">
                  <div className="qty-stepper">
                    <button data-testid={`cart-dec-${it.menu_item_id}`}
                            onClick={() => changeQty(it.menu_item_id, -1)} aria-label="수량 감소">−</button>
                    <span className="qty-num" data-testid={`cart-qty-${it.menu_item_id}`}>{it.quantity}</span>
                    <button data-testid={`cart-inc-${it.menu_item_id}`}
                            onClick={() => changeQty(it.menu_item_id, 1)} aria-label="수량 증가">+</button>
                  </div>
                  <span className="cart-item-subtotal">{(it.price * it.quantity).toLocaleString()}원</span>
                </div>
              </li>
            ))}
          </ul>

          <div className="cart-footer-bar">
            <div className="cart-total-row">
              <span className="label">총 합계</span>
              <span className="amount" data-testid="cart-total">{total.toLocaleString()}원</span>
            </div>
            <div className="cart-actions">
              <button className="btn-text" data-testid="cart-clear" onClick={clearAll}>장바구니 비우기</button>
              <button className="btn primary" data-testid="cart-checkout-button"
                      onClick={() => navigate('/customer/confirm')}>주문하기</button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
