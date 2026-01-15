#!/usr/bin/env python3
"""Markdown to Google Docs 변환 + 스타일 적용 통합 스크립트"""

import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_FILE = r'C:\claude\json\token.json'
SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']

# Colors
PRIMARY_BLUE = {'red': 0.10, 'green': 0.30, 'blue': 0.55}
ACCENT_BLUE = {'red': 0.20, 'green': 0.45, 'blue': 0.70}
DARK_GRAY = {'red': 0.25, 'green': 0.25, 'blue': 0.25}
TABLE_HEADER_BG = {'red': 0.9, 'green': 0.9, 'blue': 0.9}


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


@dataclass
class Block:
    type: BlockType
    content: str = ''
    level: int = 0
    segments: list = field(default_factory=list)
    table_data: list = field(default_factory=list)


def parse_inline_formatting(text):
    segments = []
    pattern = r'(\*\*(.+?)\*\*)'
    last_end = 0
    for match in re.finditer(pattern, text):
        if match.start() > last_end:
            segments.append(TextSegment(text=text[last_end:match.start()]))
        segments.append(TextSegment(text=match.group(2), bold=True))
        last_end = match.end()
    if last_end < len(text):
        segments.append(TextSegment(text=text[last_end:]))
    return segments if segments else [TextSegment(text=text)]


def get_plain_text(segments):
    return ''.join(seg.text for seg in segments)


def parse_table_lines(lines):
    table_data = []
    for line in lines:
        if '---' in line or ':--' in line:
            continue
        cells = [cell.strip() for cell in line.strip().split('|')[1:-1]]
        if cells:
            table_data.append(cells)
    return table_data


def parse_markdown(content):
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
        header_match = re.match(r'^(#{1,4})\s+(.+)$', line)
        if header_match:
            level = len(header_match.group(1))
            text = header_match.group(2).strip()
            blocks.append(Block(type=BlockType.HEADER, content=text, level=level, segments=parse_inline_formatting(text)))
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
        list_match = re.match(r'^(\s*)[-*]\s+(.+)$', line)
        if list_match:
            indent = len(list_match.group(1)) // 2
            text = list_match.group(2)
            blocks.append(Block(type=BlockType.LIST, content=text, level=indent, segments=parse_inline_formatting(text)))
            i += 1
            continue
        blocks.append(Block(type=BlockType.PARAGRAPH, content=line, segments=parse_inline_formatting(line)))
        i += 1
    return blocks


