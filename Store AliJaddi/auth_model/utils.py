"""أدوات مساعدة."""
import re
from typing import Tuple


def validate_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email or "") is not None


def validate_password(password: str) -> Tuple[bool, str]:
    if len(password) < 8:
        return False, "كلمة المرور 8 أحرف على الأقل"
    if not any(c.isupper() for c in password):
        return False, "تحتاج حرفاً كبيراً"
    if not any(c.islower() for c in password):
        return False, "تحتاج حرفاً صغيراً"
    if not any(c.isdigit() for c in password):
        return False, "تحتاج رقماً"
    return True, "موافق"
