"""
뉴스 RSS 수집 모듈
다양한 언론사에서 키워드 기반으로 뉴스를 수집합니다.
"""

import feedparser
import requests
from urllib.parse import quote
from datetime import datetime
from typing import TypedDict
import re


class NewsArticle(TypedDict):
    """뉴스 기사 타입 정의"""
    title: str
    link: str
    published: str
    source: str
    summary: str


# 주요 언론사 RSS 피드 목록
RSS_FEEDS = {
    # 종합 일간지
    '조선일보': 'https://www.chosun.com/arc/outboundfeeds/rss/?outputType=xml',
    '중앙일보': 'https://rss.joins.com/joins_news_list.xml',
    '동아일보': 'https://rss.donga.com/total.xml',
    '한겨레': 'https://www.hani.co.kr/rss/',
    '경향신문': 'https://www.khan.co.kr/rss/rssdata/total_news.xml',
    '한국일보': 'https://www.hankookilbo.com/RSS',
    '세계일보': 'https://www.segye.com/Articles/RSSList/segye_recent.xml',
    '국민일보': 'http://rss.kmib.co.kr/data/kmibRssAll.xml',

    # 경제지
    '매일경제': 'https://www.mk.co.kr/rss/30000001/',
    '한국경제': 'https://www.hankyung.com/feed/all-news',
    '서울경제': 'https://www.sedaily.com/RSS/Section/',
    '머니투데이': 'https://rss.mt.co.kr/mt_news.xml',
    '이데일리': 'https://rss.edaily.co.kr/edaily_news.xml',
    '아시아경제': 'https://www.asiae.co.kr/rss/all.htm',
    '파이낸셜뉴스': 'https://www.fnnews.com/rss/fn_realnews_all.xml',
    '헤럴드경제': 'http://biz.heraldcorp.com/common/rss_xml.php?ct=010000000000',

    # IT/테크
    'ZDNet Korea': 'https://zdnet.co.kr/rss/all_news.xml',
    '전자신문': 'https://rss.etnews.com/Section901.xml',
    '디지털타임스': 'http://www.dt.co.kr/rss/all_news.xml',
    '블로터': 'https://www.bloter.net/feed',

    # 통신사
    '연합뉴스': 'https://www.yna.co.kr/rss/all.xml',
    '뉴시스': 'https://www.newsis.com/rss/all_rss.xml',
    '뉴스1': 'https://www.news1.kr/rss/all_news.xml',

    # 방송사
    'KBS': 'https://world.kbs.co.kr/rss/rss_news.htm?lang=k',
    'MBC': 'https://imnews.imbc.com/rss/news/news_00.xml',
    'SBS': 'https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=01&plink=RSSREADER',
    'YTN': 'https://www.ytn.co.kr/rss/headline.xml',
    'JTBC': 'https://fs.jtbc.co.kr/RSS/newsflash.xml',
    'MBN': 'https://www.mbn.co.kr/rss/',

    # 해외 뉴스 (영문)
    'Reuters': 'https://www.reutersagency.com/feed/',
    'BBC': 'http://feeds.bbci.co.uk/news/rss.xml',
    'CNN': 'http://rss.cnn.com/rss/edition.rss',
    'TechCrunch': 'https://techcrunch.com/feed/',
    'The Verge': 'https://www.theverge.com/rss/index.xml',
    'Wired': 'https://www.wired.com/feed/rss',
    'Ars Technica': 'https://feeds.arstechnica.com/arstechnica/index',
}


