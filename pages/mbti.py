import streamlit as st

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="MBTI 포켓몬 매칭",
    page_icon="⚡",
    layout="centered"
)

# --- 데이터베이스 (딕셔너리로 하드코딩) ---
# 별도 라이브러리 없이 데이터를 관리하기 위해 딕셔너리를 사용합니다.
# 이미지 URL은 PokéAPI의 공식 아트워크 주소를 사용합니다.
mbti_pokemon_db = {
    "ISTJ": {
        "pokemon": "코일 (Magnemite)",
        "image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/81.png",
        "reason": "원칙을 중요시하고 책임감이 강하며, 기계처럼 정확하고 성실하게 임무를 수행하는 모습이 코일과 닮았습니다."
    },
    "ISFJ": {
        "pokemon": "해피너스 (Blissey)",
        "image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/242.png",
        "reason": "타인을 돕는 것을 기쁨으로 여기며, 온화하고 헌신적인 성격으로 주변을 치유하는 포켓몬입니다."
    },
    "INFJ": {
        "pokemon": "가디안 (Gardevoir)",
        "image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/282.png",
        "reason": "깊은 통찰력과 직관을 가졌으며, 트레이너를 지키기 위해 미래를 예지하고 헌신하는 신비로운 포켓몬입니다."
    },
    "INTJ": {
        "pokemon": "후딘 (Alakazam)",
        "image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/65.png",
        "reason": "IQ 5000의 천재 포켓몬으로, 논리적이고 전략적인 사고를 하며 냉철하게 상황을 분석하는 모습이 INTJ와 같습니다."
    },
    "ISTP": {
        "pokemon": "나무킹 (Sceptile)",
        "image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/254.png",
        "reason": "조용하고 과묵하지만 위기 상황에서 뛰어난 순발력과 상황 판단력을 보여주는 실용적인 해결사입니다."
    },
    "ISFP": {
        "pokemon": "이브이 (Eevee)",
        "image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/133.png",
        "reason": "온화하고 예술적인 감각을 지녔으며, 주변 환경에 따라 다양하게 변화할 수 있는 유연함과 잠재력을 가졌습니다."
    },
    "INFP": {
        "pokemon": "미뇽 (Dratini)",
        "image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/147.png",
        "reason": "이상적이고 몽환적인 분위기를 풍기며, 내면에 거대한 잠재력(망나뇽으로 진화)을 숨기고 있는 신비로운 존재입니다."
    },
    "INTP": {
        "pokemon": "폴리곤 (Porygon)",
        "image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/137.png",
        "reason": "인공적으로 만들어진 포켓몬처럼 논리적이고 분석적이며, 호기심이 많아 끊임없이 지적 탐구를 즐기는 유형입니다."
    },
    "ESTP": {
        "pokemon": "번치코 (Blaziken)",
        "image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/257.png",
        "reason": "에너지가 넘치고 활동적이며, 순간의 스릴을 즐기고 행동으로 바로 옮기는 열정적인 파이터입니다."
    },
    "ESFP": {
        "pokemon": "푸린 (Jigglypuff)",
        "image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/39.png",
        "reason": "주목받는 것을 좋아하고 노래하기를 즐기는 천부적인 연예인 기질을 가졌습니다. 주변을 즐겁게 만듭니다."
    },
    "ENFP": {
        "pokemon": "토게피 (Togepi)",
        "image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/175.png",
        "reason": "순수하고 호기심이 많으며, 긍정적인 에너지를 주변에 전파하여 모두에게 행복을 가져다주는 존재입니다."
    },
    "ENTP": {
        "pokemon": "팬텀 (Gengar)",
        "image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/94.png",
        "reason": "장난기가 많고 재치가 넘치며, 기존의 틀을 깨는 독창적인 아이디어로 상대를 놀래키는 것을 즐깁니다."
    },
    "ESTJ": {
        "pokemon": "윈디 (Arcanine)",
        "image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/59.png",
        "reason": "용맹하고 충성심이 강하며, 규칙과 질서를 수호하는 리더십 있는 모습이 경찰견 포켓몬 윈디와 닮았습니다."
    },
    "ESFJ": {
        "pokemon": "치코리타 (Chikorita)",
        "image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/152.png",
        "reason": "사교적이고 친절하며, 트레이너와의 유대감을 중요하게 생각하고 주변 분위기를 따뜻하게 만드는 포켓몬입니다."
    },
    "ENFJ": {
        "pokemon": "라프라스 (Lapras)",
        "image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/131.png",
        "reason": "높은 지능과 온화한 마음씨로 사람들을 등에 태우고 바다를 건너는, 이타적이고 카리스마 있는 리더형 포켓몬입니다."
    },
    "ENTJ": {
        "pokemon": "뮤츠 (Mewtwo)",
        "image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/150.png",
        "reason": "강력한 힘과 냉철한 판단력을 가졌으며, 목표를 달성하기 위해 전략적으로 행동하는 타고난 지배자입니다."
    },
}

# --- UI 구현 ---
st.title("⚡ 나와 닮은 포켓몬 찾기!")
st.write("당신의 MBTI를 선택하면 가장 비슷한 성향의 포켓몬을 알려줍니다.")
st.markdown("---")

# MBTI 선택 셀렉트박스
mbti_list = sorted(mbti_pokemon_db.keys())
selected_mbti = st.selectbox("당신의 MBTI 유형을 선택해주세요:", mbti_list)

# 결과 출력 영역
if selected_mbti:
    data = mbti_pokemon_db[selected_mbti]
    
    st.header(f"당신은... {data['pokemon']} 타입!")
    
    # 2단 컬럼 레이아웃 (왼쪽: 텍스트, 오른쪽: 이미지)
    col1, col2 = st.columns([3, 2]) # 텍스트 영역을 조금 더 넓게
    
    with col1:
        st.subheader("💡 선정 이유")
        st.info(data['reason'])
        
    with col2:
        # st.image는 웹 URL 이미지를 바로 표시할 수 있습니다.
        st.image(data['image_url'], caption=data['pokemon'], use_container_width=True)
        
    st.balloons()
