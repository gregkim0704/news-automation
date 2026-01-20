"""
뉴스 추출기 웹 앱
Streamlit 기반의 맞춤형 뉴스 뷰어
"""

import streamlit as st
import time
from datetime import datetime
from src.fetcher import fetch_news_by_keywords, fetch_news
from src.summarizer import summarize_articles

# 페이지 설정
st.set_page_config(
    page_title="맞춤 뉴스 리더",
    page_icon="📰",
    layout="wide"
)

# 세션 상태 초기화
if 'articles' not in st.session_state:
    st.session_state.articles = []
if 'keywords' not in st.session_state:
    st.session_state.keywords = []
if 'loading' not in st.session_state:
    st.session_state.loading = False

# 커스텀 CSS
st.markdown("""
<style>
    .news-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
        border-left: 4px solid #1f77b4;
    }
    .news-title {
        font-size: 18px;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 10px;
    }
    .news-meta {
        font-size: 12px;
        color: #666;
        margin-bottom: 10px;
    }
    .news-summary {
        font-size: 14px;
        color: #333;
        line-height: 1.6;
    }
    .main-header {
        text-align: center;
        padding: 20px 0;
    }
    .keyword-tag {
        background-color: #e3f2fd;
        padding: 5px 10px;
        border-radius: 15px;
        margin: 2px;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)


def display_article(article, index):
    """기사를 카드 형태로 표시"""
    with st.container():
        st.markdown(f"""
        <div class="news-card">
            <div class="news-title">{article['title']}</div>
            <div class="news-meta">
                📌 {article['source']} | 🕐 {article['published']}
            </div>
            <div class="news-summary">{article.get('summary', '요약 없음')}</div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([1, 5])
        with col1:
            st.link_button("📖 원문 보기", article['link'])


def fetch_and_display_news(keywords, limit):
    """뉴스 수집 및 표시"""
    st.session_state.loading = True

    progress_bar = st.progress(0)
    status_text = st.empty()

    all_articles = []

    for i, keyword in enumerate(keywords):
        status_text.text(f"'{keyword}' 키워드로 뉴스 수집 중...")
        articles = fetch_news(keyword, limit=limit)

        # 중복 제거
        seen_links = {a['link'] for a in all_articles}
        for article in articles:
            if article['link'] not in seen_links:
                all_articles.append(article)
                seen_links.add(article['link'])

        progress_bar.progress((i + 1) / (len(keywords) + 1))

    # 요약 생성
    if all_articles:
        status_text.text("기사 요약 생성 중...")
        all_articles = summarize_articles(all_articles, delay=0.3)

    progress_bar.progress(1.0)
    status_text.text("완료!")
    time.sleep(0.5)
    progress_bar.empty()
    status_text.empty()

    st.session_state.articles = all_articles
    st.session_state.loading = False

    return all_articles


# 메인 UI
st.markdown("<h1 class='main-header'>📰 맞춤 뉴스 리더</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>관심 키워드를 입력하고 최신 뉴스를 확인하세요</p>", unsafe_allow_html=True)

# 사이드바 - 설정
with st.sidebar:
    st.header("⚙️ 설정")

    # 키워드 입력
    st.subheader("🔑 관심 키워드")
    keyword_input = st.text_input(
        "키워드 입력 (쉼표로 구분)",
        value="인공지능, 스타트업, 테크",
        help="관심 있는 키워드를 쉼표로 구분하여 입력하세요"
    )

    # 기사 수 설정
    article_limit = st.slider(
        "키워드당 기사 수",
        min_value=5,
        max_value=30,
        value=10,
        help="각 키워드당 수집할 기사 수"
    )

    # 검색 버튼
    if st.button("🔍 뉴스 검색", type="primary", use_container_width=True):
        keywords = [k.strip() for k in keyword_input.split(",") if k.strip()]
        if keywords:
            st.session_state.keywords = keywords
            fetch_and_display_news(keywords, article_limit)
        else:
            st.warning("키워드를 입력해주세요!")

    st.divider()

    # 현재 설정 표시
    if st.session_state.keywords:
        st.subheader("📋 현재 키워드")
        for kw in st.session_state.keywords:
            st.markdown(f"<span class='keyword-tag'>{kw}</span>", unsafe_allow_html=True)

    st.divider()

    # 정보
    st.caption("💡 Tip: 여러 키워드를 입력하면 더 다양한 뉴스를 볼 수 있어요!")
    st.caption(f"마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# 메인 콘텐츠
if st.session_state.loading:
    st.info("뉴스를 불러오는 중입니다...")

elif st.session_state.articles:
    # 통계 표시
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📰 총 기사 수", len(st.session_state.articles))
    with col2:
        sources = set(a['source'] for a in st.session_state.articles)
        st.metric("📌 언론사 수", len(sources))
    with col3:
        success_count = sum(1 for a in st.session_state.articles if not a.get('summary', '').startswith('('))
        st.metric("✅ 요약 성공", f"{success_count}개")

    st.divider()

    # 필터 옵션
    col1, col2 = st.columns([2, 1])
    with col1:
        search_in_results = st.text_input("🔎 결과 내 검색", placeholder="기사 제목 검색...")
    with col2:
        sort_option = st.selectbox("정렬", ["최신순", "언론사별"])

    # 필터링
    filtered_articles = st.session_state.articles
    if search_in_results:
        filtered_articles = [a for a in filtered_articles if search_in_results.lower() in a['title'].lower()]

    # 정렬
    if sort_option == "언론사별":
        filtered_articles = sorted(filtered_articles, key=lambda x: x['source'])

    st.divider()

    # 기사 표시
    if filtered_articles:
        st.subheader(f"📄 뉴스 목록 ({len(filtered_articles)}개)")

        for i, article in enumerate(filtered_articles):
            display_article(article, i)
    else:
        st.info("검색 결과가 없습니다.")

else:
    # 초기 화면
    st.markdown("""
    <div style='text-align: center; padding: 50px;'>
        <h3>👈 왼쪽 사이드바에서 키워드를 설정하고<br>뉴스 검색 버튼을 클릭하세요!</h3>
        <p style='color: #888;'>
            예시 키워드: 인공지능, 반도체, 스타트업, 주식, 부동산 등
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 빠른 시작 버튼들
    st.markdown("### 🚀 빠른 시작")
    col1, col2, col3, col4 = st.columns(4)

    quick_keywords = {
        "🤖 AI/기술": ["인공지능", "ChatGPT", "테크"],
        "💰 경제/금융": ["주식", "부동산", "경제"],
        "🎮 게임/엔터": ["게임", "넷플릭스", "K-POP"],
        "🏥 건강/의료": ["건강", "의료", "헬스케어"]
    }

    for col, (category, keywords) in zip([col1, col2, col3, col4], quick_keywords.items()):
        with col:
            if st.button(category, use_container_width=True):
                st.session_state.keywords = keywords
                fetch_and_display_news(keywords, 10)
                st.rerun()

# 푸터
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #888; font-size: 12px;'>"
    "Made with ❤️ using Streamlit | 뉴스 출처: 네이버 뉴스"
    "</p>",
    unsafe_allow_html=True
)
