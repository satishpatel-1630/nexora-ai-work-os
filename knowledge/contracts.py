from dataclasses import dataclass
from typing import Any
@dataclass(frozen=True)
class KnowledgeDocument:
    source:str; content:str; metadata:dict[str,Any]
class KnowledgeRetriever:
    async def search(self,query:str,limit:int=10)->list[KnowledgeDocument]: raise NotImplementedError
