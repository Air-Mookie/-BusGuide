"""
버스 서비스
- TAGO(전국 버스정보시스템) API 연동
- 실시간 도착 정보, 가장 가까운 정류장 검색
- API 키는 환경변수에서 로드 (하드코딩 X)
"""
import os
import httpx

# TAGO API 기본 URL
TAGO_BASE_URL = "http://apis.data.go.kr/1613000"

# API 엔드포인트 경로
ARRIVAL_PATH = "/ArvlInfoInqireService/getSttnAcctoArvlPrearngeInfoList"
STATION_PATH = "/BusSttnInfoInqireService/getCrdntPrxmtSttnList"


class BusService:
    """
    TAGO 버스 API 연동 서비스
    - get_nearest_station(): GPS → 가장 가까운 정류장
    - get_arrivals(): 정류장 → 실시간 도착 버스 목록
    """

    def __init__(self, api_key: str | None = None):
        self._api_key = api_key or os.getenv("TAGO_API_KEY", "")

    async def _call_tago_api(self, path: str, params: dict) -> dict:
        """TAGO API 공통 호출 메서드"""
        base_params = {
            "serviceKey": self._api_key,
            "_type": "json",
            "numOfRows": 20,
            "pageNo": 1,
        }
        base_params.update(params)
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{TAGO_BASE_URL}{path}", params=base_params)
            response.raise_for_status()
            return response.json()

    def _extract_items(self, data: dict) -> list[dict]:
        """TAGO API 응답에서 items 추출"""
        items = data.get("response", {}).get("body", {}).get("items", "")
        if not items or items == "":
            return []
        item_list = items.get("item", [])
        if isinstance(item_list, dict):
            return [item_list]
        return item_list

    async def get_nearest_station(self, lat: float, lng: float) -> dict | None:
        """GPS 좌표에서 가장 가까운 정류장 찾기"""
        data = await self._call_tago_api(STATION_PATH, {"gpsLati": lat, "gpsLong": lng})
        items = self._extract_items(data)
        if not items:
            return None
        first = items[0]
        return {
            "id": first["nodeid"],
            "name": first["nodenm"],
            "lat": first["gpslati"],
            "lng": first["gpslong"],
        }

    async def get_arrivals(self, station_id: str) -> list[dict]:
        """특정 정류장의 실시간 도착 정보"""
        data = await self._call_tago_api(ARRIVAL_PATH, {"nodeId": station_id})
        items = self._extract_items(data)
        arrivals = []
        for item in items:
            arrivals.append({
                "bus_number": str(item["routeno"]),
                "arrival_min": item["arrtime"] // 60,
                "remaining_stops": item["arrprevstationcnt"],
                "destination": item.get("nodenm", ""),
            })
        arrivals.sort(key=lambda x: x["arrival_min"])
        return arrivals
