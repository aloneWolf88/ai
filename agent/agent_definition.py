from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class AgentDefinition:
    """
    Claude Code의 AgentDefinition을 단순화한 구조.

    현재 구현하는 핵심 속성:
        agent_type
        description
        prompt
        tools
        model
        max_turns
    """

    agent_type: str
    description: str
    prompt: str

    tools: List[str] = field(default_factory=list)

    model: Optional[str] = None
    max_turns: Optional[int] = None

    def get_system_prompt(self) -> str:
        """
        Agent가 사용할 System Prompt를 반환한다.
        """

        return self.prompt

    def __str__(self):
        return (
            f"AgentDefinition("
            f"agent_type={self.agent_type}, "
            f"model={self.model}, "
            f"tools={self.tools}, "
            f"max_turns={self.max_turns}"
            f")"
        )