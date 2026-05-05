from typing import Any
from .interfaces import FeatureFlagProvider


class FeatureFlagService:
    def __init__(self, provider: FeatureFlagProvider):
        self.provider = provider

    def enabled(
        self,
        flag: str,
        *,
        user: Any = None,
        default: bool = False,
    ) -> bool:
        return self.provider.is_enabled(
            flag,
            user=user,
            default=default,
        )