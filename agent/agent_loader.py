import json
from pathlib import Path

from agent.agent_definition import AgentDefinition


def load_agent_from_json(file_path):
    """
    Agent JSON 파일 하나를 읽어 AgentDefinition으로 변환한다.

    Claude Code loadAgentsDir.ts의
    parseAgentFromJson()을 단순화한 구현이다.
    """

    file_path = Path(file_path)

    try:
        with file_path.open(
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        agent_type = file_path.stem

        description = data.get("description")
        prompt = data.get("prompt")

        if not description:
            print(
                f"[Agent 경고] description이 없습니다: "
                f"{file_path}"
            )
            return None

        if not prompt:
            print(
                f"[Agent 경고] prompt가 없습니다: "
                f"{file_path}"
            )
            return None

        tools = data.get("tools", [])

        if tools is None:
            tools = []

        model = data.get("model")

        max_turns = data.get("maxTurns")

        return AgentDefinition(
            agent_type=agent_type,
            description=description,
            prompt=prompt,
            tools=tools,
            model=model,
            max_turns=max_turns
        )

    except Exception as e:

        print(
            f"[Agent 오류] "
            f"{file_path}: {e}"
        )

        return None


def load_agents(directory="agents"):
    """
    agents 디렉터리의 JSON Agent 정의를 모두 읽는다.

    반환:
        dict[str, AgentDefinition]
    """

    directory = Path(directory)

    agents = {}

    if not directory.exists():

        print(
            f"[Agent] Agent 디렉터리가 없습니다: "
            f"{directory}"
        )

        return agents

    for file_path in directory.glob("*.json"):

        agent = load_agent_from_json(file_path)

        if agent is None:
            continue

        agents[agent.agent_type] = agent

    return agents


def get_agent(
    agent_type,
    directory="agents"
):
    """
    특정 Agent를 가져온다.
    """

    agents = load_agents(directory)

    return agents.get(agent_type)