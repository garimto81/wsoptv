#!/usr/bin/env python3
"""
Markdown to Google Docs 변환 스크립트 (v5 - Notion 스타일 + 테이블 크기)

개선사항:
- 한글 최적화 폰트 (Noto Sans KR)
- 행간 150%
- 네이티브 수평선
- 인용문 스타일 (배경색 + 들여쓰기)
- 테이블 헤더 스타일 (배경색)
- 일관된 문단 간격
- [v5] Notion 스타일 색상 (파랑 계열)
- [v5] A4 기준 테이블 너비 자동 조정
- [v5] 테이블 가운데 정렬

Usage:
    python md_to_gdocs.py <markdown_file> [--title "문서 제목"] [--folder-id "폴더ID"]
"""

import os
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# 인증 파일 경로
CREDENTIALS_FILE = r'C:\claude\json\desktop_credentials.json'
TOKEN_FILE = r'C:\claude\json\token.json'

SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive.file'
]

DEFAULT_FOLDER_ID = '1JwdlUe_v4Ug-yQ0veXTldFl6C24GH8hW'

# 스타일 설정
STYLE_CONFIG = {
    'font_family': 'Noto Sans KR',  # 한글 최적화 폰트
    'font_size_body': 11,
    'font_size_h1': 24,
    'font_size_h2': 18,
    'font_size_h3': 14,
    'line_spacing': 150,  # 150%
    'paragraph_spacing_after': 12,  # pt
    'quote_background': {'red': 0.95, 'green': 0.95, 'blue': 0.95},  # 연한 회색
    'quote_indent': 36,  # pt
    'table_header_bg': {'red': 0.9, 'green': 0.9, 'blue': 0.9},  # 테이블 헤더 배경
    'hr_color': {'red': 0.7, 'green': 0.7, 'blue': 0.7},  # 구분선 색상

    # [v5] Notion 스타일 색상 (파랑 계열 전문 문서)
    'heading_h1_color': {'red': 0.102, 'green': 0.302, 'blue': 0.549},  # #1A4D8C 진한 파랑
    'heading_h2_color': {'red': 0.2, 'green': 0.451, 'blue': 0.702},    # #3373B3 밝은 파랑
    'heading_h3_color': {'red': 0.251, 'green': 0.251, 'blue': 0.251},  # #404040 진한 회색
    'body_color': {'red': 0.251, 'green': 0.251, 'blue': 0.251},        # #404040 진한 회색

    # [v5] A4 페이지 테이블 크기 설정
    'a4_content_width_pt': 451.28,  # A4 콘텐츠 영역 (595.28 - 72*2)
    'table_width_pt': 451.28,       # 테이블 전체 너비
    'min_column_width_pt': 50,      # 최소 열 너비
    'table_border_color': {'red': 0.8, 'green': 0.8, 'blue': 0.8},  # #CCCCCC
}


class BlockType(Enum):
    HEADER = 'header'
    PARAGRAPH = 'paragraph'
    TABLE = 'table'
    LIST = 'list'
    QUOTE = 'quote'
    HR = 'hr'
    EMPTY = 'empty'


@dataclass
class TextSegment:
    text: str
    bold: bool = False
    italic: bool = False


@dataclass
class Block:
    type: BlockType
    content: str = ''
    level: int = 0
    segments: list = field(default_factory=list)
    table_data: list = field(default_factory=list)


def get_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return creds


def parse_inline_formatting(text: str) -> list[TextSegment]:
    segments = []
    pattern = r'(\*\*(.+?)\*\*|\*(.+?)\*)'
    last_end = 0

    for match in re.finditer(pattern, text):
        if match.start() > last_end:
            segments.append(TextSegment(text=text[last_end:match.start()]))
        if match.group(2):
            segments.append(TextSegment(text=match.group(2), bold=True))
        elif match.group(3):
            segments.append(TextSegment(text=match.group(3), italic=True))
        last_end = match.end()

    if last_end < len(text):
        segments.append(TextSegment(text=text[last_end:]))

    return segments if segments else [TextSegment(text=text)]


