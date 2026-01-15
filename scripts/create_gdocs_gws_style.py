# -*- coding: utf-8 -*-
"""
Google Workspace 스킬 스타일로 Google Docs 문서 생성

스타일 정의:
- H1: 진한 파랑 #1A4D8C, 18pt, 하단 구분선
- H2: 밝은 파랑 #3373B3, 14pt
- H3: 진한 회색 #404040, 12pt
- 본문: 115% 줄간격, 11pt
- 페이지: A4, 72pt 여백
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


# 색상 팔레트 (Google Workspace 스킬 정의)
COLORS = {
    'primary_blue': hex_to_rgb('#1A4D8C'),   # 진한 파랑
    'accent_blue': hex_to_rgb('#3373B3'),    # 밝은 파랑
    'dark_gray': hex_to_rgb('#404040'),      # 진한 회색
    'light_gray': hex_to_rgb('#F2F2F2'),     # 연한 회색
    'table_header': hex_to_rgb('#E6E6E6'),   # 테이블 헤더 배경
    'text_black': hex_to_rgb('#333333'),     # 본문 텍스트
}

# 헤딩 스타일 (Google Workspace 스킬 정의)
HEADING_STYLES = {
    1: {'color': 'primary_blue', 'size': 18, 'border': True},
    2: {'color': 'accent_blue', 'size': 14, 'border': False},
    3: {'color': 'dark_gray', 'size': 12, 'border': False},
    4: {'color': 'dark_gray', 'size': 11, 'border': False},
}


# ============================================================================
# 마크다운 파싱 및 Google Docs 요청 생성
# ============================================================================

class GoogleWorkspaceConverter:
    def __init__(self, content):
        self.content = content
        self.requests = []
        self.current_index = 1
        self.headings = []

    def parse(self):
        lines = self.content.split('\n')
        i = 0
        in_table = False
        table_lines = []

        while i < len(lines):
            line = lines[i]

            # 테이블 처리
            if '|' in line and not in_table:
                if i + 1 < len(lines) and ('---' in lines[i + 1] or ':-' in lines[i + 1]):
                    in_table = True
                    table_lines = [line]
                    i += 1
                    continue

            if in_table:
                if '|' in line:
                    table_lines.append(line)
                    i += 1
                    continue
                else:
                    self._add_table(table_lines)
                    in_table = False
                    table_lines = []
                    continue

            # 제목 처리
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                text = line.lstrip('#').strip()
                if text and level <= 4:
                    self._add_heading(text, level)
                i += 1
                continue

            # 수평선 처리 (무시 - Google Workspace 스킬 규칙)
            if line.strip() in ['---', '***', '___']:
                i += 1
                continue

            # 일반 텍스트
            if line.strip():
                self._add_paragraph(line)
            else:
                self._add_text('\n')

            i += 1

        # 남은 테이블 처리
        if table_lines:
            self._add_table(table_lines)

        return self.requests

    def _add_text(self, text):
        if not text:
            text = '\n'
        elif not text.endswith('\n'):
            text = text + '\n'

        self.requests.append({
            'insertText': {
                'location': {'index': self.current_index},
                'text': text
            }
        })

        start_index = self.current_index
        self.current_index += len(text)
        return start_index

    def _add_heading(self, text, level):
        start = self._add_text(text)
        end = self.current_index - 1

        self.headings.append({
            'start': start,
            'end': end,
            'level': level,
            'text': text
        })

        style = HEADING_STYLES.get(level, HEADING_STYLES[4])

        # Named Style 적용
        self.requests.append({
            'updateParagraphStyle': {
                'range': {'startIndex': start, 'endIndex': end + 1},
                'paragraphStyle': {
                    'namedStyleType': f'HEADING_{level}',
                    'spaceAbove': {'magnitude': 16 if level > 1 else 24, 'unit': 'PT'},
                    'spaceBelow': {'magnitude': 8, 'unit': 'PT'},
                    'lineSpacing': 115,
                },
                'fields': 'namedStyleType,spaceAbove,spaceBelow,lineSpacing'
            }
        })

        # 색상 및 폰트 적용
        self.requests.append({
            'updateTextStyle': {
                'range': {'startIndex': start, 'endIndex': end},
                'textStyle': {
                    'foregroundColor': {'color': {'rgbColor': COLORS[style['color']]}},
                    'fontSize': {'magnitude': style['size'], 'unit': 'PT'},
                    'bold': True,
                },
                'fields': 'foregroundColor,fontSize,bold'
            }
        })

        # H1에 하단 구분선 추가
        if style.get('border'):
            self.requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': start, 'endIndex': end + 1},
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

    def _add_paragraph(self, text):
        # 인라인 볼드/이탤릭 제거 (간단 처리)
        clean_text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        clean_text = re.sub(r'\*(.+?)\*', r'\1', clean_text)
        clean_text = re.sub(r'__(.+?)__', r'\1', clean_text)
        clean_text = re.sub(r'_(.+?)_', r'\1', clean_text)

        start = self._add_text(clean_text)
        end = self.current_index - 1

        # 본문 스타일 적용 (115% 줄간격)
        self.requests.append({
            'updateParagraphStyle': {
                'range': {'startIndex': start, 'endIndex': end + 1},
                'paragraphStyle': {
                    'namedStyleType': 'NORMAL_TEXT',
                    'lineSpacing': 115,
                    'spaceBelow': {'magnitude': 4, 'unit': 'PT'},
                },
                'fields': 'namedStyleType,lineSpacing,spaceBelow'
            }
        })

        self.requests.append({
            'updateTextStyle': {
                'range': {'startIndex': start, 'endIndex': end},
                'textStyle': {
                    'foregroundColor': {'color': {'rgbColor': COLORS['text_black']}},
                    'fontSize': {'magnitude': 11, 'unit': 'PT'},
                },
                'fields': 'foregroundColor,fontSize'
            }
        })

    def _add_table(self, table_lines):
        # 테이블 파싱
        rows = []
        for line in table_lines:
            if '---' in line or ':-' in line:
                continue
            cells = [c.strip() for c in line.strip('|').split('|')]
            if cells:
                rows.append(cells)

        if not rows:
            return

        # 열 너비 계산
        col_count = max(len(row) for row in rows)
        col_widths = [0] * col_count
        for row in rows:
            for i, cell in enumerate(row):
                if i < col_count:
                    col_widths[i] = max(col_widths[i], len(cell))

        # 텍스트 테이블로 출력
        for row_idx, row in enumerate(rows):
            padded_cells = []
            for i in range(col_count):
                cell = row[i] if i < len(row) else ''
                padded_cells.append(cell.ljust(col_widths[i]))

            line_text = ' | '.join(padded_cells)
            start = self._add_text(line_text)
            end = self.current_index - 1

            # 헤더 행 스타일 (볼드)
            if row_idx == 0:
                self.requests.append({
                    'updateTextStyle': {
                        'range': {'startIndex': start, 'endIndex': end},
                        'textStyle': {'bold': True},
                        'fields': 'bold'
                    }
                })
                # 구분선 추가
                separator = '-+-'.join('-' * w for w in col_widths)
                self._add_text(separator)

            # 테이블 줄간격
            self.requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': start, 'endIndex': end + 1},
                    'paragraphStyle': {
                        'lineSpacing': 115,
                        'spaceBelow': {'magnitude': 2, 'unit': 'PT'},
                    },
                    'fields': 'lineSpacing,spaceBelow'
                }
            })


def main():
    # ========================================================================
    # 인증
    # ========================================================================

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

    # ========================================================================
    # 문서 생성
    # ========================================================================

    # 마크다운 파일 읽기
    md_path = Path('C:/claude/WSOPTV/docs/meeting_vimeo_questions.md')
    content = md_path.read_text(encoding='utf-8')

    # 1. 빈 문서 생성
    title = '[WSOPTV] Vimeo OTT 미팅 질문지 v1'
    doc = docs_service.documents().create(body={'title': title}).execute()
    doc_id = doc.get('documentId')
    print(f'[1/4] 문서 생성됨: {title}')
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
    print('[2/4] 폴더로 이동됨')

    # 3. 콘텐츠 변환 및 추가
    converter = GoogleWorkspaceConverter(content)
    requests = converter.parse()

    if requests:
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()
        print(f'[3/4] 콘텐츠 추가됨: {len(requests)} 요청')

    # 4. 페이지 스타일 적용 (A4, 여백 72pt)
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
    print('[4/4] 페이지 스타일 적용됨 (A4, 72pt 여백, 115% 줄간격)')

    # 결과 출력
    doc_url = f'https://docs.google.com/document/d/{doc_id}/edit'
    print()
    print('=' * 60)
    print('Google Docs 생성 완료! (Google Workspace 스킬 스타일)')
    print(f'URL: {doc_url}')
    print('=' * 60)
    print()
    print('적용된 스타일:')
    print('  - H1: 진한 파랑 #1A4D8C, 18pt, 하단 구분선')
    print('  - H2: 밝은 파랑 #3373B3, 14pt')
    print('  - H3: 진한 회색 #404040, 12pt')
    print('  - 본문: 115% 줄간격, 11pt')
    print('  - 페이지: A4, 72pt 여백')


if __name__ == '__main__':
    main()
