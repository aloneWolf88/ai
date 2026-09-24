from agent.agent import create_local_agent
from memory.memory import Memory


def main():

    agent = create_local_agent()

    memory = Memory(max_messages=10)

    # 첫 번째 질문
    question1 = "나는 Python으로 로컬 LLM Agent를 만들고 있다."

    memory.add("user", question1)

    result1 = agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": question1
            }
        ]
    })

    answer1 = result1["messages"][-1].content

    memory.add("assistant", answer1)

    print("\n===== 첫 번째 질문 =====")
    print(question1)

    print("\n===== AI 응답 =====")
    print(answer1)

    # 두 번째 질문
    question2 = "내가 지금 만들고 있는 프로그램의 목적이 뭐지?"

    history = memory.build()

    prompt = f"""
다음은 이전 대화 내용입니다.

===== 이전 대화 =====
{history}

===== 현재 질문 =====
{question2}

이전 대화 내용을 참고하여 현재 질문에 답변하세요.
"""

    memory.add("user", question2)

    result2 = agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    })

    answer2 = result2["messages"][-1].content

    memory.add("assistant", answer2)

    print("\n===== 두 번째 질문 =====")
    print(question2)

    print("\n===== AI 응답 =====")
    print(answer2)


if __name__ == "__main__":
    main()