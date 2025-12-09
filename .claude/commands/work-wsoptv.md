---
name: work-wsoptv
description: WSOPTV Block Agent System 기반 작업 실행 (Orchestrator → Domain → Block 라우팅)
---

# /work-wsoptv - Block Agent 기반 작업 실행

Block Agent System의 **문서 참조 프로세스**를 따라 작업을 수행합니다.

```
Orchestrator → Domain Agent → Block AGENT_RULES → 구현 → 검증
```

## 사용법

```
/work-wsoptv <작업 지시>
/work-wsoptv "Auth에 2FA 기능 추가"
/work-wsoptv "검색 결과 정렬 방식 변경"
/work-wsoptv "플레이어에 키보드 단축키 추가"
```

---

## 실행 흐름

```
/work-wsoptv 실행
    │
    ├─ Phase 0: Agent 라우팅 ────────────────────────────────────────┐
    │      │                                                         │
    │      ├─ Step 0.1: Orchestrator 규칙 로딩                       │
    │      │      📄 .claude/agents/orchestrator.md                  │
    │      │                                                         │
    │      ├─ Step 0.2: 작업 지시 파싱 및 도메인 라우팅              │
    │      │      "Auth" → auth-domain                               │
    │      │      "검색" → search-domain                             │
    │      │      "스트리밍/플레이어" → stream-domain                │
    │      │      "콘텐츠" → content-domain                          │
    │      │                                                         │
    │      ├─ Step 0.3: Domain Agent 규칙 로딩                       │
    │      │      📄 .claude/agents/{domain}-domain.md               │
    │      │                                                         │
    │      └─ Step 0.4: Block AGENT_RULES 로딩                       │
    │             📄 apps/web/features/{domain}/AGENT_RULES.md       │
    │                                                         ───────┘
    │
    ├─ Phase 1: 컨텍스트 분석 (병렬) ────────────────────────────────┐
    │      │                                                         │
    │      ├─ [Agent 1] Architecture/LLD 분석                        │ 병렬
    │      │      📄 docs/architecture/0001-block-agent-system.md    │
    │      │      📄 docs/lld/ (관련 문서)                           │
    │      │                                                         │
    │      └─ [Agent 2] 블럭 코드 분석                               │
    │             📄 features/{domain}/types.ts                      │
    │             📄 features/{domain}/index.ts                      │
    │                                                         ───────┘
    │
    ├─ Phase 2: 이슈 생성 + 브랜치
    │      │
    │      ├─ GitHub 이슈 생성 (도메인 라벨 포함)
    │      └─ Feature 브랜치 생성
    │
    ├─ Phase 3: 구현 (컨텍스트 격리)
    │      │
    │      ├─ AGENT_RULES.md DO 규칙 준수
    │      ├─ 블럭 폴더 내에서만 작업
    │      └─ types.ts 먼저 수정
    │
    ├─ Phase 4: 검증
    │      │
    │      ├─ AGENT_RULES.md 체크리스트 검증
    │      ├─ DON'T 규칙 위반 검사
    │      └─ 테스트 실행
    │
    └─ Phase 5: 보고 + PR
           │
           ├─ 변경 파일 범위 검증
           ├─ 커밋 생성
           └─ PR 생성 제안
```

---

## Phase 0: Agent 라우팅

### Step 0.1: Orchestrator 규칙 로딩

```python
# 필수: Orchestrator 규칙 확인
Read(".claude/agents/orchestrator.md")

# 라우팅 테이블 확인
routing_rules = {
    "인증|로그인|JWT|세션|2FA|비밀번호": "auth-domain",
    "콘텐츠|목록|핸드|타임라인|에피소드": "content-domain",
    "스트리밍|HLS|트랜스코딩|플레이어|비디오": "stream-domain",
    "검색|MeiliSearch|자동완성|필터": "search-domain"
}
```

### Step 0.2: 도메인 라우팅 결정

| 키워드 패턴 | 라우팅 도메인 | 블럭 범위 |
|------------|--------------|----------|
| 인증, 로그인, JWT, 세션, 2FA | `auth-domain` | `features/auth/` |
| 콘텐츠, 목록, 핸드, 타임라인 | `content-domain` | `features/content/` |
| 스트리밍, HLS, 플레이어, 비디오 | `stream-domain` | `features/player/` |
| 검색, MeiliSearch, 자동완성 | `search-domain` | `features/search/` |

### Step 0.3: Domain Agent 규칙 로딩

```python
# 도메인 에이전트 규칙 로딩
domain = detect_domain(instruction)
Read(f".claude/agents/{domain}-domain.md")

# 확인 항목
# - Managed Blocks
# - Capabilities
# - Scope
# - Error Codes
```

### Step 0.4: Block AGENT_RULES 로딩

```python
# 블럭 규칙 로딩 (핵심!)
block_folder = get_block_folder(domain)  # e.g., "auth" → "features/auth/"
Read(f"apps/web/{block_folder}/AGENT_RULES.md")

# 로딩 항목
# - DO (해야 할 것)
# - DON'T (하지 말 것)
# - Dependencies
# - Testing 정책
# - Security/Performance Checklist
```

