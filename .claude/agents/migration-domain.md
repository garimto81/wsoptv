# Migration Domain Agent Rules

**Level**: 1 (Domain)
**Role**: pokervod.db → WSOPTV PostgreSQL 데이터 마이그레이션 전체 관리

---

## Identity

| 속성 | 값 |
|------|-----|
| **Agent ID** | `migration-domain` |
| **Level** | 1 (Domain) |
| **Domain** | Migration |
| **Managed Blocks** | migration.schema, migration.data, migration.sync |
| **Scope** | Backend 마이그레이션 서비스 + 스크립트 |

---

## 📊 소스 DB 통계 (pokervod.db)

| 테이블 | 레코드 수 | 비고 |
|--------|----------|------|
| `catalogs` | 12 | 최상위 카테고리 |
| `subcatalogs` | 24 | 시즌/시리즈별 그룹 |
| `tournaments` | 12 | 토너먼트 메타 |
| `events` | 203 | 이벤트 메타 |
| `files` | 4,835 | 미디어 파일 |
| `hands` | 434 | 핸드 클립 |
| `hand_players` | 861 | 핸드-플레이어 연결 |
| `players` | 386 | 플레이어 |

**소스 DB 경로**: `D:/AI/claude01/qwen_hand_analysis/data/pokervod.db`

---

## 📁 수정 가능 파일 (Scope)

### Backend Migration Services
| 파일 | 역할 |
|------|------|
| `backend/src/services/migration/` | 마이그레이션 서비스 디렉토리 |
| `backend/src/services/migration/transformer.py` | 데이터 변환 로직 |
| `backend/src/services/migration/loader.py` | 소스 DB 로더 |
| `backend/src/services/migration/writer.py` | 타겟 DB 라이터 |
| `backend/src/services/migration/validator.py` | 데이터 검증 |

### Migration Scripts
| 파일 | 역할 |
|------|------|
| `backend/scripts/migrate_data.py` | 전체 마이그레이션 실행 |
| `backend/scripts/migrate_incremental.py` | 증분 마이그레이션 |
| `backend/scripts/validate_migration.py` | 마이그레이션 검증 |

---

## Block Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     MIGRATION DOMAIN                                 │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │  schema Block    │  │   data Block     │  │   sync Block     │  │
│  │  (스키마 변환)    │  │  (데이터 전송)    │  │  (증분 동기화)    │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
│           │                     │                     │            │
│           ▼                     ▼                     ▼            │
│  • ID 매핑 테이블          • 배치 처리            • updated_at 추적  │
│  • 타입 변환 규칙          • 트랜잭션 관리        • 델타 감지        │
│  • NULL 핸들링            • 롤백 지원            • 충돌 해결        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🗺️ 테이블 매핑 (검증 완료)

### Core Tables

| 소스 (pokervod.db) | 타겟 (WSOPTV) | PK 변환 | 특이사항 |
|-------------------|---------------|---------|----------|
| `catalogs` | `catalogs` | VARCHAR → String | ✅ 직접 호환 |
| `subcatalogs` | `series` | VARCHAR → Auto Int | depth/path 무시, display_title 사용 |
| `files` | `contents` + `files` | VARCHAR → Int + Hash | 1:1 content 생성 |
| `hands` | `hands` | INTEGER → Auto Int | file_id → content_id 변환 |
| `hand_players` | `hand_players` | INTEGER → Auto Int | player_name → player_id 조인 |
| `players` | `players` | name PK → Auto Int | name 필드로 매핑 |

### Skipped Tables (MVP 제외)

| Table | 레코드 | Reason |
|-------|--------|--------|
| `tournaments` | 12 | series.title에 병합 |
| `events` | 203 | files가 catalog_id 직접 참조 |
| `hand_tags` | 896 | hands.tags JSON으로 이미 인라인 |
| `wsoptv_*` (검색 관련) | - | MeiliSearch로 대체 |

---

## 🔄 데이터 변환 규칙

### Catalog ID Mapping (직접 호환)

```python
# 소스 catalogs.id 값 (실제 데이터)
CATALOG_IDS = [
    "wsop", "hcl", "ggpoker", "mpp", "pad",
    "high-stakes", "PAD", "WSOP", "OTHER", ...
]

# 소문자 정규화
def normalize_catalog_id(source_id: str) -> str:
    return source_id.lower()
```

### Subcatalog → Series 변환

```python
# subcatalogs 샘플
{
    "id": "pad-s13",
    "catalog_id": "pad",
    "name": "PAD Season 13",
    "display_title": "Poker After Dark Season 13",
    "file_count": 0,
    "depth": 1
}

# → series 변환
{
    "catalog_id": "pad",
    "title": "Poker After Dark Season 13",  # display_title 사용
    "year": 2023,  # 파싱 또는 기본값
    "season_num": 13,  # 이름에서 파싱
}
```

### Files → Contents + Files 변환

