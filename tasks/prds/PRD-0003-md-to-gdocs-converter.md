# PRD-0003: Markdown to Google Docs 변환 도구

| 항목 | 값 |
|------|---|
| **Version** | 1.0 |
| **Status** | Completed |
| **Priority** | P1 |
| **Created** | 2026-01-07 |
| **Author** | Claude Code |

---

## Executive Summary

### 목적
Markdown 문서를 Google Docs로 변환하는 Python 스크립트 개발. 네이티브 테이블, 스타일, 폰트를 적용하여 전문적인 문서 품질 달성.

### 배경
- Google Docs URL로 직접 콘텐츠 접근 불가 (JavaScript 동적 로딩)
- 기존 변환 도구의 품질 문제 (ASCII 테이블, 스타일 누락)
- WSOPTV 프로젝트의 미팅 보고서 등 문서화 필요

### 핵심 결과물
- `scripts/md_to_gdocs.py` - 변환 스크립트 (v5)
- 네이티브 Google Docs 테이블
- 한글 최적화 폰트 (Noto Sans KR)
- 인용문/헤더/Bold 스타일 완벽 지원

---

## 기술 스펙

### 입력
- Markdown 파일 (.md)
- 옵션: 문서 제목, 대상 폴더 ID

### 출력
- Google Docs 문서
- URL 반환

### 변환 매핑

| Markdown | Google Docs |
|----------|-------------|
| `# H1` | Title (24pt, Bold) |
| `## H2` | Heading 1 (18pt, Bold) |
| `### H3` | Heading 2 (14pt, Bold) |
| `**bold**` | Bold 스타일 |
| `> quote` | 배경색 + 왼쪽 테두리 + 들여쓰기 |
| `| 표 |` | 네이티브 테이블 (헤더 배경색) |
| `---` | 회색 구분선 |
| `- 목록` | Bullet list (•) |

### 스타일 설정

```python
STYLE_CONFIG = {
    'font_family': 'Noto Sans KR',
    'font_size_body': 11,
    'font_size_h1': 24,
    'font_size_h2': 18,
    'font_size_h3': 14,
    'line_spacing': 150,  # 150%
    'quote_background': {'red': 0.95, 'green': 0.95, 'blue': 0.95},
    'quote_indent': 36,  # pt
    'table_header_bg': {'red': 0.9, 'green': 0.9, 'blue': 0.9},
}
```

---

## 아키텍처

### 처리 흐름

```
Markdown 파일
      │
      ▼
┌─────────────────────────────────┐
│ 1. 파싱 (parse_markdown_to_blocks) │
│    - Block 타입 분류            │
│    - 인라인 포맷팅 파싱         │
└─────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────┐
│ 2. 문서 생성 (create_document)  │
│    - 빈 Google Docs 생성        │
│    - 폴더 이동                  │
└─────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────┐
│ 3. 역순 삽입 (insert_content)   │
│    - index=1에 역순 삽입        │
│    - 인덱스 계산 회피           │
└─────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────┐
│ 4. 테이블 채우기 (fill_table)   │
│    - 셀 데이터 삽입 (역순)      │
│    - 헤더 배경색 적용           │
└─────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────┐
│ 5. 스타일 적용 (apply_styles)   │
│    - 텍스트 매칭 기반           │
│    - 폰트/행간/인용문 스타일    │
└─────────────────────────────────┘
      │
      ▼
Google Docs URL 반환
```

### Block 타입

```python
class BlockType(Enum):
    HEADER = 'header'
    PARAGRAPH = 'paragraph'
    TABLE = 'table'
    LIST = 'list'
    QUOTE = 'quote'
    HR = 'hr'
    EMPTY = 'empty'
```

---

## 버전 히스토리

| 버전 | 날짜 | 변경 사항 |
|------|------|----------|
| v1 | 2026-01-07 | 초기 구현 (순차 삽입, ASCII 테이블) |
| v2 | 2026-01-07 | 역순 삽입 방식 도입 |
| v3 | 2026-01-07 | 네이티브 테이블 + Bold 적용 |
| v4 | 2026-01-07 | 톤앤매너 개선 (폰트, 행간, 인용문) |
| v5 | 2026-01-07 | 텍스트 매칭 기반 스타일 적용 |

### 품질 개선 추이

| 항목 | v1 | v5 |
|------|:--:|:--:|
| 테이블 | ASCII 텍스트 | 네이티브 |
| 테이블 헤더 배경 | ❌ | ✅ |
| Bold | 43% | 100% |
| 인용문 스타일 | ❌ | ✅ |
| 한글 폰트 | Arial | Noto Sans KR |
| 행간 | 115% | 150% |
| **종합 점수** | C+ | B+ |

---

## 사용법

### CLI

```bash
python scripts/md_to_gdocs.py <markdown_file> [--title "문서 제목"] [--folder-id "폴더ID"]
```

### 예시

```bash
# 기본 사용
python scripts/md_to_gdocs.py docs/meeting_report.md

# 제목 지정
python scripts/md_to_gdocs.py docs/report.md --title "[WSOPTV] 미팅 보고서"

# 특정 폴더에 저장
python scripts/md_to_gdocs.py docs/report.md --folder-id "1JwdlUe..."
```

---

## 의존성

### Python 패키지

```
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
```

### 인증 파일

| 파일 | 경로 | 용도 |
|------|------|------|
| OAuth 클라이언트 | `C:\claude\json\desktop_credentials.json` | API 인증 |
| OAuth 토큰 | `C:\claude\json\token.json` | 액세스 토큰 |

### 필요 스코프

```python
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive.file'
]
```

---

## 제한 사항

| 항목 | 상태 | 비고 |
|------|:----:|------|
| 이미지 삽입 | ❌ | 미지원 (향후 추가) |
| 코드 블록 | ⚠️ | 일반 텍스트로 처리 |
| 중첩 리스트 | ⚠️ | 단일 레벨만 |
| 테이블 셀 병합 | ❌ | 미지원 |

---

## 테스트 결과

### 검증 문서
- 소스: `docs/meeting_malkum_report.md`
- 결과: `[WSOPTV] 맑음 소프트 미팅 보고서 v5`
- URL: https://docs.google.com/document/d/1dgUxLaaSQFeA1077hTN_A4pqVM-VICVFJl9KmOd48Y4/edit

### 검증 항목

| 항목 | 원본 | 변환 결과 | 일치 |
|------|:---:|:--------:|:----:|
| H1 | 1 | 1 | ✅ |
| H2 | 7 | 7 | ✅ |
| H3 | 7 | 7 | ✅ |
| 테이블 | 9 | 9 | ✅ |
| 테이블 행 | 47 | 47 | ✅ |
| Bold | 7 | 7 | ✅ |
| 인용문 | 3 | 3 | ✅ |

---

## 관련 문서

- Google Workspace Skill: `.claude/skills/google-workspace/google-workspace.md`
- 변환 스크립트: `scripts/md_to_gdocs.py`
