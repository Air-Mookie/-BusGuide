"""질의 라우터 통합 테스트"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_기본_노선_검색():
    """명지병원 노선 검색 — 58번 버스 응답 검증"""
    mock_arrivals = [
        {"bus_number": "58", "arrival_min": 5, "remaining_stops": 1, "destination": "명지병원"}
    ]
    with patch("routers.query.bus_service.get_arrivals", new_callable=AsyncMock, return_value=mock_arrivals):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/query", json={
                "text": "명지병원 가는 버스 있나요?",
                "station_id": "BUS_1234",
                "session_id": "test-session",
            })
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "노선_검색"
    assert data["destination"] == "명지병원"
    assert len(data["buses"]) == 1
    assert "58" in data["answer_tts"]


@pytest.mark.asyncio
async def test_사투리_질의():
    """경상도 사투리 '카는' → 표준어 변환 후 목적지 추출 검증"""
    mock_arrivals = [
        {"bus_number": "58", "arrival_min": 5, "remaining_stops": 1, "destination": "명지병원"}
    ]
    with patch("routers.query.bus_service.get_arrivals", new_callable=AsyncMock, return_value=mock_arrivals):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/query", json={
                "text": "명지병원 카는 버스 있나예?",
                "station_id": "BUS_1234",
                "session_id": "test-session",
            })
    assert response.status_code == 200
    data = response.json()
    assert data["destination"] == "명지병원"


@pytest.mark.asyncio
async def test_health_엔드포인트():
    """/health 엔드포인트 정상 응답 검증"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
