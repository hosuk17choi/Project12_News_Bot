import os
import requests
import google.generativeai as genai
from email.message import EmailMessage
import smtplib
from datetime import datetime

# 1. 환경 변수 로드
NAVER_ID = os.environ.get('NAVER_CLIENT_ID')
NAVER_SECRET = os.environ.get('NAVER_CLIENT_SECRET')
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
SENDER_PASS = os.environ.get('SENDER_PASSWORD')

def get_news():
    # 'PROJECT 12'에 걸맞은 입시 키워드 설정
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
    genai.configure(api_key=GEMINI_KEY)
    # 현재 가장 안정적인 모델인 gemini-1.5-flash를 사용합니다.
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    당신은 'PROJECT 12' 스터디카페의 입시 전문 기자입니다.
    아래 뉴스를 바탕으로 [PROJECT12 간추린 입시뉴스]를 작성하세요.
    
    [작성 규칙]
    1. 형식: 구체적인 정보가 담긴 정중하고 신뢰감 있는 신문 기사 스타일
    2. 카테고리: ⚡헤드라인, 📍주요 입시 소식, 💡오늘의 전략, 🔥동기부여 한마디
    3. 대상: 목표를 향해 달리는 스터디카페 학생들과 학부모님
    4. 하단 문구: PROJECT 12 : 나만의 성공 프로젝트를 완성하다.
    
    [수집 데이터]
    {news_data}
    """
    
    response = model.generate_content(prompt)
    return response.text

def send_email(content):
    today = datetime.now().strftime('%Y-%m-%d')
    msg = EmailMessage()
    msg['Subject'] = f"[PROJECT 12] 오늘의 간추린 입시뉴스 ({today})"
    msg['From'] = SENDER_EMAIL
    msg['To'] = "hosuk.choi@byulha.kr" # 수신인 설정
    msg.set_content(content)
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASS)
            smtp.send_message(msg)
        print("🎉 성공: 뉴스 리포트가 발송되었습니다!")
    except Exception as e:
        print(f"❌ 실패: 메일 발송 중 오류 발생 ({e})")

if __name__ == "__main__":
    news = get_news()
    if news:
        report = generate_report(news)
        send_email(report)
    else:
        # 뉴스가 없을 경우 격려 메시지 발송
        msg = "오늘의 주요 입시 뉴스가 아직 없습니다. 공부에 온전히 집중할 수 있는 하루입니다!\n\nPROJECT 12"
        send_email(msg)
