# Jellyfin 설치 가이드 (Phase 6 Week 1-2)

**Version**: 1.0.0 | **Date**: 2025-12-09 | **Status**: 진행 중

> WSOPTV Phase 6 Week 1-2 작업: Windows에 Jellyfin 서버 설치 및 라이브러리 구성

---

## 사전 요구사항

### 시스템 요구사항

| 항목 | 최소 | 권장 |
|------|------|------|
| OS | Windows 10 | Windows 11 |
| RAM | 4GB | **8GB+** (2,500+ 콘텐츠) |
| CPU | Intel Core i3 / AMD Ryzen 3 | Intel Core i5 / AMD Ryzen 5 (HW 트랜스코딩) |
| 저장소 | 10GB (메타데이터) | 50GB (썸네일 + 메타데이터 캐시) |
| 네트워크 | NAS SMB 접근 가능 | 1Gbps LAN |

### 하드웨어 가속 (선택)

| GPU | 지원 | 코덱 |
|-----|------|------|
| Intel Quick Sync | ✅ | H.264, H.265 (HEVC) |
| NVIDIA NVENC | ✅ | H.264, H.265 (무료) |
| AMD VCE | ✅ | H.264, H.265 |

### NAS 접근 확인

```powershell
# NAS 마운트 확인
net use Z: \\10.10.100.122\GGPNAs\ARCHIVE /persistent:yes

# 연결 테스트
dir Z:\
```

---

## Step 1: Jellyfin 설치

### 1.1 다운로드

```
https://jellyfin.org/downloads/windows
```

- **권장 버전**: 10.10.7 (안정) 또는 10.11.x (최신)
- **설치 유형**: Windows Installer (.exe)

