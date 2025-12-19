import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="110년 기온 변화 분석", layout="wide")

def load_data():
    """데이터를 로드하고 전처리하는 함수 (인코딩 자동 감지 추가)"""
    file_name = "test.csv"
    df = None
    
    # 시도할 인코딩 목록 (순서대로 시도합니다)
    encodings = ['utf-8', 'cp949', 'euc-kr']
    
    for enc in encodings:
        try:
            # 해당 인코딩으로 읽기 시도
            df = pd.read_csv(file_name, encoding=enc)
            # 성공했다면 루프 탈출
            break
        except UnicodeDecodeError:
            # 이 인코딩이 아니면 다음 것으로 넘어감
            continue
        except Exception as e:
            st.error(f"파일 읽기 중 예상치 못한 오류 발생 ({enc}): {e}")
            return None
            
    if df is None:
        st.error(f"데이터를 읽을 수 없습니다. ({', '.join(encodings)} 모두 실패). 파일 인코딩을 확인해주세요.")
        return None

    # --- 데이터 전처리 로직 ---
    try:
        # 기상청 데이터 특유의 날짜 컬럼 깨짐('\t', '"') 해결
        # 컬럼명에 공백이 있을 수 있으므로 공백 제거
        df.columns = df.columns.str.strip()
        
        if '날짜' in df.columns:
            # 문자열로 변환 후 불필요한 특수문자 제거
            df['날짜'] = df['날짜'].astype(str).str.replace('\t', '').str.replace('"', '').str.strip()
            # 날짜 형식으로 변환
            df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
            
        return df
    except Exception as e:
        st.error(f"데이터 전처리 중 오류가 발생했습니다: {e}")
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
    # 컬럼명이 정확한지 확인 (공백 제거 등)
    temp_col = '평균기온(℃)'
    if temp_col not in df.columns:
        # 혹시 컬럼명이 다를 경우를 대비해 비슷한 컬럼 찾기
        cols = [c for c in df.columns if '평균기온' in c]
        if cols:
            temp_col = cols[0]
    
    if temp_col in df.columns:
        yearly_avg = df.groupby('년도')[temp_col].mean().reset_index()
        yearly_avg.columns = ['년도', '연평균기온']

        # 2. 10년 이동 평균 계산 (장기 추세선)
        yearly_avg['10년 이동평균'] = yearly_avg['연평균기온'].rolling(window=10).mean()

        # 3. 데이터 시각화 준비
        chart_data = yearly_avg.set_index('년도')

        # --- 화면 구성 ---
        
        # [섹션 1] 핵심 지표 비교
        st.subheader("📊 과거와 현재 비교")
        
        start_year = yearly_avg['년도'].min()
        end_year = yearly_avg['년도'].max()
        
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
        st.caption("파란선: 해당 연도의 평균 기온 / 붉은선: 10년 이동 평균(장기 추세)")
        
        st.line_chart(chart_data[['연평균기온', '10년 이동평균']], color=["#85C1E9", "#FF5733"])

        # [섹션 3] 데이터 확인
        with st.expander("분석에 사용된 연도별 데이터 보기"):
            st.dataframe(yearly_avg.style.format("{:.2f}"))
    else:
        st.error(f"'{temp_col}' 컬럼을 찾을 수 없습니다. 데이터 파일의 컬럼명을 확인해주세요.")
        st.write("현재 컬럼 목록:", df.columns.tolist())

else:
    st.warning("데이터 파일을 읽을 수 없습니다. test.csv 파일이 같은 폴더에 있는지 확인해주세요.")
