# LLD: Flows (시퀀스 다이어그램)

**Version**: 1.0.0 | **Master**: [0001-lld-wsoptv-platform.md](./0001-lld-wsoptv-platform.md)

---

## 1. Video Playback

콘텐츠 선택 → HLS 스트리밍 → 핸드 감지.

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Web as Frontend
    participant API as Backend
    participant HLS as HLS Service
    participant NAS
    participant DB

    %% 콘텐츠 로드
    User->>Web: 콘텐츠 클릭
    Web->>API: GET /contents/{id}
    API->>DB: 콘텐츠 + 핸드 조회
    DB-->>API: Content, Hands[]
    API-->>Web: { content, hands, streamUrl }

    %% 스트림 요청
    Web->>API: GET /stream/{id}/master.m3u8

    alt HLS 캐시 있음
        API-->>Web: HLS Manifest (캐시)
    else HLS 캐시 없음
        API->>HLS: get_stream_url()
        HLS->>NAS: 원본 파일 읽기
        NAS-->>HLS: MP4 스트림
        HLS->>HLS: FFmpeg 트랜스코딩
        HLS-->>API: master.m3u8
        API-->>Web: HLS Manifest
    end

    %% 재생 시작
    Web->>Web: VideoPlayer 초기화
    Web->>Web: buildTimeline(hands)

    %% 재생 루프
    loop 재생 중 (매 프레임)
        Web->>Web: timeupdate 이벤트
        Web->>Web: findCurrentSegment()

        alt 핸드 구간 진입
            Web->>Web: dispatch('handenter')
            Web->>Web: 핸드 정보 표시
        else 비핸드 구간 진입
            Web->>Web: dispatch('nonhandsegment')
            Web->>Web: SkipButtons 표시
        end
    end

    %% 진행률 저장
    Web->>API: POST /progress (30초마다)
    API->>DB: UPSERT watch_progress
```

---

## 2. Auth (회원가입/승인)

### 2.1 회원가입

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Web as Frontend
    participant API as Backend
    participant DB

    User->>Web: 회원가입 폼 작성
    Web->>Web: 클라이언트 유효성 검사
    Web->>API: POST /auth/register

    API->>DB: SELECT username 중복 체크
    DB-->>API: 결과

    alt 아이디 중복
        API-->>Web: 409 AUTH_USERNAME_EXISTS
        Web-->>User: "이미 존재하는 아이디입니다"
    else 정상
        API->>API: 비밀번호 해시 (bcrypt)
        API->>DB: INSERT user (status='pending')
        DB-->>API: User 생성됨
        API-->>Web: 201 { user, message }
        Web-->>User: "가입 완료. 승인을 기다려주세요"
    end
```

### 2.2 관리자 승인

```mermaid
sequenceDiagram
    autonumber
    actor Admin
    participant Web as Frontend
    participant API as Backend
    participant DB

    Admin->>Web: Admin 대시보드 접근
    Web->>API: GET /admin/users/pending
    API->>DB: SELECT * WHERE status='pending'
    DB-->>API: 대기 목록
    API-->>Web: [{ id, username, createdAt }]

    Admin->>Web: 사용자 "승인" 클릭
    Web->>API: POST /admin/users/{id}/approve

    API->>DB: UPDATE status='approved', approved_by, approved_at
    DB-->>API: 업데이트 완료
    API-->>Web: { user: { status: 'approved' } }
    Web-->>Admin: "승인 완료"

    Note over User: 사용자가 재로그인 시
    User->>Web: 로그인
    Web->>API: POST /auth/login
    API-->>Web: { status: 'approved', token }
    Web-->>User: 메인 화면 접근 허용
```

