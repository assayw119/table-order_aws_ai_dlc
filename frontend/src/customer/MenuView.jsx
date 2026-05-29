// 고객용 메뉴 탐색 + 장바구니 요약 화면 (US-C2, US-C3)
import { useEffect, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client.js'
import { authStore } from '../store/auth.js'
import { cartStore } from '../store/cart.js'

// 카테고리명 기반 간단한 음식 이모지 매핑 (이미지 placeholder)
function foodEmoji(name) {
  const n = name || ''
  if (/(콜라|사이다|음료|커피|아메리카노|라떼)/.test(n)) return '🥤'
  if (/(맥주|소주|주류)/.test(n)) return '🍺'
  if (/(밥|덮밥|비빔밥)/.test(n)) return '🍚'
  if (/(찌개|국|탕)/.test(n)) return '🍲'
  if (/(면|국수|라면|파스타)/.test(n)) return '🍜'
  if (/(튀김|감자)/.test(n)) return '🍟'
  if (/(고기|불고기|스테이크|구이)/.test(n)) return '🍖'
  if (/(계란|달걀)/.test(n)) return '🍳'
  return '🍽️'
}

export default function MenuView() {
  const navigate = useNavigate()
  const token = authStore.getTableToken()
  const table = authStore.getTable()

  const [categories, setCategories] = useState([])
  const [items, setItems] = useState([])
  const [activeCat, setActiveCat] = useState(null)
  const [cartItems, setCartItems] = useState(cartStore.getItems())
  const [error, setError] = useState('')

  useEffect(() => {
    async function load() {
      try {
        setCategories(await api.get('/api/menu/categories', token))
        setItems(await api.get('/api/menu/items', token))
      } catch (err) {
        setError(err.detail || '메뉴를 불러오지 못했습니다.')
      }
    }
    load()
  }, [token])

  const filtered = activeCat ? items.filter((i) => i.category_id === activeCat) : items

  const qtyOf = useCallback(
    (id) => {
      const found = cartItems.find((it) => it.menu_item_id === id)
      return found ? found.quantity : 0
    },
    [cartItems],
  )

  const addToCart = (item) => {
    cartStore.addItem(item)
    setCartItems([...cartStore.getItems()])
  }

  const decreaseFromCart = (item) => {
    const current = qtyOf(item.id)
    cartStore.setQty(item.id, current - 1) // 0이 되면 항목 제거됨
    setCartItems([...cartStore.getItems()])
  }

  const totalCount = cartItems.reduce((s, it) => s + it.quantity, 0)
  const totalAmount = cartItems.reduce((s, it) => s + it.price * it.quantity, 0)
  const hasItems = totalCount > 0

  return (
    <>
      <header className="cust-header">
        <div className="store-info">
          <span className="store-name">{table?.store_name || '테이블오더'}</span>
          <span className="table-badge">테이블 {table?.table_number ?? '-'}번</span>
        </div>
        <button className="header-action" data-testid="goto-orders"
                onClick={() => navigate('/customer/orders')}>
          🧾 주문내역
        </button>
      </header>

      <div className="cust-main">
        <div className="category-bar">
          <button className={!activeCat ? 'chip active' : 'chip'}
                  onClick={() => setActiveCat(null)} data-testid="cat-all">전체</button>
          {categories.map((c) => (
            <button key={c.id}
                    className={activeCat === c.id ? 'chip active' : 'chip'}
                    onClick={() => setActiveCat(c.id)}
                    data-testid={`cat-${c.id}`}>{c.name}</button>
          ))}
        </div>

        {error && <div className="error" style={{ margin: '16px 20px' }}>{error}</div>}

        <div className="menu-grid">
          {filtered.map((item) => {
            const qty = qtyOf(item.id)
            return (
              <div className="menu-card" key={item.id}>
                {qty > 0 && <span className="qty-badge" data-testid={`menu-badge-${item.id}`}>{qty}</span>}
                <div className="menu-card-img">
                  {item.image_url
                    ? <img src={item.image_url} alt={item.name}
                           style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                    : <span>{foodEmoji(item.name)}</span>}
                </div>
                <div className="menu-card-body">
                  <div className="menu-name">{item.name}</div>
                  {item.description && <div className="menu-desc">{item.description}</div>}
                  <div className="menu-card-footer">
                    <span className="menu-price">{item.price.toLocaleString()}원</span>
                    {qty > 0 ? (
                      <div className="card-qty-stepper">
                        <button className="step-btn" data-testid={`menu-card-remove-${item.id}`}
                                aria-label={`${item.name} 빼기`}
                                onClick={() => decreaseFromCart(item)}>−</button>
                        <span className="step-qty" data-testid={`menu-card-qty-${item.id}`}>{qty}</span>
                        <button className="step-btn add" data-testid={`menu-card-add-${item.id}`}
                                aria-label={`${item.name} 담기`}
                                onClick={() => addToCart(item)}>+</button>
                      </div>
                    ) : (
                      <button className="add-btn" data-testid={`menu-card-add-${item.id}`}
                              aria-label={`${item.name} 담기`}
                              onClick={() => addToCart(item)}>+</button>
                    )}
                  </div>
                </div>
              </div>
            )
          })}
          {filtered.length === 0 && !error && (
            <p className="muted" style={{ gridColumn: '1 / -1' }}>메뉴가 없습니다.</p>
          )}
        </div>
      </div>

      <div className={`cart-summary-bar ${hasItems ? '' : 'disabled'}`}>
        <div className="cart-summary-info">
          <span className="cart-summary-count" data-testid="summary-count">선택 {totalCount}개</span>
          <span className="cart-summary-total" data-testid="summary-total">{totalAmount.toLocaleString()}원</span>
        </div>
        <button className="btn primary" data-testid="cart-view-button"
                disabled={!hasItems}
                onClick={() => navigate('/customer/cart')}>
          장바구니 보기
        </button>
      </div>
    </>
  )
}
