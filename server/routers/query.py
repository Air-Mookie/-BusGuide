"""
질의 라우터 — /query 엔드포인트
전체 처리 흐름: 사투리 변환 → 대명사 해석 → 의도 파악 → 목적지 추출 → API 호출 → 응답 생성
"""
from fastapi import APIRouter
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models import QueryRequest, QueryResponse
from services.nlp_service import NlpService
from services.bus_service import BusService
from services.context_service import ContextService
from services.response_builder import build_response

router = APIRouter()

# 서비스 싱글턴 — 라우터 모듈 로드 시 한 번만 초기화
nlp_service = NlpService()
bus_service = BusService()
context_service = ContextService(ttl_seconds=300)


@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest) -> QueryResponse:
    """음성 질의 처리 파이프라인"""
    text = request.text
    # ① 사투리 → 표준어 변환
    text = nlp_service.convert_dialect(text)
    # ② 대명사 해석 (이전 대화 컨텍스트 활용)
    text = context_service.resolve_pronoun(request.session_id, text)
    # ③ 의도 파악 (노선_검색 / 도착_시간 / 환승_안내 / 정류장_확인)
    intent = nlp_service.classify_intent(text)
    # ④ 목적지 추출
    destination = nlp_service.extract_destination(text)
    # ⑤ TAGO API 호출하여 버스 도착 정보 가져오기
    buses = await bus_service.get_arrivals(station_id=request.station_id)
    # ⑥ 다음 질의 해석을 위해 컨텍스트 저장
    first_bus = buses[0]["bus_number"] if buses else None
    context_service.save(session_id=request.session_id, destination=destination, bus_number=first_bus)
    # ⑦ 화면 표시용 + TTS용 응답 생성
    return build_response(intent=intent, destination=destination, buses=buses)
