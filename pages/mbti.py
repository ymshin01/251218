import streamlit as st

# 1. 페이지 레이아웃 및 제목 설정
st.set_page_config(page_title="MBTI 진로 추천기", page_icon="🔍")

# 2. MBTI 데이터베이스 (별도 라이브러리 없이 딕셔너리로 관리)
mbti_db = {
    "ISTJ": {"jobs": ["회계사", "공무원"], "book": "아주 작은 습관의 힘"},
    "ISFJ": {"jobs": ["사회복지사", "초등교사"], "book": "나를 사랑하는 법"},
    "INFJ": {"jobs": ["상담심리사", "작가"], "book": "데미안"},
    "INTJ": {"jobs": ["소프트웨어 아키텍트", "전략 기획자"], "book": "생각에 관한 생각"},
    "ISTP": {"jobs": ["시스템 분석가", "파일럿"], "book": "미움받을 용기"},
    "ISFP": {"jobs": ["패션 디자이너", "조경가"], "book": "월든"},
    "INFP": {"jobs": ["카피라이터", "예술 치료사"], "book": "어린 왕자"},
    "INTP": {"jobs": ["대학 교수", "데이터 분석가"], "book": "사피엔스"},
    "ESTP": {"jobs": ["경찰관", "영업 실무자"], "book": "부자 아빠 가난한 아빠"},
    "ESFP": {"jobs": ["이벤트 플래너", "연예인"], "book": "인간관계론"},
    "ENFP": {"jobs": ["홍보 전문가", "여행 작가"], "book": "연금술사"},
    "ENTP": {"jobs": ["기업가", "정치인"], "book": "오리지널스"},
    "ESTJ": {"jobs": ["프로젝트 매니저", "군 장교"], "book": "원칙"},
    "ESFJ": {"jobs": ["호텔 지배인", "초등 교육자"], "book": "기브앤테이크"},
    "ENFJ": {"jobs": ["코치", "비영리 단체장"], "book": "사람은 무엇으로 사는가"},
    "ENTJ": {"jobs": ["경영 컨설턴트", "변호사"], "book": "손자병법"},
}

# 3. 사용자 인터페이스(UI) 구성
st.title("🌟 MBTI 맞춤형 진로 & 도서 추천")
st.write("본인의 MBTI를 선택하시면 어울리는 직업과 도서를 추천해 드립니다.")

# 드롭다운 메뉴 생성
mbti_list = sorted(list(mbti_db.keys()))
selected_mbti = st.selectbox("당신의 MBTI 유형을 선택하세요:", mbti_list)

# 4. 결과 출력
if selected_mbti:
    data = mbti_db[selected_mbti]
    
    st.markdown("---")
    st.subheader(f"✅ {selected_mbti} 유형을 위한 추천 결과")
    
    # 두 개의 열(Column)로 나누어 출력
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### 🎯 추천 진로")
        for job in data["jobs"]:
            st.write(f"- {job}")
            
    with col2:
        st.write("### 📚 추천 도서")
        st.write(f"**[{data['book']}]**")

    # 축하 효과
    st.balloons()
