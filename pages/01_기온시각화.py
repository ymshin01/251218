import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 기본 설정 (와이드 모드)
st.set_page_config(page_title="110년 기온 분석기", layout="wide")

# 2. 데이터 불러오기 및 전처리
@st.cache_data
def load_data():
    # 같은 폴더의 test.csv 읽기
    df = pd.read_csv('test.csv')
    
    # 날짜 데이터 정제 (앞에 붙은 \t 기호 제거)
    df['날짜'] = df['날짜'].astype(str).str.replace('\t', '').str.strip()
    df['날짜'] = pd.to_datetime(df['날짜'])
    
    # 연도 컬럼 생성
    df['연도'] = df['날짜'].dt.year
    
    # 기온 데이터가 없는 행은 삭제
    df = df.dropna(subset=['평균기온(℃)'])
    return df

# 앱 제목 부분
st.title("🌡️ 지난 110년간 기온은 정말 올랐을까?")
st.markdown("마우스를 그래프 위에 올려 기온을 확인하고, 드래그해서 구간을 확대해 보세요!")

try:
    df = load_data()

    # 연도별 평균 기온 계산
    annual_temp = df.groupby('연도')['평균기온(℃)'].mean().reset_index()

    # 3. 분석 지표 계산 (초기 10년 vs 최근 10년)
    start_avg = annual_temp.head(10)['평균기온(℃)'].mean()
    end_avg = annual_temp.tail(10)['평균기온(℃)'].mean()
    diff = end_avg - start_avg

    # 메트릭(숫자 카드) 표시
    col1, col2, col3 = st.columns(3)
    col1.metric("관측 시작", f"{int(annual_temp['연도'].min())}년")
    col2.metric("최근 관측", f"{int(annual_temp['연도'].max())}년")
    col3.metric("기온 변화량", f"{diff:.2f} ℃", delta=f"{diff:.2f} ℃")

    # 4. Plotly 인터랙티브 그래프 그리기
    # 
    fig = px.line(
        annual_temp, 
        x='연도', 
        y='평균기온(℃)',
        title='연도별 평균 기온 변화 (1907년 ~ 현재)',
        labels={'연도': 'Year', '평균기온(℃)': 'Avg Temp (℃)'},
        markers=True # 각 지점에 점 표시
    )

    # 그래프 선 색상 및 디자인 살짝 수정
    fig.update_traces(line_color='#FF4B4B', marker=dict(size=4))
    fig.update_layout(hovermode="x unified") # 마우스 올렸을 때 설명창 스타일

    # 스트림릿에 Plotly 그래프 표시
    st.plotly_chart(fig, use_container_width=True)

    # 5. 분석 결론 요약
    st.divider()
    st.subheader("🔍 분석 결과")
    
    if diff > 0:
        st.write(f"📈 데이터 분석 결과, 관측 초기 대비 최근 10년의 평균 기온이 약 **{diff:.2f}도 상승**했습니다.")
        st.info("이 그래프는 약 110년 동안 기온이 꾸준히 상승하는 '지구 온난화' 추세를 명확히 보여주고 있습니다.")
    else:
        st.write("📉 기온의 뚜렷한 상승 추세가 보이지 않습니다.")

    # 데이터 표 보기 옵션
    if st.checkbox("전체 연도별 데이터 표 보기"):
        st.dataframe(annual_temp)

except FileNotFoundError:
    st.error("'test.csv' 파일을 찾을 수 없습니다. 파일이 코드와 같은 폴더에 있는지 확인해주세요.")
except Exception as e:
    st.error(f"오류가 발생했습니다: {e}")
