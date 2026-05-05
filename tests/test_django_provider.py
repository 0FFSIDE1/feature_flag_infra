import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache

from feature_flag_infra.django.models import FeatureFlag
from feature_flag_infra.django.providers import DjangoDBFlagProvider


User = get_user_model()


@pytest.mark.django_db
def test_missing_flag_returns_default_false(provider):
    assert provider.is_enabled("missing_flag") is False


@pytest.mark.django_db
def test_missing_flag_returns_custom_default(provider):
    assert provider.is_enabled("missing_flag", default=True) is True


@pytest.mark.django_db
def test_disabled_flag_returns_false(provider, user):
    FeatureFlag.objects.create(
        name="new_dashboard",
        enabled=False,
        rollout_percentage=100,
    )

    assert provider.is_enabled("new_dashboard", user=user) is False


@pytest.mark.django_db
def test_enabled_flag_with_100_percent_rollout_returns_true(provider, user):
    FeatureFlag.objects.create(
        name="new_dashboard",
        enabled=True,
        rollout_percentage=100,
    )

    assert provider.is_enabled("new_dashboard", user=user) is True


@pytest.mark.django_db
def test_enabled_flag_with_zero_percent_rollout_returns_false(provider, user):
    FeatureFlag.objects.create(
        name="new_dashboard",
        enabled=True,
        rollout_percentage=0,
    )

    assert provider.is_enabled("new_dashboard", user=user) is False


@pytest.mark.django_db
def test_anonymous_user_gets_true_only_for_100_percent_rollout(provider):
    FeatureFlag.objects.create(
        name="public_feature",
        enabled=True,
        rollout_percentage=100,
    )

    assert provider.is_enabled("public_feature") is True


@pytest.mark.django_db
def test_anonymous_user_gets_false_for_partial_rollout(provider):
    FeatureFlag.objects.create(
        name="partial_feature",
        enabled=True,
        rollout_percentage=50,
    )

    assert provider.is_enabled("partial_feature") is False


@pytest.mark.django_db
def test_staff_only_allows_staff_user(provider, staff_user):
    FeatureFlag.objects.create(
        name="internal_feature",
        enabled=True,
        staff_only=True,
        rollout_percentage=0,
    )

    assert provider.is_enabled("internal_feature", user=staff_user) is True


@pytest.mark.django_db
def test_staff_only_blocks_normal_user_even_if_enabled(provider, user):
    FeatureFlag.objects.create(
        name="internal_feature",
        enabled=True,
        staff_only=True,
        rollout_percentage=100,
    )

    assert provider.is_enabled("internal_feature", user=user) is False


@pytest.mark.django_db
def test_staff_only_blocks_anonymous_user(provider):
    FeatureFlag.objects.create(
        name="internal_feature",
        enabled=True,
        staff_only=True,
        rollout_percentage=100,
    )

    assert provider.is_enabled("internal_feature") is False


@pytest.mark.django_db
def test_explicit_user_allowlist_enables_user_even_with_zero_rollout(provider, user):
    flag = FeatureFlag.objects.create(
        name="beta_feature",
        enabled=True,
        rollout_percentage=0,
    )
    flag.users.add(user)

    assert provider.is_enabled("beta_feature", user=user) is True


@pytest.mark.django_db
def test_explicit_user_allowlist_does_not_override_staff_only(provider, user):
    flag = FeatureFlag.objects.create(
        name="staff_beta",
        enabled=True,
        staff_only=True,
        rollout_percentage=0,
    )
    flag.users.add(user)

    assert provider.is_enabled("staff_beta", user=user) is False


@pytest.mark.django_db
def test_user_not_in_allowlist_still_uses_rollout(provider, user):
    FeatureFlag.objects.create(
        name="rollout_feature",
        enabled=True,
        rollout_percentage=100,
    )

    assert provider.is_enabled("rollout_feature", user=user) is True


@pytest.mark.django_db
def test_rollout_is_deterministic(provider, user):
    FeatureFlag.objects.create(
        name="partial_rollout",
        enabled=True,
        rollout_percentage=50,
    )

    first = provider.is_enabled("partial_rollout", user=user)
    second = provider.is_enabled("partial_rollout", user=user)

    assert first == second


@pytest.mark.django_db
def test_cache_prevents_repeated_flag_fetches(provider, user, django_assert_num_queries):
    FeatureFlag.objects.create(
        name="cached_feature",
        enabled=True,
        rollout_percentage=100,
    )

    with django_assert_num_queries(1):
        assert provider.is_enabled("cached_feature", user=user) is True

    with django_assert_num_queries(0):
        assert provider.is_enabled("cached_feature", user=user) is True