# BusGuide 구현 계획서

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 어르신 음성 기반 버스 안내 시스템 — FastAPI 서버 + Android 태블릿 앱

**Architecture:** 심플 클라이언트 패턴. Android 앱은 STT/TTS/UI만 담당하고, FastAPI 서버가 NLP(사투리 변환, 의도 파악, 유사어 매칭), TAGO API 연동, 컨텍스트 관리를 전부 처리. 모든 매핑 데이터는 JSON 파일로 분리하여 하드코딩 방지.

**Tech Stack:** Kotlin + Jetpack Compose + Hilt + Retrofit (Android) / FastAPI + Kiwi + httpx (Server) / TAGO 공공 버스 API

---

## Part A: FastAPI 서버

---

### Task 1: 서버 프로젝트 초기 설정

**Files:**
- Create: `server/main.py`
- Create: `server/requirements.txt`
- Create: `server/.env.example`
- Create: `server/.gitignore`

- [ ] **Step 1: 프로젝트 디렉토리 생성**

```bash
mkdir -p server
cd server
python -m venv venv
source venv/Scripts/activate   # Windows Git Bash
```

- [ ] **Step 2: requirements.txt 작성**

```text
fastapi==0.115.0
uvicorn[standard]==0.30.0
httpx==0.27.0
python-dotenv==1.0.1
kiwipiepy==0.18.0
pydantic==2.9.0
```

- [ ] **Step 3: 의존성 설치**

```bash
pip install -r requirements.txt
```

- [ ] **Step 4: .env.example 작성**

```env
# TAGO 공공데이터 API 키 (https://www.data.go.kr 에서 발급)
TAGO_API_KEY=your_api_key_here

# 서버 설정
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
```

- [ ] **Step 5: .gitignore 작성**

```gitignore
venv/
__pycache__/
*.pyc
.env
```

- [ ] **Step 6: main.py 작성 — FastAPI 앱 엔트리포인트**

```python
"""
BusGuide 서버 엔트리포인트
- 어르신 음성 질의를 받아 버스 안내를 반환하는 API 서버
"""
from fastapi import FastAPI
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드 (API 키 등)
load_dotenv()

app = FastAPI(
    title="BusGuide API",
    description="어르신 음성 기반 버스 안내 시스템 백엔드",
    version="1.0.0",
)


@app.get("/health")
async def health_check():
    """서버 상태 확인 — 키오스크 모니터링용"""
    return {"status": "ok"}
```

- [ ] **Step 7: 서버 실행 테스트**

```bash
cd server
uvicorn main:app --reload
```

브라우저에서 `http://localhost:8000/health` 접속 → `{"status": "ok"}` 확인
`http://localhost:8000/docs` 접속 → Swagger UI 확인

- [ ] **Step 8: 커밋**

```bash
git add server/
git commit -m "feat(server): FastAPI 프로젝트 초기 설정"
```

---

### Task 2: 데이터 모델 (Pydantic) 정의

**Files:**
- Create: `server/models.py`

- [ ] **Step 1: 테스트 작성 — 모델 직렬화/역직렬화**

Create: `server/tests/__init__.py` (빈 파일)
Create: `server/tests/test_models.py`

```python
"""
데이터 모델 테스트
- Pydantic 모델의 직렬화/역직렬화가 올바르게 동작하는지 검증
"""
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
```

- [ ] **Step 2: 테스트 실행 — 실패 확인**

```bash
cd server
python -m pytest tests/test_models.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'models'`

- [ ] **Step 3: models.py 구현**

```python
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
```

- [ ] **Step 4: 테스트 실행 — 통과 확인**

```bash
cd server
python -m pytest tests/test_models.py -v
```

Expected: 4 passed

- [ ] **Step 5: 커밋**

```bash
git add server/models.py server/tests/
git commit -m "feat(server): Pydantic 데이터 모델 정의"
```

---

### Task 3: NLP 서비스 — 사투리 변환

**Files:**
- Create: `server/data/dialect_map.json`
- Create: `server/services/__init__.py`
- Create: `server/services/nlp_service.py`
- Create: `server/tests/test_nlp_dialect.py`

- [ ] **Step 1: dialect_map.json 작성 — 부산 사투리 매핑 데이터**

```json
{
  "어데": "어디",
  "카는": "가는",
  "카요": "가요",
  "갈끄예": "갈게요",
  "있나예": "있나요",
  "없나예": "없나요",
  "됩니꺼": "됩니까",
  "합니꺼": "합니까",
  "모": "뭐",
  "와": "왜",
  "캐": "해",
  "안카나": "아닌가",
  "하이소": "하세요",
  "가이소": "가세요",
  "오이소": "오세요",
  "마": "야",
  "아이가": "아닌가",
  "거": "것",
  "데이": "데요"
}
```

- [ ] **Step 2: 테스트 작성 — 사투리 변환**

Create: `server/tests/test_nlp_dialect.py`

```python
"""
사투리 변환 테스트
- 부산 사투리가 표준어로 올바르게 변환되는지 검증
"""
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
```

- [ ] **Step 3: 테스트 실행 — 실패 확인**

```bash
cd server
python -m pytest tests/test_nlp_dialect.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'services'`

- [ ] **Step 4: NlpService 구현 — 사투리 변환 부분**

Create: `server/services/__init__.py` (빈 파일)
Create: `server/services/nlp_service.py`

```python
"""
NLP 서비스
- 사투리 변환, 의도 파악, 유사어 매칭을 담당
- 모든 매핑 데이터는 JSON 파일에서 로드 (하드코딩 X)
"""
import json
import re
from pathlib import Path

# 데이터 파일 경로 — server/data/ 디렉토리 기준
DATA_DIR = Path(__file__).parent.parent / "data"


class NlpService:
    """
    자연어 처리 서비스
    - convert_dialect(): 사투리 → 표준어 변환
    - classify_intent(): 질문 의도 분류
    - match_synonym(): 유사어 → 표준 지명 매칭
    """

    def __init__(self):
        # JSON 파일에서 매핑 데이터 로드
        self._dialect_map = self._load_json("dialect_map.json")

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
```

- [ ] **Step 5: 테스트 실행 — 통과 확인**

```bash
cd server
python -m pytest tests/test_nlp_dialect.py -v
```

Expected: 4 passed

- [ ] **Step 6: 커밋**

```bash
git add server/data/dialect_map.json server/services/ server/tests/test_nlp_dialect.py
git commit -m "feat(server): 사투리 변환 NLP 서비스 구현"
```

---

### Task 4: NLP 서비스 — 의도 분류

**Files:**
- Create: `server/data/intent_rules.json`
- Modify: `server/services/nlp_service.py`
- Create: `server/tests/test_nlp_intent.py`

- [ ] **Step 1: intent_rules.json 작성 — 의도 분류 키워드 규칙**

```json
{
  "노선_검색": {
    "keywords": ["가는 버스", "타면", "가려면", "가고 싶", "가는 거", "타는 거", "가는"],
    "description": "특정 목적지로 가는 버스 노선 검색"
  },
  "도착_시간": {
    "keywords": ["몇 분", "언제", "얼마나", "도착", "오나", "와요", "옵니까"],
    "description": "특정 버스의 도착 예정 시간 확인"
  },
  "환승_안내": {
    "keywords": ["갈아타", "환승", "갔다가", "들렀다", "경유", "거쳐서"],
    "description": "환승이 필요한 경로 안내"
  },
  "정류장_확인": {
    "keywords": ["여기 어디", "정류장", "뭐가 서", "무슨 버스", "어디예요"],
    "description": "현재 정류장 정보 확인"
  }
}
```

- [ ] **Step 2: 테스트 작성 — 의도 분류**

```python
"""
의도 분류 테스트
- 어르신의 다양한 질문 패턴에서 올바른 의도를 파악하는지 검증
"""
from services.nlp_service import NlpService


def test_노선_검색_의도():
    """'~가는 버스' 패턴에서 노선_검색 의도 파악"""
    nlp = NlpService()
    intent = nlp.classify_intent("명지병원 가는 버스 있나요?")
    assert intent == "노선_검색"


def test_도착_시간_의도():
    """'몇 분' '언제' 패턴에서 도착_시간 의도 파악"""
    nlp = NlpService()
    assert nlp.classify_intent("58번 몇 분 후에 와요?") == "도착_시간"
    assert nlp.classify_intent("버스 언제 오나요?") == "도착_시간"


def test_환승_안내_의도():
    """'갈아타' '갔다가' 패턴에서 환승_안내 의도 파악"""
    nlp = NlpService()
    intent = nlp.classify_intent("명지병원 갔다가 해운대 가려면?")
    assert intent == "환승_안내"


def test_정류장_확인_의도():
    """'여기 어디' '무슨 버스' 패턴에서 정류장_확인 의도 파악"""
    nlp = NlpService()
    assert nlp.classify_intent("여기 어디예요?") == "정류장_확인"
    assert nlp.classify_intent("여기 무슨 버스 서요?") == "정류장_확인"


def test_기본_의도_폴백():
    """어떤 키워드도 매칭되지 않으면 노선_검색을 기본값으로 반환"""
    nlp = NlpService()
    intent = nlp.classify_intent("명지병원")
    assert intent == "노선_검색"
```

- [ ] **Step 3: 테스트 실행 — 실패 확인**

```bash
cd server
python -m pytest tests/test_nlp_intent.py -v
```

Expected: FAIL — `AttributeError: 'NlpService' object has no attribute 'classify_intent'`

- [ ] **Step 4: classify_intent 구현 — nlp_service.py에 추가**

`server/services/nlp_service.py`의 `__init__`에 intent_rules 로드 추가:

```python
    def __init__(self):
        self._dialect_map = self._load_json("dialect_map.json")
        self._intent_rules = self._load_json("intent_rules.json")
```

그리고 클래스에 메서드 추가:

```python
    def classify_intent(self, text: str) -> str:
        """
        질문 의도 분류
        - intent_rules.json의 키워드 매칭으로 의도 파악
        - 환승_안내 > 도착_시간 > 정류장_확인 > 노선_검색 우선순위
        - 아무것도 매칭 안 되면 "노선_검색" (가장 흔한 질문)
        """
        # 우선순위: 환승이 가장 구체적 → 먼저 체크
        priority_order = ["환승_안내", "도착_시간", "정류장_확인", "노선_검색"]

        for intent_name in priority_order:
            rule = self._intent_rules.get(intent_name, {})
            keywords = rule.get("keywords", [])
            for keyword in keywords:
                if keyword in text:
                    return intent_name

        # 기본값: 노선 검색 (어르신들의 가장 흔한 질문)
        return "노선_검색"
```

- [ ] **Step 5: 테스트 실행 — 통과 확인**

```bash
cd server
python -m pytest tests/test_nlp_intent.py -v
```

Expected: 5 passed

- [ ] **Step 6: 커밋**

