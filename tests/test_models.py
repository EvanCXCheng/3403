"""Unit tests for model properties — no DB queries needed."""
from app.models import User


class TestUserAccuracyPct:

    def test_zero_segments_returns_zero(self):
        u = User(username='a', email='a@x.com', password_hash='h',
                 total_segments=0, accuracy_sum=0.0)
        assert u.accuracy_pct == 0.0

    def test_none_total_segments_returns_zero(self):
        # Regression: previously caused TypeError (None compared to 0)
        u = User(username='b', email='b@x.com', password_hash='h',
                 total_segments=None, accuracy_sum=None)
        assert u.accuracy_pct == 0.0

    def test_single_perfect_submission(self):
        u = User(username='c', email='c@x.com', password_hash='h',
                 total_segments=1, accuracy_sum=1.0)
        assert u.accuracy_pct == 100.0

    def test_cumulative_mean_across_multiple_submissions(self):
        # dice scores: 0.8 + 0.6 + 1.0 = 2.4 over 3 → mean 80.0%
        u = User(username='d', email='d@x.com', password_hash='h',
                 total_segments=3, accuracy_sum=2.4)
        assert u.accuracy_pct == 80.0

    def test_result_rounded_to_one_decimal(self):
        # 2.0 / 3 = 66.666...% → rounds to 66.7
        u = User(username='e', email='e@x.com', password_hash='h',
                 total_segments=3, accuracy_sum=2.0)
        assert u.accuracy_pct == 66.7
