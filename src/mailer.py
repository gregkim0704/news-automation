"""
이메일 전송 모듈
뉴스 요약을 HTML 형식으로 변환하고 이메일로 전송합니다.
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
            }}
            h1 {{
                color: #1a73e8;
                border-bottom: 2px solid #1a73e8;
                padding-bottom: 10px;
            }}
            .meta {{
                color: #666;
                font-size: 14px;
                margin-bottom: 20px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            th {{
                background-color: #1a73e8;
                color: white;
                padding: 12px;
                text-align: left;
            }}
            td {{
                padding: 10px;
                border-bottom: 1px solid #ddd;
                vertical-align: top;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            tr:hover {{
                background-color: #f1f1f1;
            }}
            .title-link {{
                color: #1a73e8;
                text-decoration: none;
                font-weight: bold;
            }}
            .title-link:hover {{
                text-decoration: underline;
            }}
            .source {{
                color: #666;
                font-size: 12px;
            }}
            .time {{
                color: #888;
                font-size: 12px;
                white-space: nowrap;
            }}
            .summary {{
                font-size: 13px;
                color: #555;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                font-size: 12px;
                color: #888;
            }}
        </style>
    </head>
    <body>
        <h1>📰 오늘의 뉴스 다이제스트</h1>
        <div class="meta">
            <strong>날짜:</strong> {today}<br>
            <strong>키워드:</strong> {keywords_str}<br>
            <strong>총 기사 수:</strong> {len(articles)}개
        </div>

        <table>
            <thead>
                <tr>
                    <th style="width: 5%;">#</th>
                    <th style="width: 30%;">제목</th>
                    <th style="width: 10%;">출처</th>
                    <th style="width: 12%;">시간</th>
                    <th style="width: 43%;">요약</th>
                </tr>
            </thead>
            <tbody>
    """

    for i, article in enumerate(articles, 1):
        title = article['title'][:60] + '...' if len(article['title']) > 60 else article['title']
        summary = article['summary'][:150] + '...' if len(article['summary']) > 150 else article['summary']

        html += f"""
                <tr>
                    <td>{i}</td>
                    <td><a href="{article['link']}" class="title-link" target="_blank">{title}</a></td>
                    <td class="source">{article['source']}</td>
                    <td class="time">{article['published']}</td>
                    <td class="summary">{summary}</td>
                </tr>
        """

    html += """
            </tbody>
        </table>

        <div class="footer">
            이 이메일은 자동으로 생성되었습니다.<br>
            Google News RSS를 통해 수집된 뉴스입니다.
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
        print("\n[HTML 미리보기 - 처음 1000자]")
        print("-" * 60)
        print(html_content[:1000])
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
            'title': '테스트 기사 제목',
            'link': 'https://example.com',
            'published': '2025-01-20 10:00',
            'source': '테스트 뉴스',
            'summary': '이것은 테스트 요약입니다.'
        }
    ]
    html = create_html_digest(test_articles, ['테스트'])
    print(html[:500])
