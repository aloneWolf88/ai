from langchain_core.tools import tool


@tool
def calculator(expression: str) -> str:
    """
    간단한 수식을 계산합니다. 한국말로 대답해주세요.
    예: 100 + 200, 50 * 3, 100 / 4
    """

    try:
        # 테스트 단계에서는 간단한 수식만 허용
        allowed = "0123456789+-*/(). "

        if not all(char in allowed for char in expression):
            return "허용되지 않는 문자가 포함되어 있습니다."

        result = eval(expression, {"__builtins__": {}}, {})

        return str(result)

    except Exception as e:
        return f"계산 오류: {e}"