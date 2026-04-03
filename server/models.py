"""
BusGuide 데이터 모델
- 클라이언트-서버 간 주고받는 데이터 구조 정의
- Android 앱의 Kotlin data class와 1:1 대응
"""
from pydantic import BaseModel


class QueryRequest(BaseModel):
    """
    음성 질의 요청
    - text: 음성 인식 결과 텍스트 (예: "명지병원 카는 버스 있나예?")
    - station_id: 현재 정류장 ID (GPS 기반으로 앱에서 결정)
    - session_id: 대화 세션 ID (컨텍스트 유지용)
    """
    text: str
    station_id: str
    session_id: str


class BusArrival(BaseModel):
    """
    버스 도착 정보
    - bus_number: 버스 번호 (예: "58")
    - arrival_min: 도착 예정 시간(분) (예: 5)
    - remaining_stops: 남은 정거장 수 (예: 1)
    - destination: 버스 종점 (예: "명지병원")
    """
    bus_number: str
    arrival_min: int
    remaining_stops: int
    destination: str


class Station(BaseModel):
    """
    정류장 정보
    - id: 정류장 고유 ID (TAGO API 기준)
    - name: 정류장 이름
    - lat, lng: 위도, 경도
    """
    id: str
    name: str
    lat: float
    lng: float


class QueryResponse(BaseModel):
    """
    음성 질의 응답
    - answer_text: 화면에 표시할 텍스트
    - answer_tts: TTS로 읽어줄 텍스트 (더 자연스러운 말투)
    - buses: 도착 버스 목록
    - intent: 파악된 의도 (노선_검색, 도착_시간, 환승_안내, 정류장_확인)
    - destination: 파악된 목적지 (없을 수 있음)
    """
    answer_text: str
    answer_tts: str
    buses: list[BusArrival]
    intent: str
    destination: str | None
