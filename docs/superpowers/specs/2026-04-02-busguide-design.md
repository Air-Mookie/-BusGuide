# BusGuide - 어르신 음성 기반 버스 안내 시스템 설계서

## 1. 개요

### 프로젝트명
BusGuide (패키지: `com.hyeonsu.busguide`)

### 목적
디지털 소외 계층(70대 이상)을 위한 음성 기반 버스 안내 태블릿 시스템.
음성으로 질문하면 실시간 버스 도착 정보를 안내해주는 정류장 설치형 키오스크.

### 타겟 사용자
- 스마트폰 미사용 또는 앱 사용이 어려운 70대 이상
- 부산시 기준 약 24만 명 (70대 이상 스마트폰 미사용자 68%)

### 핵심 차별점
1. **대화형 AI** — 한 번의 질문으로 버스 안내 완료
2. **컨텍스트 기억** — 연속 대화에서 이전 질문 맥락 유지
3. **시니어 특화 UX** — 48pt 폰트, 5cm 버튼, 고대비 색상, 삼중 피드백
4. **사투리 + 유사어 처리** — 직접 구현한 NLP 엔진
5. **멀티모달** — 음성 실패 시 터치로 자동 전환

---

## 2. 아키텍처

### 심플 클라이언트 패턴

```
Android (UI + STT + TTS)  →  FastAPI (모든 로직)  →  TAGO API
      얇은 클라이언트              두꺼운 서버          공공 버스 데이터
```

- 앱: 음성 입출력 + 화면 표시만 담당
- 서버: NLP, 사투리 변환, 노선 검색, 컨텍스트 관리 전부 처리
- 장점: 서버만 수정하면 앱 업데이트 없이 개선 가능

### 프로젝트 구조

```
busguide/
├── app/                              ← Android 앱
│   └── src/main/java/com/hyeonsu/busguide/
│       ├── di/                       ← Hilt DI 모듈
│       ├── data/
│       │   ├── remote/               ← FastAPI 통신 (Retrofit)
│       │   └── local/                ← 즐겨찾기, 설정 (DataStore)
│       ├── domain/
│       │   ├── model/                ← BusArrival, BusRoute, Station 등
│       │   ├── repository/           ← Repository 인터페이스
│       │   └── usecase/              ← 음성질의, 노선검색 등
│       ├── presentation/
│       │   ├── main/                 ← 메인 화면 (큰 말하기 버튼)
│       │   ├── result/               ← 버스 안내 결과 화면
│       │   ├── conversation/         ← 대화 히스토리 화면
│       │   └── theme/                ← 시니어 특화 테마
│       ├── speech/                   ← STT/TTS 래퍼
│       └── kiosk/                    ← 키오스크 모드 관리
│
├── server/                           ← FastAPI 백엔드
│   ├── main.py                       ← 엔트리포인트
│   ├── routers/
│   │   ├── query.py                  ← 음성 질의 처리 API
│   │   └── bus.py                    ← 버스 정보 조회 API
│   ├── services/
│   │   ├── nlp_service.py            ← 의도 파악 + 사투리 변환
│   │   ├── bus_service.py            ← TAGO API 연동
│   │   └── context_service.py        ← 대화 컨텍스트 관리
│   ├── data/
│   │   ├── dialect_map.json          ← 사투리 매핑 데이터
│   │   ├── synonyms.json             ← 유사어 매핑 데이터
│   │   ├── intent_rules.json         ← 의도 분류 키워드 규칙
│   │   └── presets.json              ← 자주 가는 곳 프리셋
│   ├── .env                          ← API 키 (git 제외)
│   └── requirements.txt
│
└── docs/                             ← 설계 문서, 발표 자료
```

---

## 3. Android 앱 설계

### 화면 구성

#### MainScreen — 메인 화면
- 10cm 원형 "말하기" 버튼 (중앙 배치)
- "어디 가시려고요?" 안내 문구
- 자주 가는 곳 프리셋 버튼 (설정 파일에서 로드, 하드코딩 X)
- GPS 기반 현재 정류장 자동 표시

