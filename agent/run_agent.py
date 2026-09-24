from agent.agent_loop import query
from tools.registry import get_tools


# ============================================================
# Agent 실행
# ============================================================

def run_agent(
    agent_definition,
    llm,
    available_tools=None,
    messages=None,
    session_id="default"
):
    """
    Agent Definition을 기준으로 Agent를 실행한다.

    역할:
        1. Agent가 사용할 Tool 결정
        2. Agent 설정 출력
        3. Agent Query Loop 실행
    """

    print("\n========== run_agent ==========")

    # ========================================================
    # Agent 정보
    # ========================================================

    print(
        f"agent_type: "
        f"{agent_definition.agent_type}"
    )

    print(
        f"model: "
        f"{agent_definition.model}"
    )

    print(
        f"tools: "
        f"{agent_definition.tools}"
    )

    print(
        f"max_turns: "
        f"{agent_definition.max_turns}"
    )

    print(
        f"session_id: "
        f"{session_id}"
    )


    # ========================================================
    # Agent Tool 결정
    # ========================================================

    tools = get_tools(
        agent_definition.tools
    )


    # ========================================================
    # 사용할 수 없는 Tool 확인
    # ========================================================

    registered_tool_names = {
        tool.name
        for tool in tools
    }

    for tool_name in agent_definition.tools:

        if tool_name not in registered_tool_names:

            print(
                f"[Tool 경고] "
                f"'{tool_name}' Tool을 "
                f"Registry에서 찾을 수 없습니다."
            )


    # ========================================================
    # Tool 정보 출력
    # ========================================================

    print(
        "resolved tools: "
        f"{[tool.name for tool in tools]}"
    )


    # ========================================================
    # 메시지 확인
    # ========================================================

    if messages is None:
        messages = []


    # ========================================================
    # Agent Query 실행
    # ========================================================

    result = query(
        llm=llm,
        tools=tools,
        messages=messages,
        max_turns=agent_definition.max_turns,
        system_prompt=agent_definition.get_system_prompt(),
        session_id=session_id,
        agent_name=agent_definition.agent_type
    )


    # ========================================================
    # 완료
    # ========================================================

    print(
        "[Agent] 실행 완료"
    )

    return result