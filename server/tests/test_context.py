"""
컨텍스트 서비스 테스트
"""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from services.context_service import ContextService


def test_컨텍스트_저장_조회():
    ctx = ContextService(ttl_seconds=60)
    ctx.save(session_id="sess-001", destination="명지병원", bus_number="58")
    result = ctx.get("sess-001")
    assert result is not None
    assert result["destination"] == "명지병원"
    assert result["bus_number"] == "58"

def test_존재하지_않는_세션():
    ctx = ContextService(ttl_seconds=60)
    assert ctx.get("없는세션") is None

def test_컨텍스트_업데이트():
    ctx = ContextService(ttl_seconds=60)
    ctx.save(session_id="sess-001", destination="명지병원", bus_number="58")
    ctx.save(session_id="sess-001", destination="해운대", bus_number="181")
    result = ctx.get("sess-001")
    assert result["destination"] == "해운대"
    assert result["bus_number"] == "181"

def test_컨텍스트_TTL_만료():
    ctx = ContextService(ttl_seconds=1)
    ctx.save(session_id="sess-001", destination="명지병원", bus_number="58")
    time.sleep(1.5)
    assert ctx.get("sess-001") is None

def test_대명사_해석():
    ctx = ContextService(ttl_seconds=60)
    ctx.save(session_id="sess-001", destination="명지병원", bus_number="58")
    resolved = ctx.resolve_pronoun("sess-001", "거기서 해운대 가려면?")
    assert "명지병원" in resolved
