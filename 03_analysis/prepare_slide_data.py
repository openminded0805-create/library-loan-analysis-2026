import json
import pandas as pd
import numpy as np

df = pd.read_csv('02_data/processed/인기대출도서_2026_전처리.csv')
total_loans = int(df['대출건수_수치'].sum())

# Resolve reader segment cleanly
def resolve_segment(row):
    if row['순위'] == 20:
        return '일반성인(교양)'
    if row['순위'] in [128, 133, 141, 152]:
        return '아동/초등'
    target = str(row['독자대상(부가기호)'])
    if '아동' in target or '초등' in target:
        return '아동/초등'
    if '성인' in target:
        return '일반성인(교양)'
    if '청소년' in target:
        return '청소년'
    return target

df['독자세그먼트'] = df.apply(resolve_segment, axis=1)

# Resolve KDC clean
def resolve_kdc(row):
    if row['순위'] == 20:
        return '800 문학 (미분류 소설)'
    if row['순위'] in [128, 133, 141, 152]:
        return '400 자연과학 (미분류 과학만화)'
    return str(row['KDC_대분류'])

df['KDC_보정'] = df.apply(resolve_kdc, axis=1)

# Check KDC x Reader Segment cross-tab
ct_kdc = df.groupby(['KDC_대분류', '독자세그먼트']).agg(
    권수=('순위', 'count'),
    대출합=('대출건수_수치', 'sum')
).reset_index()
print("=== KDC x 독자세그먼트 ===")
print(ct_kdc.to_string(index=False))

# Export Top 200 JSON for interactive explorer in HTML slide deck
books_records = []
for idx, r in df.iterrows():
    books_records.append({
        'rank': int(r['순위']),
        'title': str(r['서명']).strip(),
        'vol': '' if pd.isna(r['권']) else str(r['권']).replace('.0', ''),
        'author': str(r['대표저자']).strip(),
        'author_full': str(r['저자']).strip(),
        'publisher': str(r['출판사']).strip(),
        'year': int(r['출판년도_추출']),
        'kdc': '미분류' if pd.isna(r['KDC']) else str(r['KDC']),
        'kdc_main': str(r['KDC_대분류']),
        'segment': str(r['독자세그먼트']),
        'loans': int(r['대출건수_수치'])
    })

with open('03_analysis/books_200.json', 'w', encoding='utf-8') as f:
    json.dump(books_records, f, ensure_ascii=False, indent=2)

print("Saved 03_analysis/books_200.json successfully. Count:", len(books_records))
