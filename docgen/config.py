import os
from pathlib import Path
from typing import List, Optional
import tomllib
from pydantic import BaseModel, ConfigDict

class DocgenConfig(BaseModel):
    format: str = "google"
    exclude_patterns: List[str] = []
    skip_private: bool = True
    model: str = "gpt-4o"
    language: str = "auto"
    
    model_config = ConfigDict(extra="ignore")

def load_config() -> DocgenConfig:
    config_path = Path(".docgenrc.toml")
    if config_path.is_file():
        try:
            with open(config_path, "rb") as f:
                data = tomllib.load(f)
            return DocgenConfig(**data)
        except Exception:
            pass
    return DocgenConfig()
