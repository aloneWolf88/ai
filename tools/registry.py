from typing import Dict, List

from tools.calculator import calculator
from tools.document_reader import read_text_file
from tools.pdf_reader import read_pdf_file
from tools.file_writer import write_text_file


class ToolRegistry:

    def __init__(self):

        self._tools: Dict[str, object] = {}

        self.register(calculator)
        self.register(read_text_file)
        self.register(read_pdf_file)
        self.register(write_text_file)


    # ========================================================
    # Tool 등록
    # ========================================================

    def register(self, tool):

        if tool is None:
            return

        self._tools[tool.name] = tool


    # ========================================================
    # Tool 1개 조회
    # ========================================================

    def get_tool(self, name: str):

        return self._tools.get(name)


    # ========================================================
    # 지정된 Tool 조회
    # ========================================================

    def get_tools(
        self,
        tool_names: List[str]
    ) -> List:

        tools = []

        for tool_name in tool_names:

            tool = self.get_tool(
                tool_name
            )

            if tool is not None:

                tools.append(tool)

        return tools


    # ========================================================
    # 전체 Tool 조회
    # ========================================================

    def get_all_tools(self) -> List:

        return list(
            self._tools.values()
        )


    # ========================================================
    # Tool 이름 목록
    # ========================================================

    def get_tool_names(self) -> List[str]:

        return list(
            self._tools.keys()
        )


# ============================================================
# 전역 Registry
# ============================================================

tool_registry = ToolRegistry()


# ============================================================
# 기존 코드 호환용 함수
# ============================================================

def get_tool(
    tool_name: str
):

    return tool_registry.get_tool(
        tool_name
    )


def get_tools(
    tool_names: List[str]
) -> List:

    return tool_registry.get_tools(
        tool_names
    )


def get_available_tools() -> List:

    return tool_registry.get_all_tools()


def get_tool_names() -> List[str]:

    return tool_registry.get_tool_names()