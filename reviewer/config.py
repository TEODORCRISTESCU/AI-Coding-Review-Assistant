from pathlib import Path

import yaml
from pydantic import BaseModel, Field

class ReviewerConfig(BaseModel):
    max_diff_chars : int = Field(default=50000, gt=0)
    ignored_paths: list[str] = Field(default_factory=list)

def load_config(path: str | Path = ".reviewer.yml") -> ReviewerConfig:
    config_path = Path(path)

    if not config_path.exists():
        return ReviewerConfig()

    with config_path.open(encoding="utf-8") as file:
        data = yaml.safe_load(file)

    if data is None:
        data = {}

    return ReviewerConfig.model_validate(data)