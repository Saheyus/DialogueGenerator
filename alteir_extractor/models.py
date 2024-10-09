# models.py
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class Feature:
    Properties: Dict[str, Any]

@dataclass
class Entity:
    Id: str
    DisplayName: str
    Text: str
    Features: List[Feature] = field(default_factory=list)
    References: List[Any] = field(default_factory=list)

@dataclass
class Location:
    Id: str
    Name: str
    Data: Dict[str, Any]

@dataclass
class Dialogue:
    Id: str
    DisplayName: str
    Text: str
    StartingFragments: List[str] = field(default_factory=list)

@dataclass
class Fragment:
    Id: str
    DisplayName: str
    Text: str
    SpeakerId: Optional[str]
    SpeakerName: str

@dataclass
class Connection:
    Source: str
    Target: str
