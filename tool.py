import json
from openai import OpenAI
from dotenv import load_dotenv
import os
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# 로컬 LLM(Ollama) 사용함수
# role: LLM 역할  예) 너는 문화 해설가야
# prompt: 질문 메시지
# format='': 출력 세부 형식, 파라미터 전달이 안되면 아무 값도 사용하지 않는다는 선언
# llm='qwen3.5:9b': 사용할 인공지능 모델
# output='json': 출력 형식

# [삭제] 기존 함수 정의 주석 처리
# def answer(role, prompt, format='json', llm='gpt-5.5', output='json'):

# [추가] 로컬 LLM 모델(qwen3.5:9b) 기본값 적용
def answer(role, prompt, format='json', llm='qwen2.5:3b', output='json'):
    
    # [삭제] 기존 OpenAI API Key 로드 주석 처리
    # load_dotenv()
    # api_key = os.getenv('OPENAI_API_KEY')
    # client = OpenAI(api_key = api_key)
    logging.info(f"[로컬 LLM 호출 시작]")     
    # [추가] 로컬 Ollama 엔드포인트 연결 (OpenAI API 호환)
    client = OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",
        timeout=180.0  # [추가] 외부 호출 타임아웃(초) 설정
    )

    try:
        if output.lower() == 'json':
            response = client.chat.completions.create(
                model=llm,
                messages=[
                    {
                        'role': 'system',
                        'content': role
                    },
                    {
                        'role': 'user',
                        'content': prompt + '\n\n출력 형식(json): ' + format
                    }
                ],
                temperature=0,
                n=1,             # 응답수 
                max_completion_tokens=2024,  # 생성할 최대 토큰 수 제한
            )
            content = response.choices[0].message.content
            return json.loads(content) # str -> json
        else:
            response = client.chat.completions.create(
                model=llm,
                messages=[
                    {
                        'role': 'system',
                        'content': role
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                temperature=0,
                n=1,             # 응답수 
                max_completion_tokens=2024,  # 생성할 최대 토큰 수 제한 응답이 생성됨
            )
            return response.choices[0].message.content
    except Exception as e:
        # [추가] 외부 호출 오류 로깅 및 안전 반환
        logging.error(f"[로컬 LLM 호출 실패] {e}")
        if output.lower() == 'json':
            return {"error": f"로컬 LLM 호출 오류: {str(e)}"}
        return f"로컬 LLM 호출 오류: {str(e)}" 
  
# 문자열을 라인단위로 분리하여, 빈 라인을 제거하고, 문장들로 이루어진 리스트 생성
def remove_empty_lines(text):
    lines = [line for line in text.splitlines() if line.strip()]
    # print('-> lines:', lines)
    # print('-' * 80)
    # 문장들을 다시 합쳐서 하나의 문자열로 반환
    result = '\n'.join(lines)
    return result

