from django.apps import AppConfig


class FeatureFlagInfraConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "feature_flag_infra.django"
    label = "feature_flag_infra"