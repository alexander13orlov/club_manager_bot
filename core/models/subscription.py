\"\"\"Subscription model (placeholder).\"\"\"

from dataclasses import dataclass
from datetime import date

@dataclass
class Subscription:
    user_id: int
    total_sessions: int
    used_sessions: int
    valid_until: date
