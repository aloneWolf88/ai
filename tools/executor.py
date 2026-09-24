from typing import Any, Dict

from tools.registry import get_tool


class ToolExecutor:

    def __init__(self):
        pass

    # ========================================================
    # Tool 실행
    # ========================================================

    def execute(
        self,
        tool_name: str,
        tool_args: Dict[str, Any]
    ):
        """
        Tool 이름과 arguments를 받아 Tool을 실행한다.

        Args:
            tool_name: Tool 이름
            tool_args: Tool 실행 arguments

        Returns:
            Tool 실행 결과
        """

        # ----------------------------------------------------
        # Tool 검색
        # ----------------------------------------------------

        tool = get_tool(tool_name)

        if tool is None:
            return (
                f"알 수 없는 Tool입니다: "
                f"{tool_name}"
            )

        # ----------------------------------------------------
        # Tool 실행
        # ----------------------------------------------------

        try:

            result = tool.invoke(
                tool_args
            )

            return result

        except Exception as e:

            return (
                f"Tool 실행 오류: {e}"
            )