# WSOPTV 프로젝트 현재 상태

**Last Updated**: 2025-12-09
**Session**: Phase 6 Jellyfin 설치 진행 중

---

## 🚀 Quick Resume (재부팅 후 이어서 작업)

```powershell
# 1. Docker 서비스 확인
cd D:\AI\claude01\wsoptv
docker compose ps

# 2. 서비스가 내려가 있으면 시작
docker compose up -d

# 3. Jellyfin 서버 시작 (Windows Native)
Start-Process "C:\Program Files\Jellyfin\Server\jellyfin.exe"

# 4. 서비스 확인
curl http://localhost:8096/System/Info/Public   # Jellyfin
curl http://localhost:8001/docs                  # Backend API

# 5. 다음 작업
# Jellyfin API 키 생성 → Docker Backend 연동 테스트
```

---

## 📊 현재 진행률

| Phase | 상태 | 진행률 |
|-------|------|--------|
| Phase 0: 프로젝트 설정 | ✅ 완료 | 100% |
| Phase 1: Backend 구축 | ✅ 완료 | 100% |
| Phase 2: Frontend 페이지 | ✅ 완료 | 100% |
| Phase 3: 통합 & 스트리밍 | ⚠️ 부분 완료 | 80% |
| Phase 4: 테스트 & QA | 🟡 진행 중 | 20% |
| Phase 5: 배포 & DevOps | ⬜ 대기 | 0% |
| **Phase 6: Jellyfin 전환** | 🟡 **진행 중** | 40% |

**전체 진행률**: 80%

---

## 🔧 현재 Docker 서비스 상태

| 서비스 | 컨테이너 | 포트 | 상태 |
|--------|----------|------|------|
| PostgreSQL | wsoptv-postgres | 5433:5432 | ✅ healthy |
| MeiliSearch | wsoptv-meili | 7700:7700 | ✅ healthy |
| Redis | wsoptv-redis | 6379:6379 | ✅ healthy |
| Backend | wsoptv-backend | 8001:8001 | ✅ healthy |
| Frontend | wsoptv-frontend | 3000:3000 | ✅ running |

### 접속 URL
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001/docs
- **MeiliSearch**: http://localhost:7700

### 테스트 계정
| 사용자 | 비밀번호 | 권한 |
|--------|----------|------|
| admin | test123 | admin (approved) |

---

## ⚠️ 알려진 이슈

### Docker Desktop + NAS 마운트 제약
- **문제**: Docker Desktop WSL2 백엔드는 Windows SMB 네트워크 드라이브 pass-through 불가
- **영향**: HLS 스트리밍 서비스가 NAS 파일에 접근 불가
- **해결 방안**: Jellyfin 하이브리드 아키텍처로 전환 결정 (승인됨)
- **상세**: `docs/proposals/0002-jellyfin-migration.md`

---

## 🎯 다음 작업 (Phase 6)

### Week 1-2: Jellyfin 서버 설정 ← **진행 중**

> 📄 설치 가이드: `docs/guides/jellyfin-installation.md`

```
[x] Jellyfin 서버 설치 (Windows 네이티브)
    - 설치 경로: C:\Program Files\Jellyfin\Server
    - 버전: 10.11.4
[x] 관리자 계정 생성 (wsoptv-admin)
[x] NAS 라이브러리 구성
    - 경로: Z:\GGPNAs\ARCHIVE\
    - 폴더: WSOP, HCL, PAD, MPP, GGMillions, GOG 최종
[ ] 라이브러리 스캔 (백그라운드 진행 중)
[x] 트랜스코딩 설정 (HW 가속) - 나중에 필요시 설정
[ ] API 키 생성 ← **다음 작업**
[ ] Docker Backend 연동 테스트
```

### ⚠️ 다음 세션에서 할 일
1. Jellyfin 로그인 후 Dashboard → API Keys → 새 키 생성
2. `.env` 파일에 `JELLYFIN_API_KEY` 추가
3. Docker Backend에서 Jellyfin 연동 테스트