### 2.3 로그인

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Web as Frontend
    participant API as Backend
    participant DB

    User->>Web: 로그인 폼 제출
    Web->>API: POST /auth/login

    API->>DB: SELECT user WHERE username
    DB-->>API: User (with password_hash)

    alt 사용자 없음 or 비밀번호 불일치
        API-->>Web: 401 AUTH_INVALID_CREDENTIALS
        Web-->>User: "아이디 또는 비밀번호가 틀렸습니다"
    else 승인 대기 중
        API-->>Web: 403 AUTH_PENDING_APPROVAL
        Web-->>User: "관리자 승인을 기다려주세요"
    else 가입 거절됨
        API-->>Web: 403 AUTH_REJECTED
        Web-->>User: "가입이 거절되었습니다"
    else 정상
        API->>API: JWT 토큰 생성
        API->>DB: INSERT session / UPDATE last_login_at
        API-->>Web: 200 { user, token, expiresAt }
        Web->>Web: localStorage.setItem('token')
        Web-->>User: 메인 화면으로 이동
    end
```

---

## 3. Search

검색어 입력 → MeiliSearch → 결과 표시.

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Web as Frontend
    participant API as Backend
    participant Meili as MeiliSearch
    participant DB

    User->>Web: 검색어 입력 "Phil Ivey"
    Web->>Web: 디바운스 (300ms)

    %% 자동완성
    Web->>API: GET /search/suggest?q=Phil
    API->>Meili: autocomplete("Phil")
    Meili-->>API: ["Phil Ivey", "Phil Hellmuth"]
    API-->>Web: { suggestions }
    Web-->>User: 자동완성 드롭다운

    %% 검색 실행
    User->>Web: Enter 또는 제안 선택
    Web->>API: GET /search?q=Phil+Ivey&limit=20

    API->>Meili: search("Phil Ivey", {})
    Meili-->>API: { hits, facets, total }

    API->>DB: 썸네일 등 추가 정보
    DB-->>API: 보강된 데이터

    API-->>Web: SearchResult
    Web-->>User: 검색 결과 + 패싯 필터

    %% 필터 적용
    User->>Web: 필터 선택 (WSOP, S등급)
    Web->>API: GET /search?q=Phil+Ivey&catalogId=wsop&handGrade=S

    API->>Meili: search with filters
    Meili-->>API: 필터링된 결과
    API-->>Web: 업데이트된 SearchResult
    Web-->>User: 필터링된 결과
```

---

## 4. Hand Skip

비핸드 구간 진입 → 스킵 버튼 표시 → 다음 핸드로 이동.

```mermaid
sequenceDiagram
    autonumber
    participant Player as VideoPlayer
    participant Timeline as HandTimeline
    participant Skip as SkipButtons
    participant Hands as @wsoptv/hands

    Note over Player: 재생 중...

    Player->>Hands: findCurrentSegment(currentTime)
    Hands-->>Player: { type: 'shuffle', ... }

    Player->>Player: dispatch('nonhandsegment')
    Player->>Skip: visible = true

    Skip->>Skip: 5초 타이머 시작

    alt 사용자가 "핸드 모아보기" 클릭
        Skip->>Player: dispatch('skiptohand')
        Player->>Hands: findNextHand(currentTime)
        Hands-->>Player: nextHand
        Player->>Player: seek(nextHand.startSec)
        Player->>Skip: visible = false
    else 사용자가 "하이라이트만 보기" 클릭
        Skip->>Player: dispatch('highlightsonly')
        Player->>Hands: filterHighlights(hands, 'A')
        Hands-->>Player: highlightHands[]
        Player->>Player: 하이라이트 모드 활성화
        Player->>Player: seek(firstHighlight.startSec)
        Skip->>Skip: visible = false
    else 5초 경과
        Skip->>Skip: visible = false (자동 숨김)
    end

    Note over Player: 다음 핸드 구간 진입
    Player->>Hands: findCurrentSegment(currentTime)
    Hands-->>Player: { type: 'hand', hand: {...} }
    Player->>Player: dispatch('handenter', hand)
    Player->>Timeline: 현재 핸드 하이라이트
```

---

## 5. Watch Progress Sync

시청 진행률 저장 및 이어보기.

### 5.1 진행률 저장

