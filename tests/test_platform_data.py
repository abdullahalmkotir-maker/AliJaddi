"""بيانات مشتركة للواجهات."""
from __future__ import annotations

from services.platform_data import LEADERBOARD


def test_leaderboard_shape():
    assert len(LEADERBOARD) >= 3
    ranks = [u["rank"] for u in LEADERBOARD]
    assert ranks == sorted(ranks)
    for u in LEADERBOARD:
        assert "name" in u and "stars" in u and "rank" in u
        assert isinstance(u["stars"], int)
