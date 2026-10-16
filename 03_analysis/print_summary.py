import pandas as pd

df = pd.read_csv('02_data/processed/인기대출도서_2026_전처리.csv')
total_loans = df['대출건수_수치'].sum()

print("=== 1. IP / 작가별 점유율 ===")
for kw in ['흔한남매', '흔한 남매', '에그박사', '슈뻘맨', '설민석', '야코', '깜냥', '똥볶이', '전천당', '한강', '김애란', '김호연', '이꽃님', '히가시노', '구병모', '성해나', '양귀자', '놓지 마']:
    sub = df[df['서명'].str.contains(kw, na=False) | df['저자'].str.contains(kw, na=False)]
    if len(sub) > 0:
        print(f"{kw:8s}: {len(sub):3d}권 | {sub['대출건수_수치'].sum():9,d}건 ({sub['대출건수_수치'].sum()/total_loans*100:5.2f}%) | 최고 {sub['순위'].min():3d}위")

heun = df[df['서명'].str.contains('흔한남매|흔한 남매', na=False) | df['저자'].str.contains('흔한남매|흔한 남매', na=False)]
print(f"\n-> 흔한남매 통합: {len(heun)}권 (전체 200권 중 {len(heun)/200*100:.1f}%) | {heun['대출건수_수치'].sum():,d}건 ({heun['대출건수_수치'].sum()/total_loans*100:.2f}%)")

# All YouTuber/Creator comics (흔한남매 + 에그박사 + 슈뻘맨 + 빨간내복야코 + 설민석)
yt = df[df['서명'].str.contains('흔한남매|흔한 남매|에그박사|슈뻘맨|야코|설민석', na=False) | df['저자'].str.contains('흔한남매|흔한 남매|에그박사|슈뻘맨|야코|설민석', na=False)]
print(f"-> 유튜브/크리에이터 학습만화/코믹북 통합: {len(yt)}권 ({len(yt)/200*100:.1f}%) | {yt['대출건수_수치'].sum():,d}건 ({yt['대출건수_수치'].sum()/total_loans*100:.2f}%)")

adult = df[df['독자대상(부가기호)'].isin(['교양 (일반성인)']) | (df['순위']==20)]
print("\n=== 2. 성인(교양) 62권 KDC 분포 ===")
print(adult.groupby('KDC_대분류', dropna=False).agg(권수=('순위','count'), 대출합=('대출건수_수치','sum'), 평균=('대출건수_수치','mean')))

print("\n=== 3. 성인(교양) 비문학 도서 전체 ===")
non_lit_adult = adult[adult['KDC_대분류'] != '800 문학']
print(non_lit_adult[['순위', '서명', '저자', '출판사', '출판년도_추출', 'KDC_대분류', 'KDC', '대출건수_수치']].to_string(index=False))

print("\n=== 4. 성인(교양) 문학 도서 국가별(한국/일본/영미 등) 분포 ===")
lit_adult = adult[adult['KDC_대분류'] == '800 문학']
print(lit_adult.groupby('KDC_강세분야').agg(권수=('순위','count'), 대출합=('대출건수_수치','sum'), 평균=('대출건수_수치','mean')))

print("\n=== 5. 아동/초등 도서 중 비-유튜브(창작동화/일반학습만화 등) 목록 ===")
child_all = df[df['독자대상(부가기호)'].isin(['아동 (어린이)', '학습참고서 (초등)']) | df['순위'].isin([128,133,141,152])]
child_non_yt = child_all[~child_all.index.isin(yt.index)]
print(f"아동 비-유튜브 도서수: {len(child_non_yt)}권 | 대출합: {child_non_yt['대출건수_수치'].sum():,d}건")
print(child_non_yt[['순위', '서명', '권', '저자', '출판사', '출판년도_추출', 'KDC', '대출건수_수치']].to_string(index=False))