#### ResultScreen — 결과 화면
- 도착 버스 목록 (번호, 도착 시간, 남은 정거장)
- TTS 자동 안내
- "다시 물어보기" / "처음으로" 버튼

#### ConversationScreen — 연속 대화 화면
- 대화 히스토리 표시 (나 / 시스템)
- "더 물어보기" 버튼
- 컨텍스트 유지 (이전 대화 기억)

### 시니어 특화 UX

| 항목 | 설정값 | 이유 |
|------|--------|------|
| 폰트 크기 | 32~48sp | 노안 고려 |
| 버튼 최소 크기 | 120dp | 손떨림 대응 |
| 색상 | 검정 배경 + 노란 텍스트 | 고대비, 시력 약해도 가독성 |
| 피드백 | 음성 + 시각 + 진동 | 삼중 확인 |
| 터치 영역 | 넓은 패딩 | 오터치 방지 |

### 핵심 컴포넌트

- **SpeechManager**: Android `SpeechRecognizer` 래핑, 인식 시작/중지/결과 콜백
- **TtsManager**: `TextToSpeech` 래핑, 한국어 음성 출력
- **KioskManager**: `LOCK_TASK` 모드, 상태바/네비바 숨김, 홈버튼 차단
- **LocationManager**: GPS로 현재 가장 가까운 정류장 자동 감지

### API 인터페이스 (Retrofit)

```kotlin
interface BusGuideApi {
    @POST("query")
    suspend fun sendQuery(@Body request: QueryRequest): QueryResponse

    @GET("bus/arrivals/{stationId}")
    suspend fun getArrivals(@Path("stationId") stationId: String): List<BusArrival>

    @GET("bus/nearest-station")
    suspend fun getNearestStation(
        @Query("lat") lat: Double,
        @Query("lng") lng: Double
    ): Station
}
```

---

## 4. FastAPI 서버 설계

### API 엔드포인트

| Method | Path | 설명 |
|--------|------|------|
| `POST` | `/query` | 음성 텍스트 → NLP 처리 → 버스 안내 반환 |
| `GET` | `/bus/arrivals/{station_id}` | 특정 정류장 실시간 도착 정보 |
| `GET` | `/bus/nearest-station` | GPS 좌표 → 가장 가까운 정류장 |
| `GET` | `/bus/routes` | 목적지까지 가는 노선 검색 |
| `GET` | `/health` | 서버 상태 체크 |

### `/query` 처리 파이프라인

```
입력: "명지병원 카는 버스 있나예?"
  ↓
① 사투리 변환: "카는" → "가는", "있나예" → "있나요"
  ↓
② 의도 파악: intent = "노선_검색", destination = "명지병원"
  ↓
③ 유사어 매칭: "명지병원" → station_id 매핑
  ↓
④ TAGO API 호출: 해당 노선 + 실시간 도착 정보
  ↓
⑤ 컨텍스트 저장: session에 "명지병원", "58번" 기억
  ↓
⑥ 응답 생성: 화면 텍스트 + TTS 텍스트 + 버스 목록
```

### NLP 서비스

#### 사투리 변환
- `dialect_map.json`에서 매핑 로드
- 정규식 기반 치환 (단어 경계 인식)
- 예: "어데" → "어디", "카는" → "가는"

#### 의도 분류
- `intent_rules.json`에서 키워드 규칙 로드
- 4가지 의도: 노선_검색, 도착_시간, 환승_안내, 정류장_확인
- 키워드 매칭 우선, 형태소 분석(Kiwi) 보조

#### 유사어 매칭
- `synonyms.json`에서 매핑 로드
- 부분 매칭 + 편집 거리(Levenshtein) 활용
- "명지" → "명지병원", "바다" → "해운대"

#### 컨텍스트 관리
- 세션 ID별 인메모리 저장
- 최근 목적지, 버스 번호, 정류장 기억
- TTL 5분 (자동 만료)
- "거기", "그거" 같은 대명사 해석에 활용

### TAGO API 연동

