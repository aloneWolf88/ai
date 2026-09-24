from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from langchain_core.messages import BaseMessage


@dataclass
class AgentContext:
    """
    하나의 Agent 실행에 대한 Context.

    관리 대상:
    - session_id
    - agent_name
    - messages
    - tool_results
    - metadata
    """

    session_id: str

    agent_name: Optional[str] = None

    messages: List[BaseMessage] = field(
        default_factory=list
    )

    tool_results: List[Dict[str, Any]] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


class ContextManager:
    """
    Agent Context를 관리한다.

    현재는 메모리 기반으로 관리한다.
    추후 Telegram, Redis, DB 등의 영속 저장소로
    확장할 수 있다.
    """

    def __init__(self):
        self._contexts: Dict[str, AgentContext] = {}

    # ---------------------------------------------------------
    # Context 생성
    # ---------------------------------------------------------

    def create_context(
        self,
        session_id: str,
        agent_name: Optional[str] = None
    ) -> AgentContext:

        context = AgentContext(
            session_id=session_id,
            agent_name=agent_name
        )

        self._contexts[session_id] = context

        return context

    # ---------------------------------------------------------
    # Context 조회
    # ---------------------------------------------------------

    def get_context(
        self,
        session_id: str
    ) -> Optional[AgentContext]:

        return self._contexts.get(session_id)

    # ---------------------------------------------------------
    # Context가 없으면 생성
    # ---------------------------------------------------------

    def get_or_create(
        self,
        session_id: str,
        agent_name: Optional[str] = None
    ) -> AgentContext:

        context = self.get_context(session_id)

        if context is None:

            context = self.create_context(
                session_id=session_id,
                agent_name=agent_name
            )

        elif agent_name is not None:

            context.agent_name = agent_name

        return context

    # ---------------------------------------------------------
    # Agent 설정
    # ---------------------------------------------------------

    def set_agent(
        self,
        session_id: str,
        agent_name: str
    ) -> None:

        context = self.get_or_create(
            session_id
        )

        context.agent_name = agent_name

    # ---------------------------------------------------------
    # Message 추가
    # ---------------------------------------------------------

    def add_message(
        self,
        session_id: str,
        message: BaseMessage
    ) -> None:

        context = self.get_or_create(
            session_id
        )

        context.messages.append(
            message
        )

    # ---------------------------------------------------------
    # Messages 추가
    # ---------------------------------------------------------

    def add_messages(
        self,
        session_id: str,
        messages: List[BaseMessage]
    ) -> None:

        context = self.get_or_create(
            session_id
        )

        context.messages.extend(
            messages
        )

    # ---------------------------------------------------------
    # Messages 조회
    # ---------------------------------------------------------

    def get_messages(
        self,
        session_id: str
    ) -> List[BaseMessage]:

        context = self.get_context(
            session_id
        )

        if context is None:
            return []

        return list(
            context.messages
        )

    # ---------------------------------------------------------
    # Tool 결과 저장
    # ---------------------------------------------------------

    def add_tool_result(
        self,
        session_id: str,
        tool_name: str,
        tool_args: Dict[str, Any],
        result: Any,
        tool_call_id: Optional[str] = None
    ) -> None:

        context = self.get_or_create(
            session_id
        )

        context.tool_results.append({
            "tool_name": tool_name,
            "tool_args": tool_args,
            "result": result,
            "tool_call_id": tool_call_id
        })

    # ---------------------------------------------------------
    # Tool 결과 조회
    # ---------------------------------------------------------

    def get_tool_results(
        self,
        session_id: str
    ) -> List[Dict[str, Any]]:

        context = self.get_context(
            session_id
        )

        if context is None:
            return []

        return list(
            context.tool_results
        )

    # ---------------------------------------------------------
    # Metadata 저장
    # ---------------------------------------------------------

    def set_metadata(
        self,
        session_id: str,
        key: str,
        value: Any
    ) -> None:

        context = self.get_or_create(
            session_id
        )

        context.metadata[key] = value

    # ---------------------------------------------------------
    # Metadata 조회
    # ---------------------------------------------------------

    def get_metadata(
        self,
        session_id: str,
        key: str,
        default: Any = None
    ) -> Any:

        context = self.get_context(
            session_id
        )

        if context is None:
            return default

        return context.metadata.get(
            key,
            default
        )

    # ---------------------------------------------------------
    # Context 삭제
    # ---------------------------------------------------------

    def clear(
        self,
        session_id: str
    ) -> None:

        self._contexts.pop(
            session_id,
            None
        )

    # ---------------------------------------------------------
    # 전체 Context 삭제
    # ---------------------------------------------------------

    def clear_all(self) -> None:

        self._contexts.clear()