def fetch_news_from_naver(query: str, limit: int = 50) -> list[NewsArticle]:
    """
    네이버 뉴스 검색 결과를 스크래핑합니다.
    """
    encoded_query = quote(query)
    articles: list[NewsArticle] = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        search_url = f"https://search.naver.com/search.naver?where=news&query={encoded_query}&sort=1"
        response = requests.get(search_url, headers=headers, timeout=10)
        response.encoding = 'utf-8'

        link_pattern = r'href="(https://n\.news\.naver\.com/mnews/article/[^"]+)"'
        links = list(set(re.findall(link_pattern, response.text)))

        seen = set()
        for link in links[:limit]:
            if link in seen:
                continue
            seen.add(link)

            try:
                article_response = requests.get(link, headers=headers, timeout=5)
                article_response.encoding = 'utf-8'

                title_match = re.search(r'<meta property="og:title" content="([^"]+)"', article_response.text)
                if title_match:
                    title = title_match.group(1)
                else:
                    title_match = re.search(r'<title>([^<]+)</title>', article_response.text)
                    title = title_match.group(1) if title_match else '제목 없음'

                source_match = re.search(r'<meta property="og:article:author" content="([^"]+)"', article_response.text)
                source = source_match.group(1) if source_match else '네이버뉴스'

                articles.append({
                    'title': title,
                    'link': link,
                    'published': datetime.now().strftime('%Y-%m-%d'),
                    'source': source,
                    'summary': ''
                })

                if len(articles) >= limit:
                    break

            except Exception:
                continue

    except Exception as e:
        print(f"    [경고] 네이버 뉴스 검색 실패: {e}")

    return articles


def fetch_from_rss(rss_url: str, source_name: str, query: str = '', limit: int = 50) -> list[NewsArticle]:
    """
    RSS 피드에서 뉴스를 수집합니다.

    Args:
        rss_url: RSS 피드 URL
        source_name: 언론사 이름
        query: 검색 키워드 (빈 문자열이면 필터링 안함)
        limit: 최대 수집 개수
    """
    articles: list[NewsArticle] = []

    try:
        feed = feedparser.parse(rss_url)

        for entry in feed.entries:
            if len(articles) >= limit:
                break

            title = entry.get('title', '')

            # 키워드 필터링 (query가 있으면)
            if query and query.lower() not in title.lower():
                # description에서도 검색
                description = entry.get('summary', '') or entry.get('description', '')
                if query.lower() not in description.lower():
                    continue

            # 발행일 파싱
            published = ''
            try:
                if entry.get('published_parsed'):
                    pub_date = datetime(*entry.published_parsed[:6])
                    published = pub_date.strftime('%Y-%m-%d %H:%M')
                elif entry.get('updated_parsed'):
                    pub_date = datetime(*entry.updated_parsed[:6])
                    published = pub_date.strftime('%Y-%m-%d %H:%M')
            except:
                published = datetime.now().strftime('%Y-%m-%d')

            articles.append({
                'title': title,
                'link': entry.get('link', ''),
                'published': published,
                'source': source_name,
                'summary': ''
            })

    except Exception as e:
        print(f"    [경고] {source_name} RSS 실패: {str(e)[:50]}")

    return articles


def fetch_from_multiple_rss(query: str, limit: int = 50) -> list[NewsArticle]:
    """
    여러 RSS 피드에서 뉴스를 수집합니다.
    """
    all_articles: list[NewsArticle] = []
    seen_titles: set[str] = set()

    for source_name, rss_url in RSS_FEEDS.items():
        if len(all_articles) >= limit:
            break

        try:
            articles = fetch_from_rss(rss_url, source_name, query, limit=10)

            for article in articles:
                # 중복 제거 (제목 기준)
                title_normalized = article['title'].lower().strip()
                if title_normalized not in seen_titles:
                    seen_titles.add(title_normalized)
                    all_articles.append(article)

                    if len(all_articles) >= limit:
                        break

        except Exception:
            continue

    return all_articles


def fetch_news_from_daum(query: str, limit: int = 50) -> list[NewsArticle]:
    """
    다음 뉴스 검색 페이지에서 뉴스를 수집합니다.
    """
    encoded_query = quote(query)
    articles: list[NewsArticle] = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        search_url = f"https://search.daum.net/search?w=news&q={encoded_query}&sort=recency"
        response = requests.get(search_url, headers=headers, timeout=10)
        response.encoding = 'utf-8'

        # 다음 뉴스 링크 패턴
        link_pattern = r'href="(https://v\.daum\.net/v/[^"]+)"'
        links = list(set(re.findall(link_pattern, response.text)))

        for link in links[:limit]:
            try:
                article_response = requests.get(link, headers=headers, timeout=5)
                article_response.encoding = 'utf-8'

                title_match = re.search(r'<meta property="og:title" content="([^"]+)"', article_response.text)
                title = title_match.group(1) if title_match else '제목 없음'

                source_match = re.search(r'<meta property="og:article:author" content="([^"]+)"', article_response.text)
                source = source_match.group(1) if source_match else '다음뉴스'

                articles.append({
                    'title': title,
                    'link': link,
                    'published': datetime.now().strftime('%Y-%m-%d'),
                    'source': source,
                    'summary': ''
                })

                if len(articles) >= limit:
                    break

            except Exception:
                continue

    except Exception as e:
        print(f"    [경고] 다음 뉴스 검색 실패: {e}")

    return articles


