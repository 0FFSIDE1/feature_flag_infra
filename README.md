feature-flag-infra

A lightweight, production-ready feature flag infrastructure for Python applications.

Built for clean architecture, progressive rollout, and multi-project reuse.

Supports:

Django (first-class)
Any Python project (framework-agnostic)
Pluggable providers (DB, Redis, API, etc.)
Deterministic rollout (percentage-based)
✨ Why this exists

Most feature flag implementations are:

tightly coupled to a framework
hard to reuse across services
missing rollout logic
not test-friendly

feature-flag-infra solves that by providing:

a clean provider interface
a central service layer
reusable rollout logic
optional Django integration
📦 Installation
pip install feature-flag-infra
🧠 Core Concept

Everything revolves around one abstraction:

FeatureFlagService -> FeatureFlagProvider

You plug in your provider (DB, Redis, API), and the service handles usage.

🚀 Quick Start (Framework Agnostic)
1. Create a provider
from feature_flag_infra.interfaces import FeatureFlagProvider


class InMemoryProvider(FeatureFlagProvider):
    def __init__(self):
        self.flags = {
            "new_feature": True
        }

    def is_enabled(self, flag, *, user=None, default=False):
        return self.flags.get(flag, default)
2. Use the service
from feature_flag_infra.service import FeatureFlagService

flags = FeatureFlagService(provider=InMemoryProvider())

if flags.enabled("new_feature"):
    print("Feature is ON")
⚙️ Django Integration
1. Add to installed apps
INSTALLED_APPS = [
    ...
    "feature_flag_infra.django",
]
2. Run migrations
python manage.py migrate
3. Use in your code
from feature_flag_infra.django import get_feature_flags

flags = get_feature_flags()

if flags.enabled("anomaly_detection", user=request.user):
    # new logic
    ...
🗃️ Feature Flag Model (Django)
FeatureFlag:
- name (unique)
- enabled (bool)
- staff_only (bool)
- rollout_percentage (0–100)
🎯 Rollout Behavior

The library supports deterministic percentage rollout:

user_id + flag_name → hash → bucket (0–99)
Example
rollout %	behavior
0	nobody gets it
50	~50% of users
100	everyone

This ensures:

consistency (same user always gets same result)
safe gradual rollout
no randomness issues
🔐 Staff-only Flags
if obj.staff_only:
    return user.is_staff

Use this for:

internal testing
admin-only features
beta previews
🧠 Caching

Django provider uses caching:

CACHE_TTL = 30  # seconds

This prevents repeated DB hits.

You can plug in:

Redis
Memcached
local memory
🧩 Extending Providers

You can easily plug in your own provider.

Example: Redis Provider
class RedisFlagProvider(FeatureFlagProvider):
    def __init__(self, redis_client):
        self.redis = redis_client

    def is_enabled(self, flag, *, user=None, default=False):
        value = self.redis.get(flag)

        if value is None:
            return default

        return value == b"1"
🧪 Testing
class FakeProvider(FeatureFlagProvider):
    def is_enabled(self, flag, *, user=None, default=False):
        return True
flags = FeatureFlagService(FakeProvider())

assert flags.enabled("anything") is True
🧱 Design Principles
Dependency Inversion (DIP) → provider-based architecture
Deterministic rollout → safe progressive delivery
Framework isolation → Django is optional
Composable → plug into any system
Testability first
🔄 Real-world Usage
Example: Safe feature release
if flags.enabled("new_checkout_flow", user=request.user):
    return NewCheckoutService.process(...)
else:
    return OldCheckoutService.process(...)
Example: Anomaly Detection Toggle
if flags.enabled("anomaly_detection", user=request.user):
    run_detection()
📌 Roadmap
 Redis provider (first-class)
 API provider (central flag service)
 CLI for flag management
 Admin dashboard improvements
 Metrics / exposure tracking
🤝 Contributing

PRs are welcome. Focus on:

clean abstractions
backward compatibility
performance
📄 License

MIT

🧠 Final Note

This library is intentionally minimal but powerful.

It gives you:

control over rollout
clean architecture
portability across services

Without locking you into a specific ecosystem.