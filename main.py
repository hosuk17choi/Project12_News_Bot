import os
import requests
from google import genai
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
    client = genai.Client(api_key=GEMINI_KEY)
    
    # AI에게 HTML 형식으로 작성하도록 구체적인 가이드를 줍니다.
    prompt = f"""
    당신은 'PROJECT 12'의 수석 입시 전문 기자입니다. 
    아래 데이터를 바탕으로 HTML 형식을 사용하여 시각적으로 아름다운 뉴스레터를 작성하세요.
    
    [디자인 지침]
    1. 전체를 <div style="font-family: sans-serif; line-height: 1.6; color: #333; max-width: 600px; border: 1px solid #eee; padding: 20px;">으로 감싸주세요.
    2. 제목은 <h1 style="color: #1a73e8; border-bottom: 2px solid #1a73e8; padding-bottom: 10px;">으로 강조하세요.
    3. 각 섹션은 <h2 style="background: #f8f9fa; padding: 5px 10px; border-left: 5px solid #1a73e8;">를 사용하세요.
    4. 주요 키워드는 <strong> 태그를 사용하여 강조하세요.
    5. 하단에는 <hr> 구분선 뒤에 <p style="text-align: center; color: #888;">PROJECT 12 : 나만의 성공 프로젝트를 완성하다.</p>를 넣어주세요.
    
    [데이터]
    {news_data}
    """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text

def send_email(html_content):
    today = datetime.now().strftime('%Y-%m-%d')
    msg = EmailMessage()
    msg['Subject'] = f"[PROJECT 12] 오늘의 입시 리포트 ({today})"
    msg['From'] = SENDER_EMAIL
    msg['To'] = "hosuk.choi@byulha.kr"
    
    # 중요: 일반 텍스트 대신 HTML 본문으로 설정합니다.
    msg.set_content("이 메일은 HTML 형식을 지원하는 메일함에서 확인하실 수 있습니다.")
    msg.add_alternative(html_content, subtype='html')
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASS)
            smtp.send_message(msg)
        print("🎉 뉴스레터 발송 성공!")
    except Exception as e:
        print(f"❌ 발송 실패: {e}")

if __name__ == "__main__":
    news_content = get_news()
    if news_content:
        report = generate_report(news_content)
        send_email(report)
    else:
        fallback_html = """
        <div style="padding: 20px; text-align: center;">
            <h2>오늘의 뉴스 없음</h2>
            <p>오늘 수집된 주요 입시 소식이 없습니다. 집중력 있는 하루 보내세요!</p>
            <hr>
            <p>PROJECT 12</p>
        </div>
        """
        send_email(fallback_html)
