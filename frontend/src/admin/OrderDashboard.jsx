// 실시간 주문 모니터링 대시보드 (US-A2, US-T1)
import { useEffect, useState, useCallback } from 'react'
import { api } from '../api/client.js'
import { authStore } from '../store/auth.js'
import { useSse } from '../api/sse.js'

const STATUSES = ['대기중', '준비중', '완료']

export default function OrderDashboard() {
  const token = authStore.getAdminToken()
  const [tables, setTables] = useState([])
  const [selectedOrder, setSelectedOrder] = useState(null)
  const [highlight, setHighlight] = useState({}) // table_id -> true
  const [error, setError] = useState('')

  const reload = useCallback(async () => {
    try {
      const data = await api.get('/api/admin/tables', token)
      setTables(data)
    } catch (err) {
      setError(err.detail || '주문 현황을 불러오지 못했습니다.')
    }
  }, [token])

  useEffect(() => {
    reload()
  }, [reload])

  // SSE 실시간 갱신 + 신규 주문 강조
  useSse('/api/admin/stream', token, (event) => {
    reload()
    if (event.type === 'order_created' && event.table_id) {
      setHighlight((h) => ({ ...h, [event.table_id]: true }))
      setTimeout(() => {
        setHighlight((h) => {
          const next = { ...h }
          delete next[event.table_id]
          return next
        })
      }, 3000)
    }
  })

  const changeStatus = async (orderId, status) => {
    await api.patch(`/api/admin/orders/${orderId}/status`, { status }, token)
    await reload()
    setSelectedOrder(null)
  }

  const deleteOrder = async (orderId) => {
    if (!window.confirm('이 주문을 삭제하시겠습니까?')) return
    await api.del(`/api/admin/orders/${orderId}`, token)
    await reload()
    setSelectedOrder(null)
  }

  return (
    <div className="dashboard">
      <h2>실시간 주문 모니터링</h2>
      {error && <div className="error">{error}</div>}
      <div className="table-grid">
        {tables.map((t) => (
          <div key={t.table_id}
               className={`table-card ${highlight[t.table_id] ? 'highlight' : ''}`}
               data-testid={`table-card-${t.table_number}`}>
            <div className="table-card-head">
              <span className="table-no">테이블 {t.table_number}</span>
              <span className="total">{t.total_amount.toLocaleString()}원</span>
            </div>
            <div className="muted small">{t.session_active ? '이용중' : '비어있음'} · 주문 {t.orders.length}건</div>
            <ul className="mini-orders">
              {t.orders.slice(0, 3).map((o) => (
                <li key={o.id} className="mini-order"
                    data-testid={`dash-order-${o.id}`}
                    onClick={() => setSelectedOrder(o)}>
                  <span>#{o.order_number}</span>
                  <span className="badge">{o.status}</span>
                </li>
              ))}
            </ul>
          </div>
        ))}
        {tables.length === 0 && !error && <p className="muted">등록된 테이블이 없습니다.</p>}
      </div>

      {selectedOrder && (
        <div className="modal-backdrop" onClick={() => setSelectedOrder(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()} data-testid="order-detail-modal">
            <h3>주문 #{selectedOrder.order_number} 상세</h3>
            <ul className="order-items">
              {selectedOrder.items.map((it, idx) => (
                <li key={idx}>{it.menu_name} × {it.quantity} ({(it.unit_price * it.quantity).toLocaleString()}원)</li>
              ))}
            </ul>
            <div className="total">합계: {selectedOrder.total_amount.toLocaleString()}원</div>
            <div className="status-buttons">
              {STATUSES.map((s) => (
                <button key={s}
                        className={`btn ${selectedOrder.status === s ? 'primary' : ''}`}
                        data-testid={`set-status-${s}`}
                        onClick={() => changeStatus(selectedOrder.id, s)}>{s}</button>
              ))}
            </div>
            <div className="row">
              <button className="btn danger" data-testid="delete-order"
                      onClick={() => deleteOrder(selectedOrder.id)}>주문 삭제</button>
              <button className="btn" onClick={() => setSelectedOrder(null)}>닫기</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
