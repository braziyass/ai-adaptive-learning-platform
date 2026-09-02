from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(slots=True)
class AIChunk:
    id: Optional[int]
    source_document: str
    chunk_index: int
    text: str
    page_number: Optional[int] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    embedding: list[float] | None = None