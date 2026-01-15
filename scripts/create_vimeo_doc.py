#!/usr/bin/env python3
"""Vimeo OTT 미팅 질문지를 Google AI Studio 폴더에 생성"""

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# 인증 설정
TOKEN_PATH = Path("C:/claude/json/token_docs.json")
FOLDER_ID = "1JwdlUe_v4Ug-yQ0veXTldFl6C24GH8hW"
SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.file",
]

# Colors (v2.3.0 스타일 가이드)
PRIMARY_BLUE = {'red': 0.10, 'green': 0.30, 'blue': 0.55}   # #1A4D8C - Title, H1
ACCENT_BLUE = {'red': 0.20, 'green': 0.45, 'blue': 0.70}    # #3373B3 - H2, 구분선
DARK_GRAY = {'red': 0.25, 'green': 0.25, 'blue': 0.25}      # #404040 - H3, 본문
TABLE_HEADER_BG = {'red': 0.90, 'green': 0.90, 'blue': 0.90}  # #E6E6E6


class BlockType(Enum):
    HEADER = 'header'
    PARAGRAPH = 'paragraph'
    TABLE = 'table'
    LIST = 'list'
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


def get_credentials():
    """OAuth 자격증명 로드"""
    if not TOKEN_PATH.exists():
        raise FileNotFoundError(f"Token file not found: {TOKEN_PATH}")

    with open(TOKEN_PATH, "r", encoding="utf-8") as f:
        token_data = json.load(f)

    creds = Credentials(
        token=token_data.get("token"),
        refresh_token=token_data.get("refresh_token"),
        token_uri=token_data.get("token_uri"),
        client_id=token_data.get("client_id"),
        client_secret=token_data.get("client_secret"),
        scopes=token_data.get("scopes", SCOPES),
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        # Save refreshed token
        token_data["token"] = creds.token
        with open(TOKEN_PATH, "w", encoding="utf-8") as f:
            json.dump(token_data, f, indent=2)

    return creds


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


def apply_styles(docs_service, doc_id):
    """스타일 적용 (v2.3.0 스타일 가이드)"""
    doc = docs_service.documents().get(documentId=doc_id).execute()
    content = doc.get('body', {}).get('content', [])
    end_index = max(el.get('endIndex', 1) for el in content)

    requests = []

    # Page style (A4) - v2.3.0
    requests.append({
        'updateDocumentStyle': {
            'documentStyle': {
                'pageSize': {'width': {'magnitude': 595.28, 'unit': 'PT'}, 'height': {'magnitude': 841.89, 'unit': 'PT'}},
                'marginTop': {'magnitude': 72, 'unit': 'PT'},
                'marginBottom': {'magnitude': 72, 'unit': 'PT'},
                'marginLeft': {'magnitude': 72, 'unit': 'PT'},
                'marginRight': {'magnitude': 72, 'unit': 'PT'},
            },
            'fields': 'pageSize,marginTop,marginBottom,marginLeft,marginRight'
        }
    })

    # Body text style - v2.3.0: 115% 줄간격, 4pt 문단 간격
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
                    'lineSpacing': 115,  # v2.3.0: 115%
                    'spaceAbove': {'magnitude': 0, 'unit': 'PT'},
                    'spaceBelow': {'magnitude': 4, 'unit': 'PT'}  # v2.3.0: 4pt
                },
                'fields': 'lineSpacing,spaceAbove,spaceBelow'
            }
        })

    docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()
    print(f'  Base styles applied (v2.3.0: 115% line spacing, 4pt paragraph)')

    # Heading styles (v2.3.0 스타일 가이드)
    doc = docs_service.documents().get(documentId=doc_id).execute()
    content = doc.get('body', {}).get('content', [])

    # H1 키워드 (진한 파랑 18pt + 하단 구분선)
    h1_kw = ['Executive Summary']
    # H2 키워드 (밝은 파랑 14pt, 구분선 없음)
    h2_kw = ['미팅 목적', '업체 개요', '핵심 확인 항목', '질문 목록', '기술 검증 결과', '비용 영향 요소', '고려사항', '권고 사항', '후속 조치', '미결 사항']
    # H3 키워드 (진한 회색 12pt)
    h3_kw = ['플레이어/SDK', 'OTT/앱', '인프라/수익화', '연동/운영', '확인된 역량', '기술적 제약', '비용 절감', '비용 증가']

    heading_reqs = []
    for element in content:
        if 'paragraph' not in element:
            continue
        para = element['paragraph']
        start_idx = element.get('startIndex', 1)
        end_idx = element.get('endIndex', start_idx + 1)
        text = ''.join(e['textRun'].get('content', '') for e in para.get('elements', []) if 'textRun' in e).strip()

        if not text or end_idx <= start_idx + 1:
            continue

        # HR (─) 숨기기 - v2.3.0: 금지 항목
        is_hr = chr(9472) in text
        if is_hr:
            heading_reqs.extend([
                {'updateTextStyle': {'range': {'startIndex': start_idx, 'endIndex': end_idx - 1}, 'textStyle': {'foregroundColor': {'color': {'rgbColor': {'red': 0.95, 'green': 0.95, 'blue': 0.95}}}, 'fontSize': {'magnitude': 1, 'unit': 'PT'}}, 'fields': 'foregroundColor,fontSize'}}
            ])
            continue

        is_title = text.startswith('[WSOPTV]')
        is_h1 = any(kw in text for kw in h1_kw)
        is_h2 = any(kw in text for kw in h2_kw)
        is_h3 = any(kw in text for kw in h3_kw) or (text.startswith('Q') and '.' in text[:4])

        # Title: v2.3.0 - 진한 파랑 26pt Bold
        if is_title:
            heading_reqs.extend([
                {'updateTextStyle': {'range': {'startIndex': start_idx, 'endIndex': end_idx - 1}, 'textStyle': {'foregroundColor': {'color': {'rgbColor': PRIMARY_BLUE}}, 'bold': True, 'fontSize': {'magnitude': 26, 'unit': 'PT'}}, 'fields': 'foregroundColor,bold,fontSize'}},
                {'updateParagraphStyle': {'range': {'startIndex': start_idx, 'endIndex': end_idx}, 'paragraphStyle': {'spaceBelow': {'magnitude': 16, 'unit': 'PT'}, 'alignment': 'CENTER'}, 'fields': 'spaceBelow,alignment'}}
            ])
        # H1: v2.3.0 - 진한 파랑 18pt Bold + 하단 구분선
        elif is_h1:
            heading_reqs.extend([
                {'updateTextStyle': {'range': {'startIndex': start_idx, 'endIndex': end_idx - 1}, 'textStyle': {'foregroundColor': {'color': {'rgbColor': PRIMARY_BLUE}}, 'bold': True, 'fontSize': {'magnitude': 18, 'unit': 'PT'}}, 'fields': 'foregroundColor,bold,fontSize'}},
                {'updateParagraphStyle': {'range': {'startIndex': start_idx, 'endIndex': end_idx}, 'paragraphStyle': {'borderBottom': {'color': {'color': {'rgbColor': ACCENT_BLUE}}, 'width': {'magnitude': 1, 'unit': 'PT'}, 'padding': {'magnitude': 4, 'unit': 'PT'}, 'dashStyle': 'SOLID'}, 'spaceAbove': {'magnitude': 18, 'unit': 'PT'}, 'spaceBelow': {'magnitude': 10, 'unit': 'PT'}}, 'fields': 'borderBottom,spaceAbove,spaceBelow'}}
            ])
        # H2: v2.3.0 - 밝은 파랑 14pt Bold (구분선 없음)
        elif is_h2:
            heading_reqs.extend([
                {'updateTextStyle': {'range': {'startIndex': start_idx, 'endIndex': end_idx - 1}, 'textStyle': {'foregroundColor': {'color': {'rgbColor': ACCENT_BLUE}}, 'bold': True, 'fontSize': {'magnitude': 14, 'unit': 'PT'}}, 'fields': 'foregroundColor,bold,fontSize'}},
                {'updateParagraphStyle': {'range': {'startIndex': start_idx, 'endIndex': end_idx}, 'paragraphStyle': {'spaceAbove': {'magnitude': 16, 'unit': 'PT'}, 'spaceBelow': {'magnitude': 8, 'unit': 'PT'}}, 'fields': 'spaceAbove,spaceBelow'}}
            ])
        # H3: v2.3.0 - 진한 회색 12pt Bold
        elif is_h3:
            heading_reqs.extend([
                {'updateTextStyle': {'range': {'startIndex': start_idx, 'endIndex': end_idx - 1}, 'textStyle': {'foregroundColor': {'color': {'rgbColor': DARK_GRAY}}, 'bold': True, 'fontSize': {'magnitude': 12, 'unit': 'PT'}}, 'fields': 'foregroundColor,bold,fontSize'}},
                {'updateParagraphStyle': {'range': {'startIndex': start_idx, 'endIndex': end_idx}, 'paragraphStyle': {'spaceAbove': {'magnitude': 12, 'unit': 'PT'}, 'spaceBelow': {'magnitude': 4, 'unit': 'PT'}}, 'fields': 'spaceAbove,spaceBelow'}}
            ])

    if heading_reqs:
        for i in range(0, len(heading_reqs), 50):
            docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': heading_reqs[i:i+50]}).execute()
        print(f'  Heading styles applied (v2.3.0): {len(heading_reqs)}')

    # Table styles (v2.3.0: 헤더 배경 #E6E6E6, 헤더 텍스트 #404040 Bold)
    doc = docs_service.documents().get(documentId=doc_id).execute()
    content = doc.get('body', {}).get('content', [])
    table_reqs = []
    for element in content:
        if 'table' not in element:
            continue
        table = element['table']
        table_start = element.get('startIndex', 0)
        num_cols = table.get('columns', 0)
        if num_cols > 0:
            # 헤더 배경색 #E6E6E6
            table_reqs.append({'updateTableCellStyle': {'tableRange': {'tableCellLocation': {'tableStartLocation': {'index': table_start}, 'rowIndex': 0, 'columnIndex': 0}, 'rowSpan': 1, 'columnSpan': num_cols}, 'tableCellStyle': {'backgroundColor': {'color': {'rgbColor': TABLE_HEADER_BG}}}, 'fields': 'backgroundColor'}})
            # 헤더 텍스트: Bold + 진한 회색 (#404040)
            for row in table.get('tableRows', [])[:1]:
                for cell in row.get('tableCells', []):
                    for para in cell.get('content', []):
                        if 'paragraph' in para:
                            ps, pe = para.get('startIndex', 0), para.get('endIndex', 1)
                            if pe > ps + 1:
                                table_reqs.append({'updateTextStyle': {'range': {'startIndex': ps, 'endIndex': pe - 1}, 'textStyle': {'bold': True, 'foregroundColor': {'color': {'rgbColor': DARK_GRAY}}}, 'fields': 'bold,foregroundColor'}})

    if table_reqs:
        for i in range(0, len(table_reqs), 50):
            docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': table_reqs[i:i+50]}).execute()
        print(f'  Table styles applied (v2.3.0): {len(table_reqs)}')

    # Bold (**text**) 처리 - v2.3.0
    doc = docs_service.documents().get(documentId=doc_id).execute()
    content = doc.get('body', {}).get('content', [])
    bold_reqs = []

    for element in content:
        if 'paragraph' not in element:
            continue
        para = element['paragraph']
        for elem in para.get('elements', []):
            if 'textRun' not in elem:
                continue
            text_run = elem['textRun']
            text = text_run.get('content', '')
            start_idx = elem.get('startIndex', 0)

            # **text** 패턴 찾기 (이미 plain text로 변환되었으므로 원본 Bold 세그먼트 정보 필요)
            # 테이블 셀 내 Bold 처리는 이미 헤더에서 처리됨
            # 본문에서 Bold 키워드 패턴 적용
            bold_patterns = [
                '작성일', '업체', '미팅 형식', '참석자',
                '회사 개요', '주요 제품', '레퍼런스',
                '왜 중요한가', '기술 배경', '답변',
                '항목', '내용', '값', '질문 요약', '우선순위',
                '카테고리', '확인 사항', '결과', '대응 방안',
                '절감 내용', '영향도', '확인 방법',
                '버전', '날짜', '작성자'
            ]

            for pattern in bold_patterns:
                idx = text.find(pattern)
                if idx != -1:
                    pattern_start = start_idx + idx
                    pattern_end = pattern_start + len(pattern)
                    bold_reqs.append({
                        'updateTextStyle': {
                            'range': {'startIndex': pattern_start, 'endIndex': pattern_end},
                            'textStyle': {'bold': True},
                            'fields': 'bold'
                        }
                    })

    if bold_reqs:
        # 중복 제거 (같은 범위에 여러 번 적용 방지)
        seen = set()
        unique_reqs = []
        for req in bold_reqs:
            key = (req['updateTextStyle']['range']['startIndex'], req['updateTextStyle']['range']['endIndex'])
            if key not in seen:
                seen.add(key)
                unique_reqs.append(req)

        for i in range(0, len(unique_reqs), 50):
            docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': unique_reqs[i:i+50]}).execute()
        print(f'  Bold text applied (v2.3.0): {len(unique_reqs)}')


