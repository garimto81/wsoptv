# -*- coding: utf-8 -*-
"""
Google Workspace 스킬 스타일 + 네이티브 테이블로 Google Docs 문서 생성

핵심 전략:
- 테이블과 텍스트를 분리하여 순차적으로 삽입
- 각 테이블 삽입 후 문서를 다시 읽어서 정확한 인덱스 계산
- Google Workspace 스킬 스타일 적용 (파란색 헤딩, 115% 줄간격)
"""

import json
import re
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


# ============================================================================
# Google Workspace 스킬 스타일 정의
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
    'table_header_bg': hex_to_rgb('#E6E6E6'),
    'table_border': hex_to_rgb('#CCCCCC'),
}

HEADING_STYLES = {
    1: {'color': 'primary_blue', 'size': 18, 'border': True},
    2: {'color': 'accent_blue', 'size': 14, 'border': False},
    3: {'color': 'dark_gray', 'size': 12, 'border': False},
    4: {'color': 'dark_gray', 'size': 11, 'border': False},
}


# ============================================================================
# 마크다운 파서
# ============================================================================

def parse_markdown_sections(content):
    """
    마크다운을 섹션별로 파싱 (테이블과 비테이블 분리)

    Returns:
        list of dict: [{'type': 'text'|'table', 'content': ...}, ...]
    """
    lines = content.split('\n')
    sections = []
    current_text = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # 테이블 시작 감지
        if '|' in line and i + 1 < len(lines) and ('---' in lines[i + 1] or ':-' in lines[i + 1]):
            # 이전 텍스트 섹션 저장
            if current_text:
                sections.append({'type': 'text', 'content': '\n'.join(current_text)})
                current_text = []

            # 테이블 수집
            table_lines = []
            while i < len(lines) and '|' in lines[i]:
                table_lines.append(lines[i])
                i += 1

            sections.append({'type': 'table', 'content': table_lines})
            continue

        current_text.append(line)
        i += 1

    # 남은 텍스트 저장
    if current_text:
        sections.append({'type': 'text', 'content': '\n'.join(current_text)})

    return sections


def parse_table(table_lines):
    """마크다운 테이블 파싱"""
    headers = []
    rows = []

    for line in table_lines:
        line = line.strip()
        if '---' in line or ':-' in line:
            continue

        cells = [c.strip() for c in line.strip('|').split('|')]
        cells = [c for c in cells if c is not None]

        if not headers:
            headers = cells
        else:
            rows.append(cells)

    # 열 수 정규화
    col_count = len(headers) if headers else 0
    normalized_rows = []
    for row in rows:
        if len(row) < col_count:
            row.extend([''] * (col_count - len(row)))
        elif len(row) > col_count:
            row = row[:col_count]
        normalized_rows.append(row)

    return {
        'headers': headers,
        'rows': normalized_rows,
        'col_count': col_count,
        'row_count': len(normalized_rows) + 1  # 헤더 포함
    }


# ============================================================================
# Google Docs API 헬퍼
# ============================================================================

def get_document_end_index(docs_service, doc_id):
    """문서의 현재 끝 인덱스 조회"""
    doc = docs_service.documents().get(documentId=doc_id).execute()
    content = doc.get('body', {}).get('content', [])

    if content:
        last_element = content[-1]
        return last_element.get('endIndex', 1) - 1
    return 1


