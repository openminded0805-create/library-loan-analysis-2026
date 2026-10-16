import pandas as pd
import numpy as np

df = pd.read_csv('02_data/processed/인기대출도서_2026_전처리.csv')

print("=== 1. BASIC STATS ===")
total_loans = df['대출건수_수치'].sum()
print(f"Total books: {len(df)}")
print(f"Total loans: {total_loans:,}")
print(f"Mean loans: {df['대출건수_수치'].mean():,.1f}")
print(f"Median loans: {df['대출건수_수치'].median():,.1f}")
print(f"Std loans: {df['대출건수_수치'].std():,.1f}")
print(f"Max (Rank 1): {df['대출건수_수치'].max():,} ({df.iloc[0]['서명']})")
print(f"Min (Rank 200): {df['대출건수_수치'].min():,} ({df.iloc[-1]['서명']})")
print(f"Top 10 share: {df.iloc[:10]['대출건수_수치'].sum()/total_loans*100:.2f}% ({df.iloc[:10]['대출건수_수치'].sum():,})")
print(f"Top 20 share: {df.iloc[:20]['대출건수_수치'].sum()/total_loans*100:.2f}% ({df.iloc[:20]['대출건수_수치'].sum():,})")
print(f"Top 50 share: {df.iloc[:50]['대출건수_수치'].sum()/total_loans*100:.2f}% ({df.iloc[:50]['대출건수_수치'].sum():,})")

# Check ISBN부가기호 raw values
print("\n=== 2. ISBN 부가기호 상세 ===")
df['ISBN부가기호_str'] = df['ISBN부가기호'].fillna('미상').astype(str).apply(lambda x: x.split('.')[0].zfill(5) if x != '미상' and x != 'nan' else '미상')
print(df['ISBN부가기호_str'].value_counts())

# Check series vs single books (권 컬럼 유무 및 시리즈명 추출)
df['권_유무'] = df['권'].notna() & (df['권'].astype(str).str.strip() != '')
print("\n=== 3. 권(시리즈) 유무별 통계 ===")
print(df.groupby('권_유무').agg(도서수=('순위', 'count'), 대출건수합=('대출건수_수치', 'sum'), 평균대출=('대출건수_수치', 'mean')))

# Group by exact title or series root
def extract_series_title(row):
    title = str(row['서명']).strip()
    if '흔한남매' in title:
        return f"[흔한남매 IP] {title.split(':')[0].strip()}"
    if '에그박사' in title:
        return "[에그박사 IP] 에그박사"
    if '슈뻘맨' in title:
        return "[슈뻘맨 IP] 슈뻘맨의 숨은 과학 찾기"
    if '설민석' in title:
        return f"[설민석 IP] {title.split(':')[0].strip()}"
    if '고양이 해결사 깜냥' in title:
        return "[깜냥 시리즈] 고양이 해결사 깜냥"
    if '똥볶이 할멈' in title:
        return "[똥볶이 할멈 시리즈] 똥볶이 할멈"
    if '이상한 과자 가게 전천당' in title:
        return "[전천당 시리즈] 이상한 과자 가게 전천당"
    return title.split(':')[0].strip()

df['시리즈_그룹'] = df.apply(extract_series_title, axis=1)
print("\n=== 4. 주요 시리즈/동일서명 그룹 TOP 20 ===")
series_grp = df.groupby('시리즈_그룹').agg(
    권수=('순위', 'count'),
    대출건수합=('대출건수_수치', 'sum'),
    평균대출=('대출건수_수치', 'mean'),
    최고순위=('순위', 'min'),
    출판사=('출판사', 'first'),
    독자대상=('독자대상(부가기호)', 'first')
).sort_values('대출건수합', ascending=False)
series_grp['대출비중(%)'] = (series_grp['대출건수합'] / total_loans * 100).round(2)
print(series_grp.head(20).to_string())

# Check Adult (교양 일반성인) vs Children (아동 어린이) Top 15 each
print("\n=== 5. 일반성인(교양) TOP 20 도서 ===")
adult_df = df[df['독자대상(부가기호)'] == '교양 (일반성인)']
print(adult_df[['순위', '서명', '권', '저자', '출판사', '출판년도_추출', 'KDC', '대출건수_수치']].head(20).to_string(index=False))

print("\n=== 6. 아동(어린이) 주요 시리즈/도서 요약 ===")
child_df = df[df['독자대상(부가기호)'] == '아동 (어린이)']
print(child_df.groupby('시리즈_그룹').agg(
    권수=('순위', 'count'),
    대출건수합=('대출건수_수치', 'sum'),
    최고순위=('순위', 'min'),
    출판사=('출판사', 'first'),
    KDC_대분류=('KDC_대분류', 'first')
).sort_values('대출건수합', ascending=False).head(15).to_string())

print("\n=== 7. 청소년 및 미상 도서 전체 ===")
other_df = df[~df['독자대상(부가기호)'].isin(['아동 (어린이)', '교양 (일반성인)'])]
print(other_df[['순위', '서명', '권', '저자', '출판사', '출판년도_추출', '독자대상(부가기호)', 'KDC', '대출건수_수치']].to_string(index=False))
