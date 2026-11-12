import json
from dataclasses import dataclass, asdict
from typing import List, Optional
from datetime import date

@dataclass
class Challenge:
    issue: str
    solution: str

@dataclass
class Context:
    id: str
    name: str
    description: str

@dataclass
class Tool:
    id: str
    name: str
    description: str
    doc_url: Optional[str]

@dataclass
class Environment:
    id: str
    name: str
    description: str

@dataclass
class Project:
    id: str
    title: str
    context_id: str
    environment_id: str
    start_date: date
    end_date: Optional[date]
    summary: str
    tool_ids: List[str]
    challenges: List[Challenge]
    repo_url: Optional[str]

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        def date_handler(obj):
            if isinstance(obj, date):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")
            
        return json.dumps(self.to_dict(), default=date_handler, indent=2)