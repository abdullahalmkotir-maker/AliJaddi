"""اختبارات دخان."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def test_validate_email():
    from auth_model.utils import validate_email

    assert validate_email("a@b.co")
    assert not validate_email("bad")


def test_decode_jwt_sub_invalid():
    from auth_model.cloud_client import decode_jwt_sub

    with pytest.raises(ValueError):
        decode_jwt_sub("x")


def test_model_ids():
    from auth_model import model_ids
    from config import AVAILABLE_MODELS

    assert not (set(AVAILABLE_MODELS) - model_ids.CANONICAL_MODEL_IDS)


def test_unlink_model(tmp_path):
    from auth_model.auth import AuthManager

    db = tmp_path / "u.db"
    a = AuthManager(str(db))
    assert a.register("u1", "Secret123!", "u1@x.co")[0]
    assert a.link_model("u1", "legal", "قانون")[0]
    assert "legal" in a.get_user_models("u1")
    assert a.unlink_model("u1", "legal")[0]
    assert "legal" not in a.get_user_models("u1")
    assert not a.unlink_model("u1", "legal")[0]
