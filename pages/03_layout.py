import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai  # Gemini API 라이브러리 추가
import os

# 1. 페이지 설정
st.set_page_config(page_title="AI 데이터 마법사", page_icon="🪄", layout="wide")

# --- 데이터 로드 함수 ---
@st.cache_data
def load_weather():
    df = pd.read_csv("test.csv")
    # 날짜 데이터 전처리 (공백 제거 및 변환)
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

# --- 2. 사이드바 (설정 영역) ---
with st.sidebar:
    st.title("🎨 앱 설정")
    # API 키 입력창 (password 타입으로 가림)
    user_api_key = st.text_input("🔑 Gemini API Key를 입력하세요", type="password")
    
    st.divider()
    
    # 국가 선택
    all_countries = mbti_df['Country'].unique()
    target_country = st.selectbox("🌍 분석할 국가", all_countries, index=list(all_countries).index("South Korea") if "South Korea" in all_countries else 0)

    # 연도 범위 선택
    min_year = int(weather_df['날짜'].dt.year.min())
    max_year = int(weather_df['날짜'].dt.year.max())
    year_range = st.slider("📅 기온 분석 기간", min_year, max_year, (2020, 2024))

# --- 3. 메인 화면 ---
st.title("✨ AI 데이터 인사이트 대시보드")

tab1, tab2 = st.tabs(["🌡️ 기후 변화 분석", "🧠 국가별 MBTI 통계"])

# --- [Tab 1: 기후 변화 분석] ---
with tab1:
    st.header("서울의 온도 변화 분석")
    
    filtered_weather = weather_df[(weather_df['날짜'].dt.year >= year_range[0]) & 
                                  (weather_df['날짜'].dt.year <= year_range[1])]
    
    col1, col2 = st.columns([7, 3])
    
    with col1:
        fig_line = px.line(filtered_weather, x='날짜', y='평균기온(℃)', 
                           title=f"{year_range[0]}년~{year_range[1]}년 기온 변화 추이",
                           line_shape="spline", color_discrete_sequence=['#FF4B4B'])
        st.plotly_chart(fig_line, use_container_width=True)
        
    with col2:
        st.subheader("📊 요약 수치")
        avg_temp = filtered_weather['평균기온(℃)'].mean()
        max_temp = filtered_weather['최고기온(℃)'].max()
        st.metric("평균 기온", f"{avg_temp:.1f} °C")
        st.metric("최고 기온", f"{max_temp:.1f} °C")
        
        # 기온 데이터 AI 분석 버튼
        if st.button("AI 기상 캐스터에게 물어보기"):
            if not user_api_key:
                st.warning("먼저 사이드바에 API 키를 입력해 주세요!")
            else:
                genai.configure(api_key=user_api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # AI에게 줄 프롬프트 작성
                prompt = f"""
                너는 기상 전문가야. {year_range[0]}년부터 {year_range[1]}년까지 서울의 평균 기온은 {avg_temp:.1f}도였고, 
                최고 기온은 {max_temp:.1f}도였어. 이 데이터를 보고 최근 기후 변화의 심각성과 
                우리가 주의해야 할 점을 고등학생의 눈높이에서 친절하게 설명해줘.
                """
                
                with st.spinner("AI가 데이터를 분석하고 있습니다..."):
                    response = model.generate_content(prompt)
                    st.chat_message("assistant").write(response.text)

# --- [Tab 2: MBTI 통계] ---
with tab2:
    st.header(f"{target_country} 성격 분포 분석")
    
    # 데이터 변환 (Melt)
    country_data = mbti_df[mbti_df['Country'] == target_country].drop(columns=['Country'])
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
        st.write(f"현재 {target_country}에서 가장 높은 비율을 차지하는 유형은 **{most_common}**입니다.")
        
        # MBTI 데이터 AI 분석 버튼 (요청하신 부분)
        if st.button("Gemini에게 분석 결과 물어보기"):
            if not user_api_key:
                st.warning("사이드바에 API 키를 먼저 입력해 주세요!")
            else:
                # 1. API 설정
                genai.configure(api_key=user_api_key)
                # 2. 모델 설정 (성능이 좋은 flash 모델 권장)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # 3. AI에게 전달할 데이터 정리
                mbti_list_text = ", ".join([f"{row['MBTI']}({row['Ratio']*100:.1f}%)" for _, row in top_10_mbti.iterrows()])
                
                # 4. 프롬프트 구성
                prompt = f"""
                너는 세계 성격 유형 분석 전문가야. {target_country}의 성격 분포 데이터는 다음과 같아: {mbti_list_text}.
                이 데이터를 바탕으로 {target_country} 사람들의 전반적인 국민성과 특징을 분석해줘.
                그리고 이 국가로 여행을 가거나 친구를 사귈 때 알아두면 좋은 팁을 3가지로 정리해서 알려줘.
                답변은 친절하고 흥미진진한 말투로 해줘!
                """
                
                # 5. 실행 및 결과 출력
                with st.spinner("Gemini가 데이터를 읽고 생각하는 중..."):
                    try:
                        response = model.generate_content(prompt)
                        st.markdown("---")
                        st.subheader(f"🤖 Gemini의 {target_country} 분석 리포트")
                        st.write(response.text)
                    except Exception as e:
                        st.error(f"AI 응답 생성 중 오류가 발생했습니다: {e}")

# 하단 푸터
st.divider()
st.caption("© 2024 바이브 코딩캠프 - 데이터를 읽어주는 AI 대시보드 ✨")
