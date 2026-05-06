from django.contrib import admin
from .models import FeatureFlag

@admin.register(FeatureFlag)
class FeatureFlagAdmin(admin.ModelAdmin):
    list_display = ("name", "enabled", "rollout_percentage", "staff_only", "updated_at")