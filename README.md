# feature-flag-infra

`feature-flag-infra` is a reusable Python/Django feature flag infrastructure package for progressive delivery and controlled rollouts.

It is published as:

```bash
pip install feature-flag-infra
```

And imported as:

```python
import feature_flag_infra
```

## Why this package exists

Feature flags are useful in both web apps and background services, but many implementations are tightly coupled to one framework or one storage backend.

This package provides a small, provider-driven core API that works:

- in Django projects (with a built-in database provider and model)
- in non-Django Python projects (by implementing your own provider)

It is infrastructure code intended to be reused across projects, not a standalone Django project.

## Features

- Provider abstraction via `FeatureFlagProvider`
- Core service API via `FeatureFlagService`
- Deterministic percentage rollout helper (`is_user_in_rollout`)
- Built-in Django integration:
  - `FeatureFlag` model
  - Django DB-backed provider (`DjangoDBFlagProvider`)
  - convenience accessor (`get_feature_flags`)
  - migration and management command (`register_feature`)
- Built-in cache usage in Django provider (flag metadata cache)

## Installation

```bash
pip install feature-flag-infra
```

> **Note:** This package has a Django dependency and is designed as a reusable library. Do not expect a `manage.py` inside this repository.

## Quick start

Use the framework-agnostic service API with a custom provider:

```python
from feature_flag_infra.interfaces import FeatureFlagProvider
from feature_flag_infra.service import FeatureFlagService


class InMemoryProvider(FeatureFlagProvider):
    def __init__(self):
        self.flags = {
            "new_checkout": True,
            "beta_search": False,
        }

    def is_enabled(self, flag, *, user=None, default=False):
        return self.flags.get(flag, default)


flags = FeatureFlagService(provider=InMemoryProvider())

if flags.enabled("new_checkout"):
    print("New checkout is enabled")
```

## Django usage

### 1) `INSTALLED_APPS` setup

Use the package app config:

```python
INSTALLED_APPS = [
    # ...
    "feature_flag_infra.django.apps.FeatureFlagInfraConfig",
]
```

- App config path: `feature_flag_infra.django.apps.FeatureFlagInfraConfig`
- App label: `feature_flag_infra`

### 2) Migrations

This package ships with migrations for the `FeatureFlag` model.

Run:

```bash
python manage.py migrate
```

You do **not** need to generate migrations for this package yourself.

### 3) Creating feature flags

#### Option A: Django admin / ORM

```python
from feature_flag_infra.django.models import FeatureFlag

FeatureFlag.objects.create(
    name="new_invoice_flow",
    enabled=True,
    rollout_percentage=100,
)
```

#### Option B: management command

```bash
python manage.py register_feature new_invoice_flow --enable --rollout 100
```

You can register multiple flags at once:

```bash
python manage.py register_feature flag_a flag_b --rollout 50
```

### 4) Using `get_feature_flags`

```python
from feature_flag_infra.django.service import get_feature_flags

flags = get_feature_flags()

if flags.enabled("new_invoice_flow", user=request.user):
    # gated behavior
    ...
```

### 5) Example usage in views/services

```python
# views.py
from django.http import JsonResponse
from feature_flag_infra.django.service import get_feature_flags


def checkout_view(request):
    flags = get_feature_flags()

    if flags.enabled("new_checkout", user=request.user):
        return JsonResponse({"flow": "new"})

    return JsonResponse({"flow": "legacy"})
```

```python
# services.py
from feature_flag_infra.django.service import get_feature_flags


def maybe_run_anomaly_detection(user):
    flags = get_feature_flags()

    if flags.enabled("anomaly_detection", user=user):
        return "anomaly detection enabled"

    return "anomaly detection disabled"
```

## Non-Django Python usage

### `FeatureFlagProvider`

`FeatureFlagProvider` is the interface your backend must implement:

```python
class FeatureFlagProvider:
    def is_enabled(self, flag: str, *, user=None, default=False) -> bool:
        ...
```

### Custom in-memory provider

```python
from feature_flag_infra.interfaces import FeatureFlagProvider


class InMemoryProvider(FeatureFlagProvider):
    def __init__(self, flags=None):
        self.flags = flags or {}

    def is_enabled(self, flag, *, user=None, default=False):
        return self.flags.get(flag, default)
```

