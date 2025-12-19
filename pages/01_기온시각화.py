import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="110년 기온 변화 분석", layout="wide")

def load_data():
    """데이터를 로드하고 전처리하는 함수"""
    file_name = "test.csv"
    
    try:
        # 한글 데이터는 보통 cp949 또는 euc-kr 인코딩을 사용합니다.
        df = pd.read_csv(file_name, encoding='cp949')
        
        # 데이터 전처리: 기상청 데이터의 날짜 컬럼 깨짐('\t', '"') 해결
        if '날짜' in df.columns:
            # 문자열로 변환 후 불필요한 특수문자 제거
            df['날짜'] = df['날짜'].astype(str).str.replace('\t', '').str.replace('"', '').str.strip()
            # 날짜 형식으로 변환
            df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
            
        return df
    except Exception as e:
        st.error(f"데이터 로드 중 오류가 발생했습니다: {e}")
        return None

# 메인 타이틀
st.title("🌡️ 지난 110년, 기온은 정말 상승했을까?")
st.markdown("업로드된 데이터를 기반으로 연도별 평균 기온 변화를 분석합니다.")

# 데이터 로드
df = load_data()

if df is not None:
    # 연도 컬럼 생성
    df['년도'] = df['날짜'].dt.year

    # 1. 연도별 평균 기온 계산
    # 결측치(NaN)가 있는 행은 제외하고 계산
    yearly_avg = df.groupby('년도')['평균기온(℃)'].mean().reset_index()
    yearly_avg.columns = ['년도', '연평균기온']

    # 2. 10년 이동 평균 계산 (장기 추세선)
    yearly_avg['10년 이동평균'] = yearly_avg['연평균기온'].rolling(window=10).mean()

    # 3. 데이터 시각화 준비 (인덱스를 년도로 설정하여 차트 X축으로 사용)
    chart_data = yearly_avg.set_index('년도')

    # --- 화면 구성 ---
    
    # [섹션 1] 핵심 지표 비교 (과거 vs 현재)
    st.subheader("📊 과거와 현재 비교")
    
    # 데이터의 시작 연도와 끝 연도 확인
    start_year = yearly_avg['년도'].min()
    end_year = yearly_avg['년도'].max()
    
    # 처음 10년과 마지막 10년의 평균 기온 비교
    past_mean = yearly_avg[yearly_avg['년도'] <= start_year + 10]['연평균기온'].mean()
    recent_mean = yearly_avg[yearly_avg['년도'] >= end_year - 10]['연평균기온'].mean()
    diff = recent_mean - past_mean

    col1, col2, col3 = st.columns(3)
    col1.metric(label=f"과거 10년 평균 ({start_year}~)", value=f"{past_mean:.1f} ℃")
    col2.metric(label=f"최근 10년 평균 (~{end_year})", value=f"{recent_mean:.1f} ℃")
    col3.metric(label="기온 상승폭", value=f"{diff:.1f} ℃", delta=f"{diff:.1f} ℃")

    st.divider()

    # [섹션 2] 그래프 시각화
    st.subheader("📈 연도별 기온 변화 추세")
    st.caption("파란선: 해당 연도의 평균 기온 / 붉은선(또는 다른 색): 10년 이동 평균(장기 추세)")
    
    # 스트림릿 내장 라인 차트 (인터랙티브)
    st.line_chart(chart_data[['연평균기온', '10년 이동평균']], color=["#85C1E9", "#FF5733"])

    # [섹션 3] 데이터 확인
    with st.expander("분석에 사용된 연도별 데이터 보기"):
        st.dataframe(yearly_avg.style.format("{:.2f}"))

else:
    st.warning("데이터 파일을 읽을 수 없습니다. test.csv 파일이 같은 폴더에 있는지 확인해주세요.")