> ⚠️ **주의**: 신규 설치 권장. 기존 설치 업그레이드 시 [마이그레이션 이슈](../proposals/0002-jellyfin-migration.md#811-jellyfin-버전-업그레이드-경로-critical) 참조.

### 1.2 설치 실행

1. `jellyfin_x.x.x_windows-x64.exe` 실행
2. **서비스 모드** 선택 권장 (자동 시작)
3. 설치 완료 후 자동 시작

### 1.3 초기 설정

브라우저에서 `http://localhost:8096` 접속:

1. **언어**: 한국어 또는 영어
2. **관리자 계정**: WSOPTV 관리자 계정 생성
   - Username: `wsoptv-admin`
   - Password: 강력한 비밀번호
3. **라이브러리 설정**: (다음 섹션에서 진행)
4. **원격 접근**: 일단 비활성화 (로컬만)

---

## Step 2: 라이브러리 구성

### 2.1 미디어 라이브러리 추가

대시보드 → 라이브러리 → 라이브러리 추가

| 라이브러리 | 경로 | 콘텐츠 유형 |
|------------|------|-------------|
| WSOP | `Z:\GGPNAs\ARCHIVE\WSOP` | TV Shows |
| HCL | `Z:\GGPNAs\ARCHIVE\HCL` | TV Shows |
| PAD | `Z:\GGPNAs\ARCHIVE\PAD` | TV Shows |
| MPP | `Z:\GGPNAs\ARCHIVE\MPP` | TV Shows |
| GGMillions | `Z:\GGPNAs\ARCHIVE\GGMillions` | TV Shows |
| SuperHighRoller | `Z:\GGPNAs\ARCHIVE\SuperHighRoller` | TV Shows |
| PokerAfterDark | `Z:\GGPNAs\ARCHIVE\PokerAfterDark` | TV Shows |
| TritonPoker | `Z:\GGPNAs\ARCHIVE\TritonPoker` | TV Shows |

### 2.2 라이브러리 설정

각 라이브러리에 대해:

```
[라이브러리 설정]
✅ 실시간 모니터링 활성화
✅ 자막 다운로드 비활성화
✅ 인트로/크레딧 감지 비활성화 (포커는 불필요)
✅ 챕터 이미지 생성 비활성화 (성능)

[메타데이터 설정]
✅ 자동 다운로드 비활성화 (포커는 일반 DB에 없음)
✅ 로컬 메타데이터만 사용
```

### 2.3 라이브러리 스캔

```
대시보드 → 라이브러리 → 모두 스캔
```

> ⚠️ **주의**: 18TB+ 라이브러리 스캔은 **수 시간**이 소요됩니다. 야간에 실행 권장.

스캔 진행 확인:
```
대시보드 → 활동 로그
```

---

## Step 3: 트랜스코딩 설정

대시보드 → 재생 → 트랜스코딩

### 3.1 하드웨어 가속 설정

```
[하드웨어 가속]
✅ 활성화
   • Intel Quick Sync (Intel CPU 내장 GPU)
   • NVIDIA NVENC (NVIDIA GPU)
   • AMD VCE (AMD GPU)

[H.264/H.265]
✅ 하드웨어 디코딩
✅ 하드웨어 인코딩
```

### 3.2 트랜스코딩 경로

```
트랜스코딩 경로: C:\jellyfin\transcodes
```

> ✅ SSD에 트랜스코딩 폴더 배치 권장

### 3.3 품질 설정

| 설정 | 값 |
|------|-----|
| 비트레이트 제한 | 20 Mbps |
| 스레드 수 | 0 (자동) |
| 트랜스코딩 임시 파일 | 자동 삭제 |

---

## Step 4: 사용자 설정

대시보드 → 사용자

### 4.1 관리자 계정 (이미 생성됨)

```
Username: wsoptv-admin
역할: Administrator
```

### 4.2 API 접근용 계정 (Backend 연동)

```
Username: wsoptv-api
Password: [강력한 비밀번호]
역할: User (API 접근만)
```

> API 키 생성: 대시보드 → API 키 → 새 API 키

---

## Step 5: 네트워크 설정

대시보드 → 네트워킹

### 5.1 바인딩 설정

```
[HTTP]
포트: 8096
바인딩: 0.0.0.0 (모든 인터페이스)

[로컬 네트워크]
로컬 IP: 자동 감지 또는 수동 입력
```

### 5.2 CORS 설정 (Docker Backend 연동)

```
CORS 호스트: http://localhost:8001, http://172.28.2.1:8001
```

---

## Step 6: Docker 연동 테스트

### 6.1 환경변수 추가

`.env` 파일에 추가:

```env
# Jellyfin 연동 (Phase 2)
JELLYFIN_HOST=http://host.docker.internal:8096
JELLYFIN_API_KEY=your_jellyfin_api_key
```

### 6.2 연결 테스트

```powershell
# Windows에서 직접 테스트
curl http://localhost:8096/System/Info/Public

# Docker 컨테이너에서 테스트
docker exec -it wsoptv-backend curl http://host.docker.internal:8096/System/Info/Public
```

### 6.3 예상 응답

```json
{
  "LocalAddress": "http://192.168.x.x:8096",
  "ServerName": "WSOPTV-Jellyfin",
  "Version": "10.10.7",
  "ProductName": "Jellyfin Server",
  "OperatingSystem": "Windows",
  "Id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

---

## 체크리스트

### Week 1: 설치 및 기본 설정

- [ ] Jellyfin 설치 완료
- [ ] 관리자 계정 생성
- [ ] NAS 라이브러리 8개 추가
- [ ] 라이브러리 스캔 시작

### Week 2: 고급 설정 및 연동

- [ ] 라이브러리 스캔 완료 (2,500+ 콘텐츠)
- [ ] 하드웨어 트랜스코딩 설정
- [ ] API 키 생성
- [ ] Docker Backend 연동 테스트
- [ ] CORS 설정 확인

---

## 트러블슈팅

### 문제: NAS 접근 불가

```powershell
# SMB 자격증명 추가
cmdkey /add:10.10.100.122 /user:username /pass:password

# Windows 자격증명 관리자에서 확인
rundll32.exe keymgr.dll,KRShowKeyMgr
```

### 문제: 라이브러리 스캔 느림

- 네트워크 대역폭 확인 (NAS ↔ Windows)
- 실시간 모니터링 임시 비활성화
- 대용량 라이브러리는 야간 스캔

### 문제: Docker에서 Jellyfin 연결 실패

```powershell
# Windows 방화벽에서 8096 포트 허용
netsh advfirewall firewall add rule name="Jellyfin" dir=in action=allow protocol=TCP localport=8096
```

---

## 다음 단계

Week 1-2 완료 후:

1. **Week 3-4**: 포커 메타데이터 플러그인 개발 (C#)
2. **Week 5-6**: 커스텀 웹 UI 통합
3. **Week 7-8**: 마이그레이션 & E2E 테스트

---

**문서 작성**: Claude Code | **관련 문서**: [0002-jellyfin-migration.md](../proposals/0002-jellyfin-migration.md)
