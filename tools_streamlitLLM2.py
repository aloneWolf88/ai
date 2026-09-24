from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st
import tools_yfinace as t
import os
import json

# api_key 
# load_dotenv()
# [삭제] 로컬 LLM은 API Key가 불필요하므로 주석 처리
# api_key = os.getenv("OPENAI_API_KEY")

# [삭제] 기존 OpenAI 클라이언트 생성 주석 처리
# client = OpenAI(api_key=api_key)

# [추가] 로컬 LLM(Ollama) 클라이언트 생성 (OpenAI API 호환 규격)
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
    timeout=180.0
)

# 호출 가능한 함수 매핑
AVAILABLE_FUNCS = {
    "get_current_time":t.get_current_time,
    "get_yf_stock_info":t.get_yf_stock_info,
    "get_yf_stock_history":t.get_yf_stock_history,
    "get_yf_stock_recommendations":t.get_yf_stock_recommendations
}

def ai_response(messages):
  return client.chat.completions.create(
    # [삭제] 기존 클라우드 모델 주석 처리
    # model="gpt-5.5",
    # [추가] 로컬 LLM 모델(qwen2.5:3b) 적용 (Function Calling 지원)
    model="qwen2.5:3b",
    messages=messages,
    tools=t.tools
  )

st.title("📈 실시간 주식 분석 chatbot 💬 (Local LLM)")

# 맥락유지를 위해 messages 초기 생성
if "messages" not in st.session_state:
  st.session_state.messages = [{"role":"system","content":'너는 주식 전문 상담사야'}]

# 답변 생성 중인지 여부를 저장하는 상태 플래그 (기본값: False)
if "generating" not in st.session_state:
    st.session_state["generating"] = False

# 기존 내용 출력
for msg in st.session_state.messages:
  if msg['role'] in ['user','assistant']:
    # 내용이 존재하고, 공백을 제거했을때도 빈 문자열이 아닌경우
    if msg.get('content') and msg['content'].strip():
      st.chat_message(msg['role']).write(msg['content'])

# 입력창편집,안내 문구(placeholder)도 동적으로 변경, 
# 조건부 표현식(A if 조건 else B)을 한 줄로 인라인 작성
prompt = st.chat_input(
    placeholder="메시지를 입력하세요..."
    if not st.session_state.generating
    else "답변을 생성하는 중입니다...",
    disabled=st.session_state.generating,
)

#사용자 입력 및 결과 
if prompt:
  # [삭제] 로컬 LLM 사용으로 API Key 검증 주석 처리
  # if not api_key:
  #   st.error('API key가 설정되지 않았습니다.')
  #   st.stop()
  
  # 사용자가 입력한 메시지를 대화 기록에 추가
  st.session_state.messages.append({'role':'user','content':prompt})
  # 상태를 '생성 중(True)'으로 변경
  st.session_state.generating = True
  # 화면을 즉시 재실행하여 입력창을 잠금(disabled=True) 상태로 렌더링
  st.rerun()

# 'generating'이 True일 때만 실제 API 호출 및 응답 출력 실행
if st.session_state.generating:
  with st.chat_message("assistant"):
    #1차 AI응답 요청(도구 사용 여부 판단)
    with st.spinner("질문을 분석하고 있습니다..."):
      response = ai_response(st.session_state.messages)
      msg = response.choices[0].message

    #AI의 1차 응답(도구 호출 선언) 메시지에 추가
    st.session_state.messages.append(
      {
        "role":"assistant",
        "content": msg.content or "",
        "tool_calls":msg.tool_calls
      }
    )
    # Tool(함수) 호출이 필요한경우(입력창 잠금 상태 유지)
    if msg.tool_calls:
      with st.spinner("금융 데이터를 실시간으로 조회하고 있습니다..."):
        for tool_call in msg.tool_calls:          
            fn_name = tool_call.function.name #함수이름
            fn_args = json.loads(tool_call.function.arguments)

            if fn_name in AVAILABLE_FUNCS:
               result = AVAILABLE_FUNCS[fn_name](**fn_args) #함수호출

               st.session_state.messages.append(
                {
                  "role":"tool", #역할은 function or tool
                    "tool_call_id":tool_call.id, #어떤 요청에 대한 결과인지 연결하는 ID
                    "name":fn_name,
                    "content":str(result) #함수호출결과(주가정보등)를 문자열로 저장
                  }
               )    
        # 도구실행(함수호출)결과를 바탕으로 최종 응답 생성
        response = ai_response(st.session_state.messages)
        msg = response.choices[0].message

    # 최종 응답 저장 및 채팅창에 출력
    st.session_state.messages.append(
      {'role':'assistant',"content":msg.content}
    )
    st.write(msg.content)

  # 모든 도구 실행과 답변 생성이 끝났으므로 잠금 해제 후 화면 갱신
  st.session_state.generating = False
  st.rerun()  # 2차 재실행: 입력창 disabled=False로 복귀