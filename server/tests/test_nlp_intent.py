"""
의도 분류 테스트
- 어르신의 다양한 질문 패턴에서 올바른 의도를 파악하는지 검증
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from services.nlp_service import NlpService


def test_노선_검색_의도():
    nlp = NlpService()
    intent = nlp.classify_intent("명지병원 가는 버스 있나요?")
    assert intent == "노선_검색"

def test_도착_시간_의도():
    nlp = NlpService()
    assert nlp.classify_intent("58번 몇 분 후에 와요?") == "도착_시간"
    assert nlp.classify_intent("버스 언제 오나요?") == "도착_시간"

def test_환승_안내_의도():
    nlp = NlpService()
    intent = nlp.classify_intent("명지병원 갔다가 해운대 가려면?")
    assert intent == "환승_안내"

def test_정류장_확인_의도():
    nlp = NlpService()
    assert nlp.classify_intent("여기 어디예요?") == "정류장_확인"
    assert nlp.classify_intent("여기 무슨 버스 서요?") == "정류장_확인"

def test_기본_의도_폴백():
    nlp = NlpService()
    intent = nlp.classify_intent("명지병원")
    assert intent == "노선_검색"
