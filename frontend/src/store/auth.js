// 인증/자격증명 저장소 (localStorage 기반) - US-T2, Q6=A
const ADMIN_KEY = 'tableorder.admin'
const TABLE_KEY = 'tableorder.table'

export const authStore = {
  // ----- 관리자 -----
  saveAdmin(data) {
    localStorage.setItem(ADMIN_KEY, JSON.stringify(data))
  },
  getAdmin() {
    const raw = localStorage.getItem(ADMIN_KEY)
    return raw ? JSON.parse(raw) : null
  },
  getAdminToken() {
    const a = this.getAdmin()
    return a ? a.access_token : null
  },
  clearAdmin() {
    localStorage.removeItem(ADMIN_KEY)
  },

  // ----- 테이블 -----
  saveTable(data) {
    localStorage.setItem(TABLE_KEY, JSON.stringify(data))
  },
  getTable() {
    const raw = localStorage.getItem(TABLE_KEY)
    return raw ? JSON.parse(raw) : null
  },
  getTableToken() {
    const t = this.getTable()
    return t ? t.access_token : null
  },
  clearTable() {
    localStorage.removeItem(TABLE_KEY)
  },
}
