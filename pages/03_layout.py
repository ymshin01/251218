import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai  # 이 부분이 오류가 났던 곳입니다.
import os

# 1. 페이지 설정
st.set_page_config(page_title="AI 데이터 마법사", page_icon="🪄", layout="wide")

# --- 데이터 로드 함수 (파일이 같은 폴더에 있어야 함) ---
@st.cache_data
def load_weather():
    df = pd.read_csv("test.csv")
    df['날짜'] = pd.to_datetime(df['날짜'].str.strip())
    return df

@st.cache_data
def load_mbti():
    return pd.read_csv("countries.csv")

# 데이터 불러오기
try:
    weather_df = load_weather()
    mbti_df = load_mbti()
except Exception as e:
    st.error(f"데이터 파일 로드 중 오류 발생: {e}")
    st.stop()

# --- 2. 사이드바 ---
with st.sidebar:
    st.title("🎨 앱 설정")
    user_api_key = st.text_input("🔑 Gemini API Key를 입력하세요", type="password")
    
    st.divider()
    
    all_countries = mbti_df['Country'].unique()
    target_country = st.selectbox("🌍 분석할 국가", all_countries, index=list(all_countries).index("South Korea") if "South Korea" in all_countries else 0)

    min_year = int(weather_df['날짜'].dt.year.min())
    max_year = int(weather_df['날짜'].dt.year.max())
    year_range = st.slider("📅 기온 분석 기간", min_year, max_year, (2020, 2024))

# --- 3. 메인 화면 ---
st.title("✨ AI 데이터 인사이트 대시보드")

tab1, tab2 = st.tabs(["🌡️ 기후 변화 분석", "🧠 국가별 MBTI 통계"])

# [Tab 1: 기후 변화 분석]
with tab1:
    st.header("서울의 온도 변화 분석")
    filtered_weather = weather_df[(weather_df['날짜'].dt.year >= year_range[0]) & 
                                  (weather_df['날짜'].dt.year <= year_range[1])]
    
    col1, col2 = st.columns([7, 3])
    with col1:
        fig_line = px.line(filtered_weather, x='날짜', y='평균기온(℃)', title="기온 변화 추이")
        st.plotly_chart(fig_line, use_container_width=True)
    with col2:
        st.metric("평균 기온", f"{filtered_weather['평균기온(℃)'].mean():.1f} °C")
        if st.button("AI 기상 캐스터 분석"):
            if user_api_key:
                genai.configure(api_key=user_api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(f"서울 기온 데이터 {filtered_weather['평균기온(℃)'].mean():.1f}도에 대해 분석해줘.")
                st.chat_message("assistant").write(response.text)
            else:
                st.warning("API 키를 입력하세요.")

# [Tab 2: MBTI 통계]
with tab2:
    st.header(f"{target_country} 성격 분포")
    country_data = mbti_df[mbti_df['Country'] == target_country].drop(columns=['Country'])
    country_melted = country_data.melt(var_name='MBTI', value_name='Ratio')
    top_10 = country_melted.sort_values(by='Ratio', ascending=False).head(10)
    
    col_bar, col_info = st.columns([6, 4])
    with col_bar:
        fig_bar = px.bar(top_10, x='MBTI', y='Ratio', color='Ratio', color_continuous_scale='Purples')
        st.plotly_chart(fig_bar, use_container_width=True)
    with col_info:
        if st.button("Gemini에게 분석 요청"):
            if user_api_key:
                genai.configure(api_key=user_api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                mbti_text = ", ".join([f"{r['MBTI']}({r['Ratio']*100:.1f}%)" for _, r in top_10.iterrows()])
                response = model.generate_content(f"{target_country}의 MBTI 분포 {mbti_text}를 분석해줘.")
                st.write(response.text)
            else:
                st.warning("API 키를 입력하세요.")

st.divider()
st.caption("© 2024 바이브 코딩캠프 ✨")
