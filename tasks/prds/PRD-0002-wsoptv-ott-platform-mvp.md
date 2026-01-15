# PRD-0002: WSOPTV OTT Platform MVP

| 항목 | 값 |
|------|---|
| **Version** | 1.0 |
| **Status** | Draft |
| **Priority** | P2 |
| **Created** | 2026-01-07 |
| **Author** | Claude Code |
| **Source** | meeting_malkum_report.md |

---

## Executive Summary

WSOP(World Series of Poker) 공식 OTT 스트리밍 플랫폼 구축. 5개 플랫폼(Web, iOS, Android, Samsung TV, LG TV)에서 라이브 스트리밍, VOD, 멀티뷰, 20개국 자막을 지원하는 프리미엄 포커 방송 서비스.

### 핵심 목표
- 글로벌 50만 동시접속 대응
- 1080p Full HD 품질의 라이브/VOD 제공
- 4분할 멀티뷰 (Web/Mobile)
- 20개국 다국어 자막

---

## Problem Statement

### 현재 상황
- WSOP 콘텐츠가 분산된 플랫폼에서 제공
- 전용 OTT 서비스 부재로 브랜드 가치 저하
- 글로벌 팬베이스 대상 통합 서비스 필요

### 해결 방안
- 통합 OTT 플랫폼 구축
- GGPass SSO 연동으로 기존 사용자 활용
- 내부 빌링 시스템 연동으로 비용 절감

---

## Target Users

| 사용자 유형 | 설명 | 주요 니즈 |
|------------|------|----------|
| **포커 팬** | WSOP 시청자 | 라이브 경기, 하이라이트 |
| **GGPoker 회원** | 기존 플랫폼 사용자 | 심리스한 로그인, 연계 서비스 |
| **글로벌 시청자** | 비영어권 사용자 | 다국어 자막, 현지화 |

---

## Requirements

### Functional Requirements

#### FR-1: 라이브 스트리밍
| ID | 요구사항 | 우선순위 |
|----|---------|:--------:|
| FR-1.1 | 1080p Full HD 라이브 방송 | P0 |
| FR-1.2 | HLS 프로토콜 기반 스트리밍 | P0 |
| FR-1.3 | 30분~1시간 의도적 지연 (스포일러 방지) | P0 |
| FR-1.4 | 실시간 챗/이모지 반응 | P2 |

#### FR-2: VOD & Quick VOD
| ID | 요구사항 | 우선순위 |
|----|---------|:--------:|
| FR-2.1 | 라이브→VOD 즉시 전환 (Quick VOD) | P0 |
| FR-2.2 | 시청 이력 및 이어보기 | P1 |
| FR-2.3 | 챕터/구간 탐색 | P1 |
| FR-2.4 | 다운로드 오프라인 시청 | P2 |

#### FR-3: 멀티뷰
| ID | 요구사항 | 우선순위 |
|----|---------|:--------:|
| FR-3.1 | 4분할 화면 동시 재생 | P0 |
| FR-3.2 | 오디오 소스 선택 | P1 |
| FR-3.3 | 레이아웃 커스터마이징 | P2 |

> **제약사항**: TV 앱에서는 멀티뷰 미지원 (리모컨 UX 제약, 스토어 정책)

#### FR-4: 자막
| ID | 요구사항 | 우선순위 |
|----|---------|:--------:|
| FR-4.1 | 20개국 언어 자막 지원 | P0 |
| FR-4.2 | 영어 기반 번역 | P0 |
| FR-4.3 | VOD 자막 우선 지원 | P0 |
| FR-4.4 | 라이브 자막 (인력 투입) | P2 |

#### FR-5: 인증 & 결제
| ID | 요구사항 | 우선순위 |
|----|---------|:--------:|
| FR-5.1 | GGPass SSO 연동 | P0 |
| FR-5.2 | 내부 빌링 API 연동 | P0 |
| FR-5.3 | 구독 플랜 관리 | P1 |

### Non-Functional Requirements

#### NFR-1: 성능
| ID | 요구사항 | 목표치 |
|----|---------|-------|
| NFR-1.1 | 동시접속 | 50만 사용자 |
| NFR-1.2 | 초기 버퍼링 | < 3초 |
| NFR-1.3 | 재버퍼링 비율 | < 1% |

#### NFR-2: 보안
| ID | 요구사항 | 목표치 |
|----|---------|-------|
| NFR-2.1 | DRM | Widevine, FairPlay, PlayReady |
| NFR-2.2 | VPN 감지 | 80-90% 정확도 |
| NFR-2.3 | 국가별 블랙아웃 | 지원 |

#### NFR-3: 가용성
| ID | 요구사항 | 목표치 |
|----|---------|-------|
| NFR-3.1 | 서비스 가용성 | 99.9% |
| NFR-3.2 | CDN 파트너 | Akamai, CloudFront |

---

## Technical Architecture

### 플랫폼 구성

![Platform Architecture](../images/PRD-0002/architecture.png)

[HTML 원본](../mockups/PRD-0002/architecture.html)

### 기술 스택

| 레이어 | 기술 |
|--------|------|
| **Web Player** | hls.js 기반 커스텀 플레이어 |
| **iOS** | Swift + AVPlayer |
| **Android** | Kotlin + ExoPlayer |
| **TV** | Tizen/webOS Web App |
| **CDN** | Akamai, CloudFront |
| **DRM** | Widevine, FairPlay, PlayReady |