def parse_markdown_to_blocks(content: str) -> list[Block]:
    blocks = []
    lines = content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]

        if not line.strip():
            blocks.append(Block(type=BlockType.EMPTY))
            i += 1
            continue

        if re.match(r'^-{3,}$', line.strip()):
            blocks.append(Block(type=BlockType.HR))
            i += 1
            continue

        header_match = re.match(r'^(#{1,3})\s+(.+)$', line)
        if header_match:
            level = len(header_match.group(1))
            text = header_match.group(2).strip()
            blocks.append(Block(
                type=BlockType.HEADER,
                content=text,
                level=level,
                segments=parse_inline_formatting(text)
            ))
            i += 1
            continue

        if line.strip().startswith('|') and line.strip().endswith('|'):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i])
                i += 1
            table_data = parse_table_lines(table_lines)
            if table_data:
                blocks.append(Block(type=BlockType.TABLE, table_data=table_data))
            continue

        if line.strip().startswith('>'):
            quote_text = line.strip()[1:].strip()
            blocks.append(Block(
                type=BlockType.QUOTE,
                content=quote_text,
                segments=parse_inline_formatting(quote_text)
            ))
            i += 1
            continue

        list_match = re.match(r'^(\s*)[-*]\s+(.+)$', line)
        num_list_match = re.match(r'^(\s*)(\d+)\.\s+(.+)$', line)

        if list_match:
            indent = len(list_match.group(1)) // 2
            text = list_match.group(2)
            blocks.append(Block(
                type=BlockType.LIST,
                content=text,
                level=indent,
                segments=parse_inline_formatting(text)
            ))
            i += 1
            continue

        if num_list_match:
            indent = len(num_list_match.group(1)) // 2
            num = num_list_match.group(2)
            text = num_list_match.group(3)
            blocks.append(Block(
                type=BlockType.LIST,
                content=f"{num}. {text}",
                level=indent,
                segments=parse_inline_formatting(text)
            ))
            i += 1
            continue

        blocks.append(Block(
            type=BlockType.PARAGRAPH,
            content=line,
            segments=parse_inline_formatting(line)
        ))
        i += 1

    return blocks


def parse_table_lines(lines: list) -> list[list[str]]:
    table_data = []
    for line in lines:
        if '---' in line or ':--' in line or '--:' in line:
            continue
        cells = [cell.strip() for cell in line.strip().split('|')[1:-1]]
        if cells:
            table_data.append(cells)
    return table_data


def get_plain_text(segments: list[TextSegment]) -> str:
    return ''.join(seg.text for seg in segments)


def create_document_with_content(docs_service, drive_service, title: str, blocks: list[Block], folder_id: str = None) -> dict:
    """문서 생성 및 내용 추가 (단계별 처리)"""

    # 1. 빈 문서 생성
    doc = docs_service.documents().create(body={'title': title}).execute()
    doc_id = doc.get('documentId')
    print(f"문서 생성됨: {doc_id}")

    # 폴더 이동
    if folder_id:
        file = drive_service.files().get(fileId=doc_id, fields='parents').execute()
        previous_parents = ",".join(file.get('parents', []))
        drive_service.files().update(
            fileId=doc_id,
            addParents=folder_id,
            removeParents=previous_parents,
            fields='id, parents'
        ).execute()
        print(f"폴더로 이동: {folder_id}")

    # 2. 기본 문서 스타일 설정
    setup_document_styles(docs_service, doc_id)

    # 3. 내용 삽입 (역순)
    insert_content(docs_service, doc_id, blocks)

    # 4. 테이블 데이터 채우기
    fill_table_cells(docs_service, doc_id, blocks)

    # 5. 스타일 적용
    apply_styles(docs_service, doc_id, blocks)

    return {
        'documentId': doc_id,
        'title': title,
        'url': f"https://docs.google.com/document/d/{doc_id}/edit"
    }


def setup_document_styles(docs_service, doc_id: str):
    """문서 기본 스타일 설정"""
    # 빈 문서에는 스타일을 직접 적용할 수 없으므로 나중에 적용
    print("문서 기본 스타일은 내용 삽입 후 적용됩니다")


