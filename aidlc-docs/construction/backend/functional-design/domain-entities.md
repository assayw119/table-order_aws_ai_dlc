# 도메인 엔티티 (Domain Entities) - UoW-1 Backend

기술 비종속 도메인 모델. 구현은 SQLAlchemy(SQLite)로 매핑됩니다.

## 엔티티 관계 개요

```
Store 1---* AdminUser
Store 1---* Table 1---* TableSession 1---* Order 1---* OrderItem
Store 1---* Category 1---* MenuItem
TableSession 1---* OrderHistory   (이용 완료 시 Order에서 이동)
```

## 엔티티 정의

### Store (매장)
| 필드 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | int | PK | 내부 식별자 |
| store_code | str | unique, not null | 매장 식별자(로그인용) |
| name | str | not null | 매장명 |
| created_at | datetime | not null | 생성 시각 |

> 단일 매장 MVP이나 store_code로 데이터 식별. 시드로 1개 매장 생성.

### AdminUser (관리자)
| 필드 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | int | PK | |
| store_id | int | FK→Store, not null | 소속 매장 |
| username | str | not null, (store_id, username) unique | 로그인 아이디 |
| password_hash | str | not null | bcrypt 해시 |
| created_at | datetime | not null | |

### Table (테이블)
| 필드 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | int | PK | |
| store_id | int | FK→Store, not null | |
| table_number | int | not null, (store_id, table_number) unique | 테이블 번호 |
| password_hash | str | nullable | 테이블 비밀번호 bcrypt 해시(설정 시) |
| current_session_id | int | FK→TableSession, nullable | 활성 세션 |
| created_at | datetime | not null | |

### TableSession (테이블 세션)
| 필드 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | int | PK | 세션 ID(주문 그룹화 키) |
| store_id | int | FK→Store, not null | |
| table_id | int | FK→Table, not null | |
| status | str | not null | 'active' / 'closed' |
| started_at | datetime | not null | 첫 주문 시작 시각 |
| closed_at | datetime | nullable | 이용 완료 시각 |

### Category (카테고리)
| 필드 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | int | PK | |
| store_id | int | FK→Store, not null | |
| name | str | not null | 카테고리명 |
| display_order | int | not null, default 0 | 노출 순서 |

### MenuItem (메뉴)
| 필드 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | int | PK | |
| store_id | int | FK→Store, not null | |
| category_id | int | FK→Category, not null | |
| name | str | not null | 메뉴명 |
| price | int | not null, >= 0 | 가격(원, 정수) |
| description | str | nullable | 설명 |
| image_url | str | nullable | 이미지 URL |
| display_order | int | not null, default 0 | 노출 순서 |
| is_available | bool | not null, default true | 노출 여부 |

### Order (주문)
| 필드 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | int | PK | |
| store_id | int | FK→Store, not null | |
| table_id | int | FK→Table, not null | |
| session_id | int | FK→TableSession, not null | 세션 그룹화 |
| order_number | int | not null | 일자별 순번(매장 단위) |
| order_date | date | not null | 주문 일자(순번 리셋 기준) |
| status | str | not null | '대기중' / '준비중' / '완료' |
| total_amount | int | not null, >= 0 | 총액(원) |
| created_at | datetime | not null | 주문 시각 |

### OrderItem (주문 항목)
| 필드 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | int | PK | |
| order_id | int | FK→Order, not null | |
| menu_item_id | int | FK→MenuItem, nullable | 원본 참조(삭제 대비 nullable) |
| menu_name | str | not null | 메뉴명 스냅샷 |
| unit_price | int | not null, >= 0 | 단가 스냅샷 |
| quantity | int | not null, >= 1 | 수량 |

### OrderHistory (주문 이력)
| 필드 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | int | PK | |
| store_id | int | FK→Store | |
| table_id | int | FK→Table | |
| session_id | int | not null | 종료된 세션 ID |
| order_number | int | not null | 원 주문번호 |
| order_payload | json | not null | 주문 스냅샷(항목/금액/시각) |
| total_amount | int | not null | 주문 총액 |
| ordered_at | datetime | not null | 원 주문 시각 |
| completed_at | datetime | not null | 매장 이용 완료 시각 |

> 이용 완료 시 Order/OrderItem을 OrderHistory로 직렬화하여 이동(스냅샷). 현재 주문 테이블에서는 제거 또는 세션 종료로 자연 제외.
