from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class FeatureFlag(models.Model):
    name = models.CharField(max_length=150, unique=True)
    enabled = models.BooleanField(default=False)

    staff_only = models.BooleanField(default=False)

    rollout_percentage = models.PositiveSmallIntegerField(
        default=0, validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
    )

    description = models.TextField(blank=True)

    users = models.ManyToManyField("auth.User", blank=True, related_name="feature_flags")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Feature Flag"
        verbose_name_plural = "Feature Flags"

    def __str__(self):
        return f"{self.name} - {'Enabled' if self.enabled else 'Disabled'}"
