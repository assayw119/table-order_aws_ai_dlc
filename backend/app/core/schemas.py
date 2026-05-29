"""Pydantic 요청/응답 스키마 (FastAPI 검증용)."""
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


# ---------- 인증 ----------
class AdminLoginRequest(BaseModel):
    store_code: str
    username: str
    password: str


class TableLoginRequest(BaseModel):
    store_code: str
    table_number: int
    table_password: str


class StoreInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    store_code: str
    name: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    store: StoreInfo


class TableTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    table_id: int
    table_number: int
    store_name: str


# ---------- 메뉴 ----------
class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    display_order: int


class MenuItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    category_id: int
    name: str
    price: int
    description: str | None = None
    image_url: str | None = None
    display_order: int
    is_available: bool


class MenuItemCreateRequest(BaseModel):
    category_id: int
    name: str = Field(min_length=1)
    price: int = Field(ge=0)
    description: str | None = None
    image_url: str | None = None
    display_order: int = 0
    is_available: bool = True


class MenuItemUpdateRequest(BaseModel):
    category_id: int | None = None
    name: str | None = Field(default=None, min_length=1)
    price: int | None = Field(default=None, ge=0)
    description: str | None = None
    image_url: str | None = None
    display_order: int | None = None
    is_available: bool | None = None


class DisplayOrderRequest(BaseModel):
    display_order: int


# ---------- 주문 ----------
class OrderItemRequest(BaseModel):
    menu_item_id: int
    quantity: int = Field(ge=1)


class OrderCreateRequest(BaseModel):
    items: list[OrderItemRequest] = Field(min_length=1)


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    menu_item_id: int | None = None
    menu_name: str
    unit_price: int
    quantity: int


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    order_number: int
    table_id: int
    session_id: int
    status: str
    total_amount: int
    created_at: datetime
    items: list[OrderItemResponse]


class OrderStatusRequest(BaseModel):
    status: str


# ---------- 테이블/세션 ----------
class TableSetupRequest(BaseModel):
    table_number: int
    table_password: str = Field(min_length=1)


class TableResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    table_number: int


class TableSummaryResponse(BaseModel):
    table_id: int
    table_number: int
    session_active: bool
    total_amount: int
    orders: list[OrderResponse]


class CheckoutResponse(BaseModel):
    table_number: int
    archived_count: int


class OrderHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    session_id: int
    order_number: int
    total_amount: int
    order_payload: dict
    ordered_at: datetime
    completed_at: datetime
