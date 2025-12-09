# Task 0002: pokervod.db → WSOPTV 데이터 마이그레이션

**Status**: 📋 Planning Complete
**Created**: 2024-12-10
**Agent**: migration-domain

---

## Summary

GGP pokervod.db (SQLite)에서 WSOPTV PostgreSQL로 데이터 마이그레이션 구현

---

## Source Database

**Path**: `D:/AI/claude01/qwen_hand_analysis/data/pokervod.db`

| 테이블 | 레코드 수 | 비고 |
|--------|----------|------|
| catalogs | 12 | 최상위 카테고리 |
| subcatalogs | 24 | 시즌/시리즈별 그룹 |
| files | 4,835 | 미디어 파일 |
| hands | 434 | 핸드 클립 |
| hand_players | 861 | 핸드-플레이어 연결 |
| players | 386 | 플레이어 |

---

## Table Mapping (검증 완료)

| 소스 | 타겟 | 변환 |
|------|------|------|
| catalogs | catalogs | 직접 호환 (VARCHAR PK) |
| subcatalogs | series | VARCHAR → Auto Int |
| files | contents + files | 1:1 content 생성 |
| hands | hands | file_id → content_id 변환 |
| hand_players | hand_players | player_name → player_id 조인 |
| players | players | name → id 매핑 |

---

## Migration Order

```
1. catalogs → catalogs (12개)
2. subcatalogs → series (24개)
3. players → players (386개)
4. files → files + contents (~3,400개, NULL catalog_id 제외)
5. hands → hands (434개)
6. hand_players → hand_players (861개)
```

---

## Next Steps

### Phase 1: 서비스 구현
- [ ] `backend/src/services/migration/` 디렉토리 생성
- [ ] `loader.py` - SQLite 소스 DB 로더
- [ ] `transformer.py` - 데이터 변환 로직
- [ ] `writer.py` - PostgreSQL 타겟 DB 라이터
- [ ] `validator.py` - 데이터 검증

### Phase 2: 스크립트 구현
- [ ] `backend/scripts/migrate_data.py` - 전체 마이그레이션
- [ ] `backend/scripts/validate_migration.py` - 검증 스크립트

### Phase 3: 테스트
- [ ] 단위 테스트 작성
- [ ] 통합 테스트 실행
- [ ] 소스/타겟 카운트 비교 검증

---

## Key Considerations

1. **NULL catalog_id 파일 제외**: ~1,400개 파일은 catalog_id가 NULL이므로 스킵
2. **player_name → player_id 조인**: hand_players 테이블은 문자열 이름 사용, FK로 변환 필요
3. **FLOAT → INT 변환**: duration_sec 등 반올림 처리
4. **ID 매핑 보존**: 마이그레이션 중 source_id → target_id 매핑 테이블 유지

---

## Related Documents

- Agent Rules: `.claude/agents/migration-domain.md`
- Source Schema: `D:/AI/claude01/db_architecture/docs/lld/01_DATABASE_SCHEMA.md` (참고용, 실제와 다름)
- Target Models: `backend/src/models/`

---

## Session Notes

### 2024-12-10
- DATABASE_SCHEMA.md와 실제 pokervod.db 스키마 차이 발견
- 무작위 10개 샘플링으로 실제 데이터 구조 검증
- migration-domain.md 에이전트 문서 생성 및 커밋
