"""
응답 생성 서비스
- NLP 결과 + 버스 데이터를 조합하여 자연스러운 한국어 응답 생성
- 화면 표시용(answer_text)과 TTS용(answer_tts) 텍스트를 분리
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from models import BusArrival, QueryResponse


def build_response(intent: str, destination: str | None, buses: list[dict], station_name: str = "") -> QueryResponse:
    """의도와 버스 데이터를 조합하여 QueryResponse 생성"""
    bus_models = [
        BusArrival(bus_number=b["bus_number"], arrival_min=b["arrival_min"],
                   remaining_stops=b["remaining_stops"], destination=b["destination"])
        for b in buses
    ]

    if intent == "노선_검색":
        answer_text, answer_tts = _build_route_response(destination, bus_models)
    elif intent == "도착_시간":
        answer_text, answer_tts = _build_arrival_response(bus_models)
    elif intent == "환승_안내":
        answer_text, answer_tts = _build_transfer_response(destination, bus_models)
    elif intent == "정류장_확인":
        answer_text, answer_tts = _build_station_response(station_name, bus_models)
    else:
        answer_text, answer_tts = _build_route_response(destination, bus_models)

    return QueryResponse(
        answer_text=answer_text, answer_tts=answer_tts,
        buses=bus_models, intent=intent, destination=destination,
    )


def _build_route_response(destination: str | None, buses: list[BusArrival]) -> tuple[str, str]:
    """노선 검색 응답 — 목적지와 첫 번째 버스 정보를 조합"""
    if not buses:
        text = f"{destination}으로 가는 버스가 현재 없습니다."
        return text, text
    first = buses[0]
    text = f"{destination} 가시려면\n{first.bus_number}번 버스 타시면 됩니다.\n{first.arrival_min}분 후 도착 예정입니다."
    tts = f"{destination} 가시려면 {first.bus_number}번 버스 타시면 됩니다. {first.arrival_min}분 후에 도착합니다."
    return text, tts


def _build_arrival_response(buses: list[BusArrival]) -> tuple[str, str]:
    """도착 시간 응답 — 다음 버스 도착까지 남은 시간 안내"""
    if not buses:
        text = "현재 도착 예정인 버스가 없습니다."
        return text, text
    first = buses[0]
    text = f"{first.bus_number}번 버스가\n{first.arrival_min}분 후 도착합니다."
    tts = f"{first.bus_number}번 버스가 {first.arrival_min}분 후에 도착합니다."
    return text, tts


def _build_transfer_response(destination: str | None, buses: list[BusArrival]) -> tuple[str, str]:
    """환승 안내 응답 — 환승할 버스 번호와 목적지 안내"""
    if not buses:
        text = f"{destination}까지 환승 정보를 찾을 수 없습니다."
        return text, text
    first = buses[0]
    text = f"{first.bus_number}번 버스로 갈아타시면\n{destination}에 갈 수 있습니다."
    tts = f"{first.bus_number}번 버스로 갈아타시면 {destination}에 갈 수 있습니다."
    return text, tts


def _build_station_response(station_name: str, buses: list[BusArrival]) -> tuple[str, str]:
    """정류장 확인 응답 — 현재 정류장 이름과 정차 버스 목록 안내"""
    bus_numbers = ", ".join(b.bus_number + "번" for b in buses[:5])
    text = f"여기는 {station_name} 정류장입니다."
    if bus_numbers:
        text += f"\n{bus_numbers} 버스가 섭니다."
    tts = text.replace("\n", " ")
    return text, tts
