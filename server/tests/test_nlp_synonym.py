"""
유사어 매칭 + 목적지 추출 테스트
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from services.nlp_service import NlpService


def test_정확한_지명_매칭():
    nlp = NlpService()
    assert nlp.match_synonym("명지병원") == "명지병원"
    assert nlp.match_synonym("해운대") == "해운대"

def test_유사어_매칭():
    nlp = NlpService()
    assert nlp.match_synonym("바다") == "해운대"
    assert nlp.match_synonym("기차역") == "부산역"
    assert nlp.match_synonym("자갈치") == "남포동"

def test_부분_매칭():
    nlp = NlpService()
    assert nlp.extract_destination("명지병원 가는 버스 있나요?") == "명지병원"
    assert nlp.extract_destination("바다 가고 싶어요") == "해운대"

def test_매칭_실패():
    nlp = NlpService()
    assert nlp.match_synonym("화성") is None

def test_문장에서_목적지_없음():
    nlp = NlpService()
    assert nlp.extract_destination("여기 어디예요?") is None