def apply_styles(docs_service, doc_id, blocks):
    """Apply comprehensive styles to the document"""

    # Get document structure
    doc = docs_service.documents().get(documentId=doc_id).execute()
    content = doc.get('body', {}).get('content', [])
    end_index = max(el.get('endIndex', 1) for el in content)

    requests = []

    # 1. Page style (A4)
    requests.append({
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
    })

    # 2. Body text style
    if end_index > 2:
        requests.append({
            'updateTextStyle': {
                'range': {'startIndex': 1, 'endIndex': end_index - 1},
                'textStyle': {
                    'weightedFontFamily': {'fontFamily': 'Noto Sans KR', 'weight': 400},
                    'fontSize': {'magnitude': 11, 'unit': 'PT'}
                },
                'fields': 'weightedFontFamily,fontSize'
            }
        })
        requests.append({
            'updateParagraphStyle': {
                'range': {'startIndex': 1, 'endIndex': end_index - 1},
                'paragraphStyle': {
                    'lineSpacing': 130,
                    'spaceBelow': {'magnitude': 6, 'unit': 'PT'}
                },
                'fields': 'lineSpacing,spaceBelow'
            }
        })

    # Apply base styles
    docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()
    print(f'  Applied base styles: {len(requests)} requests')

    # 3. Find and style headings
    doc = docs_service.documents().get(documentId=doc_id).execute()
    content = doc.get('body', {}).get('content', [])

    # H2 keywords
    h2_keywords = [
        '미팅 목적', '업체 개요', '핵심 확인 항목', '질문 목록',
        '기술 검증 결과', '비용 영향 요소', '고려사항', '권고 사항',
        '후속 조치 필요 항목', '미결 사항', 'Executive Summary'
    ]

    # H3 keywords
    h3_keywords = [
        '플레이어/SDK', 'OTT/앱', '인프라/수익화', '연동/운영',
        '확인된 역량', '기술적 제약사항', '비용 절감 포인트', '비용 증가 요소'
    ]

    heading_requests = []
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

        if not text_content or end_idx <= start_idx + 1:
            continue

        # Detect heading level
        is_title = text_content.startswith('[WSOPTV]')
        is_h2 = any(kw in text_content for kw in h2_keywords)
        is_h3 = any(kw in text_content for kw in h3_keywords)
        is_question = text_content.startswith('Q') and '.' in text_content[:4]
        is_hr = chr(9472) in text_content

        if is_title:
            heading_requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': start_idx, 'endIndex': end_idx - 1},
                    'textStyle': {
                        'foregroundColor': {'color': {'rgbColor': PRIMARY_BLUE}},
                        'bold': True,
                        'fontSize': {'magnitude': 22, 'unit': 'PT'}
                    },
                    'fields': 'foregroundColor,bold,fontSize'
                }
            })
            heading_requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': start_idx, 'endIndex': end_idx},
                    'paragraphStyle': {
                        'spaceAbove': {'magnitude': 0, 'unit': 'PT'},
                        'spaceBelow': {'magnitude': 16, 'unit': 'PT'},
                        'alignment': 'CENTER'
                    },
                    'fields': 'spaceAbove,spaceBelow,alignment'
                }
            })
        elif is_h2:
            heading_requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': start_idx, 'endIndex': end_idx - 1},
                    'textStyle': {
                        'foregroundColor': {'color': {'rgbColor': PRIMARY_BLUE}},
                        'bold': True,
                        'fontSize': {'magnitude': 16, 'unit': 'PT'}
                    },
                    'fields': 'foregroundColor,bold,fontSize'
                }
            })
            heading_requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': start_idx, 'endIndex': end_idx},
                    'paragraphStyle': {
                        'borderBottom': {
                            'color': {'color': {'rgbColor': ACCENT_BLUE}},
                            'width': {'magnitude': 1, 'unit': 'PT'},
                            'padding': {'magnitude': 4, 'unit': 'PT'},
                            'dashStyle': 'SOLID'
                        },
                        'spaceAbove': {'magnitude': 18, 'unit': 'PT'},
                        'spaceBelow': {'magnitude': 10, 'unit': 'PT'}
                    },
                    'fields': 'borderBottom,spaceAbove,spaceBelow'
                }
            })
        elif is_h3 or is_question:
            heading_requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': start_idx, 'endIndex': end_idx - 1},
                    'textStyle': {
                        'foregroundColor': {'color': {'rgbColor': ACCENT_BLUE}},
                        'bold': True,
                        'fontSize': {'magnitude': 13, 'unit': 'PT'}
                    },
                    'fields': 'foregroundColor,bold,fontSize'
                }
            })
            heading_requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': start_idx, 'endIndex': end_idx},
                    'paragraphStyle': {
                        'spaceAbove': {'magnitude': 14, 'unit': 'PT'},
                        'spaceBelow': {'magnitude': 6, 'unit': 'PT'}
                    },
                    'fields': 'spaceAbove,spaceBelow'
                }
            })
        elif is_hr:
            heading_requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': start_idx, 'endIndex': end_idx - 1},
                    'textStyle': {
                        'foregroundColor': {'color': {'rgbColor': {'red': 0.7, 'green': 0.7, 'blue': 0.7}}},
                        'fontSize': {'magnitude': 6, 'unit': 'PT'}
                    },
                    'fields': 'foregroundColor,fontSize'
                }
            })
            heading_requests.append({
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

    if heading_requests:
        for i in range(0, len(heading_requests), 50):
            batch = heading_requests[i:i+50]
            docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': batch}).execute()
        print(f'  Applied heading styles: {len(heading_requests)} requests')

    # 4. Apply table header styles
    doc = docs_service.documents().get(documentId=doc_id).execute()
    content = doc.get('body', {}).get('content', [])

    table_requests = []
    for element in content:
        if 'table' not in element:
            continue

        table = element['table']
        table_start = element.get('startIndex', 0)
        num_cols = table.get('columns', 0)

        if num_cols > 0:
            table_requests.append({
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
                        'backgroundColor': {'color': {'rgbColor': TABLE_HEADER_BG}}
                    },
                    'fields': 'backgroundColor'
                }
            })

            for row in table.get('tableRows', [])[:1]:
                for cell in row.get('tableCells', []):
                    for para in cell.get('content', []):
                        if 'paragraph' in para:
                            p_start = para.get('startIndex', 0)
                            p_end = para.get('endIndex', p_start + 1)
                            if p_end > p_start + 1:
                                table_requests.append({
                                    'updateTextStyle': {
                                        'range': {'startIndex': p_start, 'endIndex': p_end - 1},
                                        'textStyle': {'bold': True},
                                        'fields': 'bold'
                                    }
                                })

    if table_requests:
        for i in range(0, len(table_requests), 50):
            batch = table_requests[i:i+50]
            docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': batch}).execute()
        print(f'  Applied table styles: {len(table_requests)} requests')


