import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 한글 폰트 설정 (Streamlit Cloud 환경 고려)
# 기본적으로 맷플롯립은 한글이 깨질 수 있으나, 여기서는 영문 레이블을 병행하여 가독성을 높였습니다.

def load_data():
    # 데이터 로드
    df = pd.read_csv('test.csv')
    
    # 1. 날짜 컬럼의 공백 및 탭 제거 후 데이트타임 변환
    df['날짜'] = df['날짜'].str.strip()
    df['날짜'] = pd.to_datetime(df['날짜'])
    
    # 2. 분석을 위해 '연도' 컬럼 생성
    df['연도'] = df['날짜'].dt.year
    
    # 3. 결측치 제거 (기온 데이터가 없는 행은 제외)
    df = df.dropna(subset=['평균기온(℃)'])
    
    return df

# 앱 제목
st.title("🌡️ 지난 110년간 기온 변화 분석기")
st.markdown("업로드된 데이터를 바탕으로 장기적인 기온 상승 추세를 확인합니다.")

try:
    df = load_data()

    # --- 데이터 요약 ---
    st.subheader("1. 데이터 요약")
    col1, col2, col3 = st.columns(3)
    col1.metric("시작 연도", int(df['연도'].min()))
    col2.metric("종료 연도", int(df['연도'].max()))
    col3.metric("총 데이터 수", f"{len(df):,}")

    # --- 연도별 평균 기온 계산 ---
    annual_temp = df.groupby('연도')['평균기온(℃)'].mean().reset_index()

    # --- 시각화 ---
    st.subheader("2. 연도별 평균 기온 추이")
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(annual_temp['연도'], annual_temp['평균기온(℃)'], marker='o', markersize=2, linestyle='-', color='red', alpha=0.7)
    
    # 추세선 추가 (간단한 이동평균)
    annual_temp['추세선'] = annual_temp['평균기온(℃)'].rolling(window=10).mean()
    ax.plot(annual_temp['연도'], annual_temp['추세선'], color='black', linewidth=2, label='10-Year Moving Avg')

    ax.set_xlabel("Year")
    ax.set_ylabel("Avg Temperature (℃)")
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend()
    
    st.pyplot(fig)

    # --- 분석 결과 ---
    st.subheader("3. 기온 변화 분석")
    
    first_year = annual_temp['연도'].min()
    last_year = annual_temp['연도'].max()
    
    # 초기 10년 vs 최근 10년 비교
    start_avg = annual_temp.head(10)['평균기온(℃)'].mean()
    end_avg = annual_temp.tail(10)['평균기온(℃)'].mean()
    diff = end_avg - start_avg

    st.write(f"📊 **{int(first_year)}년경**의 10년 평균 기온: `{start_avg:.2f}℃` 쪽")
    st.write(f"📊 **{int(last_year)}년경**의 10년 평균 기온: `{end_avg:.2f}℃` 쪽")
    
    if diff > 0:
        st.error(f"결과: 약 110년 동안 평균 기온이 **{diff:.2f}℃ 상승**했습니다. 지구 온난화 경향이 뚜렷합니다.")
    else:
        st.success(f"결과: 평균 기온이 약 {abs(diff):.2f}℃ 하락했거나 큰 변화가 없습니다.")

    # 데이터 표 보여주기
    if st.checkbox("상세 데이터 보기"):
        st.write(annual_temp)

except FileNotFoundError:
    st.error("파일을 찾을 수 없습니다. 'test.csv' 파일이 같은 폴더에 있는지 확인해주세요.")
except Exception as e:
    st.error(f"오류가 발생했습니다: {e}")