```bash
git add server/data/intent_rules.json server/services/nlp_service.py server/tests/test_nlp_intent.py
git commit -m "feat(server): 의도 분류 NLP 서비스 구현"
```

---

### Task 5: NLP 서비스 — 유사어 매칭 + 목적지 추출

**Files:**
- Create: `server/data/synonyms.json`
- Modify: `server/services/nlp_service.py`
- Create: `server/tests/test_nlp_synonym.py`

- [ ] **Step 1: synonyms.json 작성 — 부산 주요 장소 유사어**

```json
{
  "명지병원": ["명지", "명지 큰병원", "명지의료원", "큰병원"],
  "해운대": ["해운대해수욕장", "해수욕장", "바다", "해운대바다"],
  "서면": ["서면역", "롯데백화점", "서면 롯데", "서면역 롯데"],
  "부산역": ["역", "기차역", "부산 기차역", "부산기차역", "KTX"],
  "센텀시티": ["센텀", "신세계", "센텀 신세계", "센텀시티역"],
  "남포동": ["남포", "자갈치", "자갈치시장", "국제시장", "BIFF"],
  "광안리": ["광안리해수욕장", "광안", "광안대교"],
  "부산대": ["부산대학교", "부산대역", "장전동"],
  "동래": ["동래역", "동래온천", "온천장"],
  "사상": ["사상역", "사상터미널", "서부터미널"]
}
```

- [ ] **Step 2: 테스트 작성 — 유사어 매칭 + 목적지 추출**

```python
"""
유사어 매칭 + 목적지 추출 테스트
- 어르신의 다양한 표현에서 표준 지명을 찾아내는지 검증
"""
from services.nlp_service import NlpService


def test_정확한_지명_매칭():
    """표준 지명이 그대로 입력되면 바로 매칭"""
    nlp = NlpService()
    assert nlp.match_synonym("명지병원") == "명지병원"
    assert nlp.match_synonym("해운대") == "해운대"


def test_유사어_매칭():
    """유사어(별칭)로 입력해도 표준 지명으로 변환"""
    nlp = NlpService()
    assert nlp.match_synonym("바다") == "해운대"
    assert nlp.match_synonym("기차역") == "부산역"
    assert nlp.match_synonym("자갈치") == "남포동"


def test_부분_매칭():
    """문장 안에 포함된 지명도 추출"""
    nlp = NlpService()
    assert nlp.extract_destination("명지병원 가는 버스 있나요?") == "명지병원"
    assert nlp.extract_destination("바다 가고 싶어요") == "해운대"


def test_매칭_실패():
    """알 수 없는 지명은 None 반환"""
    nlp = NlpService()
    assert nlp.match_synonym("화성") is None


def test_문장에서_목적지_없음():
    """목적지가 없는 질문은 None 반환"""
    nlp = NlpService()
    assert nlp.extract_destination("여기 어디예요?") is None
```

- [ ] **Step 3: 테스트 실행 — 실패 확인**

```bash
cd server
python -m pytest tests/test_nlp_synonym.py -v
```

Expected: FAIL

- [ ] **Step 4: match_synonym + extract_destination 구현**

`server/services/nlp_service.py`의 `__init__`에 synonyms 로드 추가:

```python
    def __init__(self):
        self._dialect_map = self._load_json("dialect_map.json")
        self._intent_rules = self._load_json("intent_rules.json")
        self._synonyms = self._load_json("synonyms.json")
        # 역방향 매핑: 유사어 → 표준 지명 (빠른 검색용)
        self._reverse_synonyms = self._build_reverse_synonyms()

    def _build_reverse_synonyms(self) -> dict[str, str]:
        """
        synonyms.json의 역방향 매핑 생성
        예: {"바다": "해운대", "기차역": "부산역", ...}
        표준 지명 자체도 키로 포함 (예: "해운대": "해운대")
        """
        reverse = {}
        for standard, variations in self._synonyms.items():
            reverse[standard] = standard  # 표준 지명도 매핑에 포함
            for variation in variations:
                reverse[variation] = standard
        return reverse
```

그리고 메서드 추가:

```python
    def match_synonym(self, word: str) -> str | None:
        """
        유사어를 표준 지명으로 변환
        - "바다" → "해운대", "기차역" → "부산역"
        - 매칭 안 되면 None 반환
        """
        return self._reverse_synonyms.get(word)

    def extract_destination(self, text: str) -> str | None:
        """
        문장에서 목적지 추출
        - 긴 키워드부터 먼저 매칭 (예: "명지병원"이 "명지"보다 우선)
        - 유사어도 인식 (예: "바다 가고 싶어요" → "해운대")
        """
        # 긴 키워드부터 검색 (부분 매칭 충돌 방지)
        sorted_keys = sorted(
            self._reverse_synonyms.keys(),
            key=len,
            reverse=True,
        )

        for keyword in sorted_keys:
            if keyword in text:
                return self._reverse_synonyms[keyword]

        return None
```

- [ ] **Step 5: 테스트 실행 — 통과 확인**

```bash
cd server
python -m pytest tests/test_nlp_synonym.py -v
```

Expected: 5 passed

- [ ] **Step 6: 커밋**

```bash
git add server/data/synonyms.json server/services/nlp_service.py server/tests/test_nlp_synonym.py
git commit -m "feat(server): 유사어 매칭 + 목적지 추출 구현"
```

---

### Task 6: 컨텍스트 서비스 — 대화 기억

**Files:**
- Create: `server/services/context_service.py`
- Create: `server/tests/test_context.py`

- [ ] **Step 1: 테스트 작성 — 컨텍스트 저장/조회/만료**

```python
"""
컨텍스트 서비스 테스트
- 세션별 대화 맥락이 올바르게 저장/조회/만료되는지 검증
"""
import time
from services.context_service import ContextService


def test_컨텍스트_저장_조회():
    """세션에 목적지와 버스 번호를 저장하고 조회"""
    ctx = ContextService(ttl_seconds=60)
    ctx.save(
        session_id="sess-001",
        destination="명지병원",
        bus_number="58",
    )

    result = ctx.get("sess-001")
    assert result is not None
    assert result["destination"] == "명지병원"
    assert result["bus_number"] == "58"


def test_존재하지_않는_세션():
    """없는 세션 ID로 조회하면 None 반환"""
    ctx = ContextService(ttl_seconds=60)
    assert ctx.get("없는세션") is None


def test_컨텍스트_업데이트():
    """같은 세션에 새 데이터를 저장하면 덮어쓰기"""
    ctx = ContextService(ttl_seconds=60)
    ctx.save(session_id="sess-001", destination="명지병원", bus_number="58")
    ctx.save(session_id="sess-001", destination="해운대", bus_number="181")

    result = ctx.get("sess-001")
    assert result["destination"] == "해운대"
    assert result["bus_number"] == "181"


def test_컨텍스트_TTL_만료():
    """TTL이 지나면 컨텍스트가 자동 삭제"""
    ctx = ContextService(ttl_seconds=1)  # 1초 TTL
    ctx.save(session_id="sess-001", destination="명지병원", bus_number="58")

    time.sleep(1.5)  # TTL 초과 대기

    assert ctx.get("sess-001") is None


def test_대명사_해석():
    """'거기', '그거' 같은 대명사를 이전 컨텍스트로 해석"""
    ctx = ContextService(ttl_seconds=60)
    ctx.save(session_id="sess-001", destination="명지병원", bus_number="58")

    resolved = ctx.resolve_pronoun("sess-001", "거기서 해운대 가려면?")
    assert "명지병원" in resolved
```

- [ ] **Step 2: 테스트 실행 — 실패 확인**

```bash
cd server
python -m pytest tests/test_context.py -v
```

Expected: FAIL

- [ ] **Step 3: ContextService 구현**

```python
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

    def save(
        self,
        session_id: str,
        destination: str | None = None,
        bus_number: str | None = None,
    ) -> None:
        """
        세션에 컨텍스트 저장
        - 기존 세션이 있으면 덮어쓰기
        - 저장 시각을 함께 기록 (TTL 계산용)
        """
        self._store[session_id] = {
            "destination": destination,
            "bus_number": bus_number,
            "timestamp": time.time(),
        }

    def get(self, session_id: str) -> dict | None:
        """
        세션 컨텍스트 조회
        - TTL 초과 시 삭제 후 None 반환
        """
        context = self._store.get(session_id)
        if context is None:
            return None

        # TTL 체크: 저장 시각으로부터 경과 시간 확인
        elapsed = time.time() - context["timestamp"]
        if elapsed > self._ttl_seconds:
            del self._store[session_id]
            return None

        return context

    def resolve_pronoun(self, session_id: str, text: str) -> str:
        """
        대명사를 이전 컨텍스트로 치환
        - "거기서 해운대 가려면?" → "명지병원에서 해운대 가려면?"
        - 컨텍스트가 없으면 원문 그대로 반환
        """
        context = self.get(session_id)
        if context is None or context["destination"] is None:
            return text

        result = text
        for pronoun in PRONOUNS:
            if pronoun in result:
                result = result.replace(pronoun, context["destination"])

        return result
```

- [ ] **Step 4: 테스트 실행 — 통과 확인**

```bash
cd server
python -m pytest tests/test_context.py -v
```

Expected: 5 passed

- [ ] **Step 5: 커밋**

```bash
git add server/services/context_service.py server/tests/test_context.py
git commit -m "feat(server): 대화 컨텍스트 관리 서비스 구현"
```

---

### Task 7: TAGO 버스 API 연동 서비스

**Files:**
- Create: `server/services/bus_service.py`
- Create: `server/tests/test_bus_service.py`

- [ ] **Step 1: 테스트 작성 — 버스 서비스 (모킹)**