def main():
    md_path = Path(r"C:\claude\WSOPTV\docs\meeting_vimeo_questions.md")
    title = "[WSOPTV] Vimeo OTT 미팅 질문지 v1"

    print(f"Source: {md_path}")
    print(f"Title: {title}")
    print("-" * 60)

    # 1. 인증
    print("Authenticating...")
    creds = get_credentials()
    docs_service = build('docs', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)
    print("OK!")

    # 2. 폴더 권한 확인
    folder = drive_service.files().get(fileId=FOLDER_ID, fields="name,capabilities").execute()
    print(f"Target folder: {folder.get('name')}")
    can_add = folder.get("capabilities", {}).get("canAddChildren", False)
    print(f"canAddChildren: {can_add}")

    if not can_add:
        print("ERROR: No write permission!")
        return

    # 3. 문서 생성
    print("\nCreating document...")
    doc = docs_service.documents().create(body={"title": title}).execute()
    doc_id = doc["documentId"]
    print(f"Created: {doc_id}")

    # 4. 폴더로 이동
    file_info = drive_service.files().get(fileId=doc_id, fields="parents").execute()
    current_parents = ",".join(file_info.get("parents", []))
    drive_service.files().update(fileId=doc_id, addParents=FOLDER_ID, removeParents=current_parents, fields="id,parents").execute()
    print(f"Moved to folder: {folder.get('name')}")

    # 5. 콘텐츠 삽입 (v2.3.0 줄바꿈 정책 적용)
    print("\nInserting content...")
    content = md_path.read_text(encoding="utf-8")
    blocks = parse_markdown(content)
    print(f"Parsed: {len(blocks)} blocks")

    # v2.3.0 줄바꿈 정책: 테이블 앞뒤, 헤딩 뒤 줄바꿈 제거
    # 불필요한 연속 빈 줄 제거
    filtered_blocks = []
    prev_type = None
    for i, block in enumerate(blocks):
        # 빈 줄 처리
        if block.type == BlockType.EMPTY:
            # 연속 빈 줄 제거
            if prev_type == BlockType.EMPTY:
                continue
            # 헤딩 뒤 빈 줄 제거
            if prev_type == BlockType.HEADER:
                continue
            # 테이블 앞 빈 줄 제거
            if i + 1 < len(blocks) and blocks[i + 1].type == BlockType.TABLE:
                continue
            # 테이블 뒤 빈 줄 제거
            if prev_type == BlockType.TABLE:
                continue
        filtered_blocks.append(block)
        prev_type = block.type

    print(f"After line break optimization: {len(filtered_blocks)} blocks")

    reqs = []
    for block in reversed(filtered_blocks):
        if block.type == BlockType.EMPTY:
            reqs.append({'insertText': {'location': {'index': 1}, 'text': '\n'}})
        elif block.type == BlockType.HR:
            reqs.append({'insertText': {'location': {'index': 1}, 'text': chr(9472) * 60 + '\n'}})
        elif block.type == BlockType.HEADER:
            reqs.append({'insertText': {'location': {'index': 1}, 'text': get_plain_text(block.segments) + '\n'}})
        elif block.type == BlockType.TABLE:
            if block.table_data:
                reqs.append({'insertTable': {'rows': len(block.table_data), 'columns': len(block.table_data[0]), 'location': {'index': 1}}})
        elif block.type == BlockType.LIST:
            reqs.append({'insertText': {'location': {'index': 1}, 'text': '  ' * block.level + chr(8226) + ' ' + get_plain_text(block.segments) + '\n'}})
        else:
            reqs.append({'insertText': {'location': {'index': 1}, 'text': get_plain_text(block.segments) + '\n'}})

    docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': reqs}).execute()
    print(f"Inserted: {len(reqs)} requests")

    # 6. 테이블 셀 채우기
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
                                    table_cells.append((para.get('startIndex', 0), cell_text))
                                    break
            table_idx += 1

    table_cells.sort(key=lambda x: x[0], reverse=True)
    if table_cells:
        cell_reqs = [{'insertText': {'location': {'index': idx}, 'text': text}} for idx, text in table_cells]
        docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': cell_reqs}).execute()
        print(f"Filled: {len(cell_reqs)} table cells")

    # 7. 스타일 적용
    print("\nApplying styles...")
    apply_styles(docs_service, doc_id)

    # 결과
    print("\n" + "=" * 60)
    print("DONE!")
    print(f"URL: https://docs.google.com/document/d/{doc_id}/edit")
    print("=" * 60)


if __name__ == "__main__":
    main()
