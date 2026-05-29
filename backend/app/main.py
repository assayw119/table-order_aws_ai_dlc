"""FastAPI 애플리케이션 진입점: 라우터 등록, CORS, DB 초기화."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core import config
from app.core.database import init_db
from app.auth.router import router as auth_router
from app.menu.router import router as menu_router
from app.orders.router import router as orders_router
from app.tables.router import router as tables_router
from app.realtime.router import router as realtime_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작 시 DB 스키마 생성."""
    init_db()
    yield


app = FastAPI(title="테이블오더 API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(menu_router)
app.include_router(orders_router)
app.include_router(tables_router)
app.include_router(realtime_router)


@app.get("/api/health")
def health():
    """헬스 체크."""
    return {"status": "ok"}
