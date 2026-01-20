"""
설정 관리 모듈
환경 변수를 로드하고 설정값을 관리합니다.
"""

import os
from dotenv import load_dotenv
from pathlib import Path


# .env 파일 로드
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)


class Config:
    """환경 변수 기반 설정 클래스"""

    # SMTP 설정
    SMTP_SERVER: str = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT: int = int(os.getenv('SMTP_PORT', '587'))
    SENDER_EMAIL: str = os.getenv('SENDER_EMAIL', '')
    SENDER_PASSWORD: str = os.getenv('SENDER_PASSWORD', '')

    # 수신자 목록 (쉼표로 구분된 문자열을 리스트로 변환)
    @staticmethod
    def get_recipients() -> list[str]:
        recipients_str = os.getenv('RECIPIENT_EMAILS', '')
        if not recipients_str:
            return []
        return [email.strip() for email in recipients_str.split(',') if email.strip()]

    # 검색 키워드 (쉼표로 구분된 문자열을 리스트로 변환)
    @staticmethod
    def get_keywords() -> list[str]:
        keywords_str = os.getenv('KEYWORDS', '')
        if not keywords_str:
            return []
        return [kw.strip() for kw in keywords_str.split(',') if kw.strip()]

    # 스케줄 시간
    SCHEDULE_TIME: str = os.getenv('SCHEDULE_TIME', '08:00')

    @classmethod
    def validate(cls) -> tuple[bool, list[str]]:
        """설정값 유효성 검증"""
        errors = []

        if not cls.SENDER_EMAIL:
            errors.append("SENDER_EMAIL이 설정되지 않았습니다.")
        if not cls.SENDER_PASSWORD:
            errors.append("SENDER_PASSWORD가 설정되지 않았습니다.")
        if not cls.get_recipients():
            errors.append("RECIPIENT_EMAILS가 설정되지 않았습니다.")
        if not cls.get_keywords():
            errors.append("KEYWORDS가 설정되지 않았습니다.")

        return len(errors) == 0, errors

    @classmethod
    def print_config(cls, hide_password: bool = True) -> None:
        """현재 설정값 출력 (디버그용)"""
        print("=" * 50)
        print("현재 설정")
        print("=" * 50)
        print(f"SMTP 서버: {cls.SMTP_SERVER}:{cls.SMTP_PORT}")
        print(f"발신자 이메일: {cls.SENDER_EMAIL}")
        print(f"발신자 비밀번호: {'*' * 8 if hide_password else cls.SENDER_PASSWORD}")
        print(f"수신자 목록: {cls.get_recipients()}")
        print(f"검색 키워드: {cls.get_keywords()}")
        print(f"스케줄 시간: {cls.SCHEDULE_TIME}")
        print("=" * 50)
