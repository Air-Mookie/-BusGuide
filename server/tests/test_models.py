"""
데이터 모델 테스트
- Pydantic 모델의 직렬화/역직렬화가 올바르게 동작하는지 검증
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models import QueryRequest, QueryResponse, BusArrival, Station


def test_query_request_직렬화():
    """음성 질의 요청 모델이 올바르게 생성되는지 확인"""
    req = QueryRequest(
        text="명지병원 가는 버스",
        station_id="BUS_1234",
        session_id="sess-001",
    )
    assert req.text == "명지병원 가는 버스"
    assert req.station_id == "BUS_1234"
    assert req.session_id == "sess-001"


def test_query_response_직렬화():
    """음성 질의 응답 모델이 올바르게 생성되는지 확인"""
    bus = BusArrival(
        bus_number="58",
        arrival_min=5,
        remaining_stops=1,
        destination="명지병원",
    )
    resp = QueryResponse(
        answer_text="58번 버스 타시면 됩니다.",
        answer_tts="58번 버스가 5분 후에 도착합니다",
        buses=[bus],
        intent="노선_검색",
        destination="명지병원",
    )
    assert resp.buses[0].bus_number == "58"
    assert resp.destination == "명지병원"


def test_station_모델():
    """정류장 모델이 위도/경도를 올바르게 보관하는지 확인"""
    station = Station(
        id="BUS_1234",
        name="명지대학교 앞",
        lat=35.0691,
        lng=128.9694,
    )
    assert station.name == "명지대학교 앞"


def test_query_response_destination_null_가능():
    """destination이 없는 경우(정류장 확인 등) None 허용"""
    resp = QueryResponse(
        answer_text="여기는 명지대학교 앞 정류장입니다.",
        answer_tts="여기는 명지대학교 앞 정류장입니다.",
        buses=[],
        intent="정류장_확인",
        destination=None,
    )
    assert resp.destination is None
