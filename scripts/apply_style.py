#!/usr/bin/env python3
"""Google Docs 스타일 적용 스크립트"""

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_FILE = r'C:\claude\json\token.json'
SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']

# Colors
PRIMARY_BLUE = {'red': 0.10, 'green': 0.30, 'blue': 0.55}
ACCENT_BLUE = {'red': 0.20, 'green': 0.45, 'blue': 0.70}
DARK_GRAY = {'red': 0.25, 'green': 0.25, 'blue': 0.25}
TABLE_HEADER_BG = {'red': 0.9, 'green': 0.9, 'blue': 0.9}


def apply_styles(doc_id: str):
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    docs_service = build('docs', 'v1', credentials=creds)

    # Get document structure
    doc = docs_service.documents().get(documentId=doc_id).execute()
    content = doc.get('body', {}).get('content', [])
    end_index = max(el.get('endIndex', 1) for el in content)

    print(f'Document: {doc.get("title")}')
    print(f'Content elements: {len(content)}')
    print(f'End index: {end_index}')

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
    print(f'Applied base styles: {len(requests)} requests')

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
        is_hr = chr(9472) in text_content  # Box drawing horizontal

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
            # Style horizontal rule
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
        # Batch in chunks
        for i in range(0, len(heading_requests), 50):
            batch = heading_requests[i:i+50]
            docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': batch}).execute()
        print(f'Applied heading styles: {len(heading_requests)} requests')

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
            # Header row background
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

            # Bold header row text
            for row in table.get('tableRows', [])[:1]:  # First row only
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
        print(f'Applied table styles: {len(table_requests)} requests')

    print()
    print('=' * 60)
    print('Style application complete!')
    print(f'URL: https://docs.google.com/document/d/{doc_id}/edit')
    print('=' * 60)


if __name__ == '__main__':
    import sys
    doc_id = sys.argv[1] if len(sys.argv) > 1 else '1_n0gxL-OTV3CYKJOIUsElwP3ayW24CUqqu8YcKuWC_Q'
    apply_styles(doc_id)