def insert_text_section(docs_service, doc_id, text, start_index):
    """텍스트 섹션 삽입 및 스타일 적용"""
    lines = text.split('\n')
    requests = []
    headings_to_style = []
    current_idx = start_index

    for line in lines:
        # 수평선 무시
        if line.strip() in ['---', '***', '___']:
            continue

        # 헤딩 처리
        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            heading_text = line.lstrip('#').strip()
            if heading_text and level <= 4:
                # 인라인 마크다운 제거
                clean_text = re.sub(r'\*\*(.+?)\*\*', r'\1', heading_text)
                clean_text = re.sub(r'\*(.+?)\*', r'\1', clean_text)

                requests.append({
                    'insertText': {
                        'location': {'index': current_idx},
                        'text': clean_text + '\n'
                    }
                })

                headings_to_style.append({
                    'start': current_idx,
                    'end': current_idx + len(clean_text),
                    'level': level
                })

                current_idx += len(clean_text) + 1
            continue

        # 일반 텍스트
        if line.strip():
            # 인라인 마크다운 제거
            clean_line = re.sub(r'\*\*(.+?)\*\*', r'\1', line)
            clean_line = re.sub(r'\*(.+?)\*', r'\1', clean_line)

            requests.append({
                'insertText': {
                    'location': {'index': current_idx},
                    'text': clean_line + '\n'
                }
            })
            current_idx += len(clean_line) + 1
        else:
            # 빈 줄
            requests.append({
                'insertText': {
                    'location': {'index': current_idx},
                    'text': '\n'
                }
            })
            current_idx += 1

    # 텍스트 삽입 실행
    if requests:
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()

    # 헤딩 스타일 적용
    style_requests = []
    for h in headings_to_style:
        style = HEADING_STYLES.get(h['level'], HEADING_STYLES[4])

        # 단락 스타일
        style_requests.append({
            'updateParagraphStyle': {
                'range': {'startIndex': h['start'], 'endIndex': h['end'] + 1},
                'paragraphStyle': {
                    'namedStyleType': f'HEADING_{h["level"]}',
                    'spaceAbove': {'magnitude': 16 if h['level'] > 1 else 24, 'unit': 'PT'},
                    'spaceBelow': {'magnitude': 8, 'unit': 'PT'},
                    'lineSpacing': 115,
                },
                'fields': 'namedStyleType,spaceAbove,spaceBelow,lineSpacing'
            }
        })

        # 텍스트 스타일
        style_requests.append({
            'updateTextStyle': {
                'range': {'startIndex': h['start'], 'endIndex': h['end']},
                'textStyle': {
                    'foregroundColor': {'color': {'rgbColor': COLORS[style['color']]}},
                    'fontSize': {'magnitude': style['size'], 'unit': 'PT'},
                    'bold': True,
                },
                'fields': 'foregroundColor,fontSize,bold'
            }
        })

        # H1 하단 구분선
        if style.get('border'):
            style_requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': h['start'], 'endIndex': h['end'] + 1},
                    'paragraphStyle': {
                        'borderBottom': {
                            'color': {'color': {'rgbColor': COLORS['accent_blue']}},
                            'width': {'magnitude': 1, 'unit': 'PT'},
                            'padding': {'magnitude': 4, 'unit': 'PT'},
                            'dashStyle': 'SOLID'
                        }
                    },
                    'fields': 'borderBottom'
                }
            })

    if style_requests:
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': style_requests}
        ).execute()


def insert_table_section(docs_service, doc_id, table_lines, start_index):
    """네이티브 테이블 삽입"""
    table_data = parse_table(table_lines)

    if table_data['col_count'] == 0:
        return

    rows = table_data['row_count']
    cols = table_data['col_count']

    # 1. 빈 테이블 생성
    docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={'requests': [{
            'insertTable': {
                'rows': rows,
                'columns': cols,
                'location': {'index': start_index}
            }
        }]}
    ).execute()

    # 2. 문서 다시 읽어서 테이블 구조 파악
    doc = docs_service.documents().get(documentId=doc_id).execute()

    # 테이블 요소 찾기
    table_element = None
    for element in doc.get('body', {}).get('content', []):
        if 'table' in element:
            if element.get('startIndex', 0) >= start_index:
                table_element = element
                break

    if not table_element:
        print('  [WARN] 테이블 요소를 찾을 수 없음')
        return

    # 3. 셀 내용 채우기 (역순으로)
    all_rows = [table_data['headers']] + table_data['rows']
    cell_requests = []
    header_style_requests = []

    table_rows = table_element['table'].get('tableRows', [])

    for row_idx, table_row in enumerate(table_rows):
        cells = table_row.get('tableCells', [])
        for col_idx, cell in enumerate(cells):
            if row_idx < len(all_rows) and col_idx < len(all_rows[row_idx]):
                content = all_rows[row_idx][col_idx]
                if content:
                    # 셀 내 단락의 시작 인덱스 찾기
                    cell_content = cell.get('content', [])
                    if cell_content:
                        para = cell_content[0]
                        cell_start = para.get('startIndex', 0)

                        # 인라인 마크다운 제거
                        clean_content = re.sub(r'\*\*(.+?)\*\*', r'\1', content)
                        clean_content = re.sub(r'\*(.+?)\*', r'\1', clean_content)

                        cell_requests.append({
                            'insertText': {
                                'location': {'index': cell_start},
                                'text': clean_content
                            }
                        })

                        # 헤더 행 스타일
                        if row_idx == 0:
                            header_style_requests.append({
                                'index': cell_start,
                                'length': len(clean_content)
                            })

    # 역순 정렬 (뒤에서부터 삽입)
    cell_requests.sort(key=lambda x: x['insertText']['location']['index'], reverse=True)

    if cell_requests:
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': cell_requests}
        ).execute()

    # 4. 헤더 스타일 적용 (테이블 다시 읽기)
    doc = docs_service.documents().get(documentId=doc_id).execute()

    style_requests = []
    for element in doc.get('body', {}).get('content', []):
        if 'table' in element:
            if element.get('startIndex', 0) >= start_index:
                table_rows = element['table'].get('tableRows', [])
                if table_rows:
                    # 첫 행 (헤더) 스타일
                    for cell in table_rows[0].get('tableCells', []):
                        cell_content = cell.get('content', [])
                        if cell_content:
                            para = cell_content[0]
                            elements = para.get('paragraph', {}).get('elements', [])
                            for elem in elements:
                                if 'textRun' in elem:
                                    text_content = elem['textRun'].get('content', '').strip()
                                    if text_content:
                                        start = elem.get('startIndex', 0)
                                        end = elem.get('endIndex', start)
                                        style_requests.append({
                                            'updateTextStyle': {
                                                'range': {'startIndex': start, 'endIndex': end - 1},
                                                'textStyle': {
                                                    'bold': True,
                                                    'foregroundColor': {'color': {'rgbColor': COLORS['dark_gray']}}
                                                },
                                                'fields': 'bold,foregroundColor'
                                            }
                                        })
                break

    if style_requests:
        try:
            docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': style_requests}
            ).execute()
        except Exception as e:
            print(f'  [WARN] 헤더 스타일 적용 실패: {e}')


