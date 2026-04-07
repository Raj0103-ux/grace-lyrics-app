from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Song:
    id: str
    title: str
    language: str # 'tamil' or 'telugu'
    lyrics: str
    number: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    composer: Optional[str] = None
    is_favorite: bool = False