| API | 용도 |
|-----|------|
| 국토교통부 버스도착정보 | 실시간 도착 시간 |
| 국토교통부 버스노선정보 | 노선 경로, 경유 정류장 |
| 국토교통부 버스정류소정보 | 정류장 위치, ID 매핑 |

- API 키는 `.env`에 저장
- 응답 캐싱: 정류장/노선 정보 1시간, 도착 정보 30초

---

## 5. 데이터 모델

### Android (Kotlin)

```kotlin
data class Station(
    val id: String,
    val name: String,
    val lat: Double,
    val lng: Double
)

data class BusArrival(
    val busNumber: String,
    val arrivalMin: Int,
    val remainingStops: Int,
    val destination: String
)

data class QueryRequest(
    val text: String,
    val stationId: String,
    val sessionId: String
)

data class QueryResponse(
    val answerText: String,
    val answerTts: String,
    val buses: List<BusArrival>,
    val intent: String,
    val destination: String?
)
```

### FastAPI (Pydantic)

```python
class QueryRequest(BaseModel):
    text: str
    station_id: str
    session_id: str

class BusArrival(BaseModel):
    bus_number: str
    arrival_min: int
    remaining_stops: int
    destination: str

class QueryResponse(BaseModel):
    answer_text: str
    answer_tts: str
    buses: list[BusArrival]
    intent: str
    destination: str | None
```

---

## 6. 기술 스택

### Android

| 역할 | 라이브러리 |
|------|-----------|
| UI | Jetpack Compose |
| DI | Hilt |
| 네트워크 | Retrofit + OkHttp |
| 직렬화 | Kotlinx Serialization |
| 위치 | Google Play Location |
| STT | Android SpeechRecognizer |
| TTS | Android TextToSpeech |
| 로컬 저장 | DataStore |
| 키오스크 | DevicePolicyManager (LOCK_TASK) |

### FastAPI 서버

| 역할 | 라이브러리 |
|------|-----------|
| 프레임워크 | FastAPI + Uvicorn |
| HTTP 클라이언트 | httpx |
| 형태소 분석 | Kiwi |
| 캐싱 | 인메모리 dict |
| 환경변수 | python-dotenv |
| 배포 | Railway (무료 티어) |

---

## 7. 추가 기능

### 관리자 모드
- 화면 우측 하단 5번 탭 → 비밀번호 입력
- 즐겨찾기 정류장 편집
- 사투리/유사어 사전 관리
- 사용 통계 확인
- 키오스크 모드 해제

### 오프라인 폴백
- 인터넷 끊김 감지 시 안내 메시지
- 캐싱된 노선표 표시 (마지막 동기화 데이터)
- DataStore에 주요 노선 정보 캐시

### 사용 로그 수집
- 질의 텍스트, 인식 성공/실패율
- 자주 검색하는 목적지 TOP 10
- 시간대별 사용 패턴
- 서버에 비동기 전송, 관리자 모드에서 확인 가능

### 음성 인식 실패 자동 전환
- 3초 타임아웃 → TTS "화면을 눌러주세요"
- 자주 가는 곳 버튼 화면으로 자동 전환
- 멀티모달 백업 (음성 → 터치)

---

## 8. 설정 파일 (하드코딩 방지)

모든 매핑 데이터를 JSON 파일로 분리:

| 파일 | 용도 |
|------|------|
| `dialect_map.json` | 사투리 → 표준어 변환 |
| `synonyms.json` | 장소 유사어 매핑 |
| `intent_rules.json` | 의도 분류 키워드 규칙 |
| `presets.json` | 자주 가는 곳 프리셋 (지역별) |
| `.env` | API 키, 서버 URL 등 |

→ 코드 수정 없이 데이터만 추가/수정 가능

---

## 9. 범위 밖 (향후 확장)

캡스톤 범위에서 제외하되, 발표 시 "향후 계획"으로 언급:

- 다국어 지원 (영어, 중국어, 일본어)
- 태양광 전원
- 외장 마이크
- 시각장애인 점자 버튼
- 헬스케어 연동
- AI 친구 모드
- 긴급 상황 112 신고
- 날씨 정보 (시간 남으면 추가 가능)