def main(md_path: str, title: str = None):
    # Read markdown
    md_file = Path(md_path)
    content = md_file.read_text(encoding='utf-8')
    doc_title = title or md_file.stem

    print(f'Converting: {md_file}')
    print(f'Title: {doc_title}')
    print('-' * 60)

    # Auth
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    docs_service = build('docs', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)

    # Parse markdown
    blocks = parse_markdown(content)
    print(f'Parsed: {len(blocks)} blocks')

    # Create document (in My Drive root)
    doc = docs_service.documents().create(body={'title': doc_title}).execute()
    doc_id = doc.get('documentId')
    print(f'Created: {doc_id}')

    # Insert content
    reqs = []
    for block in reversed(blocks):
        if block.type == BlockType.EMPTY:
            reqs.append({'insertText': {'location': {'index': 1}, 'text': '\n'}})
        elif block.type == BlockType.HR:
            reqs.append({'insertText': {'location': {'index': 1}, 'text': chr(9472) * 60 + '\n'}})
        elif block.type == BlockType.HEADER:
            text = get_plain_text(block.segments)
            reqs.append({'insertText': {'location': {'index': 1}, 'text': text + '\n'}})
        elif block.type == BlockType.TABLE:
            if block.table_data:
                rows = len(block.table_data)
                cols = len(block.table_data[0])
                reqs.append({'insertTable': {'rows': rows, 'columns': cols, 'location': {'index': 1}}})
        elif block.type == BlockType.LIST:
            prefix = '  ' * block.level + chr(8226) + ' '
            text = get_plain_text(block.segments)
            reqs.append({'insertText': {'location': {'index': 1}, 'text': prefix + text + '\n'}})
        else:
            text = get_plain_text(block.segments)
            reqs.append({'insertText': {'location': {'index': 1}, 'text': text + '\n'}})

    if reqs:
        docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': reqs}).execute()
        print(f'Inserted: {len(reqs)} requests')

    # Fill table cells
    doc = docs_service.documents().get(documentId=doc_id).execute()
    content_doc = doc.get('body', {}).get('content', [])
    table_blocks = [b for b in blocks if b.type == BlockType.TABLE]
    table_cells = []
    table_idx = 0
    for element in content_doc:
        if 'table' in element and table_idx < len(table_blocks):
            tb = table_blocks[table_idx]
            table = element['table']
            for ri, row in enumerate(table.get('tableRows', [])):
                for ci, cell in enumerate(row.get('tableCells', [])):
                    if ri < len(tb.table_data) and ci < len(tb.table_data[ri]):
                        cell_text = tb.table_data[ri][ci]
                        if cell_text:
                            for para in cell.get('content', []):
                                if 'paragraph' in para:
                                    idx = para.get('startIndex', 0)
                                    table_cells.append((idx, cell_text))
                                    break
            table_idx += 1

    table_cells.sort(key=lambda x: x[0], reverse=True)
    if table_cells:
        cell_reqs = [{'insertText': {'location': {'index': idx}, 'text': text}} for idx, text in table_cells]
        docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': cell_reqs}).execute()
        print(f'Filled: {len(cell_reqs)} table cells')

    # Apply styles
    print('Applying styles...')
    apply_styles(docs_service, doc_id, blocks)

    print()
    print('=' * 60)
    print('DONE!')
    print(f'URL: https://docs.google.com/document/d/{doc_id}/edit')
    print('=' * 60)

    return doc_id


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python create_styled_doc.py <markdown_file> [title]')
        sys.exit(1)

    md_path = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else None
    main(md_path, title)
