from django.core.management.base import BaseCommand
from feature_flag_infra.django.models import FeatureFlag


class Command(BaseCommand):
    help = "Register a new feature flag (idempotent)"

    def add_arguments(self, parser):
        parser.add_argument("names", nargs="+")
        parser.add_argument(
            "--enable",
            action="store_true",
            help="Enable immediately"
        )
        parser.add_argument(
            "--rollout",
            type=int,
            default=100,
            help="Rollout percentage (0-100)"
        )
        parser.add_argument(
            "--staff-only",
            action="store_true",
            help="Only staff users see this feature"
        )

    def handle(self, *args, **options):
        names = options["names"]
        enabled = options["enable"]
        rollout = options["rollout"]
        staff_only = options["staff_only"]

        for name in names:
            flag, created = FeatureFlag.objects.get_or_create(
                name=name,
                defaults={
                    "enabled": enabled,
                    "rollout_percentage": rollout,
                    "staff_only": staff_only,
                }
            )

            if not created:
                self.stdout.write(
                    self.style.WARNING(f"Feature '{name}' already exists")
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Feature '{name}' registered "
                        f"(enabled={enabled}, rollout={rollout}%, staff_only={staff_only})"
                    )
                )