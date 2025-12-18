import streamlit as st
import csv

# --- 페이지 설정 ---
st.set_page_config(page_title="국가별 MBTI 분석", layout="wide")

# --- 데이터 로드 함수 (표준 csv 라이브러리 사용) ---
@st.cache_data
def load_data():
    file_path = 'countries.csv'
    data = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 숫자 데이터 변환 (Country 제외 모든 컬럼)
                for key in row.keys():
                    if key != 'Country':
                        row[key] = float(row[key])
                data.append(row)
    except FileNotFoundError:
        st.error("파일을 찾을 수 없습니다. countries.csv 파일이 같은 폴더에 있는지 확인해주세요.")
    return data

data = load_data()

if data:
    # 모든 MBTI 유형 리스트 (첫 번째 행에서 국가명 제외)
    mbti_types = [key for key in data[0].keys() if key != 'Country']

    st.title("📊 국가별 MBTI 성향 분석 대시보드")
    st.info("이 앱은 업로드된 `countries.csv` 데이터를 기반으로 분석을 수행합니다.")

    # --- 1. 전체 국가 MBTI 평균 비율 ---
    st.header("🌎 1. 전 세계 MBTI 평균 분포")
    
    averages = {}
    for m_type in mbti_types:
        total = sum(row[m_type] for row in data)
        averages[m_type] = total / len(data)
    
    # 평균이 높은 순서대로 정렬
    sorted_avg = sorted(averages.items(), key=lambda x: x[1], reverse=True)
    
    # 상위 5개 표시
    cols = st.columns(5)
    for i in range(5):
        m_type, val = sorted_avg[i]
        cols[i].metric(m_type, f"{val*100:.2f}%")

    st.divider()

    # --- 2. 유형별 TOP 10 및 한국 비교 ---
    st.header("🔝 2. 유형별 국가 순위 & 한국 비교")
    
    selected_type = st.selectbox("분석할 MBTI 유형을 선택하세요:", mbti_types)
    
    # 선택된 유형 기준으로 정렬
    sorted_data = sorted(data, key=lambda x: x[selected_type], reverse=True)
    top_10 = sorted_data[:10]
    
    # 한국 데이터 찾기 (South Korea, Korea, Republic of 등 확인)
    korea_data = next((item for item in data if "Korea" in item["Country"]), None)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"🏆 {selected_type} 비율 높은 국가 TOP 10")
        # 테이블 형식으로 출력
        rank_table = []
        for i, row in enumerate(top_10, 1):
            rank_table.append({"순위": i, "국가": row["Country"], "비율": f"{row[selected_type]*100:.2f}%"})
        st.table(rank_table)

    with col2:
        st.subheader("🇰🇷 대한민국 데이터 확인")
        if korea_data:
            k_val = korea_data[selected_type]
            global_avg = averages[selected_type]
            diff = (k_val - global_avg) * 100
            
            st.write(f"**대한민국의 {selected_type} 비율:** `{k_val*100:.2f}%`")
            st.write(f"**전 세계 평균:** `{global_avg*100:.2f}%`")
            
            if diff > 0:
                st.success(f"평균보다 **{abs(diff):.2f}%p** 높습니다.")
            else:
                st.warning(f"평균보다 **{abs(diff):.2f}%p** 낮습니다.")
            
            # 간단한 비교 바 차트 (Streamlit 기본 차트 활용)
            chart_data = {
                "분류": ["세계 평균", "대한민국"],
                "비율": [global_avg, k_val]
            }
            # 데이터프레임 없이 딕셔너리로 차트 그리기
            st.bar_chart(data={"비율": [global_avg, k_val]}, y_label="비율")
        else:
            st.info("데이터셋에서 'Korea'를 포함한 국가명을 찾을 수 없습니다.")

else:
    st.warning("데이터를 불러오지 못했습니다.")
