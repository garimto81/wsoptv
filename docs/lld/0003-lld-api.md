# LLD: API Specification

**Version**: 2.0.0 | **Master**: [0001-lld-wsoptv-platform.md](./0001-lld-wsoptv-platform.md)

---

## Base URL

```
/api/v1
```

## 공통 응답 형식

### ⚠️ 중요: 목록 API 응답 구조

**모든 목록 API**는 아래 구조를 따릅니다 (배열을 직접 반환하지 않음):

```typescript
// ✅ 올바른 응답 (목록)
{
  "items": T[],    // 항상 배열
  "total": number  // 전체 개수
}

// ❌ 잘못된 기대 (배열 직접 반환)
T[]  // 이 형식은 사용하지 않음!
```

### Frontend 파싱 예시

```typescript
// ✅ 올바른 파싱
const response = await api.get<{ items: Catalog[]; total: number }>('/catalogs');
const catalogs = response.items;  // 배열 추출

// ❌ 잘못된 파싱 (런타임 에러 발생)
const catalogs = await api.get<Catalog[]>('/catalogs');  // undefined!
```

### 단일 항목 응답

```typescript
// 성공
{ "data": T, "meta": { "timestamp": string, "requestId": string } }

// 에러
{ "error": { "code": string, "message": string, "details"?: object }, "timestamp": string, "path": string }
```

---

## 1. Auth

### POST /auth/register

회원가입 (pending 상태로 생성)

**Request**
```json
{
  "username": "string (4-50자, 영문/숫자/_)",
  "password": "string (8자 이상, 대소문자+숫자)",
  "passwordConfirm": "string",
  "displayName": "string? (2-100자)"
}
```

**Response 201**
```json
{
  "data": {
    "user": {
      "id": 1,
      "username": "pokerking",
      "displayName": "Poker King",
      "status": "pending",
      "createdAt": "2025-12-09T10:00:00Z"
    },
    "message": "가입이 완료되었습니다. 관리자 승인을 기다려주세요."
  }
}
```

**Errors**
| Code | HTTP | 설명 |
|------|------|------|
| `AUTH_USERNAME_EXISTS` | 409 | 이미 존재하는 아이디 |
| `AUTH_PASSWORD_MISMATCH` | 400 | 비밀번호 불일치 |
| `VALIDATION_ERROR` | 400 | 입력값 검증 실패 |

---

### POST /auth/login

