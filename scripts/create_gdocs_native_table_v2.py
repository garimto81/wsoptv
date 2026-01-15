# -*- coding: utf-8 -*-
"""
Google Workspace 스킬 스타일 + 네이티브 테이블 (API 최적화 버전)

최적화:
- API 호출 최소화 (섹션 묶음 처리)
- 요청 간 지연 추가 (쿼터 관리)
- 테이블 처리 간소화
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
}


# ============================================================================
# 마크다운 파서
# ============================================================================

def clean_markdown(text):
    """인라인 마크다운 제거"""
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)
    return text


def parse_table(table_lines):
    """마크다운 테이블 파싱"""
    headers = []
    rows = []

    for line in table_lines:
        line = line.strip()
        if '---' in line or ':-' in line:
            continue
        cells = [clean_markdown(c.strip()) for c in line.strip('|').split('|')]
        cells = [c for c in cells if c is not None]
        if not headers:
            headers = cells
        else:
            rows.append(cells)

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
        'row_count': len(normalized_rows) + 1
    }


def parse_markdown_to_elements(content):
    """마크다운을 요소 리스트로 변환"""
    lines = content.split('\n')
    elements = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # 테이블 감지
        if '|' in line and i + 1 < len(lines) and ('---' in lines[i + 1] or ':-' in lines[i + 1]):
            table_lines = []
            while i < len(lines) and '|' in lines[i]:
                table_lines.append(lines[i])
                i += 1
            elements.append({'type': 'table', 'data': parse_table(table_lines)})
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
                elements.append({'type': 'heading', 'level': level, 'text': text})
            i += 1
            continue

        # 일반 텍스트
        text = clean_markdown(line)
        elements.append({'type': 'text', 'text': text})
        i += 1

    return elements


# ============================================================================
# Google Docs 생성
# ============================================================================

def main():
    print('=' * 60)
    print('Google Docs 생성 (네이티브 테이블 + API 최적화)')
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

    # 마크다운 파일 읽기
    md_path = Path('C:/claude/WSOPTV/docs/meeting_vimeo_questions.md')
    content = md_path.read_text(encoding='utf-8')

    # 요소 파싱
    elements = parse_markdown_to_elements(content)
    table_count = sum(1 for e in elements if e['type'] == 'table')
    print(f'[INFO] 파싱 완료: {len(elements)} 요소 (테이블 {table_count}개)')

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

    # 3. 콘텐츠 삽입 (배치 처리)
    print('[3/4] 콘텐츠 삽입 중...')

    current_index = 1
    batch_count = 0
    headings_info = []  # 나중에 스타일 적용용

    # 요소를 배치로 묶어서 처리 (5개씩)
    batch_size = 5
    for batch_start in range(0, len(elements), batch_size):
        batch_elements = elements[batch_start:batch_start + batch_size]
        requests = []

        for elem in batch_elements:
            if elem['type'] == 'text':
                text = elem['text']
                if text.strip():
                    requests.append({
                        'insertText': {
                            'location': {'index': current_index},
                            'text': text + '\n'
                        }
                    })
                    current_index += len(text) + 1
                else:
                    requests.append({
                        'insertText': {
                            'location': {'index': current_index},
                            'text': '\n'
                        }
                    })
                    current_index += 1

            elif elem['type'] == 'heading':
                headings_info.append({
                    'start': current_index,
                    'end': current_index + len(elem['text']),
                    'level': elem['level']
                })
                requests.append({
                    'insertText': {
                        'location': {'index': current_index},
                        'text': elem['text'] + '\n'
                    }
                })
                current_index += len(elem['text']) + 1

            elif elem['type'] == 'table':
                table_data = elem['data']
                if table_data['col_count'] > 0:
                    # 테이블 삽입
                    requests.append({
                        'insertTable': {
                            'rows': table_data['row_count'],
                            'columns': table_data['col_count'],
                            'location': {'index': current_index}
                        }
                    })

                    # 테이블 크기 계산 (대략적)
                    # 테이블 구조: 테이블(1) + 각 행(1 + 열*2)
                    table_struct_size = 1
                    for _ in range(table_data['row_count']):
                        table_struct_size += 1 + table_data['col_count'] * 2

                    current_index += table_struct_size

        if requests:
            try:
                docs_service.documents().batchUpdate(
                    documentId=doc_id,
                    body={'requests': requests}
                ).execute()
                batch_count += 1
                print(f'      배치 {batch_count} 완료 ({len(requests)} 요청)')
            except Exception as e:
                print(f'      [WARN] 배치 {batch_count + 1} 실패: {e}')

            # 쿼터 관리: 요청 간 지연
            time.sleep(1.5)

    # 문서 다시 읽어서 테이블에 내용 채우기
    print('      테이블 내용 채우기...')
    time.sleep(2)

    doc = docs_service.documents().get(documentId=doc_id).execute()
    doc_content = doc.get('body', {}).get('content', [])

    # 테이블 찾아서 내용 채우기
    table_elements = [e for e in doc_content if 'table' in e]
    table_data_list = [e['data'] for e in elements if e['type'] == 'table']

    for table_idx, (table_elem, table_data) in enumerate(zip(table_elements, table_data_list)):
        all_rows = [table_data['headers']] + table_data['rows']
        cell_requests = []

        table_rows = table_elem['table'].get('tableRows', [])
        for row_idx, table_row in enumerate(table_rows):
            cells = table_row.get('tableCells', [])
            for col_idx, cell in enumerate(cells):
                if row_idx < len(all_rows) and col_idx < len(all_rows[row_idx]):
                    content = all_rows[row_idx][col_idx]
                    if content:
                        cell_content = cell.get('content', [])
                        if cell_content:
                            cell_start = cell_content[0].get('startIndex', 0)
                            cell_requests.append({
                                'insertText': {
                                    'location': {'index': cell_start},
                                    'text': content
                                }
                            })

        # 역순 정렬
        cell_requests.sort(key=lambda x: x['insertText']['location']['index'], reverse=True)

        if cell_requests:
            try:
                docs_service.documents().batchUpdate(
                    documentId=doc_id,
                    body={'requests': cell_requests}
                ).execute()
                print(f'      테이블 {table_idx + 1}/{len(table_elements)} 내용 채움')
            except Exception as e:
                print(f'      [WARN] 테이블 {table_idx + 1} 내용 채우기 실패: {e}')
            time.sleep(1.5)

    # 4. 스타일 적용
    print('[4/4] 스타일 적용 중...')
    time.sleep(2)

    # 문서 다시 읽기 (인덱스가 변경됨)
    doc = docs_service.documents().get(documentId=doc_id).execute()
    doc_content = doc.get('body', {}).get('content', [])

    # 헤딩 찾아서 스타일 적용
    style_requests = []
    for elem in doc_content:
        if 'paragraph' in elem:
            para = elem['paragraph']
            para_style = para.get('paragraphStyle', {})
            named_style = para_style.get('namedStyleType', '')

            # 텍스트 추출
            text = ''
            start_idx = None
            for pe in para.get('elements', []):
                if 'textRun' in pe:
                    if start_idx is None:
                        start_idx = pe.get('startIndex', 0)
                    text += pe['textRun'].get('content', '')

            text = text.strip()
            if not text or start_idx is None:
                continue

            end_idx = start_idx + len(text)

            # 헤딩 판단 (H1-H4 형식의 텍스트)
            # 원본 마크다운에서 헤딩이었던 텍스트 찾기
            for h_info in headings_info:
                # 텍스트 매칭으로 헤딩 찾기 (정확한 인덱스는 변경됨)
                pass

            # H1 스타일 (문서 제목)
            if text.startswith('[WSOPTV]'):
                style_requests.append({
                    'updateParagraphStyle': {
                        'range': {'startIndex': start_idx, 'endIndex': end_idx + 1},
                        'paragraphStyle': {
                            'namedStyleType': 'HEADING_1',
                            'spaceAbove': {'magnitude': 24, 'unit': 'PT'},
                            'spaceBelow': {'magnitude': 8, 'unit': 'PT'},
                            'borderBottom': {
                                'color': {'color': {'rgbColor': COLORS['accent_blue']}},
                                'width': {'magnitude': 1, 'unit': 'PT'},
                                'padding': {'magnitude': 4, 'unit': 'PT'},
                                'dashStyle': 'SOLID'
                            }
                        },
                        'fields': 'namedStyleType,spaceAbove,spaceBelow,borderBottom'
                    }
                })
                style_requests.append({
                    'updateTextStyle': {
                        'range': {'startIndex': start_idx, 'endIndex': end_idx},
                        'textStyle': {
                            'foregroundColor': {'color': {'rgbColor': COLORS['primary_blue']}},
                            'fontSize': {'magnitude': 18, 'unit': 'PT'},
                            'bold': True,
                        },
                        'fields': 'foregroundColor,fontSize,bold'
                    }
                })

            # Executive Summary 등 주요 섹션
            elif text in ['Executive Summary', '핵심 확인 항목 (MVP 관련)', '질문 목록 (11개)',
                          '기술 검증 결과 (미팅 후 작성)', '비용 영향 요소 (미팅 후 작성)',
                          '고려사항', '권고 사항 (미팅 후 작성)', '후속 조치 필요 항목 (미팅 후 작성)',
                          '미결 사항 (미팅 후 작성)']:
                style_requests.append({
                    'updateParagraphStyle': {
                        'range': {'startIndex': start_idx, 'endIndex': end_idx + 1},
                        'paragraphStyle': {
                            'namedStyleType': 'HEADING_2',
                            'spaceAbove': {'magnitude': 16, 'unit': 'PT'},
                            'spaceBelow': {'magnitude': 8, 'unit': 'PT'},
                        },
                        'fields': 'namedStyleType,spaceAbove,spaceBelow'
                    }
                })
                style_requests.append({
                    'updateTextStyle': {
                        'range': {'startIndex': start_idx, 'endIndex': end_idx},
                        'textStyle': {
                            'foregroundColor': {'color': {'rgbColor': COLORS['accent_blue']}},
                            'fontSize': {'magnitude': 14, 'unit': 'PT'},
                            'bold': True,
                        },
                        'fields': 'foregroundColor,fontSize,bold'
                    }
                })

            # H3 스타일 (서브섹션)
            elif text in ['미팅 목적', '업체 개요', '플레이어/SDK (3개)', 'OTT/앱 (3개)',
                          '인프라/수익화 (3개)', '연동/운영 (2개)', '확인된 역량', '기술적 제약사항',
                          '비용 절감 포인트', '비용 증가 요소']:
                style_requests.append({
                    'updateTextStyle': {
                        'range': {'startIndex': start_idx, 'endIndex': end_idx},
                        'textStyle': {
                            'foregroundColor': {'color': {'rgbColor': COLORS['dark_gray']}},
                            'fontSize': {'magnitude': 12, 'unit': 'PT'},
                            'bold': True,
                        },
                        'fields': 'foregroundColor,fontSize,bold'
                    }
                })

            # Q1-Q11 질문
            elif text.startswith('Q') and '.' in text[:4]:
                style_requests.append({
                    'updateTextStyle': {
                        'range': {'startIndex': start_idx, 'endIndex': end_idx},
                        'textStyle': {
                            'foregroundColor': {'color': {'rgbColor': COLORS['dark_gray']}},
                            'fontSize': {'magnitude': 11, 'unit': 'PT'},
                            'bold': True,
                        },
                        'fields': 'foregroundColor,fontSize,bold'
                    }
                })

    # 스타일 적용 (배치로)
    if style_requests:
        # 10개씩 배치
        for i in range(0, len(style_requests), 10):
            batch = style_requests[i:i+10]
            try:
                docs_service.documents().batchUpdate(
                    documentId=doc_id,
                    body={'requests': batch}
                ).execute()
            except Exception as e:
                print(f'      [WARN] 스타일 배치 실패: {e}')
            time.sleep(1)

    # 페이지 스타일
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

    # 결과
    doc_url = f'https://docs.google.com/document/d/{doc_id}/edit'
    print()
    print('=' * 60)
    print('완료!')
    print(f'URL: {doc_url}')
    print('=' * 60)


if __name__ == '__main__':
    main()
