// 고객용 주문 확정 + 성공 오버레이 (US-C4)
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client.js'
import { authStore } from '../store/auth.js'
import { cartStore } from '../store/cart.js'

export default function OrderConfirm() {
  const navigate = useNavigate()
  const token = authStore.getTableToken()
  const [items] = useState(cartStore.getItems())
  const [status, setStatus] = useState('review') // review | submitting | success | error
  const [orderNumber, setOrderNumber] = useState(null)
  const [countdown, setCountdown] = useState(5)
  const [error, setError] = useState('')

  const total = items.reduce((s, it) => s + it.price * it.quantity, 0)

  // 성공 시 5초 카운트다운 후 메뉴로 복귀
  useEffect(() => {
    if (status !== 'success') return
    if (countdown <= 0) {
      navigate('/customer', { replace: true })
      return
    }
    const t = setTimeout(() => setCountdown((c) => c - 1), 1000)
    return () => clearTimeout(t)
  }, [status, countdown, navigate])

  const submit = async () => {
    setStatus('submitting')
    setError('')
    try {
      const payload = {
        items: items.map((it) => ({ menu_item_id: it.menu_item_id, quantity: it.quantity })),
      }
      const result = await api.post('/api/orders', payload, token)
      setOrderNumber(result.order_number)
      cartStore.clear()
      setStatus('success')
    } catch (err) {
      setError(err.detail || '주문에 실패했습니다. 다시 시도해주세요.')
      setStatus('error')
    }
  }

  return (
    <div className="cart-page">
      <header className="page-header">
        <button className="back-btn" data-testid="confirm-back"
                onClick={() => navigate('/customer/cart')} aria-label="뒤로가기">‹</button>
        <h2>주문 확인</h2>
      </header>

      {items.length === 0 ? (
        <div className="empty-state">
          <div className="emoji">🛒</div>
          <div className="empty-title">장바구니가 비어 있어요</div>
          <button className="btn primary" onClick={() => navigate('/customer')}>메뉴 보러가기</button>
        </div>
      ) : (
        <>
          <ul className="cart-list">
            {items.map((it) => (
              <li key={it.menu_item_id} className="cart-item">
                <div className="cart-item-bottom">
                  <div>
                    <div className="cart-item-name">{it.name}</div>
                    <div className="cart-item-unit">{it.price.toLocaleString()}원 × {it.quantity}</div>
                  </div>
                  <span className="cart-item-subtotal">{(it.price * it.quantity).toLocaleString()}원</span>
                </div>
              </li>
            ))}
          </ul>

          <div className="cart-footer-bar">
            <div className="cart-total-row">
              <span className="label">총 합계</span>
              <span className="amount" data-testid="confirm-total">{total.toLocaleString()}원</span>
            </div>
            {error && <div className="error" data-testid="order-error" style={{ marginBottom: 12 }}>{error}</div>}
            <div className="cart-actions">
              <button className="btn primary" data-testid="order-submit"
                      style={{ width: '100%' }}
                      disabled={status === 'submitting'} onClick={submit}>
                {status === 'submitting' ? '주문 중...' : '주문 확정'}
              </button>
            </div>
          </div>
        </>
      )}

      {status === 'success' && (
        <div className="success-overlay" data-testid="order-success">
          <div className="success-card">
            <div className="success-check">✓</div>
            <h2>주문 완료!</h2>
            <p className="muted">주방으로 주문이 전달되었어요.</p>
            <div className="success-order-no">
              주문 번호 <strong data-testid="success-order-number">{orderNumber}</strong>
            </div>
            <p className="countdown" data-testid="countdown">{countdown}초 후 메뉴 화면으로 돌아갑니다.</p>
            <button className="btn primary" style={{ width: '100%' }}
                    onClick={() => navigate('/customer', { replace: true })}>
              메뉴로 돌아가기
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
