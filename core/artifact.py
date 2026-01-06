from abc import ABC, abstractmethod
from typing import List, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Evidence:
    """
    Represents a single piece of evidence extracted from an artifact.
    """
    source_path: str
    artifact_type: str
    data: Any
    timestamp: datetime
    hash_checksum: str | None = None

class Artifact(ABC):
    """
    Abstract base class for all forensic artifacts.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    def extract(self) -> List[Evidence]:
        """
        Extracts evidence from the target source.
        """
        pass