---

## Phase 1: 컨텍스트 분석

### Architecture/LLD 분석 에이전트

```python
Task(
    subagent_type="Explore",
    prompt="""
    작업 지시: {instruction}
    라우팅된 도메인: {domain}

    다음 문서를 분석하세요:

    1. docs/architecture/0001-block-agent-system.md
       - 해당 도메인의 블럭 구조 확인
       - 의존성 그래프 확인

    2. docs/lld/0002-lld-modules.md
       - 관련 모듈 인터페이스 확인

    3. docs/lld/0005-lld-flows.md
       - 관련 시퀀스 다이어그램 확인

    4. docs/prds/0002-prd-block-agent-system.md
       - Feature Requirements 확인

    JSON 반환:
    {
        "relevant_sections": [...],
        "interfaces": [...],
        "flows": [...],
        "constraints": [...]
    }
    """,
    description="Architecture/LLD 분석"
)
```

### 블럭 코드 분석 에이전트

```python
Task(
    subagent_type="Explore",
    prompt="""
    작업 지시: {instruction}
    블럭 폴더: apps/web/features/{domain}/

    다음을 분석하세요:

    1. types.ts - 기존 타입 정의
    2. index.ts - Public API
    3. AGENT_RULES.md - 제약사항
    4. components/, hooks/, stores/, api/ - 기존 구조

    JSON 반환:
    {
        "existing_types": [...],
        "public_api": [...],
        "constraints": {
            "do": [...],
            "dont": [...]
        },
        "files_to_modify": [...],
        "new_files_needed": [...]
    }
    """,
    description="블럭 코드 분석"
)
```

---

## Phase 2: 이슈 생성 + 브랜치

### 이슈 생성

```bash
gh issue create \
  --title "feat({domain}): {작업 제목}" \
  --body "## 개요
{작업 설명}

## 도메인
- **Domain**: {domain}
- **Block**: features/{block}/
- **AGENT_RULES**: [AGENT_RULES.md](apps/web/features/{block}/AGENT_RULES.md)

## 관련 문서
- Architecture: docs/architecture/0001-block-agent-system.md
- Domain Agent: .claude/agents/{domain}-domain.md

## 체크리스트
- [ ] AGENT_RULES.md DO 규칙 준수
- [ ] AGENT_RULES.md DON'T 규칙 위반 없음
- [ ] 블럭 폴더 범위 내에서만 수정
- [ ] types.ts 타입 정의 추가/수정
- [ ] index.ts Public API 업데이트
" \
  --label "enhancement,{domain}"
```

### 브랜치 생성

```bash
git checkout -b feat/{domain}/issue-{N}-{description}
```

---

## Phase 3: 구현 (컨텍스트 격리)

### 구현 순서

```
1. types.ts      ← 새 타입 정의 먼저
2. api/          ← API 함수 추가
3. hooks/        ← 훅 추가/수정
4. stores/       ← 스토어 업데이트
5. components/   ← UI 컴포넌트
6. index.ts      ← Public API 업데이트
```

### 컨텍스트 격리 강제

```python
# 구현 전 검증
allowed_paths = [
    f"apps/web/features/{domain}/",
    "packages/types/"  # 공유 타입 추가 시
]

# 수정하려는 파일이 허용 범위 내인지 확인
for file in files_to_modify:
    if not any(file.startswith(path) for path in allowed_paths):
        raise ContextViolationError(f"❌ 범위 외 파일: {file}")
```

### AGENT_RULES.md 준수

```markdown
## 구현 중 체크

### DO 확인
✅ 이 폴더 내 파일만 수정
✅ types.ts 타입 정의 우선
✅ Zod 스키마로 입력 검증
✅ index.ts를 통해 외부 노출

### DON'T 확인
❌ features/ 외부 파일 수정 시도?
❌ shared/ui 내부 수정 시도?
❌ 하드코딩된 비밀값?
❌ 전역 상태 직접 접근?
```

---

## Phase 4: 검증

### AGENT_RULES 체크리스트 검증

```python
# AGENT_RULES.md의 체크리스트 자동 검증
checklist = parse_checklist(f"apps/web/features/{domain}/AGENT_RULES.md")

for item in checklist:
    result = verify_checklist_item(item)
    if not result.passed:
        print(f"⚠️ 체크리스트 미충족: {item}")
```

### DON'T 규칙 위반 검사

```python
# 변경된 파일 목록 검사
changed_files = git_diff_files()

violations = []
for file in changed_files:
    # 블럭 범위 외 파일 수정 검사
    if not file.startswith(f"apps/web/features/{domain}/"):
        if file not in ["packages/types/*.ts"]:  # 허용된 예외
            violations.append(f"범위 외 수정: {file}")

if violations:
    print("❌ DON'T 규칙 위반 발견:")
    for v in violations:
        print(f"  - {v}")
```

### 테스트 실행

```bash
# 블럭 단위 테스트
cd apps/web/features/{domain}
npm test -- --coverage

# 타입 체크
npx tsc --noEmit
```

---

## Phase 5: 보고 + PR

### 변경 파일 범위 검증

