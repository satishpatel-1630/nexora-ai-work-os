from dataclasses import dataclass
@dataclass(frozen=True)
class ToolDefinition:
    name:str; description:str; input_schema:dict; output_schema:dict; risk_level:str; permissions:tuple[str,...]=(); available:bool=False
class ToolRegistry:
    def __init__(self): self._tools:dict[str,ToolDefinition]={}
    def register(self,tool:ToolDefinition)->None: self._tools[tool.name]=tool
    def get(self,name:str): return self._tools.get(name)
    def list(self): return list(self._tools.values())
