from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

st.title("💬 Chatbot")

# st.session_state에 messages 가 없으면 초기값 설정
if "messages" not in st.session_state:
  st.session_state['messages']=[{'role':"assistant","content":"How can I help you?"}]

# 답변 생성 중인지 여부를 저장하는 상태 플래그 (기본값: False)
if "generating" not in st.session_state:
    st.session_state["generating"] = False

# 대화기록 출력
for msg in st.session_state.messages:
  st.chat_message(msg['role']).write(msg['content'])

# 입력창 수정, 안내 문구(placeholder)도 동적으로 변경됩니다.
# 조건부 표현식(A if 조건 else B)을 한 줄로 인라인 작성
prompt = st.chat_input(
    placeholder="메시지를 입력하세요..."
    if not st.session_state.generating
    else "답변을 생성하는 중입니다...",
    disabled=st.session_state.generating,
)

# 사용자가 메시지를 전송했을 때의 처리
if prompt :
  if not api_key:
    st.info("OpenAI API key가 필요합니다.")
    st.stop()

  # 사용자가 입력한 메시지를 대화 기록에 추가
  st.session_state.messages.append({"role":"user","content":prompt})
  # 상태를 '생성 중(True)'으로 변경
  st.session_state.generating = True
  # 화면을 즉시 재실행하여 입력창을 잠금(disabled=True) 상태로 렌더링
  st.rerun()

# 'generating'이 True일 때만 실제 API 호출 및 응답 출력 실행
if st.session_state.generating:
    client = OpenAI(api_key=api_key)

    with st.chat_message("assistant"):
        with st.spinner("답변을 생각하는 중..."):
            response = client.chat.completions.create(
                model="gpt-5.5",
                messages=st.session_state.messages,
            )
            msg = response.choices[0].message.content
            st.write(msg)

    # 응답 완료 후 대화 기록에 어시스턴트 메시지 추가
    st.session_state.messages.append({"role": "assistant", "content": msg})

    # 생성이 완료되었으므로 상태를 False로 원복
    st.session_state.generating = False

    # 화면을 재실행하여 입력창 잠금을 풀고(disabled=False) 활성화 상태로 복귀
    st.rerun()