"""
버스 서비스 테스트 (TAGO API 모킹)
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from unittest.mock import AsyncMock, patch
from services.bus_service import BusService


@pytest.mark.asyncio
async def test_가장_가까운_정류장_찾기():
    service = BusService(api_key="test_key")
    mock_response = {
        "response": {"body": {"items": {"item": [
            {"nodeid": "BUS_1234", "nodenm": "명지대학교 앞", "gpslati": 35.0691, "gpslong": 128.9694}
        ]}}}
    }
    with patch.object(service, "_call_tago_api", new_callable=AsyncMock, return_value=mock_response):
        station = await service.get_nearest_station(lat=35.0690, lng=128.9693)
        assert station["name"] == "명지대학교 앞"
        assert station["id"] == "BUS_1234"


@pytest.mark.asyncio
async def test_실시간_도착_정보():
    service = BusService(api_key="test_key")
    mock_response = {
        "response": {"body": {"items": {"item": [
            {"routeno": "58", "arrtime": 300, "arrprevstationcnt": 1, "nodenm": "명지병원"},
            {"routeno": "181", "arrtime": 720, "arrprevstationcnt": 3, "nodenm": "해운대"},
        ]}}}
    }
    with patch.object(service, "_call_tago_api", new_callable=AsyncMock, return_value=mock_response):
        arrivals = await service.get_arrivals(station_id="BUS_1234")
        assert len(arrivals) == 2
        assert arrivals[0]["bus_number"] == "58"
        assert arrivals[0]["arrival_min"] == 5
        assert arrivals[1]["bus_number"] == "181"


@pytest.mark.asyncio
async def test_도착_정보_없음():
    service = BusService(api_key="test_key")
    mock_response = {"response": {"body": {"items": ""}}}
    with patch.object(service, "_call_tago_api", new_callable=AsyncMock, return_value=mock_response):
        arrivals = await service.get_arrivals(station_id="BUS_1234")
        assert arrivals == []
