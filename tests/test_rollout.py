from feature_flag_infra.rollout import is_user_in_rollout


class FakeUser:
    def __init__(self, id):
        self.id = id


def test_zero_percent_rollout_is_false():
    user = FakeUser(id=1)

    assert is_user_in_rollout("flag", user, 0) is False


def test_100_percent_rollout_is_true():
    user = FakeUser(id=1)

    assert is_user_in_rollout("flag", user, 100) is True


def test_rollout_is_deterministic():
    user = FakeUser(id=123)

    first = is_user_in_rollout("flag", user, 50)
    second = is_user_in_rollout("flag", user, 50)

    assert first == second


def test_rollout_without_user_is_false():
    assert is_user_in_rollout("flag", None, 50) is False