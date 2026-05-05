from abc import ABC, abstractmethod
from typing import Any


class FeatureFlagProvider(ABC):
    @abstractmethod
    def is_enabled(
        self,
        flag: str,
        *,
        user: Any = None,
        default: bool = False,
    ) -> bool:
        raise NotImplementedError