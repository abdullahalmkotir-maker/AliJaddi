import express from "express";
import cors from "cors";
import Database from "better-sqlite3";
import multer from "multer";
import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";
import { randomUUID, randomBytes } from "crypto";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.join(__dirname, "..");
const uploadDir = path.join(__dirname, "uploads");
const dataDir = path.join(__dirname, "data");
const dbPath = path.join(dataDir, "clinic.db");

fs.mkdirSync(uploadDir, { recursive: true });
fs.mkdirSync(dataDir, { recursive: true });

const db = new Database(dbPath);
db.pragma("journal_mode = WAL");
db.pragma("foreign_keys = ON");

db.exec(`
  CREATE TABLE IF NOT EXISTS patients (
    id TEXT PRIMARY KEY,
    full_name TEXT NOT NULL,
    birth_date TEXT NOT NULL,
    gender TEXT NOT NULL,
    phone TEXT NOT NULL,
    first_visit TEXT NOT NULL,
    primary_doctor TEXT NOT NULL
  );
  CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    session_type TEXT NOT NULL,
    symptoms TEXT NOT NULL,
    diagnosis TEXT NOT NULL,
    procedures TEXT NOT NULL,
    doctor_name TEXT NOT NULL,
    assistants TEXT NOT NULL DEFAULT '',
    xray_label TEXT,
    has_xray INTEGER NOT NULL DEFAULT 0,
    xray_stored_name TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
  );
`);

function patientRow(r) {
  return {
    id: r.id,
    fullName: r.full_name,
    birthDate: r.birth_date,
    gender: r.gender,
    phone: r.phone,
    firstVisit: r.first_visit,
    primaryDoctor: r.primary_doctor,
  };
}

function sessionRow(r) {
  const url = r.xray_stored_name ? `/uploads/${r.xray_stored_name}` : null;
  return {
    id: r.id,
    patientId: r.patient_id,
    date: r.date,
    time: r.time,
    sessionType: r.session_type,
    symptoms: r.symptoms,
    diagnosis: r.diagnosis,
    procedures: r.procedures,
    doctorName: r.doctor_name,
    assistants: r.assistants || "",
    xrayLabel: r.xray_label,
    hasXray: Boolean(r.has_xray),
    xrayPublicUrl: url,
  };
}

function boolish(v) {
  if (v === true || v === 1) return true;
  if (typeof v === "string") return v === "1" || v.toLowerCase?.() === "true";
  return false;
}

function parseSessionBody(req) {
  const b = req.body;
  return {
    patientId: b.patientId,
    date: b.date,
    time: b.time,
    sessionType: b.sessionType,
    symptoms: b.symptoms ?? "",
    diagnosis: b.diagnosis ?? "",
    procedures: b.procedures ?? "",
    doctorName: b.doctorName,
    assistants: b.assistants ?? "",
    xrayLabel: b.xrayLabel && String(b.xrayLabel).trim() ? String(b.xrayLabel).trim() : null,
    hasXray: boolish(b.hasXray),
  };
}

