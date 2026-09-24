from langchain_core.messages import (
    SystemMessage,
    ToolMessage,
    AIMessage
)

from agent.context_manager import ContextManager
from tools.executor import ToolExecutor


# ============================================================
# Context Manager
# ============================================================

context_manager = ContextManager()


# ============================================================
# Tool Executor
# ============================================================

tool_executor = ToolExecutor()


# ============================================================
# Agent Query Loop
# ============================================================

def query(
    llm,
    tools,
    messages,
    max_turns=None,
    system_prompt=None,
    session_id="default",
    agent_name=None
):
    """
    Local LLM Agent Query Loop

    흐름:

        사용자 질문
             ↓
        Context Manager
             ↓
        현재 Agent System Prompt
             ↓
        LLM 호출
             ↓
        Tool Call 확인
             ↓
        Tool Executor
             ↓
        Tool 실행
             ↓
        ToolMessage
             ↓
        LLM 재호출
             ↓
        최종 AIMessage
             ↓
        이번 Query 결과 반환

    Context는 계속 유지하지만,
    반환값은 이번 Query에서 생성된 메시지만 반환한다.
    """

    # ========================================================
    # 1. Context 생성 / 조회
    # ========================================================

    context = context_manager.get_or_create(
        session_id=session_id,
        agent_name=agent_name
    )


    # ========================================================
    # 2. 이번 Query에서 생성될 메시지 추적
    # ========================================================

    query_messages = []


    # ========================================================
    # 3. Agent Tool 목록
    # ========================================================

    tool_map = {
        tool.name: tool
        for tool in tools
    }


    print("\n========== Agent Query ==========")

    print(
        f"Agent      : {agent_name}"
    )

    print(
        f"Session    : {session_id}"
    )

    print(
        f"Tools      : {list(tool_map.keys())}"
    )


    # ========================================================
    # 4. LLM Tool Binding
    # ========================================================

    if tools:

        llm_with_tools = llm.bind_tools(
            tools
        )

    else:

        llm_with_tools = llm


    # ========================================================
    # 5. 사용자 메시지 Context 추가
    # ========================================================

    if messages:

        new_messages = list(messages)

        context_manager.add_messages(
            session_id,
            new_messages
        )

        query_messages.extend(
            new_messages
        )


    # ========================================================
    # 6. System Prompt
    #
    # Agent가 변경되면 기존 SystemMessage를 제거하고
    # 현재 Agent의 System Prompt를 적용한다.
    # ========================================================

    if system_prompt:

        current_messages = (
            context_manager.get_messages(
                session_id
            )
        )


        # ----------------------------------------------------
        # 기존 SystemMessage 제거
        # ----------------------------------------------------

        non_system_messages = [
            message
            for message in current_messages
            if not isinstance(
                message,
                SystemMessage
            )
        ]


        # ----------------------------------------------------
        # 현재 Agent SystemMessage 생성
        # ----------------------------------------------------

        system_message = SystemMessage(
            content=system_prompt
        )


        # ----------------------------------------------------
        # Context 재구성
        # ----------------------------------------------------

        context.messages.clear()

        context.messages.append(
            system_message
        )

        context.messages.extend(
            non_system_messages
        )


        print("\n========== System Prompt ==========")

        print(
            f"Agent: {agent_name}"
        )

        print(
            system_prompt
        )


    # ========================================================
    # 7. Agent Loop
    # ========================================================

    turn = 1

    while True:

        print(
            f"\n========== Query Loop {turn} =========="
        )


        # ====================================================
        # 현재 Context
        # ====================================================

        current_messages = (
            context_manager.get_messages(
                session_id
            )
        )


        print(
            f"[1] LLM 호출 "
            f"(messages={len(current_messages)})"
        )


        # ====================================================
        # LLM 호출
        # ====================================================

        try:

            response = llm_with_tools.invoke(
                current_messages
            )

        except Exception as e:

            print(
                f"[LLM 오류] {e}"
            )

            return query_messages


        # ====================================================
        # LLM 응답 출력
        # ====================================================

        print(
            "\n[2] LLM 응답"
        )

        print(
            f"    type: "
            f"{type(response).__name__}"
        )

        print(
            f"    content: "
            f"{response.content}"
        )

        print(
            f"    tool_calls: "
            f"{response.tool_calls}"
        )


        # ====================================================
        # AIMessage Context 저장
        # ====================================================

        context_manager.add_message(
            session_id,
            response
        )


        # 이번 Query 결과에도 추가
        query_messages.append(
            response
        )


        # ====================================================
        # 8. Tool Call 없음
        # ====================================================

        if not response.tool_calls:

            print(
                "\n[3] Tool 호출 없음"
            )

            print(
                "    → Query 종료"
            )

            return query_messages


        # ====================================================
        # 9. Tool Call 발견
        # ====================================================

        print(
            "\n[3] Tool 호출 발견"
        )

        print(
            f"    호출 개수: "
            f"{len(response.tool_calls)}"
        )


        # ====================================================
        # 10. Max Turn 확인
        # ====================================================

        if (
            max_turns is not None
            and turn >= max_turns
        ):

            print(
                "\n[3-1] 최대 Turn 도달"
            )

            print(
                f"    max_turns: "
                f"{max_turns}"
            )

            print(
                "    → Query 종료"
            )

            return query_messages


        # ====================================================
        # 11. Tool 실행
        # ====================================================

        for tool_call in response.tool_calls:

            tool_name = tool_call["name"]

            tool_args = tool_call["args"]

            tool_call_id = tool_call["id"]


            print(
                "\n[4] Tool 호출"
            )

            print(
                f"    name: "
                f"{tool_name}"
            )

            print(
                f"    args: "
                f"{tool_args}"
            )

            print(
                f"    tool_call_id: "
                f"{tool_call_id}"
            )


            # =================================================
            # Agent Tool 권한 확인
            # =================================================

            if tool_name not in tool_map:

                tool_result = (
                    f"Agent에서 사용할 수 없는 "
                    f"Tool입니다: {tool_name}"
                )

                print(
                    f"    [Tool 제한] "
                    f"{tool_name}"
                )


            else:

                # =============================================
                # Tool Executor
                # =============================================

                tool_result = (
                    tool_executor.execute(
                        tool_name=tool_name,
                        tool_args=tool_args
                    )
                )


            # =================================================
            # Tool 결과 출력
            # =================================================

            print(
                f"    결과: "
                f"{tool_result}"
            )


            # =================================================
            # Tool Result Context 저장
            # =================================================

            context_manager.add_tool_result(
                session_id=session_id,
                tool_name=tool_name,
                tool_args=tool_args,
                result=tool_result,
                tool_call_id=tool_call_id
            )


            # =================================================
            # ToolMessage 생성
            # =================================================

            tool_message = ToolMessage(
                content=str(tool_result),
                tool_call_id=tool_call_id
            )


            # =================================================
            # ToolMessage Context 저장
            # =================================================

            context_manager.add_message(
                session_id,
                tool_message
            )


            # 이번 Query 결과에도 추가
            query_messages.append(
                tool_message
            )


            print(
                "\n[5] ToolMessage 추가"
            )

            print(
                f"    content: "
                f"{tool_message.content}"
            )

            print(
                f"    tool_call_id: "
                f"{tool_message.tool_call_id}"
            )


        # ====================================================
        # 12. 다음 Query Loop
        # ====================================================

        current_count = len(
            context_manager.get_messages(
                session_id
            )
        )


        print(
            "\n[6] 다음 Query Loop 준비"
        )

        print(
            f"    현재 messages 개수: "
            f"{current_count}"
        )


        turn += 1