from pathlib import Path

from langchain_core.tools import tool


@tool
def write_text_file(
    file_path: str,
    content: str
) -> str:
    """
    텍스트 내용을 지정한 파일에 저장합니다.

    Args:
        file_path: 저장할 파일 경로
        content: 저장할 내용
    """

    path = Path(file_path)

    try:
        path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        path.write_text(
            content,
            encoding="utf-8"
        )

        return (
            f"파일 저장 완료: {file_path}"
        )

    except Exception as e:

        return (
            f"파일 저장 오류: {e}"
        )