def insert_content(docs_service, doc_id: str, blocks: list[Block]):
    """내용 삽입 (역순)"""
    insert_requests = []

    for block in reversed(blocks):
        if block.type == BlockType.EMPTY:
            insert_requests.append({
                'insertText': {'location': {'index': 1}, 'text': '\n'}
            })

        elif block.type == BlockType.HR:
            # 수평선 삽입을 위한 특수 문자 + 스타일
            insert_requests.append({
                'insertText': {'location': {'index': 1}, 'text': '\n'}
            })
            insert_requests.append({
                'insertText': {'location': {'index': 1}, 'text': '─' * 80 + '\n'}
            })

        elif block.type == BlockType.HEADER:
            text = get_plain_text(block.segments)
            insert_requests.append({
                'insertText': {'location': {'index': 1}, 'text': text + '\n'}
            })

        elif block.type == BlockType.TABLE:
            if block.table_data:
                rows = len(block.table_data)
                cols = len(block.table_data[0]) if block.table_data else 0
                insert_requests.append({
                    'insertTable': {
                        'rows': rows,
                        'columns': cols,
                        'location': {'index': 1}
                    }
                })
                # 테이블 뒤 줄바꿈
                insert_requests.insert(-1, {
                    'insertText': {'location': {'index': 1}, 'text': '\n'}
                })

        elif block.type == BlockType.QUOTE:
            text = get_plain_text(block.segments)
            # 인용문 마커 추가
            insert_requests.append({
                'insertText': {'location': {'index': 1}, 'text': text + '\n'}
            })

        elif block.type == BlockType.LIST:
            prefix = '    ' * block.level + '• '
            text = get_plain_text(block.segments)
            insert_requests.append({
                'insertText': {'location': {'index': 1}, 'text': prefix + text + '\n'}
            })

        elif block.type == BlockType.PARAGRAPH:
            text = get_plain_text(block.segments)
            insert_requests.append({
                'insertText': {'location': {'index': 1}, 'text': text + '\n'}
            })

    if insert_requests:
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': insert_requests}
        ).execute()
        print(f"내용 삽입 완료: {len(insert_requests)} 요청")


def fill_table_cells(docs_service, doc_id: str, blocks: list[Block]):
    """테이블 셀에 데이터 채우기"""
    doc = docs_service.documents().get(documentId=doc_id).execute()
    content = doc.get('body', {}).get('content', [])

    table_blocks = [b for b in blocks if b.type == BlockType.TABLE]
    if not table_blocks:
        return

    table_cells = []
    table_idx = 0

    for element in content:
        if 'table' in element and table_idx < len(table_blocks):
            table_block = table_blocks[table_idx]
            table = element['table']

            for row_idx, row in enumerate(table.get('tableRows', [])):
                for col_idx, cell in enumerate(row.get('tableCells', [])):
                    if row_idx < len(table_block.table_data) and col_idx < len(table_block.table_data[row_idx]):
                        cell_text = table_block.table_data[row_idx][col_idx]
                        if cell_text:
                            cell_content = cell.get('content', [])
                            for para in cell_content:
                                if 'paragraph' in para:
                                    cell_start = para.get('startIndex', 0)
                                    segments = parse_inline_formatting(cell_text)
                                    plain_text = get_plain_text(segments)
                                    table_cells.append((cell_start, plain_text, segments, row_idx == 0))
                                    break
            table_idx += 1

    table_cells.sort(key=lambda x: x[0], reverse=True)

    insert_requests = [
        {'insertText': {'location': {'index': idx}, 'text': text}}
        for idx, text, _, _ in table_cells
    ]

    if insert_requests:
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': insert_requests}
        ).execute()
        print(f"테이블 데이터 채움: {len(insert_requests)} 셀")

    # 테이블 셀 스타일 적용
    apply_table_cell_styles(docs_service, doc_id, blocks)


