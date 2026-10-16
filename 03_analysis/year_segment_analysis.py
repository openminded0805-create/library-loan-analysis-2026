import pandas as pd

df = pd.read_csv('02_data/processed/인기대출도서_2026_전처리.csv')

# Map reader segment cleanly (resolving the 5 missing ISBN부가기호 books)
def resolve_segment(row):
    if row['순위'] == 20: # 자몽살구클럽 (한로로 소설)
        return '일반성인 (교양)'
    if row['순위'] in [128, 133, 141, 152]: # 흔한남매 과학 탐험대 (주니어김영사)
        return '아동/초등'
    target = str(row['독자대상(부가기호)'])
    if '아동' in target or '초등' in target:
        return '아동/초등'
    if '성인' in target:
        return '일반성인 (교양)'
    if '청소년' in target:
        return '청소년'
    return target

df['독자세그먼트'] = df.apply(resolve_segment, axis=1)

print("=== 독자세그먼트별 출판년도 구간 분포 ===")
df['출판시기'] = pd.cut(df['출판년도_추출'], bins=[2000, 2018, 2021, 2024, 2026], labels=['2018년 이전(스테디셀러)', '2019~2021년', '2022~2024년', '2025~2026년(신간)'])
ct = pd.crosstab(df['독자세그먼트'], df['출판시기'], margins=True)
print(ct)

print("\n=== 일반성인(교양) 출판시기별 도서수 및 대출건수 ===")
adult = df[df['독자세그먼트'] == '일반성인 (교양)']
print(adult.groupby('출판시기', observed=False).agg(권수=('순위','count'), 대출합=('대출건수_수치','sum'), 평균=('대출건수_수치','mean')))

print("\n=== 아동/초등 출판시기별 도서수 및 대출건수 ===")
child = df[df['독자세그먼트'] == '아동/초등']
print(child.groupby('출판시기', observed=False).agg(권수=('순위','count'), 대출합=('대출건수_수치','sum'), 평균=('대출건수_수치','mean')))

print("\n=== 다작/다권 진입 성인/청소년 작가 TOP 10 (아동 학습만화 제외) ===")
non_child = df[df['독자세그먼트'].isin(['일반성인 (교양)', '청소년'])]
print(non_child.groupby('대표저자').agg(권수=('순위','count'), 대출합=('대출건수_수치','sum'), 최고순위=('순위','min'), 도서목록=('서명', lambda x: ' / '.join([s.split(':')[0].strip() for s in x]))).sort_values(['권수', '대출합'], ascending=False).head(12).to_string())
