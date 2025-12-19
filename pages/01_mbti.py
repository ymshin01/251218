import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="Global MBTI Dashboard", layout="wide")

@st.cache_data
def load_data():
    # 데이터 불러오기
    df = pd.read_csv('countries.csv')
    # MBTI 유형 컬럼들 (첫 번째 컬럼인 'Country' 제외)
    mbti_cols = df.columns[1:]
    return df, mbti_cols

try:
    df, mbti_cols = load_data()

    st.title("🌏 전 세계 MBTI 성향 분석 대시보드")
    st.markdown("업로드된 데이터를 기반으로 국가별 MBTI 분포와 순위를 분석합니다.")

    # --- 1. 전체 국가 MBTI 평균 비율 ---
    st.header("📊 전 세계 MBTI 평균 비율")
    avg_ratios = df[mbti_cols].mean().sort_values(ascending=False)
    st.bar_chart(avg_ratios)
    
    with st.expander("평균 데이터 보기"):
        st.write(avg_ratios)

    st.divider()

    # --- 2. 국가별 MBTI 성향 분석 ---
    st.header("🔍 국가별 상세 분석")
    selected_country = st.selectbox("분석할 국가를 선택하세요", df['Country'].unique())
    
    country_data = df[df['Country'] == selected_country][mbti_cols].T
    country_data.columns = ['Ratio']
    country_data = country_data.sort_values(by='Ratio', ascending=False)

    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader(f"{selected_country}의 MBTI TOP 5")
        st.table(country_data.head(5))
    with col2:
        st.bar_chart(country_data)

    st.divider()

    # --- 3. MBTI 유형별 높은 국가 TOP 10 ---
    st.header("🏆 MBTI 유형별 국가 랭킹 (TOP 10)")
    selected_mbti = st.selectbox("순위를 확인할 MBTI 유형을 선택하세요", mbti_cols)
    
    top10_countries = df[['Country', selected_mbti]].sort_values(by=selected_mbti, ascending=False).head(10)
    st.bar_chart(top10_countries.set_index('Country'))

    st.divider()

    # --- 4. 한국(South Korea) vs 선택 국가 비교 ---
    st.header("🇰🇷 한국과의 비교 분석")
    
    # 한국 데이터 확인 (데이터셋 내 명칭 확인: South Korea, Korea 등)
    korea_name = [c for c in df['Country'] if 'Korea' in c]
    
    if korea_name:
        korea_data = df[df['Country'] == korea_name[0]][mbti_cols].T
        korea_data.columns = ['South Korea']
        
        # 비교군 설정
        compare_data = pd.concat([korea_data, country_data], axis=1)
        compare_data.columns = ['South Korea', selected_country]
        
        st.write(f"**한국({korea_name[0]})**과 **{selected_country}**의 유형별 비율 비교입니다.")
        st.line_chart(compare_data)
        
        # 차이 분석
        compare_data['Difference'] = (compare_data[selected_country] - compare_data['South Korea']).abs()
        st.subheader("두 국가 간 가장 차이가 큰 유형")
        st.table(compare_data.sort_values(by='Difference', ascending=False).head(5))
    else:
        st.warning("데이터셋에서 'Korea'를 찾을 수 없습니다. 국가명을 확인해주세요.")

except FileNotFoundError:
    st.error("`countries.csv` 파일을 찾을 수 없습니다. 파일이 앱과 같은 폴더에 있는지 확인해주세요.")
except Exception as e:
    st.error(f"오류가 발생했습니다: {e}")