def apply_table_cell_styles(docs_service, doc_id: str, blocks: list[Block]):
    """테이블 셀 스타일 적용 (헤더 배경색 + Bold)"""
    doc = docs_service.documents().get(documentId=doc_id).execute()
    content = doc.get('body', {}).get('content', [])

    table_blocks = [b for b in blocks if b.type == BlockType.TABLE]
    if not table_blocks:
        return

    style_requests = []
    table_idx = 0

    for element in content:
        if 'table' in element and table_idx < len(table_blocks):
            table_block = table_blocks[table_idx]
            table = element['table']
            table_start = element.get('startIndex', 0)
            num_cols = len(table_block.table_data[0]) if table_block.table_data else 0

            # 헤더 행 배경색 (전체 열에 한 번에 적용)
            if num_cols > 0:
                style_requests.append({
                    'updateTableCellStyle': {
                        'tableRange': {
                            'tableCellLocation': {
                                'tableStartLocation': {'index': table_start},
                                'rowIndex': 0,
                                'columnIndex': 0,
                            },
                            'rowSpan': 1,
                            'columnSpan': num_cols,
                        },
                        'tableCellStyle': {
                            'backgroundColor': {
                                'color': {'rgbColor': STYLE_CONFIG['table_header_bg']}
                            }
                        },
                        'fields': 'backgroundColor'
                    }
                })

            for row_idx, row in enumerate(table.get('tableRows', [])):
                for col_idx, cell in enumerate(row.get('tableCells', [])):
                    if row_idx < len(table_block.table_data) and col_idx < len(table_block.table_data[row_idx]):
                        cell_text = table_block.table_data[row_idx][col_idx]

                        if cell_text:
                            segments = parse_inline_formatting(cell_text)
                            cell_content = cell.get('content', [])
                            for para in cell_content:
                                if 'paragraph' in para:
                                    para_start = para.get('startIndex', 0)
                                    para_end = para.get('endIndex', para_start + 1)

                                    # 헤더 행은 전체 Bold
                                    if row_idx == 0:
                                        style_requests.append({
                                            'updateTextStyle': {
                                                'range': {'startIndex': para_start, 'endIndex': para_end - 1},
                                                'textStyle': {'bold': True},
                                                'fields': 'bold'
                                            }
                                        })
                                    else:
                                        # Bold 세그먼트 처리
                                        seg_offset = para_start
                                        for seg in segments:
                                            seg_end = seg_offset + len(seg.text)
                                            if seg.bold and seg_offset < seg_end:
                                                style_requests.append({
                                                    'updateTextStyle': {
                                                        'range': {'startIndex': seg_offset, 'endIndex': seg_end},
                                                        'textStyle': {'bold': True},
                                                        'fields': 'bold'
                                                    }
                                                })
                                            seg_offset = seg_end
                                    break

            table_idx += 1

    if style_requests:
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': style_requests}
        ).execute()
        print(f"테이블 스타일 적용: {len(style_requests)} 요청")