```python
"""
버스 서비스 테스트
- TAGO API 연동 로직 검증 (실제 API 호출은 모킹)
"""
import pytest
from unittest.mock import AsyncMock, patch
from services.bus_service import BusService


@pytest.mark.asyncio
async def test_가장_가까운_정류장_찾기():
    """GPS 좌표로 가장 가까운 정류장을 찾는지 확인"""
    service = BusService(api_key="test_key")

    # TAGO API 응답 모킹
    mock_response = {
        "response": {
            "body": {
                "items": {
                    "item": [
                        {
                            "nodeid": "BUS_1234",
                            "nodenm": "명지대학교 앞",
                            "gpslati": 35.0691,
                            "gpslong": 128.9694,
                        }
                    ]
                }
            }
        }
    }

    with patch.object(service, "_call_tago_api", new_callable=AsyncMock, return_value=mock_response):
        station = await service.get_nearest_station(lat=35.0690, lng=128.9693)
        assert station["name"] == "명지대학교 앞"
        assert station["id"] == "BUS_1234"


@pytest.mark.asyncio
async def test_실시간_도착_정보():
    """정류장 ID로 실시간 도착 정보를 가져오는지 확인"""
    service = BusService(api_key="test_key")

    mock_response = {
        "response": {
            "body": {
                "items": {
                    "item": [
                        {
                            "routeno": "58",
                            "arrtime": 300,
                            "arrprevstationcnt": 1,
                            "nodenm": "명지병원",
                        },
                        {
                            "routeno": "181",
                            "arrtime": 720,
                            "arrprevstationcnt": 3,
                            "nodenm": "해운대",
                        },
                    ]
                }
            }
        }
    }

    with patch.object(service, "_call_tago_api", new_callable=AsyncMock, return_value=mock_response):
        arrivals = await service.get_arrivals(station_id="BUS_1234")
        assert len(arrivals) == 2
        assert arrivals[0]["bus_number"] == "58"
        assert arrivals[0]["arrival_min"] == 5  # 300초 → 5분
        assert arrivals[1]["bus_number"] == "181"


@pytest.mark.asyncio
async def test_도착_정보_없음():
    """운행 종료 등으로 도착 정보가 없는 경우 빈 리스트 반환"""
    service = BusService(api_key="test_key")

    mock_response = {
        "response": {
            "body": {
                "items": ""  # TAGO API가 데이터 없을 때 빈 문자열 반환
            }
        }
    }

    with patch.object(service, "_call_tago_api", new_callable=AsyncMock, return_value=mock_response):
        arrivals = await service.get_arrivals(station_id="BUS_1234")
        assert arrivals == []
```

- [ ] **Step 2: 테스트 실행 — 실패 확인**

```bash
cd server
pip install pytest-asyncio
python -m pytest tests/test_bus_service.py -v
```

Expected: FAIL

- [ ] **Step 3: BusService 구현**

```python
"""
버스 서비스
- TAGO(전국 버스정보시스템) API 연동
- 실시간 도착 정보, 가장 가까운 정류장 검색
- API 키는 환경변수에서 로드 (하드코딩 X)
"""
import os
import httpx
from typing import Any


# TAGO API 기본 URL
TAGO_BASE_URL = "http://apis.data.go.kr/1613000"

# API 엔드포인트 경로
ARRIVAL_PATH = "/ArvlInfoInqireService/getSttnAcctoArvlPrearngeInfoList"
STATION_PATH = "/BusSttnInfoInqireService/getCrdntPrxmtSttnList"


class BusService:
    """
    TAGO 버스 API 연동 서비스
    - get_nearest_station(): GPS → 가장 가까운 정류장
    - get_arrivals(): 정류장 → 실시간 도착 버스 목록
    """

    def __init__(self, api_key: str | None = None):
        # API 키: 파라미터 > 환경변수 > 빈 문자열 순서로 결정
        self._api_key = api_key or os.getenv("TAGO_API_KEY", "")

    async def _call_tago_api(self, path: str, params: dict) -> dict:
        """
        TAGO API 공통 호출 메서드
        - JSON 응답 반환
        - 타임아웃 10초
        """
        base_params = {
            "serviceKey": self._api_key,
            "_type": "json",
            "numOfRows": 20,
            "pageNo": 1,
        }
        base_params.update(params)

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{TAGO_BASE_URL}{path}",
                params=base_params,
            )
            response.raise_for_status()
            return response.json()

    def _extract_items(self, data: dict) -> list[dict]:
        """
        TAGO API 응답에서 items 추출
        - 데이터 없으면 빈 리스트 반환
        - 단일 항목이면 리스트로 감싸기
        """
        items = data.get("response", {}).get("body", {}).get("items", "")

        # 데이터 없음 (TAGO는 빈 문자열로 반환하는 경우 있음)
        if not items or items == "":
            return []

        item_list = items.get("item", [])

        # 단일 항목인 경우 리스트로 감싸기
        if isinstance(item_list, dict):
            return [item_list]

        return item_list

    async def get_nearest_station(self, lat: float, lng: float) -> dict | None:
        """
        GPS 좌표에서 가장 가까운 정류장 찾기
        - TAGO 좌표기반 근접 정류장 API 사용
        - 가장 가까운 1개 반환
        """
        data = await self._call_tago_api(STATION_PATH, {
            "gpsLati": lat,
            "gpsLong": lng,
        })

        items = self._extract_items(data)
        if not items:
            return None

        first = items[0]
        return {
            "id": first["nodeid"],
            "name": first["nodenm"],
            "lat": first["gpslati"],
            "lng": first["gpslong"],
        }

    async def get_arrivals(self, station_id: str) -> list[dict]:
        """
        특정 정류장의 실시간 도착 정보
        - 도착 시간(초)을 분 단위로 변환
        - 도착 예정 시간순 정렬
        """
        data = await self._call_tago_api(ARRIVAL_PATH, {
            "nodeId": station_id,
        })

        items = self._extract_items(data)

        arrivals = []
        for item in items:
            arrivals.append({
                "bus_number": str(item["routeno"]),
                "arrival_min": item["arrtime"] // 60,  # 초 → 분
                "remaining_stops": item["arrprevstationcnt"],
                "destination": item.get("nodenm", ""),
            })

        # 도착 시간순 정렬 (빨리 오는 버스가 위에)
        arrivals.sort(key=lambda x: x["arrival_min"])
        return arrivals
```

- [ ] **Step 4: 테스트 실행 — 통과 확인**

```bash
cd server
python -m pytest tests/test_bus_service.py -v
```

Expected: 3 passed

- [ ] **Step 5: 커밋**

```bash
git add server/services/bus_service.py server/tests/test_bus_service.py
git commit -m "feat(server): TAGO 버스 API 연동 서비스 구현"
```

---

### Task 8: 질의 라우터 — 핵심 `/query` 엔드포인트

**Files:**
- Create: `server/routers/__init__.py`
- Create: `server/routers/query.py`
- Create: `server/routers/bus.py`
- Modify: `server/main.py`
- Create: `server/tests/test_query_router.py`

- [ ] **Step 1: 테스트 작성 — /query 엔드포인트**

```python
"""
질의 라우터 통합 테스트
- /query 엔드포인트가 전체 파이프라인을 올바르게 처리하는지 검증
"""
import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_기본_노선_검색():
    """'명지병원 가는 버스' 질의에 올바른 응답 반환"""
    mock_arrivals = [
        {
            "bus_number": "58",
            "arrival_min": 5,
            "remaining_stops": 1,
            "destination": "명지병원",
        }
    ]

    with patch(
        "routers.query.bus_service.get_arrivals",
        new_callable=AsyncMock,
        return_value=mock_arrivals,
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/query", json={
                "text": "명지병원 가는 버스 있나요?",
                "station_id": "BUS_1234",
                "session_id": "test-session",
            })

    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "노선_검색"
    assert data["destination"] == "명지병원"
    assert len(data["buses"]) == 1
    assert data["buses"][0]["bus_number"] == "58"
    assert "58" in data["answer_tts"]


@pytest.mark.asyncio
async def test_사투리_질의():
    """사투리가 포함된 질의도 올바르게 처리"""
    mock_arrivals = [
        {
            "bus_number": "58",
            "arrival_min": 5,
            "remaining_stops": 1,
            "destination": "명지병원",
        }
    ]

    with patch(
        "routers.query.bus_service.get_arrivals",
        new_callable=AsyncMock,
        return_value=mock_arrivals,
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/query", json={
                "text": "명지병원 카는 버스 있나예?",
                "station_id": "BUS_1234",
                "session_id": "test-session",
            })

    assert response.status_code == 200
    data = response.json()
    assert data["destination"] == "명지병원"


@pytest.mark.asyncio
async def test_health_엔드포인트():
    """서버 상태 확인 엔드포인트"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
```

- [ ] **Step 2: 테스트 실행 — 실패 확인**

```bash
cd server
python -m pytest tests/test_query_router.py -v
```

Expected: FAIL

- [ ] **Step 3: 응답 생성 헬퍼 함수 작성**

Create: `server/services/response_builder.py`

```python
"""
응답 생성 서비스
- NLP 결과 + 버스 데이터를 조합하여 자연스러운 한국어 응답 생성
- 화면 표시용(answer_text)과 TTS용(answer_tts) 텍스트를 분리
"""
from models import BusArrival, QueryResponse


def build_response(
    intent: str,
    destination: str | None,
    buses: list[dict],
    station_name: str = "",
) -> QueryResponse:
    """
    의도와 버스 데이터를 조합하여 QueryResponse 생성
    - 의도별로 다른 응답 템플릿 사용
    - 어르신 친화적인 말투 (존댓말, 간결하게)
    """
    bus_models = [
        BusArrival(
            bus_number=b["bus_number"],
            arrival_min=b["arrival_min"],
            remaining_stops=b["remaining_stops"],
            destination=b["destination"],
        )
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
        answer_text=answer_text,
        answer_tts=answer_tts,
        buses=bus_models,
        intent=intent,
        destination=destination,
    )


def _build_route_response(
    destination: str | None,
    buses: list[BusArrival],
) -> tuple[str, str]:
    """노선 검색 응답 생성"""
    if not buses:
        text = f"{destination}으로 가는 버스가 현재 없습니다."
        tts = text
        return text, tts

    first = buses[0]
    text = (
        f"{destination} 가시려면\n"
        f"{first.bus_number}번 버스 타시면 됩니다.\n"
        f"{first.arrival_min}분 후 도착 예정입니다."
    )
    tts = (
        f"{destination} 가시려면 "
        f"{first.bus_number}번 버스 타시면 됩니다. "
        f"{first.arrival_min}분 후에 도착합니다."
    )
    return text, tts


def _build_arrival_response(buses: list[BusArrival]) -> tuple[str, str]:
    """도착 시간 응답 생성"""
    if not buses:
        text = "현재 도착 예정인 버스가 없습니다."
        return text, text

    first = buses[0]
    text = f"{first.bus_number}번 버스가\n{first.arrival_min}분 후 도착합니다."
    tts = f"{first.bus_number}번 버스가 {first.arrival_min}분 후에 도착합니다."
    return text, tts


def _build_transfer_response(
    destination: str | None,
    buses: list[BusArrival],
) -> tuple[str, str]:
    """환승 안내 응답 생성"""
    if not buses:
        text = f"{destination}까지 환승 정보를 찾을 수 없습니다."
        return text, text

    first = buses[0]
    text = (
        f"{first.bus_number}번 버스로 갈아타시면\n"
        f"{destination}에 갈 수 있습니다."
    )
    tts = (
        f"{first.bus_number}번 버스로 갈아타시면 "
        f"{destination}에 갈 수 있습니다."
    )
    return text, tts


def _build_station_response(
    station_name: str,
    buses: list[BusArrival],
) -> tuple[str, str]:
    """정류장 확인 응답 생성"""
    bus_numbers = ", ".join(b.bus_number + "번" for b in buses[:5])
    text = f"여기는 {station_name} 정류장입니다."
    if bus_numbers:
        text += f"\n{bus_numbers} 버스가 섭니다."

    tts = text.replace("\n", " ")
    return text, tts
```

- [ ] **Step 4: query.py 라우터 구현**