def fetch_news(query: str, limit: int = 50) -> list[NewsArticle]:
    """
    여러 소스에서 뉴스를 수집합니다.

    Args:
        query: 검색 키워드
        limit: 가져올 기사 수 (기본값: 50)

    Returns:
        뉴스 기사 딕셔너리 리스트
    """
    all_articles: list[NewsArticle] = []
    seen_titles: set[str] = set()

    # 1. 네이버 뉴스에서 수집
    print(f"    - 네이버 뉴스 검색 중...")
    naver_articles = fetch_news_from_naver(query, limit)
    for article in naver_articles:
        title_normalized = article['title'].lower().strip()
        if title_normalized not in seen_titles:
            seen_titles.add(title_normalized)
            all_articles.append(article)
    print(f"      → {len(naver_articles)}개 수집")

    # 2. 다음 뉴스에서 수집
    if len(all_articles) < limit:
        print(f"    - 다음 뉴스 검색 중...")
        daum_articles = fetch_news_from_daum(query, limit - len(all_articles))
        added = 0
        for article in daum_articles:
            title_normalized = article['title'].lower().strip()
            if title_normalized not in seen_titles:
                seen_titles.add(title_normalized)
                all_articles.append(article)
                added += 1
        print(f"      → {added}개 추가")

    # 3. 다양한 언론사 RSS에서 수집
    if len(all_articles) < limit:
        print(f"    - RSS 피드 검색 중 (30개 언론사)...")
        rss_articles = fetch_from_multiple_rss(query, limit - len(all_articles))
        added = 0
        for article in rss_articles:
            title_normalized = article['title'].lower().strip()
            if title_normalized not in seen_titles:
                seen_titles.add(title_normalized)
                all_articles.append(article)
                added += 1
        print(f"      → {added}개 추가")

    return all_articles[:limit]


def fetch_news_by_keywords(keywords: list[str], limit_per_keyword: int = 50) -> list[NewsArticle]:
    """
    여러 키워드로 뉴스를 수집합니다.

    Args:
        keywords: 검색 키워드 리스트
        limit_per_keyword: 키워드당 가져올 기사 수

    Returns:
        중복 제거된 뉴스 기사 리스트
    """
    all_articles: list[NewsArticle] = []
    seen_links: set[str] = set()

    for keyword in keywords:
        print(f"[수집] '{keyword}' 키워드로 뉴스 수집 중...")
        articles = fetch_news(keyword, limit_per_keyword)

        for article in articles:
            if article['link'] not in seen_links:
                seen_links.add(article['link'])
                all_articles.append(article)

        print(f"  → {len(articles)}개 기사 수집됨 (중복 제외 후 총 {len(all_articles)}개)")

    return all_articles


def get_available_sources() -> list[str]:
    """사용 가능한 뉴스 소스 목록을 반환합니다."""
    sources = ['네이버뉴스', '다음뉴스'] + list(RSS_FEEDS.keys())
    return sources


if __name__ == "__main__":
    # 테스트
    print("=== 사용 가능한 언론사 ===")
    sources = get_available_sources()
    print(f"총 {len(sources)}개: {', '.join(sources[:10])}...")

    print("\n=== 뉴스 수집 테스트 ===")
    test_articles = fetch_news("인공지능", limit=10)
    for i, article in enumerate(test_articles, 1):
        print(f"\n[{i}] {article['title'][:50]}...")
        print(f"    출처: {article['source']}")
        print(f"    시간: {article['published']}")
