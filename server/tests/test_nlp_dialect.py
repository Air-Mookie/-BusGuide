"""
사투리 변환 테스트
- 부산 사투리가 표준어로 올바르게 변환되는지 검증
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.nlp_service import NlpService


def test_사투리_기본_변환():
    """단일 사투리 단어가 표준어로 변환되는지 확인"""
    nlp = NlpService()
    result = nlp.convert_dialect("어데 카는 버스예요?")
    assert "어디" in result
    assert "가는" in result


def test_사투리_복합_변환():
    """여러 사투리가 포함된 문장에서 모두 변환되는지 확인"""
    nlp = NlpService()
    result = nlp.convert_dialect("명지병원 카는 버스 있나예?")
    assert "가는" in result
    assert "있나요" in result


def test_표준어_입력은_그대로():
    """표준어 입력은 변환 없이 그대로 반환되는지 확인"""
    nlp = NlpService()
    result = nlp.convert_dialect("명지병원 가는 버스 있나요?")
    assert result == "명지병원 가는 버스 있나요?"


def test_빈_문자열():
    """빈 입력에 대해 빈 문자열 반환"""
    nlp = NlpService()
    assert nlp.convert_dialect("") == ""
