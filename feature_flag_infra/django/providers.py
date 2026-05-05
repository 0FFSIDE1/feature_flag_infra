from __future__ import annotations
from typing import Any

from django.core.cache import cache

from feature_flag_infra.interfaces import FeatureFlagProvider
from feature_flag_infra.rollout import is_user_in_rollout

from .models import FeatureFlag


class DjangoDBFlagProvider(FeatureFlagProvider):
    CACHE_TTL = 30

    def __init__(self, cache_ttl: int | None = None):
        self.cache_ttl = cache_ttl or self.CACHE_TTL

    def is_enabled(self, flag: str, *, user: Any = None, default: bool = False) -> bool:
        cache_key = f"feature_flag:{flag}"
        data = cache.get(cache_key)

        if data is None:
            try:
                obj = FeatureFlag.objects.only(
                    "id",
                    "name",
                    "enabled",
                    "staff_only",
                    "rollout_percentage",
                ).get(name=flag)
            except FeatureFlag.DoesNotExist:
                return default

            data = {
                "id": obj.id,
                "enabled": obj.enabled,
                "staff_only": obj.staff_only,
                "rollout_percentage": obj.rollout_percentage,
            }

            cache.set(cache_key, data, self.cache_ttl)

        if data["staff_only"]:
            return bool(user and getattr(user, "is_staff", False))

        if not data["enabled"]:
            return False

        percentage = data["rollout_percentage"]
        
        if percentage >= 100:
            return True

        if user and getattr(user, "is_authenticated", True):
            is_explicit_user = FeatureFlag.objects.filter(
                id=data["id"],
                users__pk=user.pk,
            ).exists()

            if is_explicit_user:
                return True
        
        if percentage <= 0:
            return False

        return is_user_in_rollout(flag, user, percentage)