import sys
from pathlib import Path

# ============================================================
# 프로젝트 ROOT 설정
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# 외부 라이브러리
# ============================================================

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from langchain_core.messages import HumanMessage

from langchain_ollama import ChatOllama


# ============================================================
# 프로젝트 모듈
# ============================================================

from core.config import config

from agent.agent_loader import load_agents
from agent.agent_router import AgentRouter
from agent.run_agent import run_agent

from tools.registry import get_available_tools


# ============================================================
# Agent 로딩
# ============================================================

agents = load_agents()

print("\n========== Loaded Agents ==========")

for agent_type, agent in agents.items():
    print(
        f"- {agent_type} "
        f"| model={agent.model} "
        f"| tools={agent.tools}"
    )


# ============================================================
# Agent Router
# ============================================================

router = AgentRouter(agents)


# ============================================================
# Tool Registry
# ============================================================

available_tools = get_available_tools()

print("\n========== Available Tools ==========")

for tool in available_tools:
    print(f"- {tool.name}")


# ============================================================
# Ollama LLM
# ============================================================

llm = ChatOllama(
    model=config.llm_model,
    temperature=0,
)


# ============================================================
# Telegram /start
# ============================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "Local LLM Agent가 시작되었습니다.\n\n"
        "질문을 입력하세요."
    )


# ============================================================
# Telegram 메시지 처리
# ============================================================

async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.message is None:
        return

    user_text = update.message.text

    if not user_text:
        return

    print("\n\n")
    print("============================================================")
    print("Telegram Message")
    print("============================================================")
    print(f"사용자: {user_text}")


    # ========================================================
    # 1. Agent Router
    # ========================================================

    try:

        agent_type = router.route(
            user_text
        )

    except Exception as e:

        print(
            f"[Router 오류] {e}"
        )

        await update.message.reply_text(
            f"Agent Router 오류:\n{e}"
        )

        return


    # ========================================================
    # 2. Agent Definition
    # ========================================================

    agent_definition = agents.get(
        agent_type
    )

    if agent_definition is None:

        await update.message.reply_text(
            "사용 가능한 Agent를 찾을 수 없습니다."
        )

        return


    print("\n========== Selected Agent ==========")

    print(
        f"Agent Type : "
        f"{agent_definition.agent_type}"
    )

    print(
        f"Model      : "
        f"{agent_definition.model}"
    )

    print(
        f"Tools      : "
        f"{agent_definition.tools}"
    )

    print(
        f"Max Turns  : "
        f"{agent_definition.max_turns}"
    )


    # ========================================================
    # 3. Telegram 사용자별 Session
    # ========================================================

    user_id = update.effective_user.id

    session_id = (
        f"telegram:{user_id}"
    )

    print(
        f"Session ID : "
        f"{session_id}"
    )


    # ========================================================
    # 4. HumanMessage 생성
    # ========================================================

    messages = [
        HumanMessage(
            content=user_text
        )
    ]


    # ========================================================
    # 5. Agent 실행
    # ========================================================

    try:

        result = run_agent(
            agent_definition=agent_definition,
            llm=llm,
            available_tools=available_tools,
            messages=messages,
            session_id=session_id,
        )

    except Exception as e:

        print(
            f"[Agent 오류] {e}"
        )

        await update.message.reply_text(
            f"Agent 실행 오류:\n{e}"
        )

        return


    # ========================================================
    # 6. 최종 응답 추출
    # ========================================================

    answer = None

    if result:

        # 뒤에서부터 확인
        for message in reversed(result):

            content = getattr(
                message,
                "content",
                None
            )

            if not content:
                continue

            # AIMessage의 최종 응답
            if message.__class__.__name__ == "AIMessage":

                answer = content

                break


    # ========================================================
    # 7. 응답이 없는 경우
    # ========================================================

    if not answer:

        answer = (
            "처리 결과를 확인했지만 "
            "최종 응답을 생성하지 못했습니다."
        )


    # ========================================================
    # 8. Telegram 응답
    # ========================================================

    print("\n========== Final Answer ==========")

    print(answer)

    await update.message.reply_text(
        answer
    )


# ============================================================
# 오류 처리
# ============================================================

async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE
):

    print(
        "\n========== Telegram Error =========="
    )

    print(
        context.error
    )


# ============================================================
# Bot 실행
# ============================================================

def main():

    print("\n")
    print("============================================================")
    print("Local LLM Telegram Agent")
    print("============================================================")

    print(
        f"LLM Model : "
        f"{config.llm_model}"
    )

    print(
        f"Agents    : "
        f"{list(agents.keys())}"
    )

    print(
        f"Tools     : "
        f"{[tool.name for tool in available_tools]}"
    )


    # ========================================================
    # Telegram Application
    # ========================================================

    application = (
        Application
        .builder()
        .token(config.telegram_bot_token)
        .build()
    )


    # ========================================================
    # Handler 등록
    # ========================================================

    application.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT
            & ~filters.COMMAND,
            handle_message
        )
    )


    # ========================================================
    # Error Handler
    # ========================================================

    application.add_error_handler(
        error_handler
    )


    # ========================================================
    # 실행
    # ========================================================

    print(
        "\nTelegram Bot 실행..."
    )

    application.run_polling()


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    main()