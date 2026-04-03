"""
BusGuide 서버 엔트리포인트
"""
import json
from pathlib import Path
from fastapi import FastAPI
from dotenv import load_dotenv

from routers.query import router as query_router
from routers.bus import router as bus_router

load_dotenv()

app = FastAPI(
    title="BusGuide API",
    description="어르신 음성 기반 버스 안내 시스템 백엔드",
    version="1.0.0",
)

app.include_router(query_router)
app.include_router(bus_router)


@app.get("/health")
async def health_check():
    """서버 상태 확인"""
    return {"status": "ok"}


@app.get("/presets/{region}")
async def get_presets(region: str):
    """지역별 자주 가는 곳 프리셋 반환"""
    data_path = Path(__file__).parent / "data" / "presets.json"
    if not data_path.exists():
        return {"label": region, "presets": []}
    with open(data_path, "r", encoding="utf-8") as f:
        all_presets = json.load(f)
    return all_presets.get(region, {"label": region, "presets": []})