로그인 - httpOnly 쿠키 기반 (#1)

**Request**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response 200**
```json
{
  "data": {
    "user": {
      "id": 1,
      "username": "pokerking",
      "displayName": "Poker King",
      "role": "user",
      "status": "approved"
    },
    "expiresAt": "2025-12-16T10:00:00Z"
  }
}
```

**Response Headers** (토큰은 쿠키로 전달 #1)
```
Set-Cookie: access_token=eyJhbGc...; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=900
Set-Cookie: refresh_token=eyJhbGc...; HttpOnly; Secure; SameSite=Strict; Path=/api/v1/auth; Max-Age=604800
```

---

### POST /auth/refresh

Access Token 갱신 (#12)

**Request**: 없음 (Refresh Token은 httpOnly 쿠키)

**Response 200**
```json
{
  "data": {
    "expiresAt": "2025-12-09T12:15:00Z"
  }
}
```

**Response Headers**
```
Set-Cookie: access_token=eyJuZXc...; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=900
```

**Errors**
| Code | HTTP | 설명 |
|------|------|------|
| `AUTH_TOKEN_EXPIRED` | 401 | Refresh Token 만료 |
| `AUTH_TOKEN_INVALID` | 401 | 유효하지 않은 토큰 |

---

### POST /auth/logout

로그아웃 - 토큰 무효화 (#24)

**Response 200**
```json
{
  "data": {
    "message": "로그아웃되었습니다"
  }
}
```

**동작**
1. Access Token을 Blacklist에 추가 (Redis, TTL = 토큰 잔여 시간)
2. Refresh Token 무효화
3. 쿠키 삭제

**Response Headers**
```
Set-Cookie: access_token=; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=0
Set-Cookie: refresh_token=; HttpOnly; Secure; SameSite=Strict; Path=/api/v1/auth; Max-Age=0
```

**Errors**
| Code | HTTP | 설명 |
|------|------|------|
| `AUTH_INVALID_CREDENTIALS` | 401 | 아이디/비밀번호 불일치 |
| `AUTH_PENDING_APPROVAL` | 403 | 승인 대기 중 |
| `AUTH_REJECTED` | 403 | 가입 거절됨 |
| `AUTH_SUSPENDED` | 403 | 계정 정지됨 |

---

### GET /auth/me

현재 사용자 정보 (🔒 인증 필요)

**Response 200**
```json
{
  "data": {
    "id": 1,
    "username": "pokerking",
    "displayName": "Poker King",
    "avatarUrl": null,
    "role": "user",
    "status": "approved",
    "createdAt": "2025-12-09T10:00:00Z",
    "lastLoginAt": "2025-12-09T12:00:00Z"
  }
}
```

---

## 2. Catalogs

### GET /catalogs

카탈로그 목록 (🔒 인증 필요)

**Response 200**
```json
{
  "data": {
    "items": [
      {
        "id": "wsop",
        "name": "WSOP",
        "displayTitle": "World Series of Poker",
        "description": "세계 최대 포커 대회",
        "thumbnailUrl": "/images/catalogs/wsop.jpg",
        "seriesCount": 15,
        "contentCount": 450
      }
    ],
    "total": 6
  }
}
```

---

### GET /catalogs/{id}

카탈로그 상세 (🔒 인증 필요)

**Response 200**
```json
{
  "data": {
    "id": "wsop",
    "name": "WSOP",
    "displayTitle": "World Series of Poker",
    "description": "세계 최대 포커 대회",
    "thumbnailUrl": "/images/catalogs/wsop.jpg",
    "series": [
      {
        "id": 1,
        "title": "WSOP 2024",
        "year": 2024,
        "episodeCount": 30,
        "thumbnailUrl": "/images/series/wsop-2024.jpg"
      }
    ]
  }
}
```

---

## 3. Contents

### GET /series/{id}

시리즈 상세 + 콘텐츠 목록 (🔒 인증 필요)

**Query Parameters**
| Param | Type | Default | 설명 |
|-------|------|---------|------|
| page | int | 1 | 페이지 |
| limit | int | 20 | 개수 (max: 100) |

**Response 200**
```json
{
  "data": {
    "id": 1,
    "catalogId": "wsop",
    "title": "WSOP 2024",
    "year": 2024,
    "seasonNum": null,
    "description": "2024년 WSOP 메인 이벤트",
    "episodeCount": 30,
    "thumbnailUrl": "/images/series/wsop-2024.jpg",
    "contents": {
      "items": [
        {
          "id": 101,
          "episodeNum": 1,
          "title": "Day 1A - Opening",
          "durationSec": 7200,
          "thumbnailUrl": "/images/contents/101.jpg",
          "viewCount": 1234,
          "handsCount": 45
        }
      ],
      "total": 30,
      "page": 1,
      "limit": 20,
      "hasNext": true
    }
  }
}
```

---

### GET /contents/{id}

콘텐츠 상세 (🔒 인증 필요)

**Response 200**
```json
{
  "data": {
    "id": 101,
    "title": "WSOP 2024 - Day 1A Opening",
    "description": "2024 WSOP 메인 이벤트 Day 1A",
    "durationSec": 7200,
    "viewCount": 1234,
    "thumbnailUrl": "/images/contents/101.jpg",
    "series": {
      "id": 1,
      "title": "WSOP 2024",
      "catalogId": "wsop"
    },
    "players": [
      { "id": 1, "name": "Phil Ivey", "displayName": "Phil Ivey" },
      { "id": 2, "name": "Daniel Negreanu", "displayName": "Daniel Negreanu" }
    ],
    "tags": ["main-event", "day-1"],
    "handsCount": 45,
    "handGradeSummary": { "S": 3, "A": 12, "B": 20, "C": 10 },
    "streamUrl": "/api/v1/stream/101/master.m3u8",
    "watchProgress": {
      "progressSec": 1800,
      "completed": false
    }
  }
}
```

---

### GET /contents/{id}/hands

콘텐츠 핸드 목록 (🔒 인증 필요)

**Query Parameters**
| Param | Type | Default | 설명 |
|-------|------|---------|------|
| grade | S/A/B/C | - | 등급 필터 |

**Response 200**
```json
{
  "data": {
    "hands": [
      {
        "id": 1001,
        "handNumber": 1,
        "startSec": 120,
        "endSec": 240,
        "players": ["Phil Ivey", "Daniel Negreanu"],
        "winner": "Phil Ivey",
        "potSizeBb": 150,
        "grade": "S",
        "isAllIn": true,
        "isShowdown": true,
        "tags": ["bluff", "hero-call"]
      }
    ],
    "total": 45
  }
}
```

---

### GET /contents/{id}/highlights

하이라이트 핸드 (S, A 등급) (🔒 인증 필요)

**Query Parameters**
| Param | Type | Default | 설명 |
|-------|------|---------|------|
| minGrade | S/A | A | 최소 등급 |

**Response 200**
```json
{
  "data": {
    "hands": [
      {
        "id": 1001,
        "startSec": 120,
        "endSec": 240,
        "grade": "S",
        "players": ["Phil Ivey", "Daniel Negreanu"],
        "tags": ["bluff"]
      }
    ],
    "total": 15,
    "totalDurationSec": 1800
  }
}
```

---

## 4. Search

### GET /search

콘텐츠 검색 (🔒 인증 필요)

**Query Parameters**
| Param | Type | Default | 설명 |
|-------|------|---------|------|
| q | string | (필수) | 검색어 |
| catalogId | string | - | 카탈로그 필터 |
| playerId | int | - | 플레이어 필터 |
| handGrade | S/A/B/C | - | 핸드 등급 필터 |
| year | int | - | 연도 필터 |
| minDuration | int | - | 최소 재생시간 (초) |
| maxDuration | int | - | 최대 재생시간 (초) |
| page | int | 1 | 페이지 |
| limit | int | 20 | 개수 (max: 100) |
| sort | string | relevance | 정렬 (relevance/date/views) |

**Response 200**
```json
{
  "data": {
    "results": [
      {
        "id": 101,
        "title": "Phil Ivey's Legendary Bluff",
        "durationSec": 900,
        "thumbnailUrl": "/images/contents/101.jpg",
        "series": { "id": 1, "title": "WSOP 2024" },
        "catalog": { "id": "wsop", "name": "WSOP" },
        "highlight": "...Phil <em>Ivey</em> makes an incredible...",
        "score": 0.95
      }
    ],
    "total": 156,
    "page": 1,
    "limit": 20,
    "facets": {
      "catalogs": { "wsop": 100, "hcl": 56 },
      "players": { "Phil Ivey": 80, "Daniel Negreanu": 45 },
      "handGrades": { "S": 30, "A": 80, "B": 46 },
      "years": { "2024": 100, "2023": 56 }
    }
  }
}
```

---

## 5. Stream

### GET /stream/{contentId}/master.m3u8

HLS 마스터 플레이리스트 (🔒 인증 필요)

**Response 200** (Content-Type: application/vnd.apple.mpegurl)
```
#EXTM3U
#EXT-X-STREAM-INF:BANDWIDTH=2500000,RESOLUTION=1280x720
stream_0.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=1000000,RESOLUTION=854x480
stream_1.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=500000,RESOLUTION=640x360
stream_2.m3u8
```

**Errors**
| Code | HTTP | 설명 |
|------|------|------|
| `CONTENT_NOT_FOUND` | 404 | 콘텐츠 없음 |
| `STREAM_NOT_READY` | 503 | 트랜스코딩 중 |
| `STREAM_SOURCE_ERROR` | 500 | NAS 접근 실패 |
| `STREAM_ACCESS_DENIED` | 403 | 스트림 접근 권한 없음 (#4) |

---

### GET /stream/{contentId}/status

트랜스코딩 상태 조회 (#16)

**Response 200**
```json
{
  "data": {
    "status": "processing",
    "progress": 45,
    "estimatedTime": 120,
    "error": null
  }
}
```

**Status 값**
| Status | 설명 |
|--------|------|
| `pending` | 대기 중 |
| `processing` | 트랜스코딩 중 |
| `completed` | 완료 |
| `failed` | 실패 |

---

## 6. Progress

### POST /progress

시청 진행률 저장 (🔒 인증 필요) - Optimistic Locking (#7)

**Request**
```json
{
  "contentId": 101,
  "progressSec": 1800,
  "durationSec": 7200,
  "version": 5
}
```

> `version`: Race Condition 방지. 클라이언트가 알고 있는 마지막 버전. 일치하지 않으면 409 반환.

**Response 200**
```json
{
  "data": {
    "contentId": 101,
    "progressSec": 1800,
    "durationSec": 7200,
    "completed": false,
    "version": 6,
    "updatedAt": "2025-12-09T12:00:00Z"
  }
}
```

**Errors**
| Code | HTTP | 설명 |
|------|------|------|
| `PROGRESS_VERSION_CONFLICT` | 409 | 버전 충돌 (Race Condition) (#7) |

---

### GET /progress/{contentId}

시청 진행률 조회 (🔒 인증 필요)

**Response 200**
```json
{
  "data": {
    "contentId": 101,
    "progressSec": 1800,
    "durationSec": 7200,
    "completed": false,
    "updatedAt": "2025-12-09T12:00:00Z"
  }
}
```

---

## 7. Admin

### GET /admin/users/pending

승인 대기 사용자 목록 (🔒 Admin 전용)

**Response 200**
```json
{
  "data": {
    "items": [
      {
        "id": 5,
        "username": "newuser",
        "displayName": "New User",
        "createdAt": "2025-12-09T10:00:00Z"
      }
    ],
    "total": 3
  }
}
```

---

### POST /admin/users/{id}/approve

사용자 승인 (🔒 Admin 전용)

**Request**
```json
{
  "action": "approve" | "reject"
}
```

**Response 200**
```json
{
  "data": {
    "id": 5,
    "username": "newuser",
    "status": "approved",
    "approvedBy": 1,
    "approvedAt": "2025-12-09T12:00:00Z"
  }
}
```

---

## 에러 코드 전체 목록

| Code | HTTP | 설명 | 처리 |
|------|------|------|------|
| `AUTH_INVALID_CREDENTIALS` | 401 | 인증 정보 불일치 | 재로그인 |
| `AUTH_TOKEN_EXPIRED` | 401 | 토큰 만료 | 재로그인 |
| `AUTH_PENDING_APPROVAL` | 403 | 승인 대기 | 대기 화면 |
| `AUTH_REJECTED` | 403 | 가입 거절 | 거절 메시지 |
| `AUTH_SUSPENDED` | 403 | 계정 정지 | 정지 메시지 |
| `AUTH_FORBIDDEN` | 403 | 권한 없음 | - |
| `AUTH_USERNAME_EXISTS` | 409 | 아이디 중복 | 다른 아이디 |
| `AUTH_PASSWORD_MISMATCH` | 400 | 비밀번호 불일치 | 재입력 |
| `CONTENT_NOT_FOUND` | 404 | 콘텐츠 없음 | 404 페이지 |
| `SERIES_NOT_FOUND` | 404 | 시리즈 없음 | 404 페이지 |
| `CATALOG_NOT_FOUND` | 404 | 카탈로그 없음 | 404 페이지 |
| `STREAM_NOT_READY` | 503 | 트랜스코딩 중 | 로딩 + 재시도 |
| `STREAM_SOURCE_ERROR` | 500 | NAS 접근 실패 | 에러 화면 |
| `VALIDATION_ERROR` | 400 | 입력값 검증 실패 | 필드별 에러 |
| `RATE_LIMIT_EXCEEDED` | 429 | 요청 한도 초과 | 대기 후 재시도 |
| `INTERNAL_ERROR` | 500 | 서버 내부 오류 | 에러 화면 |

---

## 변경 이력

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-09 | 초기 API 스펙 |
| 2.0.0 | 2025-12-09 | 보안/로직 이슈 수정: httpOnly 쿠키, Refresh Token, 토큰 Blacklist, Optimistic Locking, 트랜스코딩 상태 API (#1, #7, #12, #16, #24) |
| 2.1.0 | 2025-12-10 | 목록 API 응답 구조 명확화 (items/total 구조 강조, Frontend 파싱 예시 추가) (#57) |
