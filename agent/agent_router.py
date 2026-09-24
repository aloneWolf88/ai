from langchain_ollama import ChatOllama


class AgentRouter:

    def __init__(self, agents):

        self.agents = agents

        self.llm = ChatOllama(
            model="qwen2.5:3b",
            temperature=0
        )


    def route(self, question):
        """
        사용자 질문을 분석하여
        가장 적절한 Agent type을 선택한다.

        반환:
            agent_type
        """

        if not self.agents:

            raise RuntimeError(
                "사용 가능한 Agent가 없습니다."
            )


        # ====================================================
        # Agent 정보 생성
        # ====================================================

        agent_descriptions = []

        for agent_type, agent in self.agents.items():

            tools = ", ".join(
                agent.tools
            ) if agent.tools else "없음"

            agent_descriptions.append(
                f"""
Agent type: {agent_type}
설명: {agent.description}
사용 가능한 Tool: {tools}
"""
            )


        agent_list = "\n".join(
            agent_descriptions
        )


        # ====================================================
        # Router Prompt
        # ====================================================

        prompt = f"""
당신은 Local LLM Agent Router입니다.

사용자의 질문을 분석하고,
아래 Agent 중 가장 적합한 Agent 하나를 선택하십시오.

반드시 아래 Agent type 중 하나만 출력하십시오.

{agent_list}

Agent 선택 기준:

1. 사용자가 일반적인 질문을 하는 경우
   → general

2. TXT, PDF, Word 등의 파일을 읽거나
   문서를 요약하거나
   문서 내용을 분석하거나
   파일로 저장하는 작업인 경우
   → document_summary

3. 주식, 종목, 주가, 투자 데이터,
   외국인, 기관, 프로그램 매매 등의
   주식 분석 작업인 경우
   → stock_analysis

중요 규칙:

- 파일을 읽는 작업은 document_summary를 선택하십시오.
- 문서를 요약하는 작업은 document_summary를 선택하십시오.
- 문서 내용을 파일로 저장하는 작업도 document_summary를 선택하십시오.
- 계산만 필요한 일반적인 질문은 general을 선택하십시오.
- 주식 관련 질문은 stock_analysis를 선택하십시오.
- Agent type 외에는 아무것도 출력하지 마십시오.
- 설명하지 마십시오.
- Markdown을 사용하지 마십시오.

사용자 질문:
{question}

선택할 Agent type:
"""


        # ====================================================
        # LLM Router 호출
        # ====================================================

        response = self.llm.invoke(
            prompt
        )


        selected_agent = (
            response.content
            .strip()
        )


        # ====================================================
        # Router 로그
        # ====================================================

        print(
            "\n========== Agent Router =========="
        )

        print(
            f"질문: {question}"
        )

        print(
            f"Router 응답: {selected_agent}"
        )


        # ====================================================
        # 정확한 Agent type 확인
        # ====================================================

        if selected_agent in self.agents:

            print(
                f"선택된 Agent: "
                f"{selected_agent}"
            )

            return selected_agent


        # ====================================================
        # LLM이 불필요한 문장을 붙이는 경우
        #
        # 예:
        # "document_summary입니다."
        # ====================================================

        for agent_type in self.agents:

            if agent_type in selected_agent:

                print(
                    f"Agent type 추출: "
                    f"{agent_type}"
                )

                return agent_type


        # ====================================================
        # 잘못된 응답
        # ====================================================

        if "general" in self.agents:

            print(
                "알 수 없는 Agent가 선택되어 "
                "general Agent를 사용합니다."
            )

            return "general"


        # ====================================================
        # general도 없는 경우
        # ====================================================

        first_agent = next(
            iter(self.agents)
        )

        print(
            f"기본 Agent 사용: "
            f"{first_agent}"
        )

        return first_agent