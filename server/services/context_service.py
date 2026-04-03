"""
컨텍스트 서비스
- 세션별 대화 맥락을 인메모리로 관리
- TTL(Time-To-Live)로 자동 만료
- 대명사("거기", "그거") 해석 지원
"""
import time

# 대명사 목록 — 이전 목적지로 치환할 단어들
PRONOUNS = ["거기", "그거", "그곳", "그 곳", "거기서"]


class ContextService:
    """
    대화 컨텍스트 관리
    - 세션 ID별로 최근 목적지, 버스 번호 등을 기억
    - TTL 초과 시 자동 삭제 (기본 5분)
    """

    def __init__(self, ttl_seconds: int = 300):
        self._store: dict[str, dict] = {}
        self._ttl_seconds = ttl_seconds

    def save(self, session_id: str, destination: str | None = None, bus_number: str | None = None) -> None:
        """세션에 컨텍스트 저장"""
        self._store[session_id] = {
            "destination": destination,
            "bus_number": bus_number,
            "timestamp": time.time(),
        }

    def get(self, session_id: str) -> dict | None:
        """세션 컨텍스트 조회 — TTL 초과 시 삭제 후 None 반환"""
        context = self._store.get(session_id)
        if context is None:
            return None
        elapsed = time.time() - context["timestamp"]
        if elapsed > self._ttl_seconds:
            del self._store[session_id]
            return None
        return context

    def resolve_pronoun(self, session_id: str, text: str) -> str:
        """대명사를 이전 컨텍스트로 치환"""
        context = self.get(session_id)
        if context is None or context["destination"] is None:
            return text
        result = text
        for pronoun in PRONOUNS:
            if pronoun in result:
                result = result.replace(pronoun, context["destination"])
        return result
