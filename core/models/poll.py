\"\"\"Poll model.\"\"\"

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Tuple

@dataclass
class Poll:
    chat_id: int
    message_id: int | None
    command: str
    expires_at: datetime
    participants: List[Tuple[int, str, str]] = field(default_factory=list)
    active: bool = True
