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
    # 최신 입시 동향과 함께 '합격 수기' 및 '공부법' 데이터를 더 많이 가져오도록 쿼리 확장
    queries = ["2027 2028 대입전형 전략", "상위권 합격 수기 공부법", "자기주도학습 실전 팁"]
    combined_items = []
    
    for q in queries:
        url = f"https://openapi.naver.com/v1/search/news.json?query={q}&display=10&sort=sim"
        headers = {"X-Naver-Client-Id": NAVER_ID, "X-Naver-Client-Secret": NAVER_SECRET}
        try:
            res = requests.get(url, headers=headers).json()
            combined_items.extend(res.get('items', []))
        except:
            continue
            
    if not combined_items: return None
    return "\n".join([f"제목: {i['title']}\n내용: {i['description']}" for i in combined_items])

def generate_report(news_data):
    client = genai.Client(api_key=GEMINI_KEY)
    
    # A4 3장 분량을 뽑아내기 위한 초정밀 프롬프트
    prompt = f"""
    당신은 'PROJECT 12'의 수석 교육 컨설턴트이자 입시 전문 기자입니다. 
    제공된 뉴스 데이터를 바탕으로 학생들이 출력해서 읽을 수 있는 **A4 용지 3장 분량(약 4,000자 이상)**의 심층 입시 리포트를 HTML로 작성하세요.

    [리포트 구성 가이드 - 매우 중요]
    1. 타이틀: <h1 style='text-align:center; font-size:32px;'>PROJECT12 간추린 입시뉴스</h1>
    2. [1페이지: NEWS & STRATEGY]
       - 핵심 입시 뉴스 요약 및 심층 분석
       - 수시/정시 카테고리별 상세 대응 전략
    3. [2페이지: PRACTICAL STUDY LAB] (이 부분을 가장 길게 작성)
       - 실질적인 공부 팁: 오늘 뉴스 내용과 연결된 구체적인 과목별 학습법
       - 메타인지(MCP) 적용 가이드: 학생들이 스스로 계획을 세울 수 있는 체크리스트 포함
    4. [3페이지: SUCCESS STORIES & MOTIVATION]
       - 가상의 합격 수기 및 사례 연구: 최신 트렌드를 반영한 '성공한 선배들의 공부 루틴'
       - 학생 Q&A: 아주 구체적인 고민(예: 6월 모평 대비, 수면 관리 등)에 대한 해결책 5가지 이상
    5. 시그니처: "PROJECT 12 : 나만의 성공 프로젝트를 완성하다."

  [중요: HTML 이메일 디자인 규칙]
- 반드시 Gmail 이메일에서 깨지지 않는 HTML로 작성
- div보다 table 기반 레이아웃 사용
- CSS는 반드시 inline style만 사용
- <style> 태그 최소화
- flex, grid 사용 금지
- width:100%, max-width:900px 적용
- 전체 문서는 흰 배경 카드형 디자인
- section마다 박스 스타일 적용:
  background:#ffffff;
  border-radius:14px;
  padding:28px;
  margin-bottom:20px;
  border:1px solid #e5e7eb;
  box-shadow:0 2px 10px rgba(0,0,0,0.05);

- 타이틀은 세련된 뉴스레터 스타일
- PROJECT12 브랜드 느낌:
  신뢰감 + 프리미엄 교육 컨설팅 분위기
- 색상:
  메인 #1E3A8A
  포인트 #3B82F6
  배경 #F8FAFC

- 폰트:
  Apple SD Gothic Neo, Pretendard, Arial, sans-serif

- HTML 결과만 출력
- ```html 같은 코드블럭 절대 금지

    [데이터 정보]
    {news_data}
    """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash", # 분량과 논리력을 위해 Pro 모델 사용 권장 (Flash도 가능)
        contents=prompt
    )
    return response.text

def send_email(html_content):
    today = datetime.now().strftime('%Y-%m-%d')
    msg = EmailMessage()
    msg['Subject'] = f"[PROJECT 12] A4 3매 분량 심층 입시 리포트 ({today})"
    msg['From'] = SENDER_EMAIL
    msg['To'] = "hosuk.choi@byulha.kr"
    
    msg.set_content("이 메일은 전문적인 입시 리포트를 포함하고 있습니다. PC에서 확인 및 인쇄를 권장합니다.")
    msg.add_alternative(html_content, subtype='html')
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASS)
            smtp.send_message(msg)
        print("🎉 대용량 입시 리포트 발송 성공!")
    except Exception as e:
        print(f"❌ 발송 실패: {e}")

if __name__ == "__main__":
    news_content = get_news()
    if news_content:
        report = generate_report(news_content)
        send_email(report)
    else:
        send_email("데이터 수집 중입니다. 잠시 후 다시 확인해 주세요.")
