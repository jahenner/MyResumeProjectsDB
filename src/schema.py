import json
from dataclasses import dataclass, asdict
from typing import List, Optional
from datetime import date

@dataclass
class Challenge:
    issue: str
    solution: str

@dataclass
class Project:
    id: str
    title: str
    context: str  # e.g., "Academic", "Personal", "Professional"
    start_date: date
    end_date: Optional[date]
    summary: str
    tools: List[str]
    environment: str
    challenges: List[Challenge]
    repo_url: Optional[str]

    def to_dict(self) -> dict:
        """Converts the dataclass to a dictionary, handling nested dataclasses."""
        return asdict(self)

    def to_json(self) -> str:
        """Serializes the project to a JSON string, natively handling date objects."""
        def date_handler(obj):
            if isinstance(obj, date):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")
            
        return json.dumps(self.to_dict(), default=date_handler, indent=2)