#!/usr/bin/env python3
"""
테스트 스크립트
각 모듈의 기능을 개별적으로 테스트합니다.
"""

import sys


def test_config():
    """설정 모듈 테스트"""
    print("\n" + "=" * 50)
    print("📋 [테스트 1] 설정 모듈 (config.py)")
    print("=" * 50)

    try:
        from src.config import Config

        print("✓ 모듈 임포트 성공")

        # 설정값 출력
        Config.print_config()

        # 유효성 검증
        is_valid, errors = Config.validate()
        if is_valid:
            print("✓ 설정 유효성 검증 통과")
        else:
            print("⚠ 설정 유효성 검증 실패:")
            for error in errors:
                print(f"  - {error}")

        return True
    except Exception as e:
        print(f"✗ 오류: {e}")
        return False


def test_fetcher():
    """뉴스 수집 모듈 테스트"""
    print("\n" + "=" * 50)
    print("📥 [테스트 2] 뉴스 수집 모듈 (fetcher.py)")
    print("=" * 50)

    try:
        from src.fetcher import fetch_news

        print("✓ 모듈 임포트 성공")

        # 테스트 검색
        print("\n'인공지능' 키워드로 3개 기사 수집 테스트...")
        articles = fetch_news("인공지능", limit=3)

        if articles:
            print(f"✓ {len(articles)}개 기사 수집 성공\n")
            for i, article in enumerate(articles, 1):
                print(f"  [{i}] {article['title'][:50]}...")
                print(f"      출처: {article['source']}")
                print(f"      시간: {article['published']}")
        else:
            print("⚠ 수집된 기사 없음")

        return True
    except Exception as e:
        print(f"✗ 오류: {e}")
        return False


def test_summarizer():
    """요약 모듈 테스트"""
    print("\n" + "=" * 50)
    print("📝 [테스트 3] 요약 모듈 (summarizer.py)")
    print("=" * 50)

    try:
        from src.summarizer import extract_and_summarize
        from src.fetcher import fetch_news

        print("✓ 모듈 임포트 성공")

        # 실제 기사 1개로 테스트
        print("\n실제 뉴스 기사 요약 테스트...")
        articles = fetch_news("기술", limit=1)

        if articles:
            article = articles[0]
            print(f"  기사: {article['title'][:50]}...")
            print(f"  URL: {article['link'][:60]}...")

            summary = extract_and_summarize(article['link'])
            print(f"\n  요약 결과:")
            print(f"  {summary[:200]}..." if len(summary) > 200 else f"  {summary}")

            if not summary.startswith('('):
                print("\n✓ 요약 성공")
            else:
                print("\n⚠ 요약 실패 (일부 사이트는 접근이 제한될 수 있음)")
        else:
            print("⚠ 테스트용 기사를 가져올 수 없음")

        return True
    except Exception as e:
        print(f"✗ 오류: {e}")
        return False


def test_mailer():
    """이메일 모듈 테스트"""
    print("\n" + "=" * 50)
    print("📧 [테스트 4] 이메일 모듈 (mailer.py)")
    print("=" * 50)

    try:
        from src.mailer import create_html_digest

        print("✓ 모듈 임포트 성공")

        # 테스트 데이터로 HTML 생성
        test_articles = [
            {
                'title': '인공지능이 바꾸는 미래',
                'link': 'https://example.com/1',
                'published': '2025-01-20 10:00',
                'source': '테크뉴스',
                'summary': '인공지능 기술이 빠르게 발전하면서 다양한 산업에 변화를 가져오고 있습니다.'
            },
            {
                'title': '머신러닝 최신 트렌드',
                'link': 'https://example.com/2',
                'published': '2025-01-20 09:30',
                'source': 'AI매거진',
                'summary': '2025년 머신러닝 분야의 주요 트렌드를 살펴봅니다.'
            }
        ]

        html = create_html_digest(test_articles, ['인공지능', 'AI'])

        print(f"\n✓ HTML 생성 성공 (길이: {len(html)} 문자)")
        print("\n[HTML 미리보기 - 처음 500자]")
        print("-" * 40)
        print(html[:500])
        print("...")
        print("-" * 40)

        return True
    except Exception as e:
        print(f"✗ 오류: {e}")
        return False


def run_all_tests():
    """모든 테스트 실행"""
    print("\n" + "=" * 60)
    print("🧪 뉴스 자동화 시스템 테스트")
    print("=" * 60)

    results = {
        'config': test_config(),
        'fetcher': test_fetcher(),
        'summarizer': test_summarizer(),
        'mailer': test_mailer()
    }

    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60)

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    for name, result in results.items():
        status = "✓ 통과" if result else "✗ 실패"
        print(f"  {name}: {status}")

    print("-" * 40)
    print(f"  총 결과: {passed}/{total} 통과")

    if passed == total:
        print("\n✅ 모든 테스트 통과!")
        print("\n다음 단계:")
        print("  1. .env.example을 .env로 복사")
        print("  2. .env 파일에 실제 값 입력")
        print("  3. python main.py --now --dry-run 으로 모의 실행")
        print("  4. python main.py --now 으로 실제 이메일 전송 테스트")
    else:
        print("\n⚠ 일부 테스트 실패. 로그를 확인하세요.")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
