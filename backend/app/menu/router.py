"""메뉴 라우터: 고객 조회(공개) + 관리자 CRUD (US-C2, US-A4)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_session
from app.core.security import get_current_admin, get_current_table
from app.core.models import Category, MenuItem
from app.core.schemas import (
    CategoryResponse, MenuItemResponse, MenuItemCreateRequest,
    MenuItemUpdateRequest, DisplayOrderRequest,
)

router = APIRouter(tags=["menu"])


# ---------- 고객/공개 조회 (테이블 토큰) ----------
@router.get("/api/menu/categories", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_session), table: dict = Depends(get_current_table)):
    """카테고리 목록 조회 (노출 순서 정렬, BR-MENU-4)."""
    rows = db.scalars(
        select(Category)
        .where(Category.store_id == table["store_id"])
        .order_by(Category.display_order, Category.id)
    ).all()
    return rows


@router.get("/api/menu/items", response_model=list[MenuItemResponse])
def list_menu_items(
    category_id: int | None = None,
    db: Session = Depends(get_session),
    table: dict = Depends(get_current_table),
):
    """고객용 메뉴 조회: is_available=true 만 노출 (BR-MENU-3)."""
    stmt = select(MenuItem).where(
        MenuItem.store_id == table["store_id"], MenuItem.is_available.is_(True)
    )
    if category_id is not None:
        stmt = stmt.where(MenuItem.category_id == category_id)
    stmt = stmt.order_by(MenuItem.display_order, MenuItem.id)
    return db.scalars(stmt).all()


# ---------- 관리자 관리 ----------
@router.get("/api/admin/menu/items", response_model=list[MenuItemResponse])
def admin_list_menu_items(
    db: Session = Depends(get_session), admin: dict = Depends(get_current_admin)
):
    """관리자 메뉴 조회: 전체(미노출 포함)."""
    return db.scalars(
        select(MenuItem)
        .where(MenuItem.store_id == admin["store_id"])
        .order_by(MenuItem.display_order, MenuItem.id)
    ).all()


@router.post("/api/admin/menu/items", response_model=MenuItemResponse, status_code=201)
def create_menu_item(
    req: MenuItemCreateRequest,
    db: Session = Depends(get_session),
    admin: dict = Depends(get_current_admin),
):
    """메뉴 등록 (BR-MENU-1, 2). 가격/필수 필드는 스키마에서 검증."""
    category = db.get(Category, req.category_id)
    if not category or category.store_id != admin["store_id"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="카테고리를 찾을 수 없습니다.")
    item = MenuItem(
        store_id=admin["store_id"],
        category_id=req.category_id,
        name=req.name,
        price=req.price,
        description=req.description,
        image_url=req.image_url,
        display_order=req.display_order,
        is_available=req.is_available,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/api/admin/menu/items/{item_id}", response_model=MenuItemResponse)
def update_menu_item(
    item_id: int,
    req: MenuItemUpdateRequest,
    db: Session = Depends(get_session),
    admin: dict = Depends(get_current_admin),
):
    """메뉴 수정."""
    item = db.get(MenuItem, item_id)
    if not item or item.store_id != admin["store_id"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="메뉴를 찾을 수 없습니다.")
    data = req.model_dump(exclude_unset=True)
    if "category_id" in data:
        category = db.get(Category, data["category_id"])
        if not category or category.store_id != admin["store_id"]:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="카테고리를 찾을 수 없습니다.")
    for key, value in data.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/api/admin/menu/items/{item_id}", status_code=204)
def delete_menu_item(
    item_id: int,
    db: Session = Depends(get_session),
    admin: dict = Depends(get_current_admin),
):
    """메뉴 삭제 (BR-MENU-5: 기존 주문 스냅샷은 영향 없음)."""
    item = db.get(MenuItem, item_id)
    if not item or item.store_id != admin["store_id"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="메뉴를 찾을 수 없습니다.")
    db.delete(item)
    db.commit()
    return None


@router.put("/api/admin/menu/items/{item_id}/order", response_model=MenuItemResponse)
def update_display_order(
    item_id: int,
    req: DisplayOrderRequest,
    db: Session = Depends(get_session),
    admin: dict = Depends(get_current_admin),
):
    """메뉴 노출 순서 조정."""
    item = db.get(MenuItem, item_id)
    if not item or item.store_id != admin["store_id"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="메뉴를 찾을 수 없습니다.")
    item.display_order = req.display_order
    db.commit()
    db.refresh(item)
    return item
