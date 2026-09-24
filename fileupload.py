from flask import Flask, request, render_template
from flask_cors import CORS
import time
import os

app = Flask(__name__)  # __name__ == '__main__'
CORS(app)

app.config['ALLOWED_EXTENSIONS']={'jpg','png','gif'}

def allowed_size(fsize):
  return True if fsize <= 1024 * 1024 * 25 else False

def allowed_file(filename): # ccc.gif
  return '.' in filename and filename.rsplit(".",1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.get('/')
def index():
  return "OpenAI 웹서비스 접속"

# /fileupload: http://127.0.0.1:5000/fileupload
@app.get('/fileupload')
def form():
  return render_template('fileupload.html')

# /fileupload: http://127.0.0.1:5000/fileupload
@app.post('/fileupload')
def proc():
  time.sleep(3) 
  # 업로드된 파일 받기(하나만 받는다)
  f = request.files.get('file')
  # 파일사이즈 확인
  file_size = len(f.read())
  #파일 포인터를 처음으로 이동(※)
  f.seek(0)
  #파일 사이즈 확인
  if allowed_size(file_size) == False:
    resp = {'message':"파일 사이즈가 25M를 넘습니다."+str(file_size/1024/1024)+' M'}
  
  #허용 가능한 파일 확장자인지 확인
  if f and allowed_file(f.filename):
    # 업로드처리(지정된 폴더에 저장:storage)
    upload_folder='storage'
    if not os.path.exists(upload_folder):
      os.makedirs(upload_folder)
    # 파일저장
    f.save(os.path.join(upload_folder,f.filename))
    resp = {'message':'파일을 저장했습니다.'}
  else:
    resp = {'message':'전송할 수 없는 파일 형식입니다.'}

  return resp

app.run(host="0.0.0.0", port=5000, debug=True) # 0.0.0.0: 어디서나 접속, debug=True: 소스 변경시 자동 재시작
'''
cd ai
python fileupload.py
'''