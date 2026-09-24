from langchain_ollama import ChatOllama

from tools.calculator import calculator
from tools.document_reader import read_text_file
from agent.run_agent import run_agent
from agent.agent_loader import load_agents
from agent.agent_router import AgentRouter


class QueryEngine:

    def __init__(self):

        # Agent 전체 로드
        self.agents = load_agents("agents")

        if not self.agents:
            raise RuntimeError(
                "사용 가능한 Agent가 없습니다."
            )

        # Agent Router
        self.router = AgentRouter(
            self.agents
        )

        # 현재 사용 가능한 전체 Tool
        self.available_tools = [
            calculator,
            read_text_file
        ]

    def run(
        self,
        messages,
        agent_type=None
    ):

        # Agent를 직접 지정하지 않았으면 Router 사용
        if agent_type is None:

            question = self._get_latest_user_message(
                messages
            )

            agent_type = self.router.route(
                question
            )

        # 선택한 Agent 가져오기
        agent_definition = self.agents.get(
            agent_type
        )

        if agent_definition is None:

            raise ValueError(
                f"존재하지 않는 Agent입니다: "
                f"{agent_type}"
            )

        print("\n========== Agent 선택 ==========")

        print(
            f"agent_type: "
            f"{agent_definition.agent_type}"
        )

        print(
            f"description: "
            f"{agent_definition.description}"
        )

        # Agent가 지정한 모델 사용
        llm = ChatOllama(
            model=agent_definition.model,
            temperature=0
        )

        return {
            "messages": run_agent(
                agent_definition=agent_definition,
                llm=llm,
                available_tools=self.available_tools,
                messages=messages
            )
        }

    @staticmethod
    def _get_latest_user_message(messages):

        for message in reversed(messages):

            if isinstance(message, dict):

                if message.get("role") == "user":
                    return message.get(
                        "content",
                        ""
                    )

            else:

                message_type = getattr(
                    message,
                    "type",
                    None
                )

                if message_type == "human":
                    return message.content

        return ""