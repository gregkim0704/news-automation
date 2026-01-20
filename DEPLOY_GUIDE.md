# 맞춤 뉴스 리더 앱 배포 가이드

## 🚀 Streamlit Cloud 무료 배포 (권장)

가장 쉬운 방법입니다. 무료이고 설정이 간단합니다.

### 1단계: GitHub 저장소 준비

현재 저장소를 GitHub에 푸시하세요 (이미 되어 있다면 스킵):

```bash
git add .
git commit -m "Add Streamlit web app"
git push
```

### 2단계: Streamlit Cloud 가입

1. https://share.streamlit.io/ 접속
2. **GitHub 계정으로 로그인**

### 3단계: 앱 배포

1. **New app** 버튼 클릭
2. 다음 정보 입력:
   - **Repository**: 본인의 GitHub 저장소 선택
   - **Branch**: `main`
   - **Main file path**: `app.py`
3. **Deploy** 클릭

### 4단계: 완료!

몇 분 후 앱이 배포됩니다.
URL 형식: `https://[앱이름].streamlit.app`

이 URL을 지인들에게 공유하면 됩니다!

---

## 💻 로컬 실행 방법

본인 PC에서 테스트하려면:

### Windows:
```cmd
cd news_automation
pip install -r requirements.txt
streamlit run app.py
```

### Mac/Linux:
```bash
cd news_automation
pip install -r requirements.txt
streamlit run app.py
```

브라우저에서 자동으로 `http://localhost:8501` 열립니다.

---

## 🎨 앱 기능

1. **맞춤 키워드 설정**: 관심 키워드를 쉼표로 구분하여 입력
2. **뉴스 수집**: 네이버 뉴스에서 최신 기사 수집
3. **자동 요약**: 각 기사의 핵심 내용 요약
4. **결과 내 검색**: 수집된 기사 중 제목 검색
5. **빠른 시작**: 미리 정의된 카테고리로 바로 시작

---

## 📋 지인에게 공유할 때

1. Streamlit Cloud URL 공유
2. 사용법 안내:
   - 왼쪽 사이드바에서 키워드 입력
   - "뉴스 검색" 버튼 클릭
   - 기사 목록에서 "원문 보기" 클릭

---

## 🔧 문제 해결

### 배포 시 에러가 나면:
1. `requirements.txt` 파일이 루트에 있는지 확인
2. `app.py` 파일이 루트에 있는지 확인
3. Streamlit Cloud 로그 확인

### 뉴스가 안 나오면:
- 네이버 뉴스 검색이 일시적으로 차단될 수 있음
- 몇 분 후 다시 시도

---

## 📱 추가 옵션: 모바일 앱처럼 사용

Streamlit 앱은 모바일 브라우저에서도 잘 작동합니다.
- 스마트폰 브라우저에서 URL 접속
- "홈 화면에 추가" 하면 앱처럼 사용 가능
