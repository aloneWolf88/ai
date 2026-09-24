import fitz
from pathlib import Path

from langchain_core.tools import tool


@tool
def read_pdf_file(file_path: str) -> str:
    """
    PDF 파일의 텍스트를 읽습니다.
    """

    path = Path(file_path)

    if not path.exists():
        return f"파일을 찾을 수 없습니다: {file_path}"

    if not path.is_file():
        return f"파일이 아닙니다: {file_path}"

    if path.suffix.lower() != ".pdf":
        return f"PDF 파일이 아닙니다: {file_path}"

    try:

        document = fitz.open(str(path))

        texts = []

        for page_number, page in enumerate(
            document,
            start=1
        ):

            text = page.get_text("text")

            if text.strip():

                texts.append(
                    f"\n===== Page {page_number} =====\n"
                    f"{text}"
                )

        document.close()

        if not texts:
            return (
                "PDF에서 텍스트를 추출할 수 없습니다.\n"
                "스캔 이미지 PDF일 가능성이 있습니다."
            )

        return "\n".join(texts)

    except Exception as e:

        return f"PDF 읽기 오류: {e}"