### Week 3-4: 포커 메타데이터 플러그인
```
[ ] C# 개발 환경 설정
[ ] Jellyfin Plugin API 학습
[ ] 핸드 메타데이터 플러그인 개발
[ ] PostgreSQL 연동
```

### Week 5-6: 커스텀 웹 UI 통합
```
[ ] Jellyfin 플레이어 통합
[ ] 핸드 타임라인 오버레이
[ ] 핸드 스킵 UI
```

### Week 7-8: 마이그레이션 & 테스트
```
[ ] E2E 테스트
[ ] 성능 테스트
[ ] 프로덕션 전환
```

---

## 📁 주요 문서 위치

| 문서 | 경로 | 버전 |
|------|------|------|
| 프로젝트 가이드 | `CLAUDE.md` | v3.0.0 |
| 태스크 목록 | `tasks/0001-tasks-wsoptv-full-build.md` | v2.0.0 |
| Jellyfin 전환 제안서 | `docs/proposals/0002-jellyfin-migration.md` | ✅ 승인 |
| LLD 마스터 | `docs/lld/0001-lld-wsoptv-platform.md` | v3.0.0 |
| 작업 로그 | `logs/work-log-2025-12-09.md` | - |

---

## 🗄️ 데이터베이스 현황

### PostgreSQL (wsoptv)
| 테이블 | 레코드 | 설명 |
|--------|--------|------|
| catalogs | 8 | WSOP, HCL, PAD, MPP 등 |
| series | 24 | 시리즈/토너먼트 |
| contents | 2,524 | 에피소드/영상 |
| files | 2,524 | 미디어 파일 메타 |
| hands | 434 | 핸드 정보 |
| players | 386 | 포커 플레이어 |
| hand_players | 833 | 핸드-플레이어 매핑 |
| users | 1 | admin 계정 |

### MeiliSearch 인덱스
| 인덱스 | 레코드 | 검색 필드 |
|--------|--------|----------|
| contents | 2,524 | title, series_title, catalog_name |
| players | 386 | name, display_name, country |
| hands | 434 | winner, player_names, board |

---

## 🔄 Git 상태

```
Branch: main (clean)
최근 커밋:
- bd691f8 fix: Docker 빌드 및 배포 오류 수정
- 88c3919 feat: WSOPTV 백엔드 + Docker + 프론트엔드 전체 구현 (#47)
```

---

## 📝 세션 요약 (2025-12-09)

### 오전 세션
1. **E2E 테스트 완료** - 로그인, 카탈로그, 검색, 콘텐츠 API 모두 정상
2. **SQLAlchemy 이슈 해결** - Eager loading 체인 추가로 async lazy loading 에러 수정
3. **NAS 마운트 이슈 발견** - Docker Desktop WSL2 구조적 제약 확인
4. **Jellyfin 전환 결정** - 하이브리드 아키텍처 제안서 작성 및 승인
5. **문서 업데이트** - CLAUDE.md, LLD, 태스크 파일 모두 v3.0.0으로 업데이트

### 저녁 세션 (Phase 6 시작)
1. **Jellyfin 10.11.4 설치 완료** - Windows Native 설치
2. **관리자 계정 생성** - wsoptv-admin
3. **NAS 라이브러리 등록** - Z:\GGPNAs\ARCHIVE\ 전체 폴더
4. **GPU 확인** - NVIDIA RTX 5070 + Intel UHD (HW 트랜스코딩 가능)
5. **API 키 생성 시도** - 인증 이슈로 중단 (다음 세션에서 계속)

---

## 💡 다음 세션 시작 시

```powershell
# 1. 서비스 시작
docker compose up -d
Start-Process "C:\Program Files\Jellyfin\Server\jellyfin.exe"

# 2. 다음 작업
# "Jellyfin API 키 생성하고 Docker 연동 테스트" 로 시작
```

### 남은 작업
1. Jellyfin API 키 생성 (Dashboard → API Keys)
2. `.env`에 JELLYFIN_API_KEY 추가
3. Docker Backend에서 `curl http://host.docker.internal:8096` 테스트
