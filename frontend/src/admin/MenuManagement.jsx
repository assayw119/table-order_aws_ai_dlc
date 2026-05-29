// 메뉴 관리: 등록/수정/삭제/순서 (US-A4)
import { useEffect, useState, useCallback } from 'react'
import { api } from '../api/client.js'
import { authStore } from '../store/auth.js'

const EMPTY = { category_id: '', name: '', price: '', description: '', image_url: '' }

export default function MenuManagement() {
  const token = authStore.getAdminToken()
  const [categories, setCategories] = useState([])
  const [items, setItems] = useState([])
  const [form, setForm] = useState(EMPTY)
  const [editingId, setEditingId] = useState(null)
  const [error, setError] = useState('')

  const reload = useCallback(async () => {
    try {
      // 카테고리는 테이블 토큰 없이도 조회 가능해야 하나, 관리자 메뉴 조회 사용
      const cats = await loadCategories()
      setCategories(cats)
      setItems(await api.get('/api/admin/menu/items', token))
    } catch (err) {
      setError(err.detail || '메뉴를 불러오지 못했습니다.')
    }
  }, [token])

  // 카테고리 조회: 관리자 화면에서는 테이블 토큰이 없으므로 메뉴 항목에서 유추하거나
  // 별도 관리자 카테고리 API가 없어 메뉴의 category_id를 사용. 여기서는 시드 카테고리 가정.
  const loadCategories = async () => {
    // 관리자용 카테고리 조회 엔드포인트가 없으므로 메뉴 항목에서 distinct category 추출
    const menuItems = await api.get('/api/admin/menu/items', token)
    const map = new Map()
    menuItems.forEach((m) => {
      if (!map.has(m.category_id)) map.set(m.category_id, { id: m.category_id, name: `카테고리 ${m.category_id}` })
    })
    return Array.from(map.values())
  }

  useEffect(() => {
    reload()
  }, [reload])

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const payload = {
        category_id: Number(form.category_id),
        name: form.name,
        price: Number(form.price),
        description: form.description || null,
        image_url: form.image_url || null,
      }
      if (editingId) {
        await api.put(`/api/admin/menu/items/${editingId}`, payload, token)
      } else {
        await api.post('/api/admin/menu/items', payload, token)
      }
      setForm(EMPTY)
      setEditingId(null)
      await reload()
    } catch (err) {
      setError(err.detail || '저장에 실패했습니다.')
    }
  }

  const edit = (item) => {
    setEditingId(item.id)
    setForm({
      category_id: String(item.category_id),
      name: item.name,
      price: String(item.price),
      description: item.description || '',
      image_url: item.image_url || '',
    })
  }

  const remove = async (id) => {
    if (!window.confirm('이 메뉴를 삭제하시겠습니까?')) return
    await api.del(`/api/admin/menu/items/${id}`, token)
    await reload()
  }

  return (
    <div className="menu-management">
      <h2>메뉴 관리</h2>
      {error && <div className="error">{error}</div>}

      <form className="card form" onSubmit={submit}>
        <h3>{editingId ? '메뉴 수정' : '메뉴 등록'}</h3>
        <label>카테고리 ID</label>
        <input data-testid="menu-form-category" type="number" value={form.category_id}
               onChange={(e) => setForm({ ...form, category_id: e.target.value })} required />
        <label>메뉴명</label>
        <input data-testid="menu-form-name" value={form.name}
               onChange={(e) => setForm({ ...form, name: e.target.value })} required />
        <label>가격</label>
        <input data-testid="menu-form-price" type="number" value={form.price}
               onChange={(e) => setForm({ ...form, price: e.target.value })} required min="0" />
        <label>설명</label>
        <input data-testid="menu-form-desc" value={form.description}
               onChange={(e) => setForm({ ...form, description: e.target.value })} />
        <div className="row">
          <button className="btn primary" data-testid="menu-form-submit">
            {editingId ? '수정' : '등록'}
          </button>
          {editingId && (
            <button type="button" className="btn" onClick={() => { setForm(EMPTY); setEditingId(null) }}>
              취소
            </button>
          )}
        </div>
      </form>

      <ul className="admin-menu-list">
        {items.map((item) => (
          <li key={item.id} className="admin-menu-item" data-testid={`admin-menu-${item.id}`}>
            <span>{item.name} · {item.price.toLocaleString()}원</span>
            <div className="row">
              <button className="btn small" data-testid={`menu-edit-${item.id}`} onClick={() => edit(item)}>수정</button>
              <button className="btn small danger" data-testid={`menu-delete-${item.id}`} onClick={() => remove(item.id)}>삭제</button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