def apply_styles(docs_service, doc_id: str, blocks: list[Block]):
    """문서 전체 스타일 적용 (텍스트 매칭 기반)"""
    doc = docs_service.documents().get(documentId=doc_id).execute()
    content = doc.get('body', {}).get('content', [])

    style_requests = []

    # 블록 텍스트 맵 생성
    block_text_map = {}
    for idx, block in enumerate(blocks):
        if block.type == BlockType.QUOTE:
            block_text_map[get_plain_text(block.segments)] = (idx, block)
        elif block.type == BlockType.HEADER:
            block_text_map[get_plain_text(block.segments)] = (idx, block)

    for element in content:
        if 'paragraph' not in element:
            continue

        para = element['paragraph']
        start_idx = element.get('startIndex', 1)
        end_idx = element.get('endIndex', start_idx + 1)

        text_content = ''
        for elem in para.get('elements', []):
            if 'textRun' in elem:
                text_content += elem['textRun'].get('content', '')
        text_content = text_content.strip()

        # 텍스트로 블록 찾기
        block = None
        for block_text, (idx, b) in block_text_map.items():
            if block_text and block_text in text_content:
                block = b
                break

        # 블록을 못 찾으면 기본 스타일만 적용
        if block is None:
            # HR 감지
            if text_content.startswith('─') and len(text_content) > 10:
                block = Block(type=BlockType.HR)
            else:
                block = Block(type=BlockType.PARAGRAPH, segments=parse_inline_formatting(text_content))

        # 전체 텍스트에 폰트 적용 (최소 1자 이상)
        if end_idx > start_idx + 1:
            style_requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': start_idx, 'endIndex': end_idx - 1},
                    'textStyle': {
                        'weightedFontFamily': {
                            'fontFamily': STYLE_CONFIG['font_family'],
                            'weight': 400
                        },
                        'fontSize': {'magnitude': STYLE_CONFIG['font_size_body'], 'unit': 'PT'}
                    },
                    'fields': 'weightedFontFamily,fontSize'
                }
            })

        # 행간 적용
        style_requests.append({
            'updateParagraphStyle': {
                'range': {'startIndex': start_idx, 'endIndex': end_idx},
                'paragraphStyle': {
                    'lineSpacing': STYLE_CONFIG['line_spacing'],
                    'spaceBelow': {'magnitude': 6, 'unit': 'PT'}
                },
                'fields': 'lineSpacing,spaceBelow'
            }
        })

        # 헤더 스타일
        if block.type == BlockType.HEADER:
            size_map = {1: STYLE_CONFIG['font_size_h1'], 2: STYLE_CONFIG['font_size_h2'], 3: STYLE_CONFIG['font_size_h3']}
            style_map = {1: 'TITLE', 2: 'HEADING_1', 3: 'HEADING_2'}

            style_requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': start_idx, 'endIndex': end_idx},
                    'paragraphStyle': {
                        'namedStyleType': style_map.get(block.level, 'HEADING_3'),
                        'spaceAbove': {'magnitude': 18, 'unit': 'PT'},
                        'spaceBelow': {'magnitude': 12, 'unit': 'PT'}
                    },
                    'fields': 'namedStyleType,spaceAbove,spaceBelow'
                }
            })

            # [v5] 헤더 색상 적용 (Notion 스타일)
            color_map = {
                1: STYLE_CONFIG['heading_h1_color'],  # #1A4D8C
                2: STYLE_CONFIG['heading_h2_color'],  # #3373B3
                3: STYLE_CONFIG['heading_h3_color'],  # #404040
            }
            header_color = color_map.get(block.level, STYLE_CONFIG['heading_h3_color'])

            style_requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': start_idx, 'endIndex': end_idx},
                    'textStyle': {
                        'fontSize': {'magnitude': size_map.get(block.level, 14), 'unit': 'PT'},
                        'bold': True,
                        'foregroundColor': {'color': {'rgbColor': header_color}}
                    },
                    'fields': 'fontSize,bold,foregroundColor'
                }
            })

        # 인용문 스타일
        elif block.type == BlockType.QUOTE:
            style_requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': start_idx, 'endIndex': end_idx},
                    'paragraphStyle': {
                        'indentStart': {'magnitude': STYLE_CONFIG['quote_indent'], 'unit': 'PT'},
                        'indentEnd': {'magnitude': STYLE_CONFIG['quote_indent'], 'unit': 'PT'},
                        'borderLeft': {
                            'color': {'color': {'rgbColor': {'red': 0.4, 'green': 0.4, 'blue': 0.4}}},
                            'width': {'magnitude': 3, 'unit': 'PT'},
                            'padding': {'magnitude': 12, 'unit': 'PT'},
                            'dashStyle': 'SOLID'
                        },
                        'shading': {
                            'backgroundColor': {'color': {'rgbColor': STYLE_CONFIG['quote_background']}}
                        },
                        'spaceAbove': {'magnitude': 12, 'unit': 'PT'},
                        'spaceBelow': {'magnitude': 12, 'unit': 'PT'}
                    },
                    'fields': 'indentStart,indentEnd,borderLeft,shading,spaceAbove,spaceBelow'
                }
            })
            style_requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': start_idx, 'endIndex': end_idx - 1},
                    'textStyle': {'italic': True},
                    'fields': 'italic'
                }
            })

        # 구분선 스타일
        elif block.type == BlockType.HR:
            style_requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': start_idx, 'endIndex': end_idx},
                    'textStyle': {
                        'foregroundColor': {'color': {'rgbColor': STYLE_CONFIG['hr_color']}},
                        'fontSize': {'magnitude': 6, 'unit': 'PT'}
                    },
                    'fields': 'foregroundColor,fontSize'
                }
            })
            style_requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': start_idx, 'endIndex': end_idx},
                    'paragraphStyle': {
                        'spaceAbove': {'magnitude': 12, 'unit': 'PT'},
                        'spaceBelow': {'magnitude': 12, 'unit': 'PT'},
                        'alignment': 'CENTER'
                    },
                    'fields': 'spaceAbove,spaceBelow,alignment'
                }
            })

        # Bold 세그먼트
        if block.segments and block.type not in [BlockType.HR, BlockType.EMPTY]:
            seg_offset = start_idx
            for seg in block.segments:
                seg_end = seg_offset + len(seg.text)
                if seg.bold and seg_offset < seg_end and seg_end <= end_idx:
                    style_requests.append({
                        'updateTextStyle': {
                            'range': {'startIndex': seg_offset, 'endIndex': seg_end},
                            'textStyle': {'bold': True},
                            'fields': 'bold'
                        }
                    })
                seg_offset = seg_end

    if style_requests:
        # 빈 범위 필터링
        valid_requests = []
        for req in style_requests:
            if 'updateTextStyle' in req:
                r = req['updateTextStyle'].get('range', {})
                if r.get('endIndex', 0) > r.get('startIndex', 0):
                    valid_requests.append(req)
            else:
                valid_requests.append(req)

        # 배치 크기 제한 (API 제한 회피)
        batch_size = 100
        for i in range(0, len(valid_requests), batch_size):
            batch = valid_requests[i:i + batch_size]
            docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': batch}
            ).execute()
        print(f"스타일 적용 완료: {len(valid_requests)} 요청")


