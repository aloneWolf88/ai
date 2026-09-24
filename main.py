# Flask 핵심 도구 가져오기: 웹 앱 본체(Flask), 사용자가 보낸 데이터 받기(request), HTML 화면 띄우기(render_template)
from flask import Flask, request, render_template
 
# 프론트엔드와 백엔드 간의 통신 차단(CORS 정책)을 풀어주는 도구 가져오기
from flask_cors import CORS
 
# 현재 파일을 기준으로 Flask 웹 애플리케이션 생성
app = Flask(__name__)
 
# 모든 출처(다른 도메인/포트)에서 이 서버로 API 요청을 보낼 수 있도록 허용
CORS(app)
 
@app.get('/') #http://localhost:5000
def index():
    return "OpenAI 웹서비스 접속"

@app.get('/trans') #http://localhost:5000/trans
def trans():
    return "번역서비스 접속"

@app.get('/hello') #http://localhost:5000/hello
def hello():
    return render_template("hello.html")

# 웹 서버 실행: 외부 접속 허용(host="0.0.0.0"), 5000번 포트 사용, 코드 수정 시 자동 재시작(debug=True)
app.run(host="0.0.0.0", port=5000, debug=True)
 