import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. 페이지 설정 (넓은 화면 모드)
st.set_page_config(page_title="나만의 데이터 인사이트 앱", page_icon="📊", layout="wide")

# --- 데이터 로드 함수 ---
@st.cache_data # 데이터를 매번 새로 읽지 않도록 속도 최적화
def load_weather():
    # test.csv 로드 (날짜, 지점, 평균기온, 최저기온, 최고기온)
    df = pd.read_csv("test.csv")
    df['날짜'] = pd.to_datetime(df['날짜'].str.strip()) # 날짜 공백 제거 후 변환
    return df

@st.cache_data
def load_mbti():
    # countries.csv 로드
    return pd.read_csv("countries.csv")

# 데이터 불러오기
try:
    weather_df = load_weather()
    mbti_df = load_mbti()
except Exception as e:
    st.error(f"데이터 파일을 찾을 수 없거나 오류가 발생했습니다: {e}")
    st.stop()

# --- 2. 사이드바 (설정 창) ---
with st.sidebar:
    st.title("🎨 디자인 & 설정")
    st.write("앱의 설정을 변경해 보세요.")
    
    # API 키 입력 (가려짐 모드)
    user_api_key = st.text_input("🔑 Gemini API Key", type="password")
    
    st.divider()
    
    # 분석 대상 국가 선택 (MBTI용)
    all_countries = mbti_df['Country'].unique()
    target_country = st.selectbox("🌍 분석할 국가", all_countries, index=list(all_countries).index("South Korea") if "South Korea" in all_countries else 0)

    # 분석 연도 선택 (기온용)
    year_range = st.slider("📅 연도 범위", 
                           int(weather_df['날짜'].dt.year.min()), 
                           int(weather_df['날짜'].dt.year.max()), 
                           (2020, 2024))

# --- 3. 메인 화면 (결과창) ---
st.title("✨ 데이터 마법 대시보드")
st.markdown(f"현재 **{target_country}**의 성격 분석과 **서울의 기온 변화**를 살펴보고 있습니다.")

# 탭으로 메뉴 나누기
tab1, tab2 = st.tabs(["🌡️ 기후 변화 분석", "🧠 국가별 MBTI 통계"])

# --- [Tab 1: 기후 변화 분석] ---
with tab1:
    st.header("서울의 온도 변화를 확인해요")
    
    # 데이터 필터링 (선택한 연도 범위)
    filtered_weather = weather_df[(weather_df['날짜'].dt.year >= year_range[0]) & 
                                  (weather_df['날짜'].dt.year <= year_range[1])]
    
    # 화면을 7:3 비율로 나누기
    col1, col2 = st.columns([7, 3])
    
    with col1:
        fig_line = px.line(filtered_weather, x='날짜', y='평균기온(℃)', 
                           title=f"{year_range[0]}년~{year_range[1]}년 기온 추이",
                           line_shape="spline", color_discrete_sequence=['#FF4B4B'])
        st.plotly_chart(fig_line, use_container_width=True)
        
    with col2:
        st.subheader("📋 요약 리포트")
        avg_temp = filtered_weather['평균기온(℃)'].mean()
        max_temp = filtered_weather['최고기온(℃)'].max()
        
        st.metric("기간 내 평균 기온", f"{avg_temp:.1f} °C")
        st.metric("기간 내 최고 기온", f"{max_temp:.1f} °C")
        
        st.info("💡 Tip: 그래프를 드래그하면 특정 구간을 확대해서 볼 수 있어요!")

# --- [Tab 2: MBTI 통계] ---
with tab2:
    st.header(f"{target_country} 사람들은 어떤 성격일까?")
    
    # 특정 국가 데이터 추출 및 시각화 준비 (Melt 과정)
    country_data = mbti_df[mbti_df['Country'] == target_country].drop(columns=['Country'])
    country_melted = country_data.melt(var_name='MBTI', value_name='Ratio')
    # 상위 10개 유형만 보기
    top_10_mbti = country_melted.sort_values(by='Ratio', ascending=False).head(10)
    
    col_bar, col_info = st.columns([6, 4])
    
    with col_bar:
        fig_bar = px.bar(top_10_mbti, x='MBTI', y='Ratio', 
                         title=f"{target_country} 상위 10개 MBTI 분포",
                         color='Ratio', color_continuous_scale='Purples')
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col_info:
        st.subheader("🧐 데이터 해석")
        most_common = top_10_mbti.iloc[0]['MBTI']
        st.write(f"현재 {target_country}에서 가장 흔한 유형은 **{most_common}**입니다.")
        
        if st.button("Gemini에게 이 결과 물어보기"):
            if not user_api_key:
                st.warning("사이드바에 API 키를 먼저 입력해 주세요!")
            else:
                st.write("AI 분석 중... (이후 2교시 코드를 연결하세요!)")

# 하단 푸터
st.divider()
st.center = st.caption("Made with Love by Vibe Coding Camp ✨")