```python
# 최종 검증: 모든 변경이 블럭 범위 내인가?
changed_files = git_diff_files()
block_path = f"apps/web/features/{domain}/"

in_scope = [f for f in changed_files if f.startswith(block_path)]
out_of_scope = [f for f in changed_files if not f.startswith(block_path)]

if out_of_scope:
    # packages/types/ 는 허용
    truly_out = [f for f in out_of_scope if not f.startswith("packages/types/")]
    if truly_out:
        raise ScopeViolationError(f"범위 외 파일 수정됨: {truly_out}")
```

### 커밋

```bash
git add apps/web/features/{domain}/
git commit -m "feat({domain}): {작업 설명}

Block: features/{domain}/
AGENT_RULES: 준수 ✅

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

### PR 생성

```bash
gh pr create \
  --title "feat({domain}): {작업 설명}" \
  --body "## Summary
- {작업 요약}

## Block Agent Compliance
| 항목 | 상태 |
|------|------|
| Domain | `{domain}` |
| Block Scope | `features/{domain}/` |
| AGENT_RULES | ✅ 준수 |
| Context Isolation | ✅ 격리됨 |

## Changes
| 파일 | 변경 |
|------|------|
| types.ts | 타입 추가 |
| ... | ... |

## Document References
- 📄 `.claude/agents/{domain}-domain.md`
- 📄 `apps/web/features/{domain}/AGENT_RULES.md`
- 📄 `docs/architecture/0001-block-agent-system.md`

Fixes #{issue_number}

🤖 Generated with [Claude Code](https://claude.com/claude-code)"
```

---

## 최종 보고서 형식

```markdown
# /work-wsoptv 완료 보고서

## 작업 정보
- **지시**: {instruction}
- **도메인**: {domain}
- **블럭**: features/{domain}/

## Phase 0: Agent 라우팅
- Orchestrator: ✅ 로딩
- Domain Agent: ✅ {domain}-domain.md
- AGENT_RULES: ✅ features/{domain}/AGENT_RULES.md

## Phase 1: 컨텍스트 분석
- Architecture 참조: ✅
- LLD 참조: ✅
- 기존 코드 분석: ✅

## Phase 2: 이슈/브랜치
- 이슈: #{issue_number}
- 브랜치: feat/{domain}/issue-{N}-{desc}

## Phase 3: 구현
| 파일 | 변경 | 설명 |
|------|------|------|
| types.ts | +30 | 새 타입 추가 |
| ... | ... | ... |

## Phase 4: 검증
- DO 규칙: ✅ 모두 준수
- DON'T 규칙: ✅ 위반 없음
- 체크리스트: ✅ 완료
- 테스트: ✅ 통과

## Phase 5: 결과
- 커밋: {commit_hash}
- PR: #{pr_number}

## Document Reference Chain
```
orchestrator.md
    ↓ routing
{domain}-domain.md
    ↓ scope
features/{domain}/AGENT_RULES.md
    ↓ constraints
구현 완료
```
```

---

## 예시

```bash
$ /work-wsoptv Auth에 2FA 기능 추가

🔀 Phase 0: Agent 라우팅
   📄 Orchestrator: .claude/agents/orchestrator.md ✅
   📄 Domain: auth-domain (키워드: "Auth", "2FA")
   📄 Domain Agent: .claude/agents/auth-domain.md ✅
   📄 AGENT_RULES: apps/web/features/auth/AGENT_RULES.md ✅

🔍 Phase 1: 컨텍스트 분석 (병렬)
   [Agent 1] Architecture/LLD 분석...
      - Auth Domain 블럭 구조 확인
      - 인증 시퀀스 다이어그램 참조

   [Agent 2] 블럭 코드 분석...
      - 기존 타입: LoginRequest, AuthResponse...
      - 신규 필요: TwoFactorRequest, TwoFactorVerify

📝 Phase 2: 이슈 생성 + 브랜치
   - 이슈 #42 생성: feat(auth): 2FA 기능 추가
   - 브랜치: feat/auth/issue-42-2fa

🔨 Phase 3: 구현 (컨텍스트 격리)
   📁 수정 범위: features/auth/ 만
   ├─ types.ts      +45 lines (TwoFactorRequest, TwoFactorVerify)
   ├─ api/authApi.ts +30 lines (verify2FA, setup2FA)
   ├─ hooks/useAuth.ts +25 lines (2FA 로직)
   └─ index.ts      +3 lines (Public API)

✅ Phase 4: 검증
   - DO 규칙: ✅ 모두 준수
   - DON'T 규칙: ✅ 위반 없음
   - Security Checklist: ✅ 완료
   - 테스트: 12/12 통과

📋 Phase 5: 보고 + PR
   - 커밋: a1b2c3d
   - PR #43 생성 준비 완료

🎉 완료! PR 생성하시겠습니까? (gh pr merge 43 --merge)
```

---

## 연동 커맨드

| 커맨드 | 연동 시점 |
|--------|----------|
| `/pre-work` | Phase 0 전 (선택) |
| `/commit` | Phase 5 |
| `/create-pr` | Phase 5 |

---

**작업 지시를 입력해 주세요.**
