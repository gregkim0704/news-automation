"""
뉴스 RSS 수집 모듈
키워드를 기반으로 뉴스를 수집합니다.
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
    summary: str  # 요약은 summarizer에서 채워짐


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
        # 네이버 뉴스 검색 페이지
        search_url = f"https://search.naver.com/search.naver?where=news&query={encoded_query}&sort=1"
        response = requests.get(search_url, headers=headers, timeout=10)
        response.encoding = 'utf-8'

        # 네이버 뉴스 링크 추출 (mnews/article 형식)
        link_pattern = r'href="(https://n\.news\.naver\.com/mnews/article/[^"]+)"'
        links = list(set(re.findall(link_pattern, response.text)))

        # 각 링크에서 제목 가져오기
        seen = set()
        for link in links[:limit]:
            if link in seen:
                continue
            seen.add(link)

            try:
                # 기사 페이지에서 제목 추출
                article_response = requests.get(link, headers=headers, timeout=5)
                article_response.encoding = 'utf-8'

                # og:title 메타 태그에서 제목 추출
                title_match = re.search(r'<meta property="og:title" content="([^"]+)"', article_response.text)
                if title_match:
                    title = title_match.group(1)
                else:
                    # title 태그에서 추출
                    title_match = re.search(r'<title>([^<]+)</title>', article_response.text)
                    title = title_match.group(1) if title_match else '제목 없음'

                # 언론사 추출
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
        print(f"[경고] 네이버 뉴스 검색 실패: {e}")

    return articles


def fetch_news_from_daum(query: str, limit: int = 50) -> list[NewsArticle]:
    """
    다음 뉴스 RSS를 사용하여 뉴스를 수집합니다.
    """
    encoded_query = quote(query)
    # 다음 뉴스 RSS
    rss_url = f"https://news.daum.net/rss/today"

    articles: list[NewsArticle] = []

    try:
        feed = feedparser.parse(rss_url)

        for entry in feed.entries[:limit]:
            title = entry.get('title', '')
            # 키워드 필터링
            if query.lower() not in title.lower():
                continue

            published = entry.get('published', '')
            try:
                if published:
                    pub_date = datetime(*entry.published_parsed[:6])
                    published = pub_date.strftime('%Y-%m-%d %H:%M')
            except:
                published = datetime.now().strftime('%Y-%m-%d')

            articles.append({
                'title': title,
                'link': entry.get('link', ''),
                'published': published,
                'source': '다음뉴스',
                'summary': ''
            })
    except Exception as e:
        print(f"[경고] 다음 뉴스 RSS 실패: {e}")

    return articles


def fetch_news_direct_search(query: str, limit: int = 50) -> list[NewsArticle]:
    """
    직접 뉴스 사이트를 검색하여 기사를 수집합니다.
    """
    articles: list[NewsArticle] = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    encoded_query = quote(query)

    # 연합뉴스 RSS
    try:
        rss_url = "https://www.yonhapnewstv.co.kr/browse/feed/"
        feed = feedparser.parse(rss_url)

        for entry in feed.entries[:limit]:
            title = entry.get('title', '')
            if query.lower() in title.lower() or not query:
                published = entry.get('published', '')
                try:
                    if entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6])
                        published = pub_date.strftime('%Y-%m-%d %H:%M')
                except:
                    published = datetime.now().strftime('%Y-%m-%d')

                articles.append({
                    'title': title,
                    'link': entry.get('link', ''),
                    'published': published,
                    'source': '연합뉴스',
                    'summary': entry.get('summary', '')[:200] if entry.get('summary') else ''
                })
    except Exception as e:
        print(f"[경고] 연합뉴스 RSS 실패: {e}")

    # 한겨레 RSS
    try:
        rss_url = "https://www.hani.co.kr/rss/"
        feed = feedparser.parse(rss_url)

        for entry in feed.entries[:limit]:
            title = entry.get('title', '')
            if query.lower() in title.lower():
                published = entry.get('published', '')
                try:
                    if entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6])
                        published = pub_date.strftime('%Y-%m-%d %H:%M')
                except:
                    published = datetime.now().strftime('%Y-%m-%d')

                articles.append({
                    'title': title,
                    'link': entry.get('link', ''),
                    'published': published,
                    'source': '한겨레',
                    'summary': entry.get('summary', '')[:200] if entry.get('summary') else ''
                })
    except:
        pass

    return articles[:limit]


def fetch_news(query: str, limit: int = 50) -> list[NewsArticle]:
    """
    여러 소스에서 뉴스를 수집합니다.
    네이버 뉴스를 우선으로 수집하고, 부족하면 다른 소스 추가.

    Args:
        query: 검색 키워드
        limit: 가져올 기사 수 (기본값: 50)

    Returns:
        뉴스 기사 딕셔너리 리스트
    """
    all_articles: list[NewsArticle] = []
    seen_titles: set[str] = set()

    # 1. 네이버 뉴스에서 수집 (가장 안정적)
    print(f"    - 네이버 뉴스 검색 중...")
    naver_articles = fetch_news_from_naver(query, limit)
    for article in naver_articles:
        if article['title'] not in seen_titles:
            seen_titles.add(article['title'])
            all_articles.append(article)
    print(f"      → {len(naver_articles)}개 수집")

    # 2. 부족하면 직접 RSS 검색
    if len(all_articles) < limit:
        print(f"    - RSS 피드 검색 중...")
        rss_articles = fetch_news_direct_search(query, limit - len(all_articles))
        for article in rss_articles:
            if article['title'] not in seen_titles:
                seen_titles.add(article['title'])
                all_articles.append(article)
        print(f"      → {len(rss_articles)}개 추가")

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
            # 중복 제거 (링크 기준)
            if article['link'] not in seen_links:
                seen_links.add(article['link'])
                all_articles.append(article)

        print(f"  → {len(articles)}개 기사 수집됨 (중복 제외 후 총 {len(all_articles)}개)")

    return all_articles


if __name__ == "__main__":
    # 테스트
    test_articles = fetch_news("인공지능", limit=5)
    for i, article in enumerate(test_articles, 1):
        print(f"\n[{i}] {article['title']}")
        print(f"    출처: {article['source']}")
        print(f"    시간: {article['published']}")
        print(f"    링크: {article['link'][:50]}...")
