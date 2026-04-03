"""
NLP 서비스
- 사투리 변환, 의도 파악, 유사어 매칭을 담당
- 모든 매핑 데이터는 JSON 파일에서 로드 (하드코딩 X)
"""
import json
from pathlib import Path

# 데이터 파일 경로 — server/data/ 디렉토리 기준
DATA_DIR = Path(__file__).parent.parent / "data"


class NlpService:
    """
    자연어 처리 서비스
    - convert_dialect(): 사투리 → 표준어 변환
    - classify_intent(): 질문 의도 분류 (Task 4에서 추가)
    - match_synonym(): 유사어 → 표준 지명 매칭 (Task 5에서 추가)
    """

    def __init__(self):
        # JSON 파일에서 매핑 데이터 로드
        self._dialect_map = self._load_json("dialect_map.json")
        # 의도 분류 규칙 로드 (Task 4)
        self._intent_rules = self._load_json("intent_rules.json")
        # 유사어 매핑 로드 + 역방향 인덱스 생성 (Task 5)
        self._synonyms = self._load_json("synonyms.json")
        self._reverse_synonyms = self._build_reverse_synonyms()

    def _load_json(self, filename: str) -> dict:
        """JSON 데이터 파일 로드 — 파일 없으면 빈 dict 반환"""
        path = DATA_DIR / filename
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def convert_dialect(self, text: str) -> str:
        """
        부산 사투리를 표준어로 변환
        - dialect_map.json의 매핑을 기반으로 치환
        - 긴 키워드부터 먼저 치환 (부분 매칭 충돌 방지)
        """
        if not text:
            return ""

        # 긴 사투리부터 먼저 치환 (예: "있나예"를 "있나" + "예"로 쪼개지 않도록)
        sorted_dialects = sorted(
            self._dialect_map.keys(),
            key=len,
            reverse=True,
        )

        result = text
        for dialect in sorted_dialects:
            standard = self._dialect_map[dialect]
            result = result.replace(dialect, standard)

        return result

    def classify_intent(self, text: str) -> str:
        """
        질문 의도 분류
        - intent_rules.json의 키워드 매칭으로 의도 파악
        - 환승_안내 > 도착_시간 > 정류장_확인 > 노선_검색 우선순위
        - 아무것도 매칭 안 되면 "노선_검색" (가장 흔한 질문)
        """
        priority_order = ["환승_안내", "도착_시간", "정류장_확인", "노선_검색"]
        for intent_name in priority_order:
            rule = self._intent_rules.get(intent_name, {})
            keywords = rule.get("keywords", [])
            for keyword in keywords:
                if keyword in text:
                    return intent_name
        return "노선_검색"

    def _build_reverse_synonyms(self) -> dict:
        """synonyms.json의 역방향 매핑 생성 — 유사어 → 표준 지명"""
        reverse = {}
        for standard, variations in self._synonyms.items():
            # 표준 지명 자체도 매칭되도록 등록
            reverse[standard] = standard
            for variation in variations:
                reverse[variation] = standard
        return reverse

    def match_synonym(self, word: str) -> "str | None":
        """유사어를 표준 지명으로 변환 — 완전 일치만"""
        return self._reverse_synonyms.get(word)

    def extract_destination(self, text: str) -> "str | None":
        """문장에서 목적지 추출 — 긴 키워드부터 먼저 매칭 (부분 포함 검색)"""
        # 긴 키워드 우선 정렬로 부분 매칭 충돌 방지
        sorted_keys = sorted(self._reverse_synonyms.keys(), key=len, reverse=True)
        for keyword in sorted_keys:
            if keyword in text:
                return self._reverse_synonyms[keyword]
        return None
