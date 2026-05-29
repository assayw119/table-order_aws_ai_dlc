// 고객용 주문 내역 화면 + SSE 실시간 갱신 (US-C5, US-T1)
import { useEffect, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client.js'
import { authStore } from '../store/auth.js'
import { useSse } from '../api/sse.js'

const STATUS_META = {
  대기중: { cls: 'pending', label: '대기중' },
  준비중: { cls: 'preparing', label: '준비중' },
  완료: { cls: 'done', label: '완료' },
}

function formatTime(iso) {
  try {
    const d = new Date(iso)
    return d.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })
  } catch {
    return ''
  }
}

export default function OrderHistoryView() {
  const navigate = useNavigate()
  const token = authStore.getTableToken()
  const [orders, setOrders] = useState([])
  const [error, setError] = useState('')

  const reload = useCallback(async () => {
    try {
      setOrders(await api.get('/api/orders/current', token))
    } catch (err) {
      setError(err.detail || '주문 내역을 불러오지 못했습니다.')
    }
  }, [token])

  useEffect(() => {
    reload()
  }, [reload])

  useSse('/api/table/stream', token, () => reload())

  // 최신 주문이 위로
  const sorted = [...orders].sort((a, b) => new Date(b.created_at) - new Date(a.created_at))

  return (
    <>
      <header className="cust-header">
        <div className="store-info">
          <span className="store-name">주문 내역</span>
          <span className="table-badge">현재 식사 세션</span>
        </div>
        <button className="header-action" data-testid="goto-menu"
                onClick={() => navigate('/customer')}>
          🍽️ 메뉴
        </button>
      </header>

      <div className="cust-main">
        {error && <div className="error" style={{ margin: '16px 20px' }}>{error}</div>}

        {sorted.length === 0 && !error ? (
          <div className="empty-state" data-testid="orders-empty">
            <div className="emoji">🧾</div>
            <div className="empty-title">아직 주문 내역이 없어요</div>
            <p className="muted">메뉴에서 마음에 드는 음식을 주문해 보세요.</p>
            <button className="btn primary" onClick={() => navigate('/customer')}>메뉴 보러가기</button>
          </div>
        ) : (
          <div className="order-history">
            {sorted.map((o) => {
              const meta = STATUS_META[o.status] || { cls: '', label: o.status }
              return (
                <div key={o.id} className="order-card" data-testid={`order-${o.id}`}>
                  <div className="order-card-head">
                    <span className="order-no">주문 #{o.order_number}</span>
                    <span className={`status-badge ${meta.cls}`} data-testid={`order-status-${o.id}`}>
                      {meta.label}
                    </span>
                  </div>
                  <div className="order-time">{formatTime(o.created_at)}</div>
                  <ul className="order-items-list">
                    {o.items.map((it, idx) => (
                      <li key={idx}>
                        <span>{it.menu_name} × {it.quantity}</span>
                        <span className="muted">{(it.unit_price * it.quantity).toLocaleString()}원</span>
                      </li>
                    ))}
                  </ul>
                  <div className="order-card-foot">
                    <span className="muted small">총 금액</span>
                    <span className="order-amount">{o.total_amount.toLocaleString()}원</span>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </>
  )
}
