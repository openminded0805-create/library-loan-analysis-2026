import pandas as pd

df = pd.read_csv('02_data/processed/인기대출도서_2026_전처리.csv')
total_loans = df['대출건수_수치'].sum()

print("=== IP / 작가별 점유율 ===")
for kw in ['흔한남매', '에그박사', '슈뻘맨', '설민석', '야코', '깜냥', '똥볶이', '전천당', '한강', '김애란', '김호연', '이꽃님', '히가시노', '구병모', '성해나', '양귀자']:
    sub = df[df['서명'].str.contains(kw, na=False) | df['저자'].str.contains(kw, na=False)]
    print(f"{kw}: {len(sub)}권 | {sub['대출건수_수치'].sum():,}건 ({sub['대출건수_수치'].sum()/total_loans*100:.2f}%) | 최고순위 {sub['순위'].min()}위")

print("\n=== 성인(교양) 61권 + 자몽살구클럽(1권) KDC 분포 ===")
adult = df[df['독자대상(부가기호)'].isin(['교양 (일반성인)']) | (df['순위']==20)]
print(adult.groupby('KDC_대분류', dropna=False).agg(권수=('순위','count'), 대출합=('대출건수_수치','sum'), 평균=('대출건수_수치','mean')))

print("\n=== 성인(교양) 전체 62권 리스트 ===")
print(adult[['순위', '서명', '권', '저자', '출판사', '출판년도_추출', 'KDC', '대출건수_수치']].to_string(index=False))

print("\n=== 아동/초등(132권: 아동127+초등1+주니어김영사4) 시리즈별 전체 집계 ===")
child = df[df['독자대상(부가기호)'].isin(['아동 (어린이)', '학습참고서 (초등)']) | df['순위'].isin([128,133,141,152])]
print(f"아동/초등 총 권수: {len(child)}, 총 대출건수: {child['대출건수_수치'].sum():,} ({child['대출건수_수치'].sum()/total_loans*100:.2f}%)")
print(child[['순위', '서명', '권', '저자', '출판사', '출판년도_추출', 'KDC', '대출건수_수치']].to_string(index=False))
