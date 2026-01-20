"""
이메일 전송 모듈
뉴스를 HTML 형식으로 변환하고 이메일로 전송합니다.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .fetcher import NewsArticle


def create_html_digest(articles: list['NewsArticle'], keywords: list[str]) -> str:
    """
    뉴스 기사들을 HTML 테이블 형식으로 변환합니다.

    Args:
        articles: 뉴스 기사 리스트
        keywords: 검색에 사용된 키워드 리스트

    Returns:
        HTML 형식의 뉴스 다이제스트
    """
    today = datetime.now().strftime('%Y년 %m월 %d일')
    keywords_str = ', '.join(keywords)

    # 언론사별 기사 수 집계
    source_counts = {}
    for article in articles:
        source = article['source']
        source_counts[source] = source_counts.get(source, 0) + 1

    # 상위 5개 언론사
    top_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    sources_summary = ', '.join([f"{name}({count})" for name, count in top_sources])

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Malgun Gothic', '맑은 고딕', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #1a73e8;
                border-bottom: 3px solid #1a73e8;
                padding-bottom: 15px;
                margin-bottom: 20px;
            }}
            .meta {{
                background-color: #e8f0fe;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 25px;
            }}
            .meta-item {{
                margin: 5px 0;
            }}
            .stats {{
                display: inline-block;
                background-color: #1a73e8;
                color: white;
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 14px;
                margin-right: 10px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            th {{
                background-color: #1a73e8;
                color: white;
                padding: 15px 12px;
                text-align: left;
                font-size: 14px;
            }}
            td {{
                padding: 12px;
                border-bottom: 1px solid #e0e0e0;
                vertical-align: top;
            }}
            tr:nth-child(even) {{
                background-color: #fafafa;
            }}
            tr:hover {{
                background-color: #f0f7ff;
            }}
            .title-link {{
                color: #1a73e8;
                text-decoration: none;
                font-weight: 600;
                font-size: 14px;
            }}
            .title-link:hover {{
                text-decoration: underline;
                color: #0d47a1;
            }}
            .source {{
                display: inline-block;
                background-color: #e3f2fd;
                color: #1565c0;
                padding: 3px 8px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: 500;
            }}
            .time {{
                color: #888;
                font-size: 12px;
                white-space: nowrap;
            }}
            .num {{
                color: #888;
                font-weight: bold;
                text-align: center;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                font-size: 12px;
                color: #888;
                text-align: center;
            }}
            .source-list {{
                font-size: 12px;
                color: #666;
                margin-top: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📰 오늘의 뉴스 다이제스트</h1>

            <div class="meta">
                <div class="meta-item"><strong>📅 날짜:</strong> {today}</div>
                <div class="meta-item"><strong>🔑 키워드:</strong> {keywords_str}</div>
                <div class="meta-item">
                    <span class="stats">총 {len(articles)}개 기사</span>
                    <span class="stats">{len(source_counts)}개 언론사</span>
                </div>
                <div class="source-list"><strong>주요 출처:</strong> {sources_summary}</div>
            </div>

            <table>
                <thead>
                    <tr>
                        <th style="width: 5%;">#</th>
                        <th style="width: 50%;">제목</th>
                        <th style="width: 15%;">출처</th>
                        <th style="width: 15%;">시간</th>
                    </tr>
                </thead>
                <tbody>
    """

    for i, article in enumerate(articles, 1):
        title = article['title'][:80] + '...' if len(article['title']) > 80 else article['title']

        html += f"""
                <tr>
                    <td class="num">{i}</td>
                    <td><a href="{article['link']}" class="title-link" target="_blank">{title}</a></td>
                    <td><span class="source">{article['source']}</span></td>
                    <td class="time">{article['published']}</td>
                </tr>
        """

    html += """
            </tbody>
        </table>

        <div class="footer">
            이 이메일은 자동으로 생성되었습니다.<br>
            네이버, 다음, 및 30개 이상의 언론사 RSS에서 수집된 뉴스입니다.
        </div>
        </div>
    </body>
    </html>
    """

    return html


def send_digest(
    articles: list['NewsArticle'],
    recipients: list[str],
    keywords: list[str],
    smtp_server: str,
    smtp_port: int,
    sender_email: str,
    sender_password: str,
    dry_run: bool = False
) -> bool:
    """
    뉴스 다이제스트를 이메일로 전송합니다.

    Args:
        articles: 뉴스 기사 리스트
        recipients: 수신자 이메일 리스트
        keywords: 검색 키워드 리스트
        smtp_server: SMTP 서버 주소
        smtp_port: SMTP 포트
        sender_email: 발신자 이메일
        sender_password: 발신자 앱 비밀번호
        dry_run: True면 실제 전송하지 않고 HTML만 출력

    Returns:
        성공 여부
    """
    # HTML 생성
    html_content = create_html_digest(articles, keywords)

    if dry_run:
        print("\n" + "=" * 60)
        print("[DRY RUN] 이메일 전송을 건너뜁니다.")
        print("=" * 60)
        print(f"수신자: {', '.join(recipients)}")
        print(f"기사 수: {len(articles)}개")

        # 언론사별 통계
        source_counts = {}
        for article in articles:
            source = article['source']
            source_counts[source] = source_counts.get(source, 0) + 1

        print(f"\n[언론사별 기사 수]")
        for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {source}: {count}개")

        print("\n[HTML 미리보기 - 처음 500자]")
        print("-" * 60)
        print(html_content[:500])
        print("...")
        print("-" * 60)
        return True

    # 이메일 메시지 생성
    today = datetime.now().strftime('%Y-%m-%d')
    keywords_str = ', '.join(keywords[:3])

    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"[뉴스 다이제스트] {today} - {keywords_str}"
    msg['From'] = sender_email
    msg['To'] = ', '.join(recipients)

    # HTML 본문 추가
    html_part = MIMEText(html_content, 'html', 'utf-8')
    msg.attach(html_part)

    try:
        print(f"\n[이메일] SMTP 서버 연결 중... ({smtp_server}:{smtp_port})")

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            print("[이메일] 로그인 중...")
            server.login(sender_email, sender_password)

            print(f"[이메일] 전송 중... (수신자: {len(recipients)}명)")
            server.sendmail(sender_email, recipients, msg.as_string())

        print("[이메일] ✓ 전송 완료!")
        return True

    except smtplib.SMTPAuthenticationError:
        print("[오류] 이메일 인증 실패. 이메일 주소와 앱 비밀번호를 확인하세요.")
        return False
    except smtplib.SMTPException as e:
        print(f"[오류] SMTP 오류: {e}")
        return False
    except Exception as e:
        print(f"[오류] 이메일 전송 실패: {e}")
        return False


if __name__ == "__main__":
    # 테스트 데이터
    test_articles = [
        {
            'title': '테스트 기사 제목 1',
            'link': 'https://example.com/1',
            'published': '2025-01-20 10:00',
            'source': '조선일보',
            'summary': ''
        },
        {
            'title': '테스트 기사 제목 2',
            'link': 'https://example.com/2',
            'published': '2025-01-20 11:00',
            'source': '연합뉴스',
            'summary': ''
        }
    ]
    html = create_html_digest(test_articles, ['테스트'])
    print(html[:500])
