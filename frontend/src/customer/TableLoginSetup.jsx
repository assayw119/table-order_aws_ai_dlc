// 테이블 자동 로그인/초기 설정 화면 (US-C1)
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client.js'
import { authStore } from '../store/auth.js'

export default function TableLoginSetup() {
  const navigate = useNavigate()
  const [storeCode, setStoreCode] = useState('store001')
  const [tableNumber, setTableNumber] = useState('1')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const data = await api.post('/api/auth/table/login', {
        store_code: storeCode,
        table_number: Number(tableNumber),
        table_password: password,
      })
      authStore.saveTable({ ...data, store_code: storeCode })
      navigate('/customer', { replace: true })
    } catch (err) {
      setError(err.detail || '로그인에 실패했습니다.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="centered-page">
      <form className="card form" onSubmit={submit}>
        <h1>테이블 설정</h1>
        <p className="muted">매장 정보와 테이블 비밀번호를 입력하세요.</p>
        <label>매장 식별자</label>
        <input data-testid="setup-store-code" value={storeCode}
               onChange={(e) => setStoreCode(e.target.value)} />
        <label>테이블 번호</label>
        <input data-testid="setup-table-number" type="number" value={tableNumber}
               onChange={(e) => setTableNumber(e.target.value)} />
        <label>테이블 비밀번호</label>
        <input data-testid="setup-table-password" type="password" value={password}
               onChange={(e) => setPassword(e.target.value)} />
        {error && <div className="error" data-testid="setup-error">{error}</div>}
        <button className="btn primary" data-testid="table-login-submit" disabled={loading}>
          {loading ? '로그인 중...' : '로그인'}
        </button>
      </form>
    </div>
  )
}
