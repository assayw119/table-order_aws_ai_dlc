import { Routes, Route, Navigate } from 'react-router-dom'

// 고객 영역
import CustomerLayout from './customer/CustomerLayout.jsx'
import TableLoginSetup from './customer/TableLoginSetup.jsx'
import MenuView from './customer/MenuView.jsx'
import CartView from './customer/CartView.jsx'
import OrderConfirm from './customer/OrderConfirm.jsx'
import OrderHistoryView from './customer/OrderHistoryView.jsx'

// 관리자 영역
import AdminLogin from './admin/AdminLogin.jsx'
import AdminLayout from './admin/AdminLayout.jsx'
import OrderDashboard from './admin/OrderDashboard.jsx'
import TableManagement from './admin/TableManagement.jsx'
import MenuManagement from './admin/MenuManagement.jsx'

import { authStore } from './store/auth.js'

// 라우트 가드
function RequireTable({ children }) {
  return authStore.getTableToken() ? children : <Navigate to="/customer/setup" replace />
}
function RequireAdmin({ children }) {
  return authStore.getAdminToken() ? children : <Navigate to="/admin/login" replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/customer" replace />} />

      {/* 고객 */}
      <Route path="/customer/setup" element={<TableLoginSetup />} />
      <Route
        path="/customer"
        element={
          <RequireTable>
            <CustomerLayout />
          </RequireTable>
        }
      >
        <Route index element={<MenuView />} />
        <Route path="cart" element={<CartView />} />
        <Route path="confirm" element={<OrderConfirm />} />
        <Route path="orders" element={<OrderHistoryView />} />
      </Route>

      {/* 관리자 */}
      <Route path="/admin/login" element={<AdminLogin />} />
      <Route
        path="/admin"
        element={
          <RequireAdmin>
            <AdminLayout />
          </RequireAdmin>
        }
      >
        <Route index element={<Navigate to="/admin/dashboard" replace />} />
        <Route path="dashboard" element={<OrderDashboard />} />
        <Route path="tables" element={<TableManagement />} />
        <Route path="menu" element={<MenuManagement />} />
      </Route>

      <Route path="*" element={<Navigate to="/customer" replace />} />
    </Routes>
  )
}
