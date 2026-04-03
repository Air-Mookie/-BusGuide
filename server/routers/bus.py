"""버스 정보 라우터 — 도착 정보 및 근처 정류장 조회"""
from fastapi import APIRouter, Query
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models import Station, BusArrival
from services.bus_service import BusService

router = APIRouter(prefix="/bus", tags=["bus"])
# 버스 서비스 싱글턴
bus_service = BusService()


@router.get("/arrivals/{station_id}", response_model=list[BusArrival])
async def get_arrivals(station_id: str) -> list:
    """특정 정류장의 버스 도착 예정 목록 반환"""
    arrivals = await bus_service.get_arrivals(station_id=station_id)
    return [BusArrival(bus_number=a["bus_number"], arrival_min=a["arrival_min"],
                       remaining_stops=a["remaining_stops"], destination=a["destination"])
            for a in arrivals]


@router.get("/nearest-station", response_model=Station)
async def get_nearest_station(lat: float = Query(...), lng: float = Query(...)) -> Station:
    """GPS 좌표 기반 가장 가까운 정류장 조회"""
    station = await bus_service.get_nearest_station(lat=lat, lng=lng)
    if station is None:
        return Station(id="", name="정류장을 찾을 수 없습니다", lat=lat, lng=lng)
    return Station(id=station["id"], name=station["name"], lat=station["lat"], lng=station["lng"])
