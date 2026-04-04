"""طبقة SQLite — عيادة الأسنان (مرضى، جلسات، مواعيد، …)."""
from __future__ import annotations

import json
import shutil
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from config import DB_PATH, DATA_DIR, BACKUPS_DIR, SQLITE_TIMEOUT_SEC, SQLITE_BUSY_TIMEOUT_MS

# أعمدة مسموحة فقط — منع حقن SQL عبر مفاتيح kwargs إن وُجدت واجهة تمرّرها من المستخدم
_PATIENT_COLUMNS = frozenset({
    "medical_record_no",
    "birth_date",
    "gender",
    "phone",
    "email",
    "address",
    "blood_type",
    "allergies",
    "medical_history",
    "notes",
    "first_visit",
    "primary_doctor",
})


def _connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), timeout=SQLITE_TIMEOUT_SEC)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute(f"PRAGMA busy_timeout={SQLITE_BUSY_TIMEOUT_MS}")
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db():
    conn = _connect()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialty TEXT DEFAULT '',
            phone TEXT DEFAULT '',
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medical_record_no TEXT UNIQUE,
            full_name TEXT NOT NULL,
            birth_date TEXT,
            gender TEXT DEFAULT 'ذكر',
            phone TEXT DEFAULT '',
            email TEXT DEFAULT '',
            address TEXT DEFAULT '',
            blood_type TEXT DEFAULT '',
            allergies TEXT DEFAULT '',
            medical_history TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            first_visit TEXT,
            primary_doctor TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now','localtime')),
            updated_at TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
            session_date TEXT NOT NULL,
            session_time TEXT DEFAULT '',
            session_type TEXT DEFAULT 'فحص أولي',
            symptoms TEXT DEFAULT '',
            diagnosis TEXT DEFAULT '',
            procedures TEXT DEFAULT '[]',
            teeth_involved TEXT DEFAULT '[]',
            tooth_surfaces TEXT DEFAULT '[]',
            doctor TEXT DEFAULT '',
            assistant TEXT DEFAULT '',
            prescription TEXT DEFAULT '',
            cost REAL DEFAULT 0,
            paid REAL DEFAULT 0,
            notes TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now','localtime')),
            updated_at TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS xray_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER REFERENCES sessions(id) ON DELETE SET NULL,
            patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
            image_path TEXT NOT NULL,
            image_type TEXT DEFAULT '',
            tooth_number TEXT DEFAULT '',
            description TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS treatment_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
            plan_name TEXT NOT NULL,
            description TEXT DEFAULT '',
            status TEXT DEFAULT 'جاري',
            procedures_json TEXT DEFAULT '[]',
            start_date TEXT,
            end_date TEXT,
            total_cost REAL DEFAULT 0,
            notes TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now','localtime')),
            updated_at TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            duration_min INTEGER DEFAULT 30,
            doctor TEXT DEFAULT '',
            reason TEXT DEFAULT '',
            status TEXT DEFAULT 'مؤكد',
            notes TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS lab_work (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
            session_id INTEGER REFERENCES sessions(id) ON DELETE SET NULL,
            work_type TEXT NOT NULL,
            lab_name TEXT DEFAULT '',
            tooth_number TEXT DEFAULT '',
            shade TEXT DEFAULT '',
            status TEXT DEFAULT 'مُرسل للمختبر',
            sent_date TEXT,
            expected_date TEXT,
            received_date TEXT,
            cost REAL DEFAULT 0,
            notes TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now','localtime')),
            updated_at TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE INDEX IF NOT EXISTS idx_sessions_patient ON sessions(patient_id);
        CREATE INDEX IF NOT EXISTS idx_sessions_date ON sessions(session_date);
        CREATE INDEX IF NOT EXISTS idx_xray_patient ON xray_images(patient_id);
        CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(appointment_date);
        CREATE INDEX IF NOT EXISTS idx_appointments_patient ON appointments(patient_id);
        CREATE INDEX IF NOT EXISTS idx_lab_patient ON lab_work(patient_id);
        """)
        _migrate(conn)


def _migrate(conn: sqlite3.Connection) -> None:
    existing = {row[1] for row in conn.execute("PRAGMA table_info(patients)").fetchall()}
    if "medical_record_no" not in existing:
        conn.execute("ALTER TABLE patients ADD COLUMN medical_record_no TEXT UNIQUE")

    existing_s = {row[1] for row in conn.execute("PRAGMA table_info(sessions)").fetchall()}
    if "tooth_surfaces" not in existing_s:
        conn.execute("ALTER TABLE sessions ADD COLUMN tooth_surfaces TEXT DEFAULT '[]'")

    existing_tp = {row[1] for row in conn.execute("PRAGMA table_info(treatment_plans)").fetchall()}
    if "notes" not in existing_tp:
        conn.execute("ALTER TABLE treatment_plans ADD COLUMN notes TEXT DEFAULT ''")


def generate_medical_record_no() -> str:
    with get_db() as conn:
        row = conn.execute("SELECT MAX(id) FROM patients").fetchone()
        next_id = (row[0] or 0) + 1
    return f"MR-{next_id:05d}"


def add_patient(full_name: str, **kwargs: Any) -> int:
    if not (full_name or "").strip():
        raise ValueError("اسم المريض مطلوب")
    full_name = full_name.strip()
    bad = [k for k in kwargs if k not in _PATIENT_COLUMNS]
    if bad:
        raise ValueError(f"حقول غير مسموحة: {', '.join(bad)}")
    if not kwargs.get("medical_record_no"):
        kwargs["medical_record_no"] = generate_medical_record_no()
    cols = ["full_name"] + list(kwargs.keys())
    placeholders = ", ".join(["?"] * len(cols))
    vals = [full_name] + list(kwargs.values())
    col_str = ", ".join(cols)
    with get_db() as conn:
        cur = conn.execute(
            f"INSERT INTO patients ({col_str}) VALUES ({placeholders})",
            vals,
        )
        return int(cur.lastrowid)


def count_patients(query: str = "") -> int:
    with get_db() as conn:
        if query.strip():
            return conn.execute(
                "SELECT COUNT(*) FROM patients WHERE full_name LIKE ? OR phone LIKE ? OR IFNULL(medical_record_no,'') LIKE ?",
                (f"%{query}%", f"%{query}%", f"%{query}%"),
            ).fetchone()[0]
        return conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0]


def get_patient(patient_id: int) -> Optional[dict]:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
        return dict(row) if row else None


def search_patients(query: str = "", limit: int = 100, offset: int = 0) -> list[dict]:
    with get_db() as conn:
        if query.strip():
            rows = conn.execute(
                """SELECT p.*, (SELECT COUNT(*) FROM sessions s WHERE s.patient_id = p.id) AS session_count
                   FROM patients p
                   WHERE p.full_name LIKE ? OR p.phone LIKE ? OR IFNULL(p.medical_record_no,'') LIKE ?
                   ORDER BY p.updated_at DESC LIMIT ? OFFSET ?""",
                (f"%{query}%", f"%{query}%", f"%{query}%", limit, offset),
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT p.*, (SELECT COUNT(*) FROM sessions s WHERE s.patient_id = p.id) AS session_count
                   FROM patients p ORDER BY p.updated_at DESC LIMIT ? OFFSET ?""",
                (limit, offset),
            ).fetchall()
        return [dict(r) for r in rows]


