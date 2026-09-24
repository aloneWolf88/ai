# Flask 핵심 도구 가져오기: 웹 앱 본체(Flask), 사용자가 보낸 데이터 받기(request), HTML 화면 띄우기(render_template)
from flask import Flask, request, render_template
from langchain_ollama import ChatOllama 
# 프론트엔드와 백엔드 간의 통신 차단(CORS 정책)을 풀어주는 도구 가져오기
from flask_cors import CORS
import tool 
# 현재 파일을 기준으로 Flask 웹 애플리케이션 생성
app = Flask(__name__)

# 모든 출처(다른 도메인/포트)에서 이 서버로 API 요청을 보낼 수 있도록 허용
CORS(app)
 
@app.get('/') #http://localhost:5000
def index():
    return "OpenAI 웹서비스 접속"

@app.get('/form') #http://localhost:5000/form
def trans():
    return render_template("translator.html")

@app.post('/proc') #http://localhost:5000/proc
def proc():
    data = request.json  #json -> dict로 변경
    sentence =data['sentence']
    language =data['language']
    age =data['age']
   
    print("sentence=",sentence)
    print("language=",language)
    print("age=",age)
    #빈라인제거 
    sentence = tool.remove_empty_lines(sentence)
    #프롬프트 생성  
    role ="""
    당신은 전문 번역가입니다. 다음 조건에 맞게 문장을 번역해주세요.    
    """
    prompt= f"""
    1. 대상 언어: {language}
    2. 대상 독자 연령: {age}세 수준 (연령대에 적합한 어휘, 문체, 어조 사용)
    3. 원본 문장:{sentence} """
    format ='''
            {
              "res":"번역된 문장"
            }
    '''
    response =tool.answer(role,prompt,format)
    print(response) 
    return response

# 웹 서버 실행: 외부 접속 허용(host="0.0.0.0"), 5000번 포트 사용, 코드 수정 시 자동 재시작(debug=True)
app.run(host="0.0.0.0", port=5000, debug=True)
 