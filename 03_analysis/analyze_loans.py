import pathlib
import re
import json
import pandas as pd
import numpy as np

# Load CSV
raw_path = pathlib.Path('02_data/raw/20261016112804/인기대출도서_2026.csv')
df = pd.read_csv(raw_path, skiprows=12, encoding='utf-8-sig', dtype=str)

# Drop empty unnamed trailing columns if any
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

print("Columns:", df.columns.tolist())
print("Shape:", df.shape)

# Clean columns
df['순위'] = df['순위'].astype(int)
df['대출건수_수치'] = df['대출건수'].str.replace(',', '').astype(int)
df['출판년도_추출'] = df['출판년도'].apply(lambda x: int(re.findall(r'\d{4}', str(x))[0]) if re.findall(r'\d{4}', str(x)) else np.nan)

# Clean author name (primary author)
def extract_main_author(s):
    if pd.isna(s):
        return '미상'
    s = str(s)
    # Remove role prefixes like '지은이: ', '글·그림: ', '글: ', '저자: '
    parts = re.split(r'[;/|]', s)[0]
    parts = re.sub(r'^(지은이|글·그림|글\.그림|글|그림|저자|지음|엮음|편저)\s*[:：]\s*', '', parts.strip())
    parts = re.sub(r'\s*(지음|글|그림|저|외).*$', '', parts.strip())
    return parts.strip()

df['대표저자'] = df['저자'].apply(extract_main_author)

# KDC classification
kdc_main_map = {
    '0': '000 총류',
    '1': '100 철학',
    '2': '200 종교',
    '3': '300 사회과학',
    '4': '400 자연과학',
    '5': '500 기술과학',
    '6': '600 예술',
    '7': '700 언어',
    '8': '800 문학',
    '9': '900 역사'
}

kdc_sub_map = {
    '81': '한국문학 (810)',
    '83': '일본문학 (830)',
    '84': '영미문학 (840)',
    '85': '독일문학 (850)',
    '86': '프랑스문학 (860)',
    '87': '스페인문학 (870)',
    '82': '중국문학 (820)',
    '89': '기타제문학 (890)',
    '32': '경제학/재테크 (320)',
    '33': '사회학/사회문제 (330)',
    '30': '사회과학총류 (300)',
    '18': '심리학 (180)',
    '19': '윤리학/자기계발 (190)',
    '10': '철학총류 (100)',
    '40': '자연과학총류 (400)',
    '47': '생명과학 (470)',
    '49': '동물학 (490)',
    '51': '의학/건강 (510)',
    '90': '역사총류 (900)',
    '91': '아시아(한국)역사 (910)',
}

def get_kdc_main(kdc):
    if pd.isna(kdc) or not str(kdc).strip():
        return '미분류'
    first = str(kdc).strip()[0]
    return kdc_main_map.get(first, '기타')

def get_kdc_sub(kdc):
    if pd.isna(kdc) or len(str(kdc).strip()) < 2:
        return '기타'
    prefix2 = str(kdc).strip()[:2]
    return kdc_sub_map.get(prefix2, f'기타 ({prefix2}0)')

df['KDC_대분류'] = df['KDC'].apply(get_kdc_main)
df['KDC_강세분야'] = df['KDC'].apply(get_kdc_sub)

# ISBN 부가기호 (5 digits: 1st digit = 독자대상, 2nd digit = 발행형태)
reader_target_map = {
    '0': '교양 (일반성인)',
    '1': '실용 (일반성인)',
    '4': '청소년',
    '5': '학습참고서 (중고)',
    '6': '학습참고서 (초등)',
    '7': '아동 (어린이)',
    '9': '전문/학술'
}
pub_form_map = {
    '3': '단행본',
    '4': '시리즈/전집',
    '7': '그림책/만화'
}

def get_reader_target(code):
    if pd.isna(code) or len(str(code).strip()) < 1:
        return '미상'
    c = str(code).strip().zfill(5)[0]
    return reader_target_map.get(c, f'기타({c})')

def get_pub_form(code):
    if pd.isna(code) or len(str(code).strip()) < 2:
        return '미상'
    c = str(code).strip().zfill(5)[1]
    return pub_form_map.get(c, f'기타({c})')

df['독자대상(부가기호)'] = df['ISBN부가기호'].apply(get_reader_target)
df['발행형태(부가기호)'] = df['ISBN부가기호'].apply(get_pub_form)
df['출판경과년수(2026기준)'] = 2026 - df['출판년도_추출']

# Save processed CSV
df.to_csv('02_data/processed/인기대출도서_2026_전처리.csv', index=False, encoding='utf-8-sig')