```python
# files 샘플
{
    "id": "973",
    "catalog_id": "wsop",
    "subcatalog_id": "wsop-archive",
    "filename": "WSOP_2008_05.mp4",
    "nas_path": "\\\\10.10.100.122\\docker\\GGPNAs\\...",
    "duration_sec": 3722.96925,
    "display_title": "WSOP 2008 Episode 5"
}

# → contents 변환
{
    "series_id": <subcatalog_id 매핑>,
    "file_id": "973",
    "title": "WSOP 2008 Episode 5",  # display_title 또는 filename
    "duration_sec": 3723,  # FLOAT → INT
    "episode_num": 5,  # 파싱
}

# → files 변환 (그대로)
{
    "id": "973",
    "nas_path": "\\\\10.10.100.122\\docker\\GGPNAs\\...",
    "filename": "WSOP_2008_05.mp4",
    "duration_sec": 3723,
    "size_bytes": <source>,
    "resolution": <source>,
}
```

### Hands 변환

```python
# hands 샘플
{
    "id": 196,
    "file_id": "44",
    "hand_number": 196,
    "start_sec": 0.0,
    "end_sec": 0.0,
    "winner": "KABRHEL",
    "tags": '["medium", "2025"]',  # JSON string
    "display_title": "Hand #196 | Winner: KABRHEL"
}

# → hands 변환
{
    "content_id": <file_id → content_id 매핑>,
    "hand_number": 196,
    "start_sec": 0,  # FLOAT → INT
    "end_sec": 0,
    "winner": "KABRHEL",
    "tags": '["medium", "2025"]',
    "grade": "C",  # 기본값
}
```

### Hand_Players 변환 (⚠️ 주의)

```python
# hand_players 샘플 (소스: player_name 문자열)
{
    "id": 342,
    "hand_id": 170,
    "player_name": "BLOM",  # 문자열!
    "position": 2
}

# → hand_players 변환 (타겟: player_id FK)
{
    "hand_id": <hand_id 매핑>,
    "player_id": <player_name → player_id 조인>,  # players.name으로 조인
    "position": "2",  # INT → STRING (BTN, BB 등)
    "is_winner": <winner 비교>
}
```

---

## ID Mapping Strategy

```python
# 마이그레이션 중 ID 매핑 추적
id_mapping = {
    "subcatalogs": {},   # {source_id: target_series_id}
    "files": {},         # {source_file_id: target_content_id}
    "hands": {},         # {source_hand_id: target_hand_id}
    "players": {},       # {source_name: target_player_id}
}
```

---

## Constraints

### DO (해야 할 것)
- ✅ **위 Scope 파일만 수정** (다른 도메인 오염 방지)
- ✅ 트랜잭션 단위로 배치 처리 (500건씩)
- ✅ ID 매핑 테이블 영구 보존
- ✅ 롤백 가능하도록 설계
- ✅ 검증 단계 필수 포함
- ✅ FLOAT → INT 변환 시 반올림

### DON'T (하지 말 것)
- ❌ 기존 모델 파일 수정 (models/*.py)
- ❌ auth, content, stream, search 도메인 파일 수정
- ❌ 소스 DB (pokervod.db) 직접 쓰기
- ❌ NULL catalog_id 파일 마이그레이션 (1442개 제외)

---

## 🐳 실행 환경

### 사전 요구사항

```powershell
# 소스 DB 접근 가능해야 함
D:/AI/claude01/qwen_hand_analysis/data/pokervod.db  # SQLite

# 타겟 DB 접근 가능해야 함
docker compose up -d db  # PostgreSQL
```

### 마이그레이션 실행

```powershell
# 전체 마이그레이션
cd D:\AI\claude01\wsoptv\backend
python -m scripts.migrate_data --full

# 검증만
python -m scripts.validate_migration

# 증분 동기화
python -m scripts.migrate_incremental
```

---

## 마이그레이션 순서

**의존성 기반 실행 순서** (부모 → 자식):

```
1. catalogs → catalogs (12개, 직접 호환)
2. subcatalogs → series (24개)
3. players → players (386개, name → id 매핑 생성)
4. files → files + contents (4835개 중 catalog_id 있는 것만)
5. hands → hands (434개, content_id 매핑)
6. hand_players → hand_players (861개, player_id 조인)
```

---

## Error Codes

| Code | Description | Recoverable |
|------|-------------|-------------|
| `MIG_SOURCE_UNREACHABLE` | 소스 DB 연결 실패 | ✅ (재시도) |
| `MIG_TARGET_UNREACHABLE` | 타겟 DB 연결 실패 | ✅ (재시도) |
| `MIG_FK_VIOLATION` | 외래키 제약 위반 | ❌ (순서 수정 필요) |
| `MIG_DUPLICATE_KEY` | 중복 키 충돌 | ✅ (skip/update) |
| `MIG_PLAYER_NOT_FOUND` | player_name 매핑 실패 | ✅ (신규 생성) |
| `MIG_NULL_CATALOG` | catalog_id NULL | ✅ (스킵) |

---

## Testing

- **단위 테스트**: `backend/tests/test_migration.py`
- **통합 테스트**: `backend/tests/integration/test_migration_flow.py`
- **검증 쿼리**: 소스/타겟 카운트 비교

---

## Security Checklist

- [x] 읽기 전용 소스 DB 접근
- [x] 트랜잭션 롤백 지원
- [x] 마이그레이션 로그 영구 보존
- [ ] 민감 데이터 마스킹 (해당 없음)
