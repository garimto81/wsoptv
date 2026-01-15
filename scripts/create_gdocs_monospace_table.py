# -*- coding: utf-8 -*-
"""
Google Workspace 스킬 스타일 + 고정폭 폰트 텍스트 테이블

특징:
- 테이블에 Consolas 폰트 적용 (정렬 유지)
- API 호출 최소화
- Google Workspace 스킬 스타일 (파란색 헤딩 등)
"""

import json
import re
import time
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


# ============================================================================
# 스타일 정의
# ============================================================================

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return {
        'red': int(hex_color[0:2], 16) / 255,
        'green': int(hex_color[2:4], 16) / 255,
        'blue': int(hex_color[4:6], 16) / 255,
    }

COLORS = {
    'primary_blue': hex_to_rgb('#1A4D8C'),
    'accent_blue': hex_to_rgb('#3373B3'),
    'dark_gray': hex_to_rgb('#404040'),
    'text_black': hex_to_rgb('#333333'),
    'table_bg': hex_to_rgb('#F5F5F5'),
}


# ============================================================================
# 마크다운 변환
# ============================================================================

def clean_markdown(text):
    """인라인 마크다운 제거"""
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)
    return text


def get_display_width(text):
    """문자열의 표시 너비 계산 (한글=2, 영문=1)"""
    width = 0
    for char in text:
        if '\uAC00' <= char <= '\uD7A3':  # 한글
            width += 2
        elif '\u4E00' <= char <= '\u9FFF':  # 한자
            width += 2
        else:
            width += 1
    return width


def pad_to_width(text, target_width):
    """목표 너비까지 공백 패딩"""
    current_width = get_display_width(text)
    padding = target_width - current_width
    return text + ' ' * max(0, padding)


def format_table_text(table_lines):
    """마크다운 테이블을 고정폭 텍스트로 변환"""
    rows = []

    for line in table_lines:
        line = line.strip()
        if '---' in line or ':-' in line:
            continue
        cells = [clean_markdown(c.strip()) for c in line.strip('|').split('|')]
        cells = [c for c in cells if c is not None]
        if cells:
            rows.append(cells)

    if not rows:
        return ''

    # 열 너비 계산
    col_count = max(len(row) for row in rows)
    col_widths = [0] * col_count

    for row in rows:
        for i, cell in enumerate(row):
            if i < col_count:
                col_widths[i] = max(col_widths[i], get_display_width(cell))

    # 최소 너비 보장
    col_widths = [max(w, 4) for w in col_widths]

    # 테이블 텍스트 생성
    lines = []

    for row_idx, row in enumerate(rows):
        padded_cells = []
        for i in range(col_count):
            cell = row[i] if i < len(row) else ''
            padded_cells.append(pad_to_width(cell, col_widths[i]))

        line = ' | '.join(padded_cells)
        lines.append(line)

        # 헤더 아래 구분선
        if row_idx == 0:
            separator_cells = ['-' * w for w in col_widths]
            lines.append('-+-'.join(separator_cells))

    return '\n'.join(lines)


def convert_markdown_to_text(content):
    """마크다운을 플레인 텍스트로 변환 (테이블 포함)"""
    lines = content.split('\n')
    result_lines = []
    table_ranges = []  # (start_line, end_line) 테이블 위치

    i = 0
    while i < len(lines):
        line = lines[i]

        # 테이블 감지
        if '|' in line and i + 1 < len(lines) and ('---' in lines[i + 1] or ':-' in lines[i + 1]):
            table_start = len(result_lines)
            table_lines = []
            while i < len(lines) and '|' in lines[i]:
                table_lines.append(lines[i])
                i += 1

            table_text = format_table_text(table_lines)
            if table_text:
                table_lines_count = len(table_text.split('\n'))
                table_ranges.append((table_start, table_start + table_lines_count))
                result_lines.append(table_text)
            continue

        # 수평선 무시
        if line.strip() in ['---', '***', '___']:
            i += 1
            continue

        # 헤딩
        if line.startswith('#'):
            level = min(len(line) - len(line.lstrip('#')), 4)
            text = clean_markdown(line.lstrip('#').strip())
            if text:
                result_lines.append(f'{"#" * level} {text}')
            i += 1
            continue

        # 일반 텍스트
        result_lines.append(clean_markdown(line))
        i += 1

    return '\n'.join(result_lines), table_ranges