def get_stats() -> dict:
    """ملخص بسيط لـ platform_sync / لوحة التحكم."""
    with get_db() as conn:
        total_patients = conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
        total_sessions = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
        today = datetime.now().strftime("%Y-%m-%d")
        today_sessions = conn.execute(
            "SELECT COUNT(*) FROM sessions WHERE session_date = ?", (today,)
        ).fetchone()[0]
        today_appointments = conn.execute(
            """SELECT COUNT(*) FROM appointments
               WHERE appointment_date = ? AND status NOT IN ('ملغى','مكتمل')""",
            (today,),
        ).fetchone()[0]
        total_revenue = conn.execute("SELECT COALESCE(SUM(cost), 0) FROM sessions").fetchone()[0]
        total_paid = conn.execute("SELECT COALESCE(SUM(paid), 0) FROM sessions").fetchone()[0]
        month_start = datetime.now().strftime("%Y-%m-01")
        month_sessions = conn.execute(
            "SELECT COUNT(*) FROM sessions WHERE session_date >= ?", (month_start,)
        ).fetchone()[0]
        month_revenue = conn.execute(
            "SELECT COALESCE(SUM(cost), 0) FROM sessions WHERE session_date >= ?",
            (month_start,),
        ).fetchone()[0]
        pending_lab = conn.execute(
            "SELECT COUNT(*) FROM lab_work WHERE status NOT IN ('مُركّب')"
        ).fetchone()[0]

        proc_stats = conn.execute("SELECT procedures FROM sessions").fetchall()
        procedure_counts: dict[str, int] = {}
        for row in proc_stats:
            try:
                procs = json.loads(row[0] or "[]")
            except json.JSONDecodeError:
                procs = []
            if not isinstance(procs, list):
                continue
            for p in procs:
                if isinstance(p, str):
                    procedure_counts[p] = procedure_counts.get(p, 0) + 1

        session_type_stats = [
            dict(r)
            for r in conn.execute(
                "SELECT session_type, COUNT(*) AS cnt FROM sessions GROUP BY session_type ORDER BY cnt DESC"
            ).fetchall()
        ]

        monthly_data = [
            dict(r)
            for r in conn.execute(
                """SELECT strftime('%Y-%m', session_date) AS month,
                          COUNT(*) AS cnt, COALESCE(SUM(cost), 0) AS revenue
                   FROM sessions GROUP BY month ORDER BY month DESC LIMIT 12"""
            ).fetchall()
        ]

        return {
            "total_patients": total_patients,
            "total_sessions": total_sessions,
            "today_sessions": today_sessions,
            "today_appointments": today_appointments,
            "total_revenue": float(total_revenue or 0),
            "total_paid": float(total_paid or 0),
            "outstanding": float((total_revenue or 0) - (total_paid or 0)),
            "month_sessions": month_sessions,
            "month_revenue": float(month_revenue or 0),
            "pending_lab": pending_lab,
            "procedure_counts": procedure_counts,
            "session_type_stats": session_type_stats,
            "monthly_data": monthly_data,
        }


def get_doctors(active_only: bool = True) -> list[dict]:
    with get_db() as conn:
        q = "SELECT * FROM doctors"
        if active_only:
            q += " WHERE active = 1"
        q += " ORDER BY name"
        return [dict(r) for r in conn.execute(q).fetchall()]


def create_backup() -> str:
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUPS_DIR / f"dental_backup_{ts}.db"
    shutil.copy2(str(DB_PATH), str(backup_path))
    return str(backup_path)
