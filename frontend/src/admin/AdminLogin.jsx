// 매장 인증 (US-A1)
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client.js'
import { authStore } from '../store/auth.js'

export default function AdminLogin() {
  const navigate = useNavigate()
  const [storeCode, setStoreCode] = useState('store001')
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const data = await api.post('/api/auth/admin/login', {
        store_code: storeCode,
        username,
        password,
      })
      authStore.saveAdmin(data)
      navigate('/admin/dashboard', { replace: true })
    } catch (err) {
      setError(err.detail || '로그인에 실패했습니다.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="centered-page">
      <form className="card form" onSubmit={submit}>
        <h1>관리자 로그인</h1>
        <label>매장 식별자</label>
        <input data-testid="admin-store-code" value={storeCode}
               onChange={(e) => setStoreCode(e.target.value)} />
        <label>사용자명</label>
        <input data-testid="admin-username" value={username}
               onChange={(e) => setUsername(e.target.value)} />
        <label>비밀번호</label>
        <input data-testid="admin-password" type="password" value={password}
               onChange={(e) => setPassword(e.target.value)} />
        {error && <div className="error" data-testid="admin-login-error">{error}</div>}
        <button className="btn primary" data-testid="admin-login-submit" disabled={loading}>
          {loading ? '로그인 중...' : '로그인'}
        </button>
      </form>
    </div>
  )
}