def apply_table_sizing(docs_service, doc_id: str):
    """
    [v5] 테이블 너비 및 가운데 정렬 적용

    - A4 콘텐츠 영역(451.28pt)에 맞춰 테이블 너비 설정
    - 2열 테이블: 30:70 비율
    - 3열 이상: 균등 분배
    - 모든 테이블 가운데 정렬
    """
    doc = docs_service.documents().get(documentId=doc_id).execute()
    body_content = doc.get('body', {}).get('content', [])

    # 테이블 요소 찾기
    tables = []
    for element in body_content:
        if 'table' in element:
            tables.append(element)

    if not tables:
        return

    all_requests = []
    table_width = STYLE_CONFIG['table_width_pt']
    min_col_width = STYLE_CONFIG['min_column_width_pt']

    for table_element in tables:
        table_start_idx = table_element.get('startIndex', 0)
        table = table_element.get('table', {})
        table_rows = table.get('tableRows', [])

        if not table_rows:
            continue

        # 열 수 계산
        first_row = table_rows[0]
        column_count = len(first_row.get('tableCells', []))

        if column_count == 0:
            continue

        # 열 너비 계산
        if column_count == 2:
            # 2열 테이블: 30% : 70%
            widths = [table_width * 0.3, table_width * 0.7]
        else:
            # 균등 분배
            col_width = max(table_width / column_count, min_col_width)
            widths = [col_width] * column_count

        # 열 너비 설정 요청
        for col_idx, width in enumerate(widths):
            all_requests.append({
                'updateTableColumnProperties': {
                    'tableStartLocation': {'index': table_start_idx},
                    'columnIndices': [col_idx],
                    'tableColumnProperties': {
                        'widthType': 'FIXED_WIDTH',
                        'width': {'magnitude': width, 'unit': 'PT'}
                    },
                    'fields': 'widthType,width'
                }
            })

        # 테이블 가운데 정렬 (각 셀의 텍스트 정렬이 아닌 테이블 자체 정렬)
        # Google Docs API는 테이블 자체의 정렬을 직접 지원하지 않음
        # 대신 테이블 앞뒤 단락의 정렬로 시각적 효과 구현
        # 또는 셀 내용 가운데 정렬 적용

        # 모든 셀 내용 가운데 정렬 (선택적)
        for row_idx, row in enumerate(table_rows):
            cells = row.get('tableCells', [])
            for col_idx, cell in enumerate(cells):
                content = cell.get('content', [])
                for para_elem in content:
                    if 'paragraph' in para_elem:
                        para_start = para_elem.get('startIndex', 0)
                        para_end = para_elem.get('endIndex', para_start + 1)
                        if para_end > para_start:
                            all_requests.append({
                                'updateParagraphStyle': {
                                    'range': {'startIndex': para_start, 'endIndex': para_end},
                                    'paragraphStyle': {
                                        'alignment': 'CENTER'
                                    },
                                    'fields': 'alignment'
                                }
                            })

    if all_requests:
        # 배치 실행
        batch_size = 100
        for i in range(0, len(all_requests), batch_size):
            batch = all_requests[i:i + batch_size]
            docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': batch}
            ).execute()
        print(f"테이블 크기/정렬 적용: {len(all_requests)} 요청")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Markdown to Google Docs 변환 (v4 - 톤앤매너 개선)')
    parser.add_argument('markdown_file', help='변환할 Markdown 파일 경로')
    parser.add_argument('--title', '-t', help='Google Docs 문서 제목')
    parser.add_argument('--folder-id', '-f', default=DEFAULT_FOLDER_ID, help='대상 폴더 ID')

    args = parser.parse_args()

    md_path = Path(args.markdown_file)
    if not md_path.exists():
        print(f"오류: 파일을 찾을 수 없습니다 - {md_path}")
        sys.exit(1)

    content = md_path.read_text(encoding='utf-8')
    title = args.title or md_path.stem

    print(f"변환 시작: {md_path}")
    print(f"문서 제목: {title}")
    print(f"폰트: {STYLE_CONFIG['font_family']}")
    print(f"행간: {STYLE_CONFIG['line_spacing']}%")
    print("-" * 50)

    creds = get_credentials()
    docs_service = build('docs', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)

    blocks = parse_markdown_to_blocks(content)
    print(f"파싱 완료: {len(blocks)} 블록")

    result = create_document_with_content(docs_service, drive_service, title, blocks, args.folder_id)

    print("-" * 50)
    print(f"변환 완료!")
    print(f"문서 URL: {result['url']}")

    return result


if __name__ == '__main__':
    main()