```mermaid
sequenceDiagram
    autonumber
    participant Player as VideoPlayer
    participant Store as progressStore
    participant API as Backend
    participant DB

    loop 30초마다
        Player->>Store: updateProgress(contentId, currentTime, duration)
        Store->>Store: 디바운스 체크

        alt 마지막 저장 후 30초 이상
            Store->>API: POST /progress
            Note right of API: { contentId, progressSec, durationSec }
            API->>DB: UPSERT watch_progress
            DB-->>API: 저장 완료
            API-->>Store: { completed: false/true }
        end
    end

    Note over Player: 재생 종료 (90% 이상)
    Player->>Store: markCompleted(contentId)
    Store->>API: POST /progress (completed: true)
    API->>DB: UPDATE completed = true
```

### 5.2 이어보기

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Web as Frontend
    participant API as Backend
    participant DB
    participant Player as VideoPlayer

    User->>Web: 콘텐츠 클릭
    Web->>API: GET /contents/{id}
    API->>DB: SELECT content + watch_progress
    DB-->>API: Content + Progress

    alt 진행률 있음 (미완료)
        API-->>Web: { content, watchProgress: { progressSec: 1800 } }
        Web->>Web: 이어보기 모달 표시

        alt "이어서 보기" 선택
            Web->>Player: startTime = 1800
        else "처음부터" 선택
            Web->>Player: startTime = 0
        end
    else 진행률 없음 or 완료됨
        API-->>Web: { content, watchProgress: null }
        Web->>Player: startTime = 0
    end

    Player->>Player: 재생 시작
```

---

## 6. Streaming (HLS 생성)

### 6.1 온디맨드 트랜스코딩

```mermaid
sequenceDiagram
    autonumber
    participant API as Backend
    participant HLS as HLSService
    participant FFmpeg
    participant NAS
    participant FS as FileSystem

    API->>HLS: get_stream_url(fileId, nasPath)
    HLS->>FS: manifest 존재 확인

    alt 캐시 있음
        FS-->>HLS: master.m3u8 존재
        HLS-->>API: "/hls/{fileId}/master.m3u8"
    else 캐시 없음
        FS-->>HLS: 없음
        HLS->>HLS: 비동기 트랜스코딩 시작
        HLS-->>API: StreamNotReadyError

        API-->>Client: 503 STREAM_NOT_READY

        par 백그라운드 트랜스코딩
            HLS->>NAS: 원본 파일 읽기
            NAS-->>FFmpeg: MP4 스트림

            FFmpeg->>FFmpeg: 멀티비트레이트 인코딩
            Note right of FFmpeg: 720p (2.5M) + 480p (1M) + 360p (500k)

            FFmpeg->>FS: HLS 세그먼트 저장
            Note right of FS: stream_0_001.ts, stream_0_002.ts...

            FFmpeg->>FS: master.m3u8 생성
        end

        Note over Client: 클라이언트 재시도 (3초 후)
        Client->>API: GET /stream/{id}/master.m3u8
        API->>HLS: get_stream_url()
        HLS->>FS: manifest 확인
        FS-->>HLS: 존재
        HLS-->>API: URL
        API-->>Client: 200 HLS Manifest
    end
```

---

## 7. Error Handling

### 7.1 스트리밍 에러 복구

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Player as VideoPlayer
    participant API as Backend
    participant HLS as HLSService

    Player->>API: GET /stream/{id}/master.m3u8
    API->>HLS: get_stream_url()

    alt NAS 접근 실패
        HLS-->>API: StreamSourceError
        API-->>Player: 500 STREAM_SOURCE_ERROR
        Player-->>User: "영상을 불러올 수 없습니다"
        Player->>Player: 에러 화면 표시

    else 트랜스코딩 중
        HLS-->>API: StreamNotReadyError
        API-->>Player: 503 STREAM_NOT_READY + Retry-After: 5

        Player->>Player: 로딩 표시 + "영상 준비 중..."

        loop 최대 3회 재시도
            Player->>Player: 5초 대기
            Player->>API: GET /stream/{id}/master.m3u8

            alt 준비 완료
                API-->>Player: 200 HLS Manifest
                Player->>Player: 재생 시작
            else 아직 준비 중
                API-->>Player: 503
            end
        end

        alt 3회 실패
            Player-->>User: "영상 준비에 실패했습니다. 잠시 후 다시 시도해주세요."
        end
    end
```

---

## 변경 이력

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-09 | 초기 플로우 다이어그램 |