### 시스템 연동

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  GGPass     │────▶│  WSOPTV     │────▶│  Billing    │
│  SSO        │     │  Platform   │     │  API        │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                    ┌──────┴──────┐
                    ▼             ▼
             ┌──────────┐  ┌──────────┐
             │ Schedule │  │ Content  │
             │ API      │  │ CMS      │
             └──────────┘  └──────────┘
```

---

## UI/UX Design

### Watch Screen

![Watch Screen](../images/PRD-0002/watch-screen.png)

[HTML 원본](../mockups/PRD-0002/watch-screen.html)

**주요 기능**:
- 대형 플레이어 (히어로 영역)
- 라이브 뱃지 표시
- 멀티뷰 전환 버튼
- 20개국 자막 선택
- Quick VOD 하이라이트 섹션

### Multi-View Screen

![Multi-View Screen](../images/PRD-0002/multiview-screen.png)

[HTML 원본](../mockups/PRD-0002/multiview-screen.html)

**주요 기능**:
- 2x2 그리드 레이아웃
- 테이블별 구분 (Feature, Secondary, Bubble, All-In)
- 오디오 소스 인디케이터
- 동기화 상태 표시
- 레이아웃 옵션

### Collections Screen

![Collections Screen](../images/PRD-0002/collections-screen.png)

[HTML 원본](../mockups/PRD-0002/collections-screen.html)

**주요 기능**:
- 히어로 배너 (Featured Collection)
- 필터 탭 (Main Event, Bracelet, High Roller, Classics)
- 시청 진행률 표시
- 큐레이티드 플레이리스트
- 검색 기능

---

## Scope

### In Scope (MVP)
| 항목 | 설명 |
|------|------|
| 플랫폼 | Web, iOS, Android, Samsung TV, LG TV |
| 화질 | 1080p Full HD |
| 지연 시간 | 표준 HLS (30분~1시간 의도적 지연) |
| 멀티뷰 | 4분할 (Web/Mobile만) |
| 자막 | 20개국 |
| 메뉴 | Watch + Collections 2개만 |

### Out of Scope
| 항목 | 사유 |
|------|------|
| 4K 지원 | 장비/인프라 비용 과다 |
| VLM (비디오 AI 분석) | 고비용, 별도 업체 필요 |
| 뉴스 섹션 | 불필요 |
| 전적/플레이어 정보 | WSOP.com 링크 연결 |
| 티켓팅 | 온라인 구독만 |
| Roku/Fire TV | Phase 2 |

---

## Cost Factors

### 비용 절감 포인트
| 항목 | 내용 | 영향도 |
|------|------|:------:|
| GGPass SSO | 로그인/가입 개발 불필요 | 높음 |
| 빌링 시스템 | 내부 API 활용 | 높음 |
| 스케줄 API | 내부 DB 연동 | 중간 |
| 사이트 범위 | 2개 메뉴만 | 높음 |

### 비용 증가 요소
| 항목 | 내용 | 영향도 |
|------|------|:------:|
| 멀티뷰 트래픽 | 4배 트래픽 증가 | 높음 |
| TV 앱 | 플랫폼별 개발 | 중간 |

---

## Risks & Mitigations

| 리스크 | 영향 | 완화 방안 |
|--------|:----:|----------|
| TV 앱 멀티뷰 불가 | 중 | PGM 화면만 제공 |
| 실시간 자막 품질 | 중 | VOD 자막 우선, 라이브는 인력 투입 |
| VPN 우회 | 중 | IP 기반 차단 + 부분 VPN 감지 |
| 브라우저 DRM | 저 | Edge/Safari 안내 또는 앱 유도 |

---

## Success Metrics

| 지표 | 목표 | 측정 방법 |
|------|------|----------|
| DAU | 10만+ | Analytics |
| 동시접속 | 50만 | CDN 리포트 |
| 평균 시청 시간 | 45분+ | Player 이벤트 |
| 재버퍼링 비율 | < 1% | QoE 모니터링 |
| 구독 전환율 | 5%+ | Billing 데이터 |

---

## Timeline (Phase)

### Phase 1: MVP
- Web + Mobile 앱
- 라이브 + VOD + 자막
- GGPass SSO + 빌링 연동

### Phase 2: 확장
- TV 앱 (Samsung, LG)
- 멀티뷰
- Quick VOD

### Phase 3: 고도화
- 4K 지원
- AI 챕터/요약
- Roku/Fire TV

---

## Open Questions

1. TV 미러링/캐스팅 지원 여부
2. AI 챕터/요약 기능 도입 범위
3. 멀티 PG 통합 API 구조
4. 블랙아웃 정책 (사이트 단위 vs 영상 단위)
5. 컨설팅 단계 진행 여부

---

## References

- [미팅 보고서](../docs/meeting_malkum_report.md)
- [RFP 문서](../docs/WSOP%20TV%20서비스%20구축%20RFP.pdf)

---

## Revision History

| 버전 | 날짜 | 작성자 | 내용 |
|------|------|--------|------|
| 1.0 | 2026-01-07 | Claude Code | 최초 작성 |