# ============================================================================
# 메인
# ============================================================================

def main():
    # 인증
    TOKEN_FILE = Path('C:/claude/json/token_docs.json')
    FOLDER_ID = '1JwdlUe_v4Ug-yQ0veXTldFl6C24GH8hW'
    SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']

    with open(TOKEN_FILE, 'r', encoding='utf-8') as f:
        token_data = json.load(f)

    creds = Credentials(
        token=token_data.get('token'),
        refresh_token=token_data.get('refresh_token'),
        token_uri=token_data.get('token_uri'),
        client_id=token_data.get('client_id'),
        client_secret=token_data.get('client_secret'),
        scopes=SCOPES,
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    docs_service = build('docs', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)

    # 마크다운 파일 읽기
    md_path = Path('C:/claude/WSOPTV/docs/meeting_vimeo_questions.md')
    content = md_path.read_text(encoding='utf-8')

    # 1. 문서 생성
    title = '[WSOPTV] Vimeo OTT 미팅 질문지 v1'
    doc = docs_service.documents().create(body={'title': title}).execute()
    doc_id = doc.get('documentId')
    print(f'[1/5] 문서 생성됨: {title}')
    print(f'      ID: {doc_id}')

    # 2. 폴더로 이동
    file = drive_service.files().get(fileId=doc_id, fields='parents').execute()
    previous_parents = ','.join(file.get('parents', []))
    drive_service.files().update(
        fileId=doc_id,
        addParents=FOLDER_ID,
        removeParents=previous_parents,
        fields='id, parents'
    ).execute()
    print('[2/5] 폴더로 이동됨')

    # 3. 섹션별 파싱
    sections = parse_markdown_sections(content)
    print(f'[3/5] 섹션 파싱 완료: {len(sections)}개 섹션')

    table_count = sum(1 for s in sections if s['type'] == 'table')
    text_count = sum(1 for s in sections if s['type'] == 'text')
    print(f'      - 텍스트 섹션: {text_count}개')
    print(f'      - 테이블 섹션: {table_count}개')

    # 4. 섹션별 삽입
    print('[4/5] 콘텐츠 삽입 중...')

    for i, section in enumerate(sections):
        start_index = get_document_end_index(docs_service, doc_id)

        if section['type'] == 'text':
            insert_text_section(docs_service, doc_id, section['content'], start_index)
            print(f'      [{i+1}/{len(sections)}] 텍스트 섹션 삽입 완료')
        else:
            insert_table_section(docs_service, doc_id, section['content'], start_index)
            print(f'      [{i+1}/{len(sections)}] 테이블 삽입 완료')

    # 5. 페이지 스타일 적용
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
    print('[5/5] 페이지 스타일 적용됨')

    # 결과 출력
    doc_url = f'https://docs.google.com/document/d/{doc_id}/edit'
    print()
    print('=' * 60)
    print('Google Docs 생성 완료!')
    print(f'URL: {doc_url}')
    print('=' * 60)
    print()
    print('적용된 스타일:')
    print('  - 네이티브 테이블 사용')
    print('  - H1: 진한 파랑 #1A4D8C, 18pt, 하단 구분선')
    print('  - H2: 밝은 파랑 #3373B3, 14pt')
    print('  - H3: 진한 회색 #404040, 12pt')
    print('  - 본문: 115% 줄간격')
    print('  - 페이지: A4, 72pt 여백')


if __name__ == '__main__':
    main()
