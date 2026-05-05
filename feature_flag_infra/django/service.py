from feature_flag_infra.service import FeatureFlagService
from .providers import DjangoDBFlagProvider


_flag_service = None


def get_feature_flags() -> FeatureFlagService:
    global _flag_service

    if _flag_service is None:
        _flag_service = FeatureFlagService(
            DjangoDBFlagProvider()
        )

    return _flag_service