import os
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(autouse=True)
def _chdir():
    prev = os.getcwd()
    os.chdir(_ROOT)
    yield
    os.chdir(prev)
