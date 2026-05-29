// 테이블 관리: 초기 설정, 이용 완료, 과거 내역 (US-A3)
import { useEffect, useState, useCallback } from 'react'
import { api } from '../api/client.js'
import { authStore } from '../store/auth.js'

export default function TableManagement() {
  const token = authStore.getAdminToken()
  const [tables, setTables] = useState([])
  const [error, setError] = useState('')

  // 초기 설정 폼
  const [tableNumber, setTableNumber] = useState('')
  const [tablePassword, setTablePassword] = useState('')

  // 과거 내역 모달
  const [historyTable, setHistoryTable] = useState(null)
  const [history, setHistory] = useState([])
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')

  const reload = useCallback(async () => {
    try {
      setTables(await api.get('/api/admin/tables', token))
    } catch (err) {
      setError(err.detail || '테이블 정보를 불러오지 못했습니다.')
    }
  }, [token])

  useEffect(() => {
    reload()
  }, [reload])

  const setupTable = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await api.post('/api/admin/tables/setup', {
        table_number: Number(tableNumber),
        table_password: tablePassword,
      }, token)
      setTableNumber('')
      setTablePassword('')
      await reload()
    } catch (err) {
      setError(err.detail || '테이블 설정에 실패했습니다.')
    }
  }

  const checkout = async (tableId) => {
    if (!window.confirm('이 테이블을 이용 완료 처리하시겠습니까? 현재 주문이 과거 내역으로 이동됩니다.')) return
    await api.post(`/api/admin/tables/${tableId}/checkout`, {}, token)
    await reload()
  }

  const openHistory = async (table) => {
    setHistoryTable(table)
    await loadHistory(table.table_id)
  }

  const loadHistory = async (tableId) => {
    let path = `/api/admin/tables/${tableId}/history`
    const params = []
    if (dateFrom) params.push(`date_from=${encodeURIComponent(dateFrom)}`)
    if (dateTo) params.push(`date_to=${encodeURIComponent(dateTo)}`)
    if (params.length) path += `?${params.join('&')}`
    setHistory(await api.get(path, token))
  }

  return (
    <div className="table-management">
      <h2>테이블 관리</h2>
      {error && <div className="error">{error}</div>}

      <form className="card form inline" onSubmit={setupTable}>
        <h3>테이블 초기 설정</h3>
        <input placeholder="테이블 번호" type="number" value={tableNumber}
               data-testid="setup-table-number-input"
               onChange={(e) => setTableNumber(e.target.value)} required />
        <input placeholder="테이블 비밀번호" type="text" value={tablePassword}
               data-testid="setup-table-password-input"
               onChange={(e) => setTablePassword(e.target.value)} required />
        <button className="btn primary" data-testid="setup-table-submit">설정 저장</button>
      </form>

      <div className="table-grid">
        {tables.map((t) => (
          <div key={t.table_id} className="table-card" data-testid={`mgmt-table-${t.table_number}`}>
            <div className="table-card-head">
              <span className="table-no">테이블 {t.table_number}</span>
              <span className="total">{t.total_amount.toLocaleString()}원</span>
            </div>
            <div className="muted small">{t.session_active ? '이용중' : '비어있음'}</div>
            <div className="row">
              <button className="btn small" data-testid={`table-checkout-${t.table_id}`}
                      onClick={() => checkout(t.table_id)}>이용 완료</button>
              <button className="btn small" data-testid={`table-history-${t.table_id}`}
                      onClick={() => openHistory(t)}>과거 내역</button>
            </div>
          </div>
        ))}
      </div>

      {historyTable && (
        <div className="modal-backdrop" onClick={() => setHistoryTable(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()} data-testid="history-modal">
            <h3>테이블 {historyTable.table_number} 과거 내역</h3>
            <div className="row">
              <input type="date" value={dateFrom} onChange={(e) => setDateFrom(e.target.value)} />
              <input type="date" value={dateTo} onChange={(e) => setDateTo(e.target.value)} />
              <button className="btn small" data-testid="history-filter"
                      onClick={() => loadHistory(historyTable.table_id)}>조회</button>
            </div>
            {history.length === 0 ? (
              <p className="muted">과거 내역이 없습니다.</p>
            ) : (
              <ul className="history-list">
                {history.map((h) => (
                  <li key={h.id} className="history-item">
                    <div>주문 #{h.order_number} · {h.total_amount.toLocaleString()}원</div>
                    <div className="muted small">완료: {new Date(h.completed_at).toLocaleString()}</div>
                  </li>
                ))}
              </ul>
            )}
            <button className="btn" onClick={() => setHistoryTable(null)}>닫기</button>
          </div>
        </div>
      )}
    </div>
  )
}
