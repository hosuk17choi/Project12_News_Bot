import os
import requests
from google import genai # 최신 SDK 임포트
from email.message import EmailMessage
import smtplib
from datetime import datetime

# 1. 환경 변수 설정
NAVER_ID = os.environ.get('NAVER_CLIENT_ID')
NAVER_SECRET = os.environ.get('NAVER_CLIENT_SECRET')
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
SENDER_PASS = os.environ.get('SENDER_PASSWORD')

def get_news():
    query = "2027 2028 대입전형 개편 수능 전략 뉴스"
    url = f"https://openapi.naver.com/v1/search/news.json?query={query}&display=15&sort=sim"
    headers = {"X-Naver-Client-Id": NAVER_ID, "X-Naver-Client-Secret": NAVER_SECRET}
    
    try:
        res = requests.get(url, headers=headers).json()
        items = res.get('items', [])
        if not items: return None
        return "\n".join([f"제목: {i['title']}\n내용: {i['description']}" for i in items])
    except:
        return None

def generate_report(news_data):
    # 새로운 Client 방식 사용 (API 버전 문제를 자동으로 해결합니다)
    client = genai.Client(api_key=GEMINI_KEY)
    
    prompt = f"""
    당신은 'PROJECT 12' 스터디카페의 입시 전문 기자입니다.
    아래 뉴스를 바탕으로 [PROJECT12 간추린 입시뉴스]를 작성하세요.
    - 형식: 신뢰감 있는 신문 기사 스타일
    - 카테고리: ⚡헤드라인, 📍주요 소식, 💡학습 전략, 🔥동기부여
    - 하단 문구: PROJECT 12 : 나만의 성공 프로젝트를 완성하다.
    - 데이터: {news_data}
    """
    
    # 2026년 기준 가장 안정적인 호출 방식
    response = client.models.generate_content(
        model="gemini-3-flash",
        contents=prompt
    )
    return response.text

def send_email(content):
    today = datetime.now().strftime('%Y-%m-%d')
    msg = EmailMessage()
    msg['Subject'] = f"[PROJECT 12] 오늘의 간추린 입시뉴스 ({today})"
    msg['From'] = SENDER_EMAIL
    msg['To'] = "hosuk.choi@byulha.kr"
    msg.set_content(content)
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASS)
            smtp.send_message(msg)
        print("🎉 발송 성공!")
    except Exception as e:
        print(f"❌ 발송 실패: {e}")

if __name__ == "__main__":
    news_content = get_news()
    if news_content:
        report = generate_report(news_content)
        send_email(report)
    else:
        send_email("오늘의 주요 입시 뉴스가 없습니다. 성실한 하루 보내세요!\n\nPROJECT 12")
