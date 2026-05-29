// 고객 영역 레이아웃 컨테이너 (각 화면이 자체 헤더/하단바를 가짐)
import { Outlet } from 'react-router-dom'

export default function CustomerLayout() {
  return (
    <div className="customer-shell">
      <Outlet />
    </div>
  )
}
