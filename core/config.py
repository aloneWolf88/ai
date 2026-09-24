from pathlib import Path
from typing import Any

import yaml


# 프로젝트 루트
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 설정 파일
CONFIG_FILE = PROJECT_ROOT / "venv" / "config.yaml"


class Config:
    """프로젝트 전체 설정을 관리한다."""

    def __init__(self, config_file: Path = CONFIG_FILE):
        self.config_file = config_file
        self.data = self._load()

    def _load(self) -> dict[str, Any]:
        if not self.config_file.exists():
            raise FileNotFoundError(
                f"설정 파일을 찾을 수 없습니다: {self.config_file}"
            )

        with open(
            self.config_file,
            "r",
            encoding="utf-8"
        ) as file:
            data = yaml.safe_load(file)

        if not isinstance(data, dict):
            raise ValueError(
                f"설정 파일 형식이 올바르지 않습니다: {self.config_file}"
            )

        return data

    def get(
        self,
        section: str,
        key: str,
        default: Any = None
    ) -> Any:

        section_data = self.data.get(section, {})

        if not isinstance(section_data, dict):
            return default

        return section_data.get(key, default)

    @property
    def telegram_bot_token(self) -> str:
        token = self.get("telegram", "bot_token")

        if not token:
            raise ValueError(
                "telegram.bot_token이 config.yaml에 설정되어 있지 않습니다."
            )

        return token

    @property
    def llm_provider(self) -> str:
        return self.get(
            "llm",
            "provider",
            "ollama"
        )

    @property
    def llm_base_url(self) -> str:
        return self.get(
            "llm",
            "base_url",
            "http://localhost:11434"
        )

    @property
    def llm_model(self) -> str:
        return self.get(
            "llm",
            "model",
            "qwen2.5:3b"
        )


config = Config()