# ============================================================================
# 메인
# ============================================================================

def main():
    print('=' * 60)
    print('Google Docs 생성 (고정폭 폰트 테이블)')
    print('=' * 60)

    # 인증
    TOKEN_FILE = Path('C:/claude/json/token_docs.json')
    FOLDER_ID = '1JwdlUe_v4Ug-yQ0veXTldFl6C24GH8hW'

    with open(TOKEN_FILE, 'r', encoding='utf-8') as f:
        token_data = json.load(f)

    creds = Credentials(
        token=token_data.get('token'),
        refresh_token=token_data.get('refresh_token'),
        token_uri=token_data.get('token_uri'),
        client_id=token_data.get('client_id'),
        client_secret=token_data.get('client_secret'),
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    docs_service = build('docs', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)

    # 마크다운 읽기 및 변환
    md_path = Path('C:/claude/WSOPTV/docs/meeting_vimeo_questions.md')
    content = md_path.read_text(encoding='utf-8')

    plain_text, table_ranges = convert_markdown_to_text(content)
    print(f'[INFO] 변환 완료 (테이블 {len(table_ranges)}개)')

    # 1. 문서 생성
    title = '[WSOPTV] Vimeo OTT 미팅 질문지 v1'
    doc = docs_service.documents().create(body={'title': title}).execute()
    doc_id = doc.get('documentId')
    print(f'[1/4] 문서 생성됨: {doc_id}')

    # 2. 폴더로 이동
    file = drive_service.files().get(fileId=doc_id, fields='parents').execute()
    previous_parents = ','.join(file.get('parents', []))
    drive_service.files().update(
        fileId=doc_id,
        addParents=FOLDER_ID,
        removeParents=previous_parents,
    ).execute()
    print('[2/4] 폴더 이동 완료')

    # 3. 콘텐츠 삽입
    print('[3/4] 콘텐츠 삽입 중...')

    requests = [{
        'insertText': {
            'location': {'index': 1},
            'text': plain_text
        }
    }]

    docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={'requests': requests}
    ).execute()
    print('      텍스트 삽입 완료')

    time.sleep(2)

    # 4. 스타일 적용
    print('[4/4] 스타일 적용 중...')

    # 문서 다시 읽기
    doc = docs_service.documents().get(documentId=doc_id).execute()
    doc_content = doc.get('body', {}).get('content', [])

    style_requests = []
    table_style_requests = []

    for elem in doc_content:
        if 'paragraph' not in elem:
            continue

        para = elem['paragraph']
        start_idx = elem.get('startIndex', 0)
        end_idx = elem.get('endIndex', start_idx)

        # 텍스트 추출
        text = ''
        for pe in para.get('elements', []):
            if 'textRun' in pe:
                text += pe['textRun'].get('content', '')
        text = text.strip()

        if not text:
            continue

        text_end = start_idx + len(text)

        # 테이블 라인 (| 포함 또는 --- 구분선)
        if '|' in text or (text.startswith('-') and '-+-' in text):
            table_style_requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': start_idx, 'endIndex': end_idx - 1},
                    'textStyle': {
                        'weightedFontFamily': {'fontFamily': 'Consolas', 'weight': 400},
                        'fontSize': {'magnitude': 9, 'unit': 'PT'},
                        'foregroundColor': {'color': {'rgbColor': COLORS['text_black']}},
                    },
                    'fields': 'weightedFontFamily,fontSize,foregroundColor'
                }
            })
            table_style_requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': start_idx, 'endIndex': end_idx},
                    'paragraphStyle': {
                        'lineSpacing': 100,
                        'spaceBelow': {'magnitude': 0, 'unit': 'PT'},
                    },
                    'fields': 'lineSpacing,spaceBelow'
                }
            })
            continue

        # H1 (# 로 시작)
        if text.startswith('# '):
            actual_text = text[2:]
            style_requests.append({
                'deleteContentRange': {
                    'range': {'startIndex': start_idx, 'endIndex': start_idx + 2}
                }
            })
            style_requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': start_idx, 'endIndex': end_idx},
                    'paragraphStyle': {
                        'namedStyleType': 'HEADING_1',
                        'spaceAbove': {'magnitude': 24, 'unit': 'PT'},
                        'spaceBelow': {'magnitude': 8, 'unit': 'PT'},
                        'lineSpacing': 115,
                        'borderBottom': {
                            'color': {'color': {'rgbColor': COLORS['accent_blue']}},
                            'width': {'magnitude': 1, 'unit': 'PT'},
                            'padding': {'magnitude': 4, 'unit': 'PT'},
                            'dashStyle': 'SOLID'
                        }
                    },
                    'fields': 'namedStyleType,spaceAbove,spaceBelow,lineSpacing,borderBottom'
                }
            })
            style_requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': start_idx, 'endIndex': text_end},
                    'textStyle': {
                        'foregroundColor': {'color': {'rgbColor': COLORS['primary_blue']}},
                        'fontSize': {'magnitude': 18, 'unit': 'PT'},
                        'bold': True,
                    },
                    'fields': 'foregroundColor,fontSize,bold'
                }
            })

        # H2 (## 로 시작)
        elif text.startswith('## '):
            style_requests.append({
                'deleteContentRange': {
                    'range': {'startIndex': start_idx, 'endIndex': start_idx + 3}
                }
            })
            style_requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': start_idx, 'endIndex': end_idx},
                    'paragraphStyle': {
                        'namedStyleType': 'HEADING_2',
                        'spaceAbove': {'magnitude': 16, 'unit': 'PT'},
                        'spaceBelow': {'magnitude': 8, 'unit': 'PT'},
                        'lineSpacing': 115,
                    },
                    'fields': 'namedStyleType,spaceAbove,spaceBelow,lineSpacing'
                }
            })
            style_requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': start_idx, 'endIndex': text_end},
                    'textStyle': {
                        'foregroundColor': {'color': {'rgbColor': COLORS['accent_blue']}},
                        'fontSize': {'magnitude': 14, 'unit': 'PT'},
                        'bold': True,
                    },
                    'fields': 'foregroundColor,fontSize,bold'
                }
            })

        # H3 (### 로 시작)
        elif text.startswith('### '):
            style_requests.append({
                'deleteContentRange': {
                    'range': {'startIndex': start_idx, 'endIndex': start_idx + 4}
                }
            })
            style_requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': start_idx, 'endIndex': end_idx},
                    'paragraphStyle': {
                        'namedStyleType': 'HEADING_3',
                        'spaceAbove': {'magnitude': 12, 'unit': 'PT'},
                        'spaceBelow': {'magnitude': 6, 'unit': 'PT'},
                        'lineSpacing': 115,
                    },
                    'fields': 'namedStyleType,spaceAbove,spaceBelow,lineSpacing'
                }
            })
            style_requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': start_idx, 'endIndex': text_end},
                    'textStyle': {
                        'foregroundColor': {'color': {'rgbColor': COLORS['dark_gray']}},
                        'fontSize': {'magnitude': 12, 'unit': 'PT'},
                        'bold': True,
                    },
                    'fields': 'foregroundColor,fontSize,bold'
                }
            })

        # H4 (#### 로 시작)
        elif text.startswith('#### '):
            style_requests.append({
                'deleteContentRange': {
                    'range': {'startIndex': start_idx, 'endIndex': start_idx + 5}
                }
            })
            style_requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': start_idx, 'endIndex': end_idx},
                    'paragraphStyle': {
                        'namedStyleType': 'HEADING_4',
                        'spaceAbove': {'magnitude': 10, 'unit': 'PT'},
                        'spaceBelow': {'magnitude': 4, 'unit': 'PT'},
                        'lineSpacing': 115,
                    },
                    'fields': 'namedStyleType,spaceAbove,spaceBelow,lineSpacing'
                }
            })
            style_requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': start_idx, 'endIndex': text_end},
                    'textStyle': {
                        'foregroundColor': {'color': {'rgbColor': COLORS['dark_gray']}},
                        'fontSize': {'magnitude': 11, 'unit': 'PT'},
                        'bold': True,
                    },
                    'fields': 'foregroundColor,fontSize,bold'
                }
            })

        # 일반 본문
        else:
            style_requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': start_idx, 'endIndex': end_idx},
                    'paragraphStyle': {
                        'lineSpacing': 115,
                        'spaceBelow': {'magnitude': 4, 'unit': 'PT'},
                    },
                    'fields': 'lineSpacing,spaceBelow'
                }
            })

    # 테이블 스타일 먼저 적용 (인덱스 변경 없음)
    if table_style_requests:
        for i in range(0, len(table_style_requests), 20):
            batch = table_style_requests[i:i+20]
            try:
                docs_service.documents().batchUpdate(
                    documentId=doc_id,
                    body={'requests': batch}
                ).execute()
            except Exception as e:
                print(f'      [WARN] 테이블 스타일 배치 실패: {e}')
            time.sleep(1)
        print(f'      테이블 스타일 적용 ({len(table_style_requests)} 요청)')

    # 헤딩 스타일은 deleteContentRange가 있어서 역순으로 적용
    # (삭제로 인한 인덱스 시프트 방지)
    style_requests.reverse()

    if style_requests:
        for i in range(0, len(style_requests), 15):
            batch = style_requests[i:i+15]
            try:
                docs_service.documents().batchUpdate(
                    documentId=doc_id,
                    body={'requests': batch}
                ).execute()
            except Exception as e:
                print(f'      [WARN] 스타일 배치 실패: {e}')
            time.sleep(1)
        print(f'      헤딩 스타일 적용 ({len(style_requests)} 요청)')

    # 페이지 스타일
    time.sleep(1)
    page_requests = [{
        'updateDocumentStyle': {
            'documentStyle': {
                'pageSize': {
                    'width': {'magnitude': 595.28, 'unit': 'PT'},
                    'height': {'magnitude': 841.89, 'unit': 'PT'}
                },
                'marginTop': {'magnitude': 72, 'unit': 'PT'},
                'marginBottom': {'magnitude': 72, 'unit': 'PT'},
                'marginLeft': {'magnitude': 72, 'unit': 'PT'},
                'marginRight': {'magnitude': 72, 'unit': 'PT'},
            },
            'fields': 'pageSize,marginTop,marginBottom,marginLeft,marginRight'
        }
    }]

    docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={'requests': page_requests}
    ).execute()
    print('      페이지 스타일 적용 (A4, 72pt 여백)')

    # 결과
    doc_url = f'https://docs.google.com/document/d/{doc_id}/edit'
    print()
    print('=' * 60)
    print('완료!')
    print(f'URL: {doc_url}')
    print('=' * 60)
    print()
    print('적용된 스타일:')
    print('  - 테이블: Consolas 9pt (고정폭)')
    print('  - H1: 진한 파랑 #1A4D8C, 18pt, 하단 구분선')
    print('  - H2: 밝은 파랑 #3373B3, 14pt')
    print('  - H3: 진한 회색 #404040, 12pt')
    print('  - 본문: 115% 줄간격')
    print('  - 페이지: A4, 72pt 여백')


if __name__ == '__main__':
    main()