Create: `server/routers/__init__.py` (빈 파일)
Create: `server/routers/query.py`

```python
"""
질의 라우터
- /query 엔드포인트: 음성 텍스트 → NLP 파이프라인 → 버스 안내 응답
- 전체 처리 흐름: 사투리 변환 → 대명사 해석 → 의도 파악 → 목적지 추출 → API 호출 → 응답 생성
"""
from fastapi import APIRouter

from models import QueryRequest, QueryResponse
from services.nlp_service import NlpService
from services.bus_service import BusService
from services.context_service import ContextService
from services.response_builder import build_response
import os

router = APIRouter()

# 서비스 인스턴스 (앱 시작 시 1회 생성)
nlp_service = NlpService()
bus_service = BusService()
context_service = ContextService(ttl_seconds=300)  # 5분 TTL


@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest) -> QueryResponse:
    """
    음성 질의 처리 파이프라인
    1. 사투리 변환
    2. 대명사 해석 (컨텍스트 활용)
    3. 의도 파악
    4. 목적지 추출
    5. TAGO API 호출
    6. 컨텍스트 저장
    7. 응답 생성
    """
    text = request.text

    # ① 사투리 → 표준어 변환
    text = nlp_service.convert_dialect(text)

    # ② 대명사 해석: "거기" → 이전 목적지
    text = context_service.resolve_pronoun(request.session_id, text)

    # ③ 의도 파악: 노선_검색 / 도착_시간 / 환승_안내 / 정류장_확인
    intent = nlp_service.classify_intent(text)

    # ④ 목적지 추출: 유사어 매칭 포함
    destination = nlp_service.extract_destination(text)

    # ⑤ TAGO API 호출: 실시간 도착 정보
    buses = await bus_service.get_arrivals(station_id=request.station_id)

    # 목적지가 있으면 해당 방면 버스만 필터링
    if destination:
        # TODO: 노선별 경유 정류장 조회로 정확한 필터링 (현재는 전체 반환)
        pass

    # ⑥ 컨텍스트 저장: 다음 질문에서 참조할 수 있도록
    first_bus = buses[0]["bus_number"] if buses else None
    context_service.save(
        session_id=request.session_id,
        destination=destination,
        bus_number=first_bus,
    )

    # ⑦ 응답 생성: 화면 텍스트 + TTS 텍스트 + 버스 목록
    response = build_response(
        intent=intent,
        destination=destination,
        buses=buses,
    )

    return response
```

- [ ] **Step 5: bus.py 라우터 구현**

Create: `server/routers/bus.py`

```python
"""
버스 정보 라우터
- 실시간 도착 정보, 가장 가까운 정류장 조회
- /query와 별도로 앱에서 직접 호출할 수 있는 API
"""
from fastapi import APIRouter, Query

from models import Station, BusArrival
from services.bus_service import BusService

router = APIRouter(prefix="/bus", tags=["bus"])

bus_service = BusService()


@router.get("/arrivals/{station_id}", response_model=list[BusArrival])
async def get_arrivals(station_id: str) -> list:
    """특정 정류장의 실시간 도착 정보"""
    arrivals = await bus_service.get_arrivals(station_id=station_id)
    return [
        BusArrival(
            bus_number=a["bus_number"],
            arrival_min=a["arrival_min"],
            remaining_stops=a["remaining_stops"],
            destination=a["destination"],
        )
        for a in arrivals
    ]


@router.get("/nearest-station", response_model=Station)
async def get_nearest_station(
    lat: float = Query(..., description="위도"),
    lng: float = Query(..., description="경도"),
) -> Station:
    """GPS 좌표로 가장 가까운 정류장 찾기"""
    station = await bus_service.get_nearest_station(lat=lat, lng=lng)
    if station is None:
        return Station(id="", name="정류장을 찾을 수 없습니다", lat=lat, lng=lng)
    return Station(
        id=station["id"],
        name=station["name"],
        lat=station["lat"],
        lng=station["lng"],
    )
```

- [ ] **Step 6: main.py에 라우터 등록**

```python
"""
BusGuide 서버 엔트리포인트
- 어르신 음성 질의를 받아 버스 안내를 반환하는 API 서버
- 라우터: /query (질의 처리), /bus (버스 정보)
"""
from fastapi import FastAPI
from dotenv import load_dotenv

from routers.query import router as query_router
from routers.bus import router as bus_router

load_dotenv()

app = FastAPI(
    title="BusGuide API",
    description="어르신 음성 기반 버스 안내 시스템 백엔드",
    version="1.0.0",
)

# 라우터 등록
app.include_router(query_router)
app.include_router(bus_router)


@app.get("/health")
async def health_check():
    """서버 상태 확인 — 키오스크 모니터링용"""
    return {"status": "ok"}
```

- [ ] **Step 7: 테스트 실행 — 통과 확인**

```bash
cd server
python -m pytest tests/test_query_router.py -v
```

Expected: 3 passed

- [ ] **Step 8: 전체 테스트 실행**

```bash
cd server
python -m pytest tests/ -v
```

Expected: 모든 테스트 통과

- [ ] **Step 9: 커밋**

```bash
git add server/routers/ server/services/response_builder.py server/main.py server/tests/test_query_router.py
git commit -m "feat(server): 질의 라우터 + 응답 생성 + 전체 파이프라인 완성"
```

---

### Task 9: 자주 가는 곳 프리셋 데이터

**Files:**
- Create: `server/data/presets.json`

- [ ] **Step 1: presets.json 작성 — 부산 주요 목적지 프리셋**

```json
{
  "busan": {
    "label": "부산",
    "presets": [
      {"name": "명지병원", "icon": "hospital"},
      {"name": "해운대", "icon": "beach"},
      {"name": "서면", "icon": "shopping"},
      {"name": "부산역", "icon": "train"},
      {"name": "센텀시티", "icon": "building"},
      {"name": "남포동", "icon": "market"}
    ]
  }
}
```

앱에서 이 JSON을 서버로부터 받아 프리셋 버튼을 동적으로 생성함.
→ 새 지역 추가 시 이 파일만 수정하면 됨.

- [ ] **Step 2: main.py에 프리셋 엔드포인트 추가**

```python
@app.get("/presets/{region}")
async def get_presets(region: str):
    """지역별 자주 가는 곳 프리셋 반환"""
    import json
    from pathlib import Path
    data_path = Path(__file__).parent / "data" / "presets.json"
    with open(data_path, "r", encoding="utf-8") as f:
        all_presets = json.load(f)
    return all_presets.get(region, {"label": region, "presets": []})
```

- [ ] **Step 3: 커밋**

```bash
git add server/data/presets.json server/main.py
git commit -m "feat(server): 자주 가는 곳 프리셋 데이터 + 엔드포인트"
```

---

## Part B: Android 앱

---

### Task 10: Android 프로젝트 생성

**Files:**
- 새 Android 프로젝트 전체

- [ ] **Step 1: Android Studio에서 새 프로젝트 생성**

- Template: Empty Compose Activity
- Name: BusGuide
- Package: `com.hyeonsu.busguide`
- Language: Kotlin
- Minimum SDK: API 26 (Android 8.0)
- Build: Gradle (Kotlin DSL)

저장 위치: `C:\Users\AirMookie\Downloads\새 폴더\busguide-android\` (서버와 분리)

- [ ] **Step 2: build.gradle.kts (app) 의존성 추가**

```kotlin
plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.compose)
    id("com.google.dagger.hilt.android")
    kotlin("kapt")
    kotlin("plugin.serialization")
}

