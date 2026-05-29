// 관리자 영역 레이아웃: 사이드 네비게이션 (US-A2~A4)
import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { authStore } from '../store/auth.js'

export default function AdminLayout() {
  const navigate = useNavigate()
  const admin = authStore.getAdmin()

  const logout = () => {
    authStore.clearAdmin()
    navigate('/admin/login', { replace: true })
  }

  return (
    <div className="admin-shell">
      <aside className="sidebar">
        <h1 className="logo">테이블오더</h1>
        <div className="muted small">{admin?.store?.name}</div>
        <nav>
          <NavLink to="/admin/dashboard" className="side-link" data-testid="nav-dashboard">대시보드</NavLink>
          <NavLink to="/admin/tables" className="side-link" data-testid="nav-tables">테이블 관리</NavLink>
          <NavLink to="/admin/menu" className="side-link" data-testid="nav-menu">메뉴 관리</NavLink>
        </nav>
        <button className="btn small" data-testid="admin-logout" onClick={logout}>로그아웃</button>
      </aside>
      <main className="admin-content">
        <Outlet />
      </main>
    </div>
  )
}
