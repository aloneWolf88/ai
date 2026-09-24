from pathlib import Path

from langchain_core.tools import tool


@tool
def read_text_file(file_path: str) -> str:
    """
    TXT 파일의 내용을 읽습니다.

    Args:
        file_path: 읽을 TXT 파일 경로
    """

    path = Path(file_path)

    if not path.exists():
        return f"파일을 찾을 수 없습니다: {file_path}"

    if not path.is_file():
        return f"파일이 아닙니다: {file_path}"

    try:
        return path.read_text(
            encoding="utf-8"
        )

    except UnicodeDecodeError:

        try:
            return path.read_text(
                encoding="cp949"
            )

        except Exception as e:
            return f"파일 읽기 오류: {e}"

    except Exception as e:
        return f"파일 읽기 오류: {e}"