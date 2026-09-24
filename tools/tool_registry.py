from typing import Dict, List

from tools.calculator import calculator
from tools.document_reader import read_text_file

try:
    from tools.pdf_reader import read_pdf_file
except Exception:
    read_pdf_file = None


class ToolRegistry:

    def __init__(self):

        self._tools: Dict[str, object] = {}

        self.register(calculator)

        self.register(read_text_file)

        if read_pdf_file:
            self.register(read_pdf_file)

    def register(self, tool):

        self._tools[tool.name] = tool

    def get_tool(self, name: str):

        return self._tools.get(name)

    def get_all_tools(self) -> List:

        return list(self._tools.values())

    def get_tool_names(self) -> List[str]:

        return list(self._tools.keys())


tool_registry = ToolRegistry()