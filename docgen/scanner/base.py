from dataclasses import dataclass
from typing import Optional, List
from abc import ABC, abstractmethod

@dataclass
class UndocumentedItem:
    filepath: str
    line_start: int
    line_end: int
    name: str
    item_type: str
    source_code: str
    existing_docstring: Optional[str]
    language: str

@dataclass
class GeneratedDoc:
    item: UndocumentedItem
    docstring: str
    format: str
    confidence: float

@dataclass
class PatchResult:
    filepath: str
    items_patched: int
    diff: str

class BaseScanner(ABC):
    @abstractmethod
    def scan(self, directory: str) -> List[UndocumentedItem]:
        pass