function seedIfEmpty() {
  const n = db.prepare("SELECT COUNT(*) AS c FROM patients").get().c;
  if (n > 0) return;

  const insP = db.prepare(`
    INSERT INTO patients (id, full_name, birth_date, gender, phone, first_visit, primary_doctor)
    VALUES (@id, @full_name, @birth_date, @gender, @phone, @first_visit, @primary_doctor)
  `);
  const insS = db.prepare(`
    INSERT INTO sessions (id, patient_id, date, time, session_type, symptoms, diagnosis, procedures,
      doctor_name, assistants, xray_label, has_xray, xray_stored_name)
    VALUES (@id, @patient_id, @date, @time, @session_type, @symptoms, @diagnosis, @procedures,
      @doctor_name, @assistants, @xray_label, @has_xray, @xray_stored_name)
  `);

  const patients = [
    {
      id: "p1",
      full_name: "علي كريم الجبوري",
      birth_date: "1990-03-15",
      gender: "ذكر",
      phone: "07901234567",
      first_visit: "2024-01-10",
      primary_doctor: "د. لمياء حسن",
    },
    {
      id: "p2",
      full_name: "سارة طارق الدليمي",
      birth_date: "1985-07-22",
      gender: "أنثى",
      phone: "07809998877",
      first_visit: "2023-11-05",
      primary_doctor: "د. علي كاظم",
    },
    {
      id: "p3",
      full_name: "محمد فاضل العبيدي",
      birth_date: "1978-12-01",
      gender: "ذكر",
      phone: "07705554433",
      first_visit: "2024-06-20",
      primary_doctor: "د. لمياء حسن",
    },
  ];

  const sessions = [
    {
      id: "s1",
      patient_id: "p1",
      date: "2024-01-15",
      time: "10:30",
      session_type: "فحص أولي",
      symptoms: "ألم في الضرس الخلفي، حساسية للبارد",
      diagnosis: "تسوس عميق في الضرس 36",
      procedures: "حشو مركب + أشعة حول الذروة",
      doctor_name: "د. لمياء حسن",
      assistants: "",
      xray_label: "أشعة حول الذروة",
      has_xray: 1,
      xray_stored_name: null,
    },
    {
      id: "s2",
      patient_id: "p1",
      date: "2024-03-10",
      time: "09:00",
      session_type: "متابعة",
      symptoms: "لا أعراض، فحص دوري",
      diagnosis: "التهاب دواعم سن خفيف",
      procedures: "تنظيف عميق + تلميع",
      doctor_name: "د. علي كاظم",
      assistants: "زينب (مساعدة)",
      xray_label: null,
      has_xray: 0,
      xray_stored_name: null,
    },
    {
      id: "s3",
      patient_id: "p1",
      date: "2024-08-22",
      time: "14:00",
      session_type: "طارئ",
      symptoms: "تورم باللثة، ألم شديد ليلاً",
      diagnosis: "خراج حول الذروة",
      procedures: "تصريف خراج، مضاد حيوي، أشعة بانورامية",
      doctor_name: "د. لمياء حسن",
      assistants: "نور، سجاد",
      xray_label: "بانورامية",
      has_xray: 1,
      xray_stored_name: null,
    },
  ];

  const tx = db.transaction(() => {
    for (const p of patients) insP.run(p);
    for (const s of sessions) insS.run(s);
  });
  tx();
}

seedIfEmpty();

const upload = multer({
  storage: multer.diskStorage({
    destination: uploadDir,
    filename(_req, file, cb) {
      const ext = path.extname(file.originalname || "") || ".bin";
      cb(null, `${Date.now()}-${randomBytes(8).toString("hex")}${ext}`);
    },
  }),
  limits: { fileSize: 15 * 1024 * 1024 },
});

const app = express();
app.use(cors());
app.use(express.json({ limit: "2mb" }));

app.use("/uploads", express.static(uploadDir));

app.get("/api/health", (_req, res) => {
  res.json({ ok: true });
});

app.get("/api/patients", (_req, res) => {
  const rows = db.prepare("SELECT * FROM patients ORDER BY full_name").all();
  res.json(rows.map(patientRow));
});

app.post("/api/patients", (req, res) => {
  const b = req.body;
  const id = randomUUID();
  db.prepare(
    `INSERT INTO patients (id, full_name, birth_date, gender, phone, first_visit, primary_doctor)
     VALUES (?, ?, ?, ?, ?, ?, ?)`
  ).run(
    id,
    b.fullName,
    b.birthDate,
    b.gender,
    b.phone,
    b.firstVisit,
    b.primaryDoctor
  );
  const row = db.prepare("SELECT * FROM patients WHERE id = ?").get(id);
  res.status(201).json(patientRow(row));
});

app.put("/api/patients/:id", (req, res) => {
  const b = req.body;
  const r = db
    .prepare(
      `UPDATE patients SET full_name=?, birth_date=?, gender=?, phone=?, first_visit=?, primary_doctor=?
       WHERE id=?`
    )
    .run(b.fullName, b.birthDate, b.gender, b.phone, b.firstVisit, b.primaryDoctor, req.params.id);
  if (r.changes === 0) return res.status(404).json({ error: "not found" });
  const row = db.prepare("SELECT * FROM patients WHERE id = ?").get(req.params.id);
  res.json(patientRow(row));
});

app.get("/api/sessions", (_req, res) => {
  const rows = db.prepare(`SELECT * FROM sessions ORDER BY date, time`).all();
  res.json(rows.map(sessionRow));
});

