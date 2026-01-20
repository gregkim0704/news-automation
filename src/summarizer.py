"""
기사 본문 추출 및 요약 모듈
네이버 뉴스 등 한국 뉴스 사이트에서 본문을 추출합니다.
"""

import requests
import re
from typing import TYPE_CHECKING
import time

if TYPE_CHECKING:
    from .fetcher import NewsArticle


def extract_naver_article(url: str) -> str:
    """
    네이버 뉴스 기사 본문을 추출합니다.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        html = response.text

        # og:description 메타 태그에서 요약 추출 (가장 신뢰성 높음)
        desc_match = re.search(r'<meta property="og:description" content="([^"]+)"', html)
        if desc_match:
            description = desc_match.group(1)
            # HTML 엔티티 디코딩
            description = description.replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
            if len(description) > 50:  # 의미있는 길이인 경우
                return description

        # article 본문에서 추출 시도
        # 네이버 뉴스 본문은 주로 _article_body 또는 newsct_article 클래스에 있음
        body_patterns = [
            r'<article[^>]*id="dic_area"[^>]*>(.*?)</article>',
            r'<div[^>]*class="[^"]*newsct_article[^"]*"[^>]*>(.*?)</div>',
            r'<div[^>]*id="_article_body"[^>]*>(.*?)</div>',
        ]

        for pattern in body_patterns:
            match = re.search(pattern, html, re.DOTALL)
            if match:
                body = match.group(1)
                # HTML 태그 제거
                text = re.sub(r'<[^>]+>', ' ', body)
                # 연속 공백 정리
                text = re.sub(r'\s+', ' ', text).strip()
                if len(text) > 100:
                    return text[:300] + '...' if len(text) > 300 else text

        return '(본문 추출 실패)'

    except Exception as e:
        return f'(추출 오류: {str(e)[:20]})'


def extract_and_summarize(url: str, language: str = 'ko') -> str:
    """
    URL에서 기사 본문을 추출합니다.

    Args:
        url: 기사 URL
        language: 언어 코드 (기본값: 'ko')

    Returns:
        요약된 텍스트 (실패 시 에러 메시지)
    """
    # 네이버 뉴스인 경우 직접 추출
    if 'naver.com' in url:
        return extract_naver_article(url)

    # 다른 사이트는 newspaper3k 시도
    try:
        from newspaper import Article
        article = Article(url, language=language)
        article.download()
        article.parse()

        # 본문의 첫 300자 반환
        if article.text:
            text = article.text[:300]
            return text + '...' if len(article.text) > 300 else text
        else:
            return '(본문 추출 실패)'

    except Exception as e:
        return f'(요약 실패: {str(e)[:30]})'


def summarize_articles(articles: list['NewsArticle'], delay: float = 0.5) -> list['NewsArticle']:
    """
    기사 리스트의 각 기사에 대해 요약을 생성합니다.

    Args:
        articles: 뉴스 기사 리스트
        delay: 요청 간 대기 시간 (초, 서버 부하 방지)

    Returns:
        요약이 추가된 기사 리스트
    """
    total = len(articles)
    print(f"\n[요약] 총 {total}개 기사 요약 시작...")

    for i, article in enumerate(articles, 1):
        print(f"  [{i}/{total}] {article['title'][:40]}... ", end='', flush=True)

        summary = extract_and_summarize(article['link'])
        article['summary'] = summary

        if summary.startswith('('):
            print("실패")
        else:
            print("완료")

        # 서버 부하 방지를 위한 딜레이
        if i < total:
            time.sleep(delay)

    success_count = sum(1 for a in articles if not a['summary'].startswith('('))
    print(f"\n[요약] 완료! 성공: {success_count}/{total}개")

    return articles


if __name__ == "__main__":
    # 테스트
    test_url = "https://news.google.com"
    result = extract_and_summarize(test_url)
    print(f"테스트 결과: {result[:100]}...")
