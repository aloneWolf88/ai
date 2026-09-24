from agent import agent_definition
import re
# Flask 핵심 도구 가져오기: 웹 앱 본체(Flask), 사용자가 보낸 데이터 받기(request), HTML 화면 띄우기(render_template)
from agent import agent_router
from flask import Flask, request, render_template
import tool 
# 프론트엔드와 백엔드 간의 통신 차단(CORS 정책)을 풀어주는 도구 가져오기
from flask_cors import CORS
import smtplib
# 본문과 첨부파일 등 여러 구성 요소를 하나로 묶어 담는 메일 상자
from email.mime.multipart import MIMEMultipart  
# 일반 텍스트나 HTML 형식으로 '편지 내용(본문)'을 작성하는 도구
from email.mime.text import MIMEText

# 현재 파일을 기준으로 Flask 웹 애플리케이션 생성
app = Flask(__name__)
 
# 모든 출처(다른 도메인/포트)에서 이 서버로 API 요청을 보낼 수 있도록 허용
CORS(app)

#Gmail SMTP 설정
SEMAIL ='termi274@gmail.com'
PASS ='auxa xiwr otiq bgkk'

def is_korean(text):
  return bool(re.search('[가-힣]',text))

#LLM 사용함수(번역)
def use_llm(msg):
  if is_korean(msg):
    language='영어'
  else:
    language ='한국어'
  role = "너는 번역가야"
  prompt = f"아래문장을{language} 번역해줘\n\n{msg}"
  format = '''
        {
          "res":"번역된 문장"
        }
  '''
  response = tool.answer(role,prompt,format)
  
  response = tool.answer(role, prompt, output='text')
  return response.strip()
       


#메일 보내기 함수 
def send_email(subject,recipient_email,message):
    body = MIMEMultipart()
    body['subject'] = subject
    body['From'] = SEMAIL
    body['To'] = recipient_email
    body.attach(MIMEText(message,'html'))

    try:
      server = smtplib.SMTP('smtp.gmail.com',587)
      server.starttls()
      server.login(SEMAIL, PASS)
      server.sendmail(SEMAIL,
                    recipient_email,  # list, str 둘 다 가능
                    body.as_string())
      print('번역해서 이메일 보내기 성공')
      return True
    except Exception as e : 
      print(f"메일보내기 실패:{e}")
      return False;
    finally:
       server.quit()
           
@app.get('/') #http://localhost:5000
def index():
    return "OpenAI 웹서비스 접속"

@app.get('/form') #http://localhost:5000/form
def form():
    return render_template("mail.html")

@app.post('/proc') #http://localhost:5000/proc
def proc():

    data = request.json  #json -> dict로 변경
    subject =data['subject']
    recipient_email =data['recipient_email']
    message =data['message']

    #print("subject=",subject)
    #print("email=",recipient_email)
    #print("message=",message)
     
    #LLM 사용(번역) 
    subject =use_llm(subject)
    message =use_llm(message)

    #메일 보내기 
    result=send_email(subject,recipient_email,message.replace('\n','<br>'))
    print(result)
    return {"result": result}

# 웹 서버 실행: 외부 접속 허용(host="0.0.0.0"), 5000번 포트 사용, 코드 수정 시 자동 재시작(debug=True)
app.run(host="0.0.0.0", port=5000, debug=True)
 