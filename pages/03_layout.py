import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import os

# 1. 페이지 설정
st.set_page_config(page_title="AI 데이터 마법사", page_icon="🪄", layout="wide")

# --- 데이터 로드 함수 ---
@st.cache_data
def load_weather():
    try:
        # 파일이 없으면 에러가 나므로 예외처리
        if not os.path.exists("test.csv"):
            return None
        df = pd.read_csv("test.csv")
        # 날짜 변환 (에러 발생 시 무시하고 넘어가는 설정 추가)
        df['날짜'] = pd.to_datetime(df['날짜'].str.strip(), errors='coerce')
        return df
    except Exception as e:
        st.error(f"날씨 데이터 로드 중 오류: {e}")
        return None

@st.cache_data
def load_mbti():
    try:
        if not os.path.exists("countries.csv"):
            return None
        return pd.read_csv("countries.csv")
    except Exception as e:
        st.error(f"MBTI 데이터 로드 중 오류: {e}")
        return None

# 데이터 불러오기
weather_df = load_weather()
mbti_df = load_mbti()

# 데이터 파일이 없을 경우 중단
if weather_df is None or mbti_df is None:
    st.error("🚨 데이터 파일(test.csv, countries.csv)을 찾을 수 없습니다. 실행 경로에 파일을 넣어주세요.")
    st.stop()

# --- 2. 사이드바 (설정 영역) ---
with st.sidebar:
    st.title("🎨 앱 설정")
    
    st.info("API 키가 없나요?")
    st.link_button("🔑 Gemini API 키 발급받기", "https://aistudio.google.com/app/apikey")
    
    st.divider()
    
    # API 키 입력창
    api_key_input = st.text_input("위 사이트에서 받은 키를 입력하세요", type="password")
    
    # 입력된 키가 있으면 공백 제거 후 저장
    user_api_key = api_key_input.strip() if api_key_input else ""
    
    st.divider()
    
    # 국가 및 연도 선택
    all_countries = mbti_df['Country'].unique()
    # South Korea가 있으면 기본값으로, 없으면 첫 번째 국가 선택
    default_ix = list(all_countries).index("South Korea") if "South Korea" in all_countries else 0
    target_country = st.selectbox("🌍 분석할 국가", all_countries, index=default_ix)

    # 연도 범위 슬라이더 (데이터에 있는 연도 기준)
    # 날짜 파싱이 실패해서 NaT가 된 경우를 제외하고 연도 계산
    valid_dates = weather_df['날짜'].dropna()
    if not valid_dates.empty:
        min_year = int(valid_dates.dt.year.min())
        max_year = int(valid_dates.dt.year.max())
    else:
        min_year, max_year = 2020, 2024 # 기본값

    year_range = st.slider("📅 기온 분석 기간", min_year, max_year, (min_year, max_year))

# --- 3. 메인 화면 ---
st.title("✨ AI 데이터 인사이트 대시보드")

tab1, tab2 = st.tabs(["🌡️ 기후 변화 분석", "🧠 국가별 MBTI 통계"])

# --- [Tab 1: 기후 변화 분석] ---
with tab1:
    st.header("서울의 온도 변화 분석")
    
    # 선택한 연도 범위로 필터링
    filtered_weather = weather_df[
        (weather_df['날짜'].dt.year >= year_range[0]) & 
        (weather_df['날짜'].dt.year <= year_range[1])
    ]
    
    col1, col2 = st.columns([7, 3])
    
    with col1:
        if not filtered_weather.empty:
            fig_line = px.line(filtered_weather, x='날짜', y='평균기온(℃)', 
                               title=f"{year_range[0]}년~{year_range[1]}년 기온 변화 추이",
                               line_shape="spline", color_discrete_sequence=['#FF4B4B'])
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.warning("선택한 기간에 해당하는 데이터가 없습니다.")
        
    with col2:
        st.subheader("📊 요약 수치")
        if not filtered_weather.empty:
            avg_temp = filtered_weather['평균기온(℃)'].mean()
            max_temp = filtered_weather['최고기온(℃)'].max()
            st.metric("평균 기온", f"{avg_temp:.1f} °C")
            st.metric("최고 기온", f"{max_temp:.1f} °C")
            
            if st.button("AI 기상 캐스터에게 물어보기"):
                if not user_api_key:
                    st.warning("👈 사이드바에 API 키를 입력해주세요!")
                else:
                    try:
                        genai.configure(api_key=user_api_key)
                        # [수정됨] 최신 모델 이름 사용
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        
                        prompt = f"서울의 평균기온 {avg_temp:.1f}도, 최고기온 {max_temp:.1f}도 데이터를 바탕으로 기후 분석을 해줘. 짧고 명확하게."
                        
                        with st.spinner("AI가 분석 중입니다..."):
                            response = model.generate_content(prompt)
                            st.chat_message("assistant").write(response.text)
                    except Exception as e:
                        st.error(f"AI 호출 오류: {e}")
        else:
            st.write("데이터 없음")

# --- [Tab 2: MBTI 통계] ---
with tab2:
    st.header(f"{target_country} 성격 분포 분석")
    
    # 해당 국가 데이터 필터링
    country_data = mbti_df[mbti_df['Country'] == target_country]
    
    if not country_data.empty:
        country_data = country_data.drop(columns=['Country'])
        country_melted = country_data.melt(var_name='MBTI', value_name='Ratio')
        top_10_mbti = country_melted.sort_values(by='Ratio', ascending=False).head(10)
        
        col_bar, col_info = st.columns([6, 4])
        
        with col_bar:
            fig_bar = px.bar(top_10_mbti, x='MBTI', y='Ratio', 
                             title=f"{target_country} 성격 유형 TOP 10",
                             color='Ratio', color_continuous_scale='Purples')
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with col_info:
            st.subheader("🧐 데이터 해석 및 AI 분석")
            most_common = top_10_mbti.iloc[0]['MBTI']
            st.write(f"가장 흔한 유형: **{most_common}**")
            
            if st.button("Gemini에게 분석 결과 물어보기"):
                if not user_api_key:
                    st.warning("👈 사이드바에 API 키를 입력해주세요!")
                else:
                    try:
                        genai.configure(api_key=user_api_key)
                        # [수정됨] 최신 모델 이름 사용
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        
                        mbti_list_text = ", ".join([f"{row['MBTI']}({row['Ratio']*100:.1f}%)" for _, row in top_10_mbti.iterrows()])
                        prompt = f"{target_country}의 MBTI 분포({mbti_list_text})를 보고 국민성 특징 3가지를 흥미롭게 분석해줘."
                        
                        with st.spinner("Gemini가 생각 중..."):
                            response = model.generate_content(prompt)
                            st.chat_message("assistant").write(response.text)
                    except Exception as e:
                        st.error(f"AI 호출 오류: {e}")
    else:
        st.error(f"{target_country}에 대한 데이터가 없습니다.")

st.divider()
st.caption("© 2024 바이브 코딩캠프 ✨")