### `FeatureFlagService` usage

```python
from feature_flag_infra.service import FeatureFlagService

provider = InMemoryProvider({"feature_x": True})
flags = FeatureFlagService(provider)

assert flags.enabled("feature_x") is True
assert flags.enabled("missing", default=False) is False
```

## Rollout behavior

The Django provider evaluates in this order:

1. If `staff_only=True`, only staff users receive the feature.
2. If `enabled=False`, feature is off.
3. If `rollout_percentage >= 100`, feature is on.
4. If user is explicitly allowlisted in `FeatureFlag.users`, feature is on.
5. If `rollout_percentage <= 0`, feature is off.
6. Otherwise, deterministic rollout is applied by hashing `"{flag}:{user_id}"` into bucket `0..99`.

### Enabled/disabled behavior

- `enabled=False` always disables (except `staff_only` is checked first, which still requires staff).
- `enabled=True` allows further checks (staff-only, allowlist, rollout).

### `staff_only` behavior

- `staff_only=True` returns `True` only when `user.is_staff` is truthy.
- Anonymous or non-staff users get `False`.

### Users allowlist behavior

Implemented via `FeatureFlag.users` many-to-many relation to `AUTH_USER_MODEL`.

- If a user is allowlisted, they get `True` even when `rollout_percentage=0`.
- `staff_only=True` still takes precedence and can block non-staff allowlisted users.

### `rollout_percentage` behavior

- `0`: no rollout users are included.
- `100`: all users are included.
- `1-99`: deterministic partial rollout using stable hash bucketing.

### Anonymous user behavior

- Anonymous/no-user requests can only receive `True` from the Django provider when rollout is effectively 100% and other conditions allow it.
- Anonymous users do not participate in percentage rollout because no user identifier is available.

## Caching behavior

`DjangoDBFlagProvider` caches flag metadata by key `feature_flag:{flag_name}` using Django cache.

- Default TTL: `30` seconds (`CACHE_TTL = 30`)
- Cached fields: `id`, `enabled`, `staff_only`, `rollout_percentage`
- User allowlist checks are still evaluated per call (DB existence check for authenticated users)

You can override TTL:

```python
from feature_flag_infra.django.providers import DjangoDBFlagProvider

provider = DjangoDBFlagProvider(cache_ttl=10)
```

## Testing

This repository uses `pytest` with `pytest-django`.

Typical commands:

```bash
pytest
pytest -q
```

The test suite covers model behavior, provider behavior (including caching and allowlist), and rollout determinism.

## Package structure

```text
feature_flag_infra/
├── interfaces.py                 # Provider interface
├── service.py                    # FeatureFlagService
├── rollout.py                    # Deterministic rollout helpers
└── django/
    ├── apps.py                   # Django AppConfig
    ├── models.py                 # FeatureFlag model
    ├── providers.py              # DjangoDBFlagProvider
    ├── service.py                # get_feature_flags()
    ├── management/commands/
    │   └── register_feature.py   # Feature registration command
    └── migrations/
        └── 0001_initial.py
```

## Extending with custom providers

To support other storage backends (Redis, remote API, config service), implement `FeatureFlagProvider` and inject it into `FeatureFlagService`.

```python
from feature_flag_infra.interfaces import FeatureFlagProvider
from feature_flag_infra.service import FeatureFlagService


class CustomProvider(FeatureFlagProvider):
    def is_enabled(self, flag, *, user=None, default=False):
        # read from your backend
        return default


flags = FeatureFlagService(CustomProvider())
```

This keeps your application logic independent from storage details.

## Security and best practices

- Treat feature flags as control-plane configuration: restrict who can modify them.
- Use `staff_only` for internal rollouts and admin-safe experiments.
- Prefer gradual rollout (`rollout_percentage`) over instant global enablement.
- Keep flag names stable and descriptive (e.g., `new_checkout_v2`).
- Audit and retire stale flags to reduce long-term branching complexity.

## Roadmap

Potential future enhancements (not currently implemented in core package):

- First-class Redis provider implementation
- Central API-backed provider
- CLI improvements for bulk operations
- Optional admin UX enhancements
- Exposure/metrics hooks

## License

MIT License. See [LICENSE](LICENSE).
