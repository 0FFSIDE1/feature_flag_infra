import pytest

from feature_flag_infra.django.models import FeatureFlag
from django.core.exceptions import ValidationError

@pytest.mark.django_db
def test_feature_flag_str_enabled():
    flag = FeatureFlag.objects.create(
        name="new_invoice_flow",
        enabled=True,
    )

    assert str(flag) == "new_invoice_flow - Enabled"


@pytest.mark.django_db
def test_feature_flag_str_disabled():
    flag = FeatureFlag.objects.create(
        name="new_invoice_flow",
        enabled=False,
    )

    assert str(flag) == "new_invoice_flow - Disabled"


@pytest.mark.django_db
def test_feature_flag_name_is_unique():
    FeatureFlag.objects.create(name="duplicate_flag")

    with pytest.raises(Exception):
        FeatureFlag.objects.create(name="duplicate_flag")

@pytest.mark.django_db
def test_rollout_percentage_cannot_exceed_100():
    flag = FeatureFlag(
        name="bad_flag",
        rollout_percentage=101,
    )

    with pytest.raises(ValidationError):
        flag.full_clean()