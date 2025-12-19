import streamlit as st
import pandas as pd

# 앱 제목 및 설명
st.set_page_config(page_title="기온 변화 분석", layout="wide")
st.title("🌡️ 지난 110년간 기온은 정말 올랐을까?")
st.markdown("`test.csv` 데이터를 분석하여 연도별 기온 변화 추이를 보여줍니다.")

@st.cache_data
def load_and_clean_data():
    # 1. 데이터 읽기
    df = pd.read_csv('test.csv')
    
    # 2. 날짜 전처리 (따옴표와 탭 문자 제거)
    df['날짜'] = df['날짜'].astype(str).str.replace('\t', '').str.strip()
    df['날짜'] = pd.to_datetime(df['날짜'])
    
    # 3. 연도 컬럼 생성 및 결측치 제거
    df['연도'] = df['날짜'].dt.year
    df = df.dropna(subset=['평균기온(℃)'])
    return df

try:
    data = load_and_clean_data()

    # 연도별 평균 기온 계산
    annual_avg = data.groupby('연도')['평균기온(℃)'].mean()

    # --- 시각화 섹션 ---
    st.subheader("📈 연도별 평균 기온 추이")
    # 별도 설치가 필요 없는 Streamlit 내장 차트 사용
    st.line_chart(annual_avg)

    # --- 분석 결과 섹션 ---
    st.divider()
    
    # 시작 시점(첫 5년)과 최근 시점(마지막 5년) 비교
    start_temp = annual_avg.head(5).mean()
    end_temp = annual_avg.tail(5).mean()
    diff = end_temp - start_temp

    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="관측 초기 평균 (5년)", value=f"{start_temp:.2f} ℃")
    with col2:
        st.metric(label="최근 평균 (5년)", value=f"{end_temp:.2f} ℃", delta=f"{diff:.2f} ℃")

    if diff > 0:
        st.warning(f"⚠️ 분석 결과: 지난 110여 년간 기온이 약 **{diff:.2f}도 상승**한 것으로 나타납니다.")
    else:
        st.success("✅ 분석 결과: 기온의 유의미한 상승이 발견되지 않았습니다.")

    if st.checkbox("전체 데이터 표 보기"):
        st.dataframe(data)

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.info("파일 이름이 'test.csv'이고 코드와 같은 폴더에 있는지 확인해주세요.")