dependencies {
    // Compose
    implementation(platform("androidx.compose:compose-bom:2024.09.00"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.activity:activity-compose:1.9.2")
    implementation("androidx.navigation:navigation-compose:2.8.0")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.8.5")

    // Hilt (DI)
    implementation("com.google.dagger:hilt-android:2.51.1")
    kapt("com.google.dagger:hilt-compiler:2.51.1")
    implementation("androidx.hilt:hilt-navigation-compose:1.2.0")

    // Retrofit (네트워크)
    implementation("com.squareup.retrofit2:retrofit:2.11.0")
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")

    // Kotlinx Serialization (JSON)
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.7.1")
    implementation("com.squareup.retrofit2:converter-kotlinx-serialization:2.11.0")

    // Location (GPS)
    implementation("com.google.android.gms:play-services-location:21.3.0")

    // DataStore (로컬 저장)
    implementation("androidx.datastore:datastore-preferences:1.1.1")
}
```

- [ ] **Step 3: AndroidManifest.xml 권한 추가**

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
<uses-permission android:name="android.permission.RECORD_AUDIO" />
<uses-permission android:name="android.permission.VIBRATE" />
```

- [ ] **Step 4: 빌드 확인**

Android Studio에서 빌드 실행 → 에러 없이 성공하는지 확인

- [ ] **Step 5: 커밋**

```bash
git add busguide-android/
git commit -m "feat(android): 프로젝트 초기 설정 + 의존성 추가"
```

---

### Task 11: 도메인 모델 + Retrofit API 인터페이스

**Files:**
- Create: `domain/model/Station.kt`
- Create: `domain/model/BusArrival.kt`
- Create: `domain/model/QueryRequest.kt`
- Create: `domain/model/QueryResponse.kt`
- Create: `domain/model/Preset.kt`
- Create: `data/remote/BusGuideApi.kt`
- Create: `data/remote/dto/PresetResponse.kt`

경로 접두사: `app/src/main/java/com/hyeonsu/busguide/`

- [ ] **Step 1: 도메인 모델 작성**

`domain/model/Station.kt`:
```kotlin
package com.hyeonsu.busguide.domain.model

import kotlinx.serialization.Serializable

/**
 * 정류장 정보
 * - TAGO API에서 받아온 정류장 데이터를 담는 모델
 * - GPS 좌표 포함 (가장 가까운 정류장 계산용)
 */
@Serializable
data class Station(
    val id: String,        // 정류장 고유 ID (TAGO 기준)
    val name: String,      // 정류장 이름 (예: "명지대학교 앞")
    val lat: Double,       // 위도
    val lng: Double,       // 경도
)
```

`domain/model/BusArrival.kt`:
```kotlin
package com.hyeonsu.busguide.domain.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

/**
 * 버스 도착 정보
 * - 실시간 도착 예정 버스 한 대의 정보
 * - 화면에 "58번 | 5분 후 | 1정거장 전" 형태로 표시
 */
@Serializable
data class BusArrival(
    @SerialName("bus_number") val busNumber: String,          // 버스 번호
    @SerialName("arrival_min") val arrivalMin: Int,           // 도착 예정 시간(분)
    @SerialName("remaining_stops") val remainingStops: Int,   // 남은 정거장 수
    val destination: String,                                   // 버스 종점
)
```

`domain/model/QueryRequest.kt`:
```kotlin
package com.hyeonsu.busguide.domain.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

/**
 * 음성 질의 요청
 * - 앱 → 서버로 보내는 데이터
 * - 음성 인식 결과 + 현재 위치 + 세션 정보
 */
@Serializable
data class QueryRequest(
    val text: String,                                // 음성 인식 결과 텍스트
    @SerialName("station_id") val stationId: String, // 현재 정류장 ID
    @SerialName("session_id") val sessionId: String, // 대화 세션 ID
)
```

`domain/model/QueryResponse.kt`:
```kotlin
package com.hyeonsu.busguide.domain.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

/**
 * 음성 질의 응답
 * - 서버 → 앱으로 받는 데이터
 * - 화면 표시용 텍스트 + TTS 텍스트 + 버스 목록
 */
@Serializable
data class QueryResponse(
    @SerialName("answer_text") val answerText: String,  // 화면에 표시할 텍스트
    @SerialName("answer_tts") val answerTts: String,    // TTS로 읽어줄 텍스트
    val buses: List<BusArrival>,                         // 도착 버스 목록
    val intent: String,                                  // 파악된 의도
    val destination: String?,                            // 파악된 목적지
)
```

`domain/model/Preset.kt`:
```kotlin
package com.hyeonsu.busguide.domain.model

import kotlinx.serialization.Serializable

/**
 * 자주 가는 곳 프리셋
 * - 메인 화면에 큰 버튼으로 표시되는 바로가기
 * - 서버의 presets.json에서 로드 (하드코딩 X)
 */
@Serializable
data class Preset(
    val name: String,   // 표시 이름 (예: "명지병원")
    val icon: String,   // 아이콘 타입 (예: "hospital")
)

/**
 * 프리셋 응답 — 서버에서 지역별 프리셋 목록을 반환
 */
@Serializable
data class PresetResponse(
    val label: String,          // 지역 이름 (예: "부산")
    val presets: List<Preset>,  // 프리셋 목록
)
```

- [ ] **Step 2: Retrofit API 인터페이스**

`data/remote/BusGuideApi.kt`:
```kotlin
package com.hyeonsu.busguide.data.remote

import com.hyeonsu.busguide.domain.model.*
import retrofit2.http.*

/**
 * BusGuide 서버 API 인터페이스
 * - FastAPI 서버와 통신하는 Retrofit 인터페이스
 * - 모든 API 호출은 suspend 함수 (코루틴 기반)
 */
interface BusGuideApi {

    /** 음성 질의 처리 — 핵심 API */
    @POST("query")
    suspend fun sendQuery(@Body request: QueryRequest): QueryResponse

    /** 특정 정류장의 실시간 도착 정보 */
    @GET("bus/arrivals/{stationId}")
    suspend fun getArrivals(@Path("stationId") stationId: String): List<BusArrival>

    /** GPS 좌표로 가장 가까운 정류장 찾기 */
    @GET("bus/nearest-station")
    suspend fun getNearestStation(
        @Query("lat") lat: Double,
        @Query("lng") lng: Double,
    ): Station

    /** 지역별 자주 가는 곳 프리셋 */
    @GET("presets/{region}")
    suspend fun getPresets(@Path("region") region: String): PresetResponse

    /** 서버 상태 확인 */
    @GET("health")
    suspend fun healthCheck(): Map<String, String>
}
```

- [ ] **Step 3: 빌드 확인**

Android Studio에서 빌드 → 에러 없이 성공

- [ ] **Step 4: 커밋**

```bash
git add busguide-android/app/src/main/java/com/hyeonsu/busguide/domain/
git add busguide-android/app/src/main/java/com/hyeonsu/busguide/data/remote/
git commit -m "feat(android): 도메인 모델 + Retrofit API 인터페이스"
```

---

### Task 12: Hilt DI 모듈 설정

**Files:**
- Create: `BusGuideApp.kt`
- Create: `di/NetworkModule.kt`

경로 접두사: `app/src/main/java/com/hyeonsu/busguide/`

- [ ] **Step 1: Application 클래스**

`BusGuideApp.kt`:
```kotlin
package com.hyeonsu.busguide

import android.app.Application
import dagger.hilt.android.HiltAndroidApp

/**
 * BusGuide 애플리케이션 클래스
 * - Hilt DI 컨테이너 초기화
 */
@HiltAndroidApp
class BusGuideApp : Application()
```

AndroidManifest.xml의 `<application>`에 `android:name=".BusGuideApp"` 추가.

- [ ] **Step 2: NetworkModule — Retrofit + OkHttp 제공**

`di/NetworkModule.kt`:
```kotlin
package com.hyeonsu.busguide.di

import com.hyeonsu.busguide.BuildConfig
import com.hyeonsu.busguide.data.remote.BusGuideApi
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import kotlinx.serialization.json.Json
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.kotlinx.serialization.asConverterFactory
import java.util.concurrent.TimeUnit
import javax.inject.Singleton

/**
 * 네트워크 DI 모듈
 * - Retrofit, OkHttp, BusGuideApi 인스턴스 제공
 * - 서버 URL은 BuildConfig에서 로드 (하드코딩 X)
 */
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    /** JSON 파서 — 알 수 없는 키 무시, null 허용 */
    private val json = Json {
        ignoreUnknownKeys = true
        coerceInputValues = true
    }

    @Provides
    @Singleton
    fun provideOkHttpClient(): OkHttpClient {
        val logging = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }
        return OkHttpClient.Builder()
            .addInterceptor(logging)
            .connectTimeout(10, TimeUnit.SECONDS)
            .readTimeout(10, TimeUnit.SECONDS)
            .build()
    }

    @Provides
    @Singleton
    fun provideRetrofit(client: OkHttpClient): Retrofit {
        return Retrofit.Builder()
            .baseUrl(BuildConfig.SERVER_URL)  // gradle에서 주입
            .client(client)
            .addConverterFactory(
                json.asConverterFactory("application/json".toMediaType())
            )
            .build()
    }

    @Provides
    @Singleton
    fun provideBusGuideApi(retrofit: Retrofit): BusGuideApi {
        return retrofit.create(BusGuideApi::class.java)
    }
}
```

- [ ] **Step 3: build.gradle.kts에 SERVER_URL BuildConfig 필드 추가**

```kotlin
android {
    buildTypes {
        debug {
            buildConfigField("String", "SERVER_URL", "\"http://10.0.2.2:8000/\"") // 에뮬레이터용
        }
        release {
            buildConfigField("String", "SERVER_URL", "\"https://your-server.railway.app/\"")
        }
    }
    buildFeatures {
        buildConfig = true
    }
}
```

- [ ] **Step 4: 빌드 확인**

Android Studio 빌드 → 성공 확인

- [ ] **Step 5: 커밋**

```bash
git add busguide-android/app/src/main/java/com/hyeonsu/busguide/BusGuideApp.kt
git add busguide-android/app/src/main/java/com/hyeonsu/busguide/di/
git commit -m "feat(android): Hilt DI + Retrofit 네트워크 모듈"
```

---

### Task 13: 시니어 특화 테마

**Files:**
- Create: `presentation/theme/SeniorTheme.kt`
- Create: `presentation/theme/Color.kt`
- Create: `presentation/theme/Type.kt`

경로 접두사: `app/src/main/java/com/hyeonsu/busguide/`

- [ ] **Step 1: Color.kt — 고대비 색상 팔레트**

```kotlin
package com.hyeonsu.busguide.presentation.theme

import androidx.compose.ui.graphics.Color

/**
 * 시니어 특화 색상 팔레트
 * - 고대비: 검정 배경 + 밝은 텍스트 (시력 약한 분도 잘 보임)
 * - 색약/색맹 고려: 빨강-초록 조합 회피
 */

// 배경색
val SeniorBackground = Color(0xFF1A1A1A)      // 짙은 검정 (순수 검정보다 눈 편함)
val SeniorSurface = Color(0xFF2D2D2D)         // 카드/버튼 배경

// 텍스트
val SeniorOnBackground = Color(0xFFFFF176)    // 노란 텍스트 (고대비)
val SeniorOnSurface = Color(0xFFFFFFFF)       // 흰색 텍스트

// 강조색
val SeniorPrimary = Color(0xFF4FC3F7)         // 하늘색 (말하기 버튼)
val SeniorPrimaryDark = Color(0xFF0288D1)     // 진한 하늘색 (눌렀을 때)
val SeniorSecondary = Color(0xFF81C784)       // 연두색 (도착 정보)

// 상태색
val SeniorError = Color(0xFFFF8A80)           // 연한 빨강 (에러)
val SeniorSuccess = Color(0xFFA5D6A7)         // 연한 초록 (성공)
```

- [ ] **Step 2: Type.kt — 대형 폰트 시스템**

```kotlin
package com.hyeonsu.busguide.presentation.theme

import androidx.compose.material3.Typography
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

/**
 * 시니어 특화 타이포그래피
 * - 최소 24sp, 핵심 정보는 48sp
 * - Bold 위주 (가독성↑)
 * - 일반 앱 대비 2~3배 큰 폰트
 */
val SeniorTypography = Typography(
    // 버스 번호, 도착 시간 등 핵심 정보
    displayLarge = TextStyle(
        fontSize = 48.sp,
        fontWeight = FontWeight.Bold,
        lineHeight = 56.sp,
    ),
    // 안내 문구 ("어디 가시려고요?")
    headlineLarge = TextStyle(
        fontSize = 36.sp,
        fontWeight = FontWeight.Bold,
        lineHeight = 44.sp,
    ),
    // 버튼 텍스트 ("명지병원", "해운대")
    headlineMedium = TextStyle(
        fontSize = 32.sp,
        fontWeight = FontWeight.Bold,
        lineHeight = 40.sp,
    ),
    // 보조 정보 ("1정거장 전")
    bodyLarge = TextStyle(
        fontSize = 28.sp,
        fontWeight = FontWeight.Normal,
        lineHeight = 36.sp,
    ),
    // 상태 표시 ("현재 정류장: OO앞")
    bodyMedium = TextStyle(
        fontSize = 24.sp,
        fontWeight = FontWeight.Normal,
        lineHeight = 32.sp,
    ),
)
```

- [ ] **Step 3: SeniorTheme.kt — 테마 통합**

```kotlin
package com.hyeonsu.busguide.presentation.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable

/**
 * BusGuide 시니어 테마
 * - 항상 다크 모드 (고대비 유지)
 * - 어르신 눈에 잘 보이는 색상 + 큰 폰트
 */
private val SeniorColorScheme = darkColorScheme(
    primary = SeniorPrimary,
    onPrimary = SeniorBackground,
    secondary = SeniorSecondary,
    background = SeniorBackground,
    onBackground = SeniorOnBackground,
    surface = SeniorSurface,
    onSurface = SeniorOnSurface,
    error = SeniorError,
)

@Composable
fun BusGuideTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = SeniorColorScheme,
        typography = SeniorTypography,
        content = content,
    )
}
```

- [ ] **Step 4: 빌드 확인**

- [ ] **Step 5: 커밋**

```bash
git add busguide-android/app/src/main/java/com/hyeonsu/busguide/presentation/theme/
git commit -m "feat(android): 시니어 특화 테마 (고대비 + 대형 폰트)"
```

---

### Task 14: SpeechManager — 음성 인식(STT) + 음성 출력(TTS)

**Files:**
- Create: `speech/SpeechManager.kt`
- Create: `speech/TtsManager.kt`

경로 접두사: `app/src/main/java/com/hyeonsu/busguide/`

- [ ] **Step 1: SpeechManager — Android STT 래퍼**

```kotlin
package com.hyeonsu.busguide.speech

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

/**
 * 음성 인식(STT) 관리자
 * - Android SpeechRecognizer 래핑
 * - 한국어 음성 → 텍스트 변환
 * - StateFlow로 상태 관리 (Compose UI와 연동)
 */
class SpeechManager(private val context: Context) {

    /** 음성 인식 상태 */
    sealed class State {
        data object Idle : State()           // 대기 중
        data object Listening : State()      // 듣는 중
        data class Result(val text: String) : State()  // 인식 완료
        data class Error(val message: String) : State() // 인식 실패
    }

    private val _state = MutableStateFlow<State>(State.Idle)
    val state: StateFlow<State> = _state

    private var recognizer: SpeechRecognizer? = null

    /**
     * 음성 인식 시작
     * - 한국어(ko-KR) 설정
     * - 3초 무음 시 자동 종료
     */
    fun startListening() {
        // 이전 인스턴스 정리
        recognizer?.destroy()
        recognizer = SpeechRecognizer.createSpeechRecognizer(context)

        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(
                RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                RecognizerIntent.LANGUAGE_MODEL_FREE_FORM,
            )
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, "ko-KR")
            putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
            // 3초 무음 시 자동 종료 (어르신 말씀 속도 고려하여 넉넉하게)
            putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_COMPLETE_SILENCE_LENGTH_MILLIS, 3000L)
        }

        recognizer?.setRecognitionListener(object : RecognitionListener {
            override fun onReadyForSpeech(params: Bundle?) {
                _state.value = State.Listening
            }

            override fun onResults(results: Bundle?) {
                val matches = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                val text = matches?.firstOrNull() ?: ""
                _state.value = if (text.isNotEmpty()) {
                    State.Result(text)
                } else {
                    State.Error("말씀을 못 알아들었어요")
                }
            }

            override fun onError(error: Int) {
                val message = when (error) {
                    SpeechRecognizer.ERROR_NO_MATCH -> "말씀을 못 알아들었어요"
                    SpeechRecognizer.ERROR_NETWORK -> "인터넷 연결을 확인해주세요"
                    SpeechRecognizer.ERROR_AUDIO -> "마이크에 문제가 있어요"
                    else -> "다시 말씀해주세요"
                }
                _state.value = State.Error(message)
            }

            // 사용하지 않는 콜백 — 빈 구현
            override fun onBeginningOfSpeech() {}
            override fun onRmsChanged(rmsdB: Float) {}
            override fun onBufferReceived(buffer: ByteArray?) {}
            override fun onEndOfSpeech() {}
            override fun onPartialResults(partialResults: Bundle?) {}
            override fun onEvent(eventType: Int, params: Bundle?) {}
        })

        recognizer?.startListening(intent)
    }

    /** 음성 인식 중지 */
    fun stopListening() {
        recognizer?.stopListening()
        _state.value = State.Idle
    }

    /** 상태 초기화 (다음 질문 준비) */
    fun reset() {
        _state.value = State.Idle
    }

    /** 리소스 해제 (Activity/Fragment 종료 시 호출) */
    fun destroy() {
        recognizer?.destroy()
        recognizer = null
    }
}
```

- [ ] **Step 2: TtsManager — 음성 출력 래퍼**

```kotlin
package com.hyeonsu.busguide.speech

import android.content.Context
import android.speech.tts.TextToSpeech
import java.util.Locale

/**
 * 음성 출력(TTS) 관리자
 * - Android TextToSpeech 래핑
 * - 한국어 음성으로 버스 안내 읽어주기
 * - 어르신이 잘 들을 수 있도록 느린 속도
 */
class TtsManager(context: Context) {

    private var tts: TextToSpeech? = null
    private var isReady = false

    init {
        tts = TextToSpeech(context) { status ->
            if (status == TextToSpeech.SUCCESS) {
                tts?.language = Locale.KOREAN
                // 어르신 맞춤: 약간 느린 속도 + 높은 피치
                tts?.setSpeechRate(0.85f)
                tts?.setPitch(1.05f)
                isReady = true
            }
        }
    }

    /**
     * 텍스트를 음성으로 읽어주기
     * - 이전 음성이 재생 중이면 중단 후 새 음성 재생
     */
    fun speak(text: String) {
        if (!isReady) return
        tts?.speak(text, TextToSpeech.QUEUE_FLUSH, null, "busguide_tts")
    }

    /** 음성 재생 중지 */
    fun stop() {
        tts?.stop()
    }

    /** 리소스 해제 */
    fun destroy() {
        tts?.stop()
        tts?.shutdown()
        tts = null
    }
}
```

- [ ] **Step 3: 빌드 확인**

- [ ] **Step 4: 커밋**

```bash
git add busguide-android/app/src/main/java/com/hyeonsu/busguide/speech/
git commit -m "feat(android): STT/TTS 음성 매니저 구현"
```

---

### Task 15: Repository 레이어

**Files:**
- Create: `domain/repository/BusGuideRepository.kt`
- Create: `data/repository/BusGuideRepositoryImpl.kt`
- Modify: `di/NetworkModule.kt` (Repository 바인딩 추가)

경로 접두사: `app/src/main/java/com/hyeonsu/busguide/`

- [ ] **Step 1: Repository 인터페이스**

```kotlin
package com.hyeonsu.busguide.domain.repository

import com.hyeonsu.busguide.domain.model.*

/**
 * BusGuide 레포지토리 인터페이스
 * - 앱의 데이터 접근 계층
 * - UseCase에서 이 인터페이스에 의존 (구현체는 Hilt가 주입)
 */
interface BusGuideRepository {
    /** 음성 질의 전송 → 버스 안내 응답 */
    suspend fun sendQuery(request: QueryRequest): Result<QueryResponse>

    /** GPS 좌표 → 가장 가까운 정류장 */
    suspend fun getNearestStation(lat: Double, lng: Double): Result<Station>

    /** 지역별 프리셋 목록 */
    suspend fun getPresets(region: String): Result<PresetResponse>
}
```

- [ ] **Step 2: Repository 구현체**

```kotlin
package com.hyeonsu.busguide.data.repository

import com.hyeonsu.busguide.data.remote.BusGuideApi
import com.hyeonsu.busguide.domain.model.*
import com.hyeonsu.busguide.domain.repository.BusGuideRepository
import javax.inject.Inject

/**
 * BusGuide 레포지토리 구현체
 * - Retrofit API 호출을 Result로 감싸서 에러 처리
 * - 네트워크 에러 시 Result.failure 반환
 */
class BusGuideRepositoryImpl @Inject constructor(
    private val api: BusGuideApi,
) : BusGuideRepository {

    override suspend fun sendQuery(request: QueryRequest): Result<QueryResponse> {
        return runCatching { api.sendQuery(request) }
    }

    override suspend fun getNearestStation(lat: Double, lng: Double): Result<Station> {
        return runCatching { api.getNearestStation(lat, lng) }
    }

    override suspend fun getPresets(region: String): Result<PresetResponse> {
        return runCatching { api.getPresets(region) }
    }
}
```

- [ ] **Step 3: DI 모듈에 Repository 바인딩 추가**

Create: `di/RepositoryModule.kt`:

```kotlin
package com.hyeonsu.busguide.di

import com.hyeonsu.busguide.data.repository.BusGuideRepositoryImpl
import com.hyeonsu.busguide.domain.repository.BusGuideRepository
import dagger.Binds
import dagger.Module
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

/**
 * Repository DI 모듈
 * - 인터페이스 → 구현체 바인딩
 */
@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {

    @Binds
    @Singleton
    abstract fun bindBusGuideRepository(
        impl: BusGuideRepositoryImpl,
    ): BusGuideRepository
}
```

- [ ] **Step 4: 빌드 확인**

- [ ] **Step 5: 커밋**

```bash
git add busguide-android/app/src/main/java/com/hyeonsu/busguide/domain/repository/
git add busguide-android/app/src/main/java/com/hyeonsu/busguide/data/repository/
git add busguide-android/app/src/main/java/com/hyeonsu/busguide/di/RepositoryModule.kt
git commit -m "feat(android): Repository 레이어 + DI 바인딩"
```

---

### Task 16: MainScreen — 메인 화면 (말하기 버튼 + 프리셋)

**Files:**
- Create: `presentation/main/MainViewModel.kt`
- Create: `presentation/main/MainScreen.kt`

경로 접두사: `app/src/main/java/com/hyeonsu/busguide/`

- [ ] **Step 1: MainViewModel**

```kotlin
package com.hyeonsu.busguide.presentation.main

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.hyeonsu.busguide.domain.model.Preset
import com.hyeonsu.busguide.domain.model.QueryRequest
import com.hyeonsu.busguide.domain.model.QueryResponse
import com.hyeonsu.busguide.domain.repository.BusGuideRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import java.util.UUID
import javax.inject.Inject

/**
 * 메인 화면 ViewModel
 * - 음성 질의 전송, 프리셋 로드, 세션 관리
 */
@HiltViewModel
class MainViewModel @Inject constructor(
    private val repository: BusGuideRepository,
) : ViewModel() {

    /** UI 상태 */
    data class UiState(
        val isLoading: Boolean = false,
        val presets: List<Preset> = emptyList(),
        val currentStation: String = "정류장 확인 중...",
        val currentStationId: String = "",
        val response: QueryResponse? = null,
        val error: String? = null,
    )

    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState

    // 대화 세션 ID — 앱 시작 시 생성, 5분 비활성 시 갱신
    private var sessionId: String = UUID.randomUUID().toString()

    init {
        loadPresets()
    }

    /** 서버에서 프리셋 목록 로드 */
    private fun loadPresets() {
        viewModelScope.launch {
            repository.getPresets("busan").onSuccess { response ->
                _uiState.value = _uiState.value.copy(presets = response.presets)
            }
        }
    }

    /** 현재 정류장 설정 (LocationManager에서 호출) */
    fun setCurrentStation(id: String, name: String) {
        _uiState.value = _uiState.value.copy(
            currentStation = name,
            currentStationId = id,
        )
    }

    /**
     * 음성 질의 전송
     * - 음성 인식 결과 텍스트를 서버로 보내고 응답 받기
     * - 프리셋 버튼 터치 시에도 동일 경로 사용
     */
    fun sendQuery(text: String) {
        val stationId = _uiState.value.currentStationId
        if (stationId.isEmpty()) {
            _uiState.value = _uiState.value.copy(
                error = "정류장 위치를 확인하고 있어요. 잠시만 기다려주세요.",
            )
            return
        }

        _uiState.value = _uiState.value.copy(isLoading = true, error = null)

        viewModelScope.launch {
            val request = QueryRequest(
                text = text,
                stationId = stationId,
                sessionId = sessionId,
            )
            repository.sendQuery(request)
                .onSuccess { response ->
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        response = response,
                    )
                }
                .onFailure { e ->
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        error = "인터넷 연결을 확인해주세요",
                    )
                }
        }
    }

    /** 응답 초기화 (처음으로 돌아가기) */
    fun clearResponse() {
        _uiState.value = _uiState.value.copy(response = null, error = null)
    }
}
```

- [ ] **Step 2: MainScreen Composable**

```kotlin
package com.hyeonsu.busguide.presentation.main

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.hyeonsu.busguide.domain.model.Preset
import com.hyeonsu.busguide.speech.SpeechManager

/**
 * 메인 화면
 * - 큰 "말하기" 버튼 + 자주 가는 곳 프리셋
 * - 어르신이 한눈에 이해할 수 있는 심플한 구성
 */
@Composable
fun MainScreen(
    viewModel: MainViewModel = hiltViewModel(),
    speechManager: SpeechManager,
    onNavigateToResult: () -> Unit,
) {
    val uiState by viewModel.uiState.collectAsState()
    val speechState by speechManager.state.collectAsState()
    val haptic = LocalHapticFeedback.current

    // 음성 인식 결과 → 서버에 질의 전송
    LaunchedEffect(speechState) {
        if (speechState is SpeechManager.State.Result) {
            val text = (speechState as SpeechManager.State.Result).text
            viewModel.sendQuery(text)
            speechManager.reset()
        }
    }

    // 서버 응답 도착 → 결과 화면으로 이동
    LaunchedEffect(uiState.response) {
        if (uiState.response != null) {
            onNavigateToResult()
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        // 현재 정류장 표시
        Text(
            text = "현재 정류장: ${uiState.currentStation}",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onBackground,
        )

        Spacer(modifier = Modifier.height(24.dp))

        // 안내 문구
        Text(
            text = "어디 가시려고요?",
            style = MaterialTheme.typography.headlineLarge,
            color = MaterialTheme.colorScheme.onBackground,
            textAlign = TextAlign.Center,
        )

        Spacer(modifier = Modifier.height(40.dp))

        // 말하기 버튼 — 10cm 원형 (120dp ≈ 약 5cm, 240dp ≈ 약 10cm)
        Button(
            onClick = {
                haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                speechManager.startListening()
            },
            modifier = Modifier.size(240.dp),
            shape = CircleShape,
            colors = ButtonDefaults.buttonColors(
                containerColor = MaterialTheme.colorScheme.primary,
            ),
        ) {
            Text(
                text = if (speechState is SpeechManager.State.Listening) "듣고 있어요..." else "말하기",
                style = MaterialTheme.typography.displayLarge,
                color = MaterialTheme.colorScheme.onPrimary,
            )
        }

        Spacer(modifier = Modifier.height(40.dp))

        // 에러 표시
        if (uiState.error != null) {
            Text(
                text = uiState.error!!,
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.error,
                textAlign = TextAlign.Center,
            )
            Spacer(modifier = Modifier.height(16.dp))
        }

        // 로딩 표시
        if (uiState.isLoading) {
            CircularProgressIndicator(
                modifier = Modifier.size(60.dp),
                color = MaterialTheme.colorScheme.primary,
                strokeWidth = 6.dp,
            )
            Spacer(modifier = Modifier.height(16.dp))
        }

        // 자주 가는 곳 프리셋 버튼
        Text(
            text = "자주 가는 곳",
            style = MaterialTheme.typography.headlineMedium,
            color = MaterialTheme.colorScheme.onBackground,
        )

        Spacer(modifier = Modifier.height(16.dp))

        LazyVerticalGrid(
            columns = GridCells.Fixed(3),
            horizontalArrangement = Arrangement.spacedBy(12.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            items(uiState.presets) { preset ->
                PresetButton(
                    preset = preset,
                    onClick = {
                        haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                        viewModel.sendQuery("${preset.name} 가는 버스")
                    },
                )
            }
        }
    }
}

/**
 * 프리셋 버튼 — 자주 가는 곳 바로가기
 * - 최소 120dp x 80dp (손떨림 대응)
 * - 큰 텍스트 + 터치 시 진동
 */
@Composable
private fun PresetButton(
    preset: Preset,
    onClick: () -> Unit,
) {
    Button(
        onClick = onClick,
        modifier = Modifier
            .fillMaxWidth()
            .height(80.dp),
        shape = RoundedCornerShape(16.dp),
        colors = ButtonDefaults.buttonColors(
            containerColor = MaterialTheme.colorScheme.surface,
        ),
    ) {
        Text(
            text = preset.name,
            style = MaterialTheme.typography.headlineMedium,
            color = MaterialTheme.colorScheme.onSurface,
        )
    }
}
```

- [ ] **Step 3: 빌드 확인**

- [ ] **Step 4: 커밋**

```bash
git add busguide-android/app/src/main/java/com/hyeonsu/busguide/presentation/main/
git commit -m "feat(android): 메인 화면 (말하기 버튼 + 프리셋)"
```

---

### Task 17: ResultScreen — 버스 안내 결과 화면

**Files:**
- Create: `presentation/result/ResultScreen.kt`

경로 접두사: `app/src/main/java/com/hyeonsu/busguide/`

- [ ] **Step 1: ResultScreen 구현**

```kotlin
package com.hyeonsu.busguide.presentation.result

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.hyeonsu.busguide.domain.model.BusArrival
import com.hyeonsu.busguide.domain.model.QueryResponse
import com.hyeonsu.busguide.speech.TtsManager

/**
 * 결과 화면
 * - 버스 도착 정보를 크게 표시
 * - TTS로 음성 안내 자동 재생
 * - "다시 물어보기" / "처음으로" 버튼
 */
@Composable
fun ResultScreen(
    response: QueryResponse,
    ttsManager: TtsManager,
    onAskAgain: () -> Unit,
    onGoHome: () -> Unit,
) {
    val haptic = LocalHapticFeedback.current

    // 화면 진입 시 TTS 자동 재생
    LaunchedEffect(response) {
        ttsManager.speak(response.answerTts)
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        // 질문에 대한 답변 텍스트
        Text(
            text = response.answerText,
            style = MaterialTheme.typography.headlineLarge,
            color = MaterialTheme.colorScheme.onBackground,
            textAlign = TextAlign.Center,
        )

        Spacer(modifier = Modifier.height(32.dp))

        // 버스 도착 목록
        LazyColumn(
            verticalArrangement = Arrangement.spacedBy(16.dp),
            modifier = Modifier.weight(1f),
        ) {
            items(response.buses) { bus ->
                BusArrivalCard(bus = bus)
            }

            // 버스가 없는 경우
            if (response.buses.isEmpty()) {
                item {
                    Text(
                        text = "도착 예정 버스가 없습니다",
                        style = MaterialTheme.typography.bodyLarge,
                        color = MaterialTheme.colorScheme.error,
                        textAlign = TextAlign.Center,
                        modifier = Modifier.fillMaxWidth(),
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        // 하단 버튼
        Row(
            horizontalArrangement = Arrangement.spacedBy(16.dp),
            modifier = Modifier.fillMaxWidth(),
        ) {
            // 다시 물어보기 버튼
            Button(
                onClick = {
                    haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                    ttsManager.stop()
                    onAskAgain()
                },
                modifier = Modifier
                    .weight(1f)
                    .height(100.dp),
                shape = RoundedCornerShape(16.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = MaterialTheme.colorScheme.primary,
                ),
            ) {
                Text(
                    text = "다시\n물어보기",
                    style = MaterialTheme.typography.headlineMedium,
                    textAlign = TextAlign.Center,
                )
            }

            // 처음으로 버튼
            Button(
                onClick = {
                    haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                    ttsManager.stop()
                    onGoHome()
                },
                modifier = Modifier
                    .weight(1f)
                    .height(100.dp),
                shape = RoundedCornerShape(16.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = MaterialTheme.colorScheme.surface,
                ),
            ) {
                Text(
                    text = "처음으로",
                    style = MaterialTheme.typography.headlineMedium,
                    color = MaterialTheme.colorScheme.onSurface,
                    textAlign = TextAlign.Center,
                )
            }
        }
    }
}

/**
 * 버스 도착 정보 카드
 * - 버스 번호 (크게) + 도착 시간 + 남은 정거장
 * - 고대비 색상으로 한눈에 파악
 */
@Composable
private fun BusArrivalCard(bus: BusArrival) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface,
        ),
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(24.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            // 버스 번호 (가장 크게)
            Text(
                text = "${bus.busNumber}번",
                style = MaterialTheme.typography.displayLarge,
                color = MaterialTheme.colorScheme.primary,
            )

            Spacer(modifier = Modifier.width(24.dp))

            Column {
                // 도착 시간
                Text(
                    text = "${bus.arrivalMin}분 후 도착",
                    style = MaterialTheme.typography.headlineMedium,
                    color = MaterialTheme.colorScheme.secondary,
                )
                // 남은 정거장
                Text(
                    text = "${bus.remainingStops}정거장 전",
                    style = MaterialTheme.typography.bodyLarge,
                    color = MaterialTheme.colorScheme.onSurface,
                )
            }
        }
    }
}
```

- [ ] **Step 2: 빌드 확인**

- [ ] **Step 3: 커밋**

```bash
git add busguide-android/app/src/main/java/com/hyeonsu/busguide/presentation/result/
git commit -m "feat(android): 결과 화면 (버스 도착 카드 + TTS)"
```

---

### Task 18: 네비게이션 + MainActivity 통합

**Files:**
- Create: `presentation/navigation/NavGraph.kt`
- Modify: `MainActivity.kt`

경로 접두사: `app/src/main/java/com/hyeonsu/busguide/`

- [ ] **Step 1: NavGraph — 화면 라우팅**

```kotlin
package com.hyeonsu.busguide.presentation.navigation

import androidx.compose.runtime.*
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import com.hyeonsu.busguide.presentation.main.MainScreen
import com.hyeonsu.busguide.presentation.main.MainViewModel
import com.hyeonsu.busguide.presentation.result.ResultScreen
import com.hyeonsu.busguide.speech.SpeechManager
import com.hyeonsu.busguide.speech.TtsManager

/**
 * 네비게이션 그래프
 * - main: 메인 화면 (말하기 + 프리셋)
 * - result: 결과 화면 (버스 안내)
 */
@Composable
fun BusGuideNavGraph(
    navController: NavHostController,
    speechManager: SpeechManager,
    ttsManager: TtsManager,
) {
    // ViewModel을 NavGraph 스코프로 공유 (화면 간 상태 유지)
    val mainViewModel: MainViewModel = hiltViewModel()

    NavHost(navController = navController, startDestination = "main") {

        composable("main") {
            MainScreen(
                viewModel = mainViewModel,
                speechManager = speechManager,
                onNavigateToResult = {
                    navController.navigate("result")
                },
            )
        }

        composable("result") {
            val response = mainViewModel.uiState.collectAsState().value.response
            if (response != null) {
                ResultScreen(
                    response = response,
                    ttsManager = ttsManager,
                    onAskAgain = {
                        // 응답 유지한 채 메인으로 (컨텍스트 대화 가능)
                        mainViewModel.clearResponse()
                        navController.popBackStack()
                    },
                    onGoHome = {
                        // 완전 초기화
                        mainViewModel.clearResponse()
                        navController.popBackStack("main", inclusive = false)
                    },
                )
            }
        }
    }
}
```

- [ ] **Step 2: MainActivity 통합**

```kotlin
package com.hyeonsu.busguide

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.navigation.compose.rememberNavController
import com.hyeonsu.busguide.presentation.navigation.BusGuideNavGraph
import com.hyeonsu.busguide.presentation.theme.BusGuideTheme
import com.hyeonsu.busguide.speech.SpeechManager
import com.hyeonsu.busguide.speech.TtsManager
import dagger.hilt.android.AndroidEntryPoint

/**
 * BusGuide 메인 액티비티
 * - 음성 매니저 초기화
 * - 네비게이션 설정
 * - 키오스크 모드 (향후 추가)
 */
@AndroidEntryPoint
class MainActivity : ComponentActivity() {

    private lateinit var speechManager: SpeechManager
    private lateinit var ttsManager: TtsManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // 음성 매니저 초기화
        speechManager = SpeechManager(this)
        ttsManager = TtsManager(this)

        setContent {
            BusGuideTheme {
                val navController = rememberNavController()
                BusGuideNavGraph(
                    navController = navController,
                    speechManager = speechManager,
                    ttsManager = ttsManager,
                )
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        speechManager.destroy()
        ttsManager.destroy()
    }
}
```

- [ ] **Step 3: 빌드 + 에뮬레이터 실행 테스트**

1. FastAPI 서버 실행: `cd server && uvicorn main:app --reload`
2. Android 에뮬레이터에서 앱 실행
3. 메인 화면 표시 확인
4. 프리셋 버튼 터치 시 서버에 질의 전송되는지 확인

- [ ] **Step 4: 커밋**

```bash
git add busguide-android/app/src/main/java/com/hyeonsu/busguide/presentation/navigation/
git add busguide-android/app/src/main/java/com/hyeonsu/busguide/MainActivity.kt
git commit -m "feat(android): 네비게이션 + MainActivity 통합"
```

---

### Task 19: 키오스크 모드

**Files:**
- Create: `kiosk/KioskManager.kt`
- Modify: `MainActivity.kt`

경로 접두사: `app/src/main/java/com/hyeonsu/busguide/`

- [ ] **Step 1: KioskManager 구현**

```kotlin
package com.hyeonsu.busguide.kiosk

import android.app.Activity
import android.app.admin.DevicePolicyManager
import android.content.ComponentName
import android.content.Context
import android.os.Build
import android.view.View
import android.view.WindowInsets
import android.view.WindowInsetsController
import android.view.WindowManager

/**
 * 키오스크 모드 관리자
 * - 상태바/네비게이션바 숨김
 * - 화면 상시 켜짐
 * - 홈 버튼/뒤로가기 차단 (Device Owner 모드 필요)
 * - 관리자 모드에서 해제 가능
 */
class KioskManager(private val activity: Activity) {

    /**
     * 키오스크 모드 활성화
     * - 전체 화면 (상태바/네비바 숨김)
     * - 화면 꺼짐 방지
     */
    fun enable() {
        // 화면 상시 켜짐
        activity.window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)

        // 전체 화면 (상태바/네비게이션바 숨김)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            activity.window.insetsController?.let { controller ->
                controller.hide(WindowInsets.Type.systemBars())
                controller.systemBarsBehavior =
                    WindowInsetsController.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
            }
        } else {
            @Suppress("DEPRECATION")
            activity.window.decorView.systemUiVisibility = (
                View.SYSTEM_UI_FLAG_FULLSCREEN
                    or View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                    or View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                )
        }
    }

    /**
     * 키오스크 모드 해제
     * - 관리자 모드에서 호출
     */
    fun disable() {
        activity.window.clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            activity.window.insetsController?.show(WindowInsets.Type.systemBars())
        } else {
            @Suppress("DEPRECATION")
            activity.window.decorView.systemUiVisibility = View.SYSTEM_UI_FLAG_VISIBLE
        }
    }
}
```

- [ ] **Step 2: MainActivity에 키오스크 모드 적용**

`onCreate`에 추가:

```kotlin
    private lateinit var kioskManager: KioskManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        speechManager = SpeechManager(this)
        ttsManager = TtsManager(this)
        kioskManager = KioskManager(this)

        // 키오스크 모드 활성화
        kioskManager.enable()

        // ... setContent ...
    }
```

- [ ] **Step 3: 빌드 확인**

- [ ] **Step 4: 커밋**

```bash
git add busguide-android/app/src/main/java/com/hyeonsu/busguide/kiosk/
git commit -m "feat(android): 키오스크 모드 (전체화면 + 화면 꺼짐 방지)"
```

---

### Task 20: 발표 자료 준비

**Files:**
- Create: `docs/presentation/BusGuide_발표자료.md`

- [ ] **Step 1: 발표 자료 마크다운 작성**

```markdown
# BusGuide — 어르신 음성 기반 버스 안내 시스템

## 발표 구성
1. 문제 정의 (2분)
2. 솔루션 소개 (3분)
3. 기술 아키텍처 (3분)
4. 핵심 기술 시연 (5분)
5. 차별화 포인트 (2분)

---

## 1. 문제 정의

### 디지털 소외 — 숫자로 보기
- 부산시 70대 이상 인구: 35만 명
- 스마트폰 미사용자: 24만 명 (68%)
- 버스 앱 사용 가능한 70대: 12%

### 현장의 불편함
- 어르신들이 매번 기사님께 "어디 가요?" 물어봄
- 운전 중 기사 방해 → 안전 문제
- 기존 BIS 전광판: 노선번호만 표시, 목적지 안내 없음

---

## 2. 솔루션

### 한 문장 요약
> 정류장에 설치된 태블릿에 **"명지병원 가는 버스 있어요?"** 라고 말하면
> **"58번 버스가 5분 후에 옵니다"** 라고 알려주는 시스템

### 핵심 기능
1. 음성으로 질문 → 음성 + 화면으로 답변
2. 연속 대화 가능 ("거기서 해운대 가려면?")
3. 부산 사투리 인식 ("어데 카는 버스예요?")
4. 터치 백업 (음성 실패 시 버튼으로)

---

## 3. 기술 아키텍처

```
태블릿 (Android)          FastAPI 서버           TAGO API
┌──────────┐         ┌──────────────┐      ┌──────────┐
│ STT 음성  │───────→│ 사투리 변환   │─────→│ 실시간   │
│ TTS 출력  │←───────│ 의도 파악     │←─────│ 도착정보 │
│ 시니어 UI │         │ 유사어 매칭   │      │ 노선정보 │
│ 키오스크  │         │ 컨텍스트 관리 │      │ 정류장   │
└──────────┘         └──────────────┘      └──────────┘
```

### 기술 스택
- **Android**: Kotlin + Jetpack Compose + Hilt
- **Server**: FastAPI + Kiwi(한국어 NLP)
- **API**: 국토교통부 TAGO 전국 버스정보

---

## 4. 핵심 기술 — 시연 포인트

### 4-1. 사투리 변환 엔진
- "명지병원 **카는** 버스 **있나예**?"
- → "명지병원 **가는** 버스 **있나요**?"
- JSON 기반 매핑 — 코드 수정 없이 확장 가능

### 4-2. 의도 분류
- "가는 버스" → 노선 검색
- "몇 분 후" → 도착 시간
- "갈아타" → 환승 안내

### 4-3. 컨텍스트 대화
- "58번 어디 가요?" → "명지병원 갑니다"
- "몇 분 후에 와요?" → (58번 기억) "5분 후 도착"
- "**거기서** 해운대 가려면?" → (명지병원 기억) "181번으로 갈아타세요"

### 4-4. 시니어 UX
- 48sp 폰트 (일반 대비 3배)
- 120dp 버튼 (손떨림 대응)
- 고대비 다크 테마 (검정 + 노란색)
- 음성 + 시각 + 진동 삼중 피드백

---

## 5. 차별화

| | 카카오맵 | BIS 전광판 | **BusGuide** |
|---|---|---|---|
| 타겟 | 젊은 층 | 모든 사람 | **디지털 약자** |
| 인터페이스 | 터치 | 시각만 | **음성 + 시각** |
| 대화형 | X | X | **O** |
| 접근성 | 앱 설치 필요 | 읽기 필요 | **말만 하면 됨** |
| 설치 비용 | - | 300~500만원 | **14만원** |

---

## 향후 계획
- 다국어 지원 (외국인 관광객)
- 지자체 협력 → 실제 정류장 설치
- 날씨/복지관 정보 통합
```

- [ ] **Step 2: 커밋**

```bash
git add docs/presentation/
git commit -m "docs: 발표 자료 마크다운 작성"
```

---

## 전체 태스크 요약

| # | 파트 | 내용 | 예상 시간 |
|---|------|------|-----------|
| 1 | Server | 프로젝트 초기 설정 | 15분 |
| 2 | Server | Pydantic 데이터 모델 | 15분 |
| 3 | Server | 사투리 변환 NLP | 20분 |
| 4 | Server | 의도 분류 NLP | 20분 |
| 5 | Server | 유사어 매칭 + 목적지 추출 | 20분 |
| 6 | Server | 컨텍스트 서비스 | 20분 |
| 7 | Server | TAGO 버스 API 연동 | 30분 |
| 8 | Server | 질의 라우터 (전체 통합) | 30분 |
| 9 | Server | 프리셋 데이터 | 10분 |
| 10 | Android | 프로젝트 생성 | 20분 |
| 11 | Android | 도메인 모델 + API 인터페이스 | 15분 |
| 12 | Android | Hilt DI 모듈 | 15분 |
| 13 | Android | 시니어 특화 테마 | 15분 |
| 14 | Android | STT/TTS 매니저 | 20분 |
| 15 | Android | Repository 레이어 | 15분 |
| 16 | Android | 메인 화면 | 30분 |
| 17 | Android | 결과 화면 | 25분 |
| 18 | Android | 네비게이션 + Activity 통합 | 20분 |
| 19 | Android | 키오스크 모드 | 15분 |
| 20 | Docs | 발표 자료 | 20분 |
