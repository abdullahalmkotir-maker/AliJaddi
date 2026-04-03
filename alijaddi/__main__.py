"""تشغيل: python -m alijaddi"""
from __future__ import annotations

import sys

from .launcher import status_report
from .workspace import workspace_report


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
    sys.stdout.write(workspace_report())
    sys.stdout.write("\n")
    sys.stdout.write(status_report())
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
