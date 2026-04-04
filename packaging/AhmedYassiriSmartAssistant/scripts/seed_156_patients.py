#!/usr/bin/env python3
"""
إدراج 156 مريضاً تجريبياً للتدريب على النظام (ليست تدريب نموذج تعلم آلي).

الاستخدام من جذر المشروع:
  python scripts/seed_156_patients.py
  python scripts/seed_156_patients.py --replace   # حذف مرضى التدريب السابقين MR-T*****
"""
from __future__ import annotations

import argparse
import random
import sys
from datetime import date, timedelta
from pathlib import Path

# جذر المشروع على sys.path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import database as db  # noqa: E402

TRAINING_MRN_PREFIX = "MR-T"
COUNT = 156

FIRST_M = [
    "أحمد", "محمد", "علي", "حسين", "حيدر", "كريم", "سجاد", "مصطفى", "عمر", "يوسف",
    "باسم", "طارق", "فاضل", "نوري", "رامي", "سامي", "وليد", "زياد", "عادل", "جاسم",
]
FIRST_F = [
    "فاطمة", "زينب", "مريم", "سارة", "نور", "هدى", "رنا", "ليلى", "يسرى", "شهد",
    "دينا", "هبة", "إيمان", "أمل", "سعاد", "كوثر", "رقية", "صفاء", "نادية", "غادة",
]
LAST = [
    "العبيدي", "الموسوي", "الكاظمي", "البغدادي", "النجفي", "البصري", "الكربلائي",
    "السامرائي", "الأمين", "الحسيني", "الجبوري", "التميمي", "الزيدي", "الراشد",
]
BLOOD = ["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
CITIES = ["بغداد", "البصرة", "أربيل", "النجف", "كربلاء", "الموصل", "ذي قار", "بابل"]


def _random_birth_date(rng: random.Random) -> str:
    start = date(1955, 1, 1)
    end = date(2015, 12, 31)
    delta = (end - start).days
    d = start + timedelta(days=rng.randint(0, delta))
    return d.strftime("%Y-%m-%d")


def _iraq_phone(rng: random.Random, index: int) -> str:
    # 10 أرقام بعد 07 — فريد تقريباً
    tail = (index * 7919 + rng.randint(1000, 9999)) % 10_000_000
    return f"07{rng.choice(['80','81','82','83','84','90','91'])}{tail:07d}"


def clear_training_patients() -> int:
    with db.get_db() as conn:
        cur = conn.execute(
            "DELETE FROM patients WHERE medical_record_no LIKE ?",
            (f"{TRAINING_MRN_PREFIX}%",),
        )
        return cur.rowcount or 0


def count_training_patients() -> int:
    with db.get_db() as conn:
        row = conn.execute(
            "SELECT COUNT(*) FROM patients WHERE medical_record_no LIKE ?",
            (f"{TRAINING_MRN_PREFIX}%",),
        ).fetchone()
        return int(row[0])


def seed_doctors(rng: random.Random) -> None:
    with db.get_db() as conn:
        n = conn.execute("SELECT COUNT(*) FROM doctors").fetchone()[0]
        if n > 0:
            return
        conn.execute(
            "INSERT INTO doctors (name, specialty, phone, active) VALUES (?,?,?,1)",
            ("د. أحمد الياسري", "طب أسنان عام", "07901234567"),
        )
        conn.execute(
            "INSERT INTO doctors (name, specialty, phone, active) VALUES (?,?,?,1)",
            ("د. سارة الموسوي", "تجميل وتركيبات", "07801112233"),
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="إدراج 156 مريض تدريب")
    parser.add_argument(
        "--replace",
        action="store_true",
        help="حذف جميع مرضى التدريب (أرقام ملف MR-T*) ثم إعادة الإدراج",
    )
    parser.add_argument("--seed", type=int, default=42, help="بذرة عشوائية لبيانات ثابتة")
    args = parser.parse_args()
    rng = random.Random(args.seed)

    db.init_db()
    seed_doctors(rng)

    if args.replace:
        removed = clear_training_patients()
        print(f"تم حذف {removed} سجل تدريب سابق.")

    existing = count_training_patients()
    if existing >= COUNT and not args.replace:
        print(f"يوجد بالفعل {existing} مريض تدريب (MR-T*). استخدم --replace لإعادة الإنشاء.")
        return

    if existing > 0 and existing < COUNT and not args.replace:
        print(
            f"تحذير: يوجد {existing} من مرضى التدريب فقط. ننصح بـ --replace لضبط العدد عند {COUNT}."
        )

    today = date.today().strftime("%Y-%m-%d")
    primary = "د. أحمد الياسري"

    inserted = 0
    with db.get_db() as conn:
        for i in range(1, COUNT + 1):
            mrn = f"{TRAINING_MRN_PREFIX}{i:05d}"
            # تجنب ازدواجية إن أُعيد التشغيل بدون --replace
            row = conn.execute(
                "SELECT 1 FROM patients WHERE medical_record_no = ?", (mrn,)
            ).fetchone()
            if row:
                continue

            gender = "ذكر" if i % 2 == 1 else "أنثى"
            pool = FIRST_M if gender == "ذكر" else FIRST_F
            name = f"{rng.choice(pool)} {rng.choice(LAST)}"
            full_name = f"{name} (تدريب {i:03d})"

            blood = rng.choice(BLOOD)
            allergies = "لا يوجد" if rng.random() > 0.12 else "البنسلين"
            history = "" if rng.random() > 0.25 else "ضغط دموي خفيف — تحت المتابعة"
            phone = _iraq_phone(rng, i)
            email = f"train{i:03d}@example.local"
            addr = f"{rng.choice(CITIES)} — حي {rng.randint(1, 60)}"

            conn.execute(
                """
                INSERT INTO patients (
                    medical_record_no, full_name, birth_date, gender, phone, email,
                    address, blood_type, allergies, medical_history, notes,
                    first_visit, primary_doctor, updated_at
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,datetime('now','localtime'))
                """,
                (
                    mrn,
                    full_name,
                    _random_birth_date(rng),
                    gender,
                    phone,
                    email,
                    addr,
                    blood,
                    allergies,
                    history,
                    "سجل تلقائي للتدريب على واجهة العيادة",
                    today,
                    primary,
                ),
            )
            inserted += 1

    total = count_training_patients()
    print(f"تم إدراج {inserted} مريضاً جديداً. إجمالي مرضى التدريب (MR-T*): {total}")
    print(f"إجمالي المرضى في القاعدة: {db.count_patients()}")


if __name__ == "__main__":
    main()