# Print comprehensive stats
print("\n--- 1. 기본 요약 통계 ---")
print("총 도서 수:", len(df))
print("총 대출건수 합계:", f"{df['대출건수_수치'].sum():,}")
print("평균 대출건수:", f"{df['대출건수_수치'].mean():,.1f}")
print("중앙값 대출건수:", f"{df['대출건수_수치'].median():,.1f}")
print("최대 대출건수 (1위):", f"{df['대출건수_수치'].max():,}", df.iloc[0]['서명'])
print("최소 대출건수 (200위):", f"{df['대출건수_수치'].min():,}", df.iloc[-1]['서명'])
print("상위 10위 비중:", f"{df.iloc[:10]['대출건수_수치'].sum() / df['대출건수_수치'].sum() * 100:.2f}%")
print("상위 20위(10%) 비중:", f"{df.iloc[:20]['대출건수_수치'].sum() / df['대출건수_수치'].sum() * 100:.2f}%")
print("상위 50위(25%) 비중:", f"{df.iloc[:50]['대출건수_수치'].sum() / df['대출건수_수치'].sum() * 100:.2f}%")

print("\n--- 2. TOP 20 도서 ---")
print(df[['순위', '서명', '대표저자', '출판사', '출판년도_추출', 'KDC', '대출건수_수치']].head(20).to_string(index=False))

print("\n--- 3. KDC 대분류별 분포 ---")
kdc_summary = df.groupby('KDC_대분류').agg(
    도서수=('순위', 'count'),
    대출건수합=('대출건수_수치', 'sum'),
    평균대출건수=('대출건수_수치', 'mean')
).sort_values('대출건수합', ascending=False)
kdc_summary['도서비중(%)'] = (kdc_summary['도서수'] / len(df) * 100).round(1)
kdc_summary['대출비중(%)'] = (kdc_summary['대출건수합'] / df['대출건수_수치'].sum() * 100).round(1)
print(kdc_summary.to_string())

print("\n--- 4. KDC 세부 강세분야별 분포 ---")
kdc_sub_summary = df.groupby('KDC_강세분야').agg(
    도서수=('순위', 'count'),
    대출건수합=('대출건수_수치', 'sum'),
    평균대출건수=('대출건수_수치', 'mean')
).sort_values('대출건수합', ascending=False)
kdc_sub_summary['도서비중(%)'] = (kdc_sub_summary['도서수'] / len(df) * 100).round(1)
kdc_sub_summary['대출비중(%)'] = (kdc_sub_summary['대출건수합'] / df['대출건수_수치'].sum() * 100).round(1)
print(kdc_sub_summary.head(15).to_string())

print("\n--- 5. 독자대상(ISBN부가기호) 분포 ---")
target_summary = df.groupby('독자대상(부가기호)').agg(
    도서수=('순위', 'count'),
    대출건수합=('대출건수_수치', 'sum'),
    평균대출건수=('대출건수_수치', 'mean')
).sort_values('대출건수합', ascending=False)
target_summary['도서비중(%)'] = (target_summary['도서수'] / len(df) * 100).round(1)
target_summary['대출비중(%)'] = (target_summary['대출건수합'] / df['대출건수_수치'].sum() * 100).round(1)
print(target_summary.to_string())

print("\n--- 6. 출판년도별 분포 ---")
year_summary = df.groupby('출판년도_추출').agg(
    도서수=('순위', 'count'),
    대출건수합=('대출건수_수치', 'sum'),
    평균대출건수=('대출건수_수치', 'mean')
).sort_index(ascending=False)
year_summary['도서비중(%)'] = (year_summary['도서수'] / len(df) * 100).round(1)
year_summary['대출비중(%)'] = (year_summary['대출건수합'] / df['대출건수_수치'].sum() * 100).round(1)
print(year_summary.to_string())

print("\n--- 7. 저자별 다관왕 TOP 15 ---")
author_summary = df.groupby('대표저자').agg(
    도서수=('순위', 'count'),
    대출건수합=('대출건수_수치', 'sum'),
    평균대출건수=('대출건수_수치', 'mean'),
    최고순위=('순위', 'min'),
    대표작=('서명', 'first')
).sort_values(['대출건수합', '도서수'], ascending=False)
print(author_summary.head(15).to_string())

print("\n--- 8. 출판사별 TOP 15 ---")
pub_summary = df.groupby('출판사').agg(
    도서수=('순위', 'count'),
    대출건수합=('대출건수_수치', 'sum'),
    평균대출건수=('대출건수_수치', 'mean'),
    최고순위=('순위', 'min')
).sort_values(['대출건수합', '도서수'], ascending=False)
print(pub_summary.head(15).to_string())