function unlinkXray(storedName) {
  if (!storedName) return;
  const fp = path.join(uploadDir, storedName);
  try {
    if (fs.existsSync(fp)) fs.unlinkSync(fp);
  } catch {
    /* ignore */
  }
}

function createSessionHandler(req, res) {
  try {
    const p = parseSessionBody(req);
    if (!p.patientId || !p.date || !p.time || !p.sessionType || !p.doctorName) {
      return res.status(400).json({ error: "missing fields" });
    }
    const id = randomUUID();
    let stored = null;
    if (req.file) {
      stored = req.file.filename;
      p.hasXray = true;
    }
    db.prepare(
      `INSERT INTO sessions (id, patient_id, date, time, session_type, symptoms, diagnosis, procedures,
        doctor_name, assistants, xray_label, has_xray, xray_stored_name)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
    ).run(
      id,
      p.patientId,
      p.date,
      p.time,
      p.sessionType,
      p.symptoms,
      p.diagnosis,
      p.procedures,
      p.doctorName,
      p.assistants,
      p.xrayLabel,
      p.hasXray ? 1 : 0,
      stored
    );
    const row = db.prepare("SELECT * FROM sessions WHERE id = ?").get(id);
    res.status(201).json(sessionRow(row));
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: String(e.message) });
  }
}

app.post(
  "/api/sessions",
  (req, res, next) => {
    const ct = req.headers["content-type"] || "";
    if (ct.includes("multipart/form-data")) {
      upload.single("xray")(req, res, next);
    } else {
      next();
    }
  },
  createSessionHandler
);

app.put(
  "/api/sessions/:id",
  (req, res, next) => {
    const ct = req.headers["content-type"] || "";
    if (ct.includes("multipart/form-data")) {
      upload.single("xray")(req, res, next);
    } else {
      next();
    }
  },
  (req, res) => {
    try {
      const prev = db.prepare("SELECT * FROM sessions WHERE id = ?").get(req.params.id);
      if (!prev) return res.status(404).json({ error: "not found" });

      const p = parseSessionBody(req);
      let stored = prev.xray_stored_name;
      if (req.file) {
        unlinkXray(prev.xray_stored_name);
        stored = req.file.filename;
        p.hasXray = true;
      } else if (!p.hasXray) {
        unlinkXray(prev.xray_stored_name);
        stored = null;
      }

      db.prepare(
        `UPDATE sessions SET patient_id=?, date=?, time=?, session_type=?, symptoms=?, diagnosis=?,
          procedures=?, doctor_name=?, assistants=?, xray_label=?, has_xray=?, xray_stored_name=?
         WHERE id=?`
      ).run(
        p.patientId,
        p.date,
        p.time,
        p.sessionType,
        p.symptoms,
        p.diagnosis,
        p.procedures,
        p.doctorName,
        p.assistants,
        p.xrayLabel,
        p.hasXray ? 1 : 0,
        stored,
        req.params.id
      );
      const row = db.prepare("SELECT * FROM sessions WHERE id = ?").get(req.params.id);
      res.json(sessionRow(row));
    } catch (e) {
      console.error(e);
      res.status(500).json({ error: String(e.message) });
    }
  }
);

app.delete("/api/sessions/:id", (req, res) => {
  const prev = db.prepare("SELECT * FROM sessions WHERE id = ?").get(req.params.id);
  if (!prev) return res.status(404).json({ error: "not found" });
  unlinkXray(prev.xray_stored_name);
  db.prepare("DELETE FROM sessions WHERE id = ?").run(req.params.id);
  res.status(204).end();
});

const PORT = Number(process.env.PORT) || 4000;
const distPath = path.join(projectRoot, "dist");

if (fs.existsSync(distPath)) {
  app.use(express.static(distPath));
  app.get(/^(?!\/api)(?!\/uploads).*/, (_req, res) => {
    res.sendFile(path.join(distPath, "index.html"));
  });
}

app.listen(PORT, () => {
  console.log(`تطبيق عيادة الأسنان — API http://localhost:${PORT}`);
  if (fs.existsSync(distPath)) {
    console.log(`واجهة ثابتة: ${distPath}`);
  }
});
