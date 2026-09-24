from flask import Flask, request, render_template
from flask_cors import CORS
import time
import os
import pymupdf
import tool

app = Flask(__name__)  # __name__ == '__main__'
CORS(app)

app.config['ALLOWED_EXTENSIONS']={'pdf','PDF'}

def allowed_size(fsize):
  return True if fsize <= 1024 * 1024 * 25 else False

def allowed_file(filename): # ccc.gif
  return '.' in filename and filename.rsplit(".",1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# pdf to text 함수
def pdf_to_text(pdf_file_path: str):
    doc = pymupdf.open(pdf_file_path)

    header_height = 80 # 단위: 포인트(pt) -> PDF 표준 규격에서 정의하는 기본 단위
    footer_height = 80 # 단위: 포인트(pt)

    full_text = ''

    for page in doc:
        rect = page.rect # 페이지 크기 가져오기        
        header = page.get_text(clip=(0, 0, rect.width , header_height))
        footer = page.get_text(clip=(0, rect.height - footer_height, rect.width , rect.height))
        # 본문내용
        text = page.get_text(clip=(0, header_height, rect.width , rect.height - footer_height))
    
        full_text += text + '\n------------------------------------\n'


    txt_file_path = f'static/pdf/pdf_text.txt'

    with open(txt_file_path, 'w', encoding='utf-8') as f:
        f.write(full_text)

    return txt_file_path

# text 요약 함수
def summarize_txt(file_path: str, ): 
    
    # 주어진 텍스트 파일을 읽어들인다.
    with open(file_path, 'r', encoding='utf-8') as f:
        txt = f.read()

    # 요약을 위한 시스템 프롬프트를 생성한다.

    role = '요약 시스템이야'
    prompt = f'''
아래 텍스트를 분석하여 웹 브라우저에 바로 표시할 수 있는 깔끔한 HTML 형식으로 요약하세요.
[요약 지침]
1. 제목, 전체 개요(2~3문장), 주요 핵심 포인트(최대 5개 항목)로 구성할 것.
2. 가독성을 위해 반드시 <br>, <p>, <ul>, <li>, <strong> 태그를 활용할 것.
3. 동일한 문장을 중복/반복하지 말 것.
4. 마크다운(```html 등) 기호 없이 순수 HTML 태그만 출력할 것.
[출력 HTML 포맷 예시]
<div style="text-align: left; line-height: 1.8; margin-top: 15px;">
  <h4 style="color: #0d6efd; border-bottom: 2px solid #dee2e6; padding-bottom: 8px;">📌 [문서 제목]</h4>
  
  <p><strong>[문서 개요]</strong><br>
  (문서의 핵심 취지와 목적을 2~3문장으로 간략히 기술)
  </p>
  <h5>📋 주요 핵심 내용</h5>
  <ul>
    <li><strong>[항목 1]</strong> : 상세 설명</li>
    <li><strong>[항목 2]</strong> : 상세 설명</li>
    <li><strong>[항목 3]</strong> : 상세 설명</li>
    <li><strong>[항목 4]</strong> : 상세 설명</li>
    <li><strong>[항목 5]</strong> : 상세 설명</li>
  </ul>
</div>
=============== 이하 텍스트 ===============
{ txt }
'''


    return tool.answer(role,prompt,output='text')

@app.get('/')
def index():
  return "업로드된 논문 요약서비스"

# http://127.0.0.1:5000/pdf_upload
@app.get('/pdf_upload')
def form():
  return render_template('pdf_upload.html')

# http://127.0.0.1:5000/pdf_upload
@app.post('/pdf_upload')
def proc():
  time.sleep(3) 
  # 업로드된 파일 받기(하나만 받는다)
  f = request.files.get('file')
  # 파일사이즈 확인
  file_size = len(f.read())
  #파일 포인터를 처음으로 이동
  f.seek(0)
  #파일 사이즈 확인
  if allowed_size(file_size) == False:
    resp = {'message':"파일 사이즈가 25M를 넘습니다."+str(file_size/1024/1024)+' M'}
  
  #허용 가능한 파일 확장자인지 확인
  if f and allowed_file(f.filename):
    # 저장할 경로 지정(예:'static/pdf' 폴더에 저장)
    upload_folder = os.path.join(os.getcwd(),'static','pdf')
    if not os.path.exists(upload_folder):
      os.makedirs(upload_folder)
    # 파일저장
    f.save(os.path.join(upload_folder,f.filename))
    # 업로드된 파일 
    file_path = os.path.join(upload_folder,f.filename)
    # pdf를 text 파일로 변환
    file = pdf_to_text(file_path)
    # text를 요약
    summary = summarize_txt(file)
    resp = {'summary':summary}
    f.close()
  else:
    resp = {'message':'전송할 수 없는 파일 형식입니다.'}

  return resp

app.run(host="0.0.0.0", port=5000, debug=True) # 0.0.0.0: 어디서나 접속, debug=True: 소스 변경시 자동 재시작
'''
python main.py
'''