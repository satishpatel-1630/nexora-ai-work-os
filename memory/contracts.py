from dataclasses import dataclass
from enum import StrEnum
from typing import Any
from uuid import UUID
class MemoryType(StrEnum):
    FACT="fact"; USER_PREFERENCE="user_preference"; PROJECT_DECISION="project_decision"; DOCUMENT="document"; RESEARCH="research"; SOURCE="source"; MODEL_OUTPUT="model_output"; ASSUMPTION="assumption"
@dataclass(frozen=True)
class MemoryRecord:
    id:UUID; memory_type:MemoryType; content:str; metadata:dict[str,Any]
