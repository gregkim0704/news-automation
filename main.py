#!/usr/bin/env python3
"""
구글 뉴스 자동 요약 및 이메일 전송 시스템
메인 진입점 및 스케줄러
"""

import argparse
import schedule
import time
from datetime import datetime

from src.config import Config
from src.fetcher import fetch_news_by_keywords
from src.summarizer import summarize_articles
from src.mailer import send_digest


def job(dry_run: bool = False, limit: int = 50) -> None:
    """
    뉴스 수집 -> 요약 -> 이메일 전송 작업을 수행합니다.

    Args:
        dry_run: True면 이메일을 실제로 전송하지 않음
        limit: 키워드당 수집할 기사 수
    """
    print("\n" + "=" * 60)
    print(f"🚀 뉴스 다이제스트 작업 시작 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 설정 검증
    is_valid, errors = Config.validate()
    if not is_valid:
        print("\n[오류] 설정이 올바르지 않습니다:")
        for error in errors:
            print(f"  - {error}")
        print("\n.env 파일을 확인하세요. (.env.example 참고)")
        return

    Config.print_config()

    keywords = Config.get_keywords()
    recipients = Config.get_recipients()

    # 1. 뉴스 수집
    print("\n📥 [1단계] 뉴스 수집")
    print("-" * 40)
    articles = fetch_news_by_keywords(keywords, limit_per_keyword=limit)

    if not articles:
        print("[경고] 수집된 기사가 없습니다.")
        return

    print(f"\n✓ 총 {len(articles)}개 기사 수집 완료")

    # 2. 기사 요약
    print("\n📝 [2단계] 기사 요약")
    print("-" * 40)
    articles = summarize_articles(articles)

    # 3. 이메일 전송
    print("\n📧 [3단계] 이메일 전송")
    print("-" * 40)
    success = send_digest(
        articles=articles,
        recipients=recipients,
        keywords=keywords,
        smtp_server=Config.SMTP_SERVER,
        smtp_port=Config.SMTP_PORT,
        sender_email=Config.SENDER_EMAIL,
        sender_password=Config.SENDER_PASSWORD,
        dry_run=dry_run
    )

    print("\n" + "=" * 60)
    if success:
        print("✅ 작업 완료!")
    else:
        print("❌ 작업 실패 - 로그를 확인하세요.")
    print("=" * 60 + "\n")


def main():
    """메인 함수 - 명령줄 인자 파싱 및 스케줄러 실행"""
    parser = argparse.ArgumentParser(
        description='구글 뉴스 자동 요약 및 이메일 전송 시스템',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python main.py --now              # 즉시 실행 (테스트)
  python main.py --now --dry-run    # 즉시 실행, 이메일 전송 없이 결과만 확인
  python main.py                    # 스케줄에 따라 실행
  python main.py --limit 10         # 키워드당 10개 기사만 수집
        """
    )
    parser.add_argument(
        '--now',
        action='store_true',
        help='스케줄을 기다리지 않고 즉시 실행'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='실제 이메일을 전송하지 않고 결과만 출력'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=50,
        help='키워드당 수집할 기사 수 (기본값: 50)'
    )

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("📰 구글 뉴스 자동 요약 및 이메일 전송 시스템")
    print("=" * 60)

    if args.now:
        # 즉시 실행
        print("\n[모드] 즉시 실행")
        job(dry_run=args.dry_run, limit=args.limit)
    else:
        # 스케줄 모드
        schedule_time = Config.SCHEDULE_TIME
        print(f"\n[모드] 스케줄 모드")
        print(f"[설정] 매일 {schedule_time}에 실행됩니다.")
        print("[안내] 종료하려면 Ctrl+C를 누르세요.\n")

        # 스케줄 등록
        schedule.every().day.at(schedule_time).do(job, dry_run=args.dry_run, limit=args.limit)

        # 스케줄 루프
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 1분마다 체크
        except KeyboardInterrupt:
            print("\n\n[종료] 프로그램을 종료합니다.")


if __name__ == "__main__":
    main()
