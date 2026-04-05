import { useCallback, useEffect, useMemo, useState } from "react";
import {
  createPatient,
  createSession,
  deleteSession as apiDeleteSession,
  fetchPatients,
  fetchSessions,
  updatePatient,
  updateSession,
} from "./api";
import { PatientAddModal, PatientEditModal } from "./components/PatientModals";
import { PatientProfilePanel } from "./components/PatientProfilePanel";
import { SessionFormPanel } from "./components/SessionFormPanel";
import { SessionsPanel } from "./components/SessionsPanel";
import { XrayPreviewContent } from "./components/XrayPreviewContent";
import { CLINIC_REGION, DOCTORS } from "./mock";
import type { Patient, SessionRecord, SessionFilter } from "./types";
import { formatDateAr, formatTimeAr } from "./utils";

type MainView = "profile" | "sessions";

type XrayPreview = { label: string; url: string | null };

export default function App() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [sessions, setSessions] = useState<SessionRecord[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [mainView, setMainView] = useState<MainView>("profile");
  const [sessionFilter, setSessionFilter] = useState<SessionFilter>("all");
  const [filterDoctor, setFilterDoctor] = useState<(typeof DOCTORS)[number]>(DOCTORS[0]);
  const [filterProcedure, setFilterProcedure] = useState<string>("حشو");

  const [editPatientOpen, setEditPatientOpen] = useState(false);
  const [addPatientOpen, setAddPatientOpen] = useState(false);
  const [sessionFormMode, setSessionFormMode] = useState<"add" | "edit" | null>(null);
  const [editingSessionId, setEditingSessionId] = useState<string | null>(null);
  const [xrayPreview, setXrayPreview] = useState<XrayPreview | null>(null);

  const refreshAll = useCallback(async () => {
    setLoadError(null);
    setLoading(true);
    try {
      const [p, s] = await Promise.all([fetchPatients(), fetchSessions()]);
      setPatients(p);
      setSessions(s);
      setSelectedId((prev) => {
        if (prev && p.some((x) => x.id === prev)) return prev;
        return p[0]?.id ?? null;
      });
    } catch (e) {
      setLoadError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refreshAll();
  }, [refreshAll]);

  const selectedPatient = useMemo(
    () => patients.find((p) => p.id === selectedId) ?? null,
    [patients, selectedId]
  );

  const patientSessions = useMemo(() => {
    if (!selectedId) return [];
    let list = sessions.filter((s) => s.patientId === selectedId);
    if (sessionFilter === "doctor") {
      list = list.filter((s) => s.doctorName === filterDoctor);
    }
    if (sessionFilter === "procedure") {
      list = list.filter((s) => s.procedures.includes(filterProcedure));
    }
    return [...list].sort(
      (a, b) =>
        new Date(a.date + "T" + a.time).getTime() - new Date(b.date + "T" + b.time).getTime()
    );
  }, [sessions, selectedId, sessionFilter, filterDoctor, filterProcedure]);

  const [search, setSearch] = useState("");

  const filteredPatientList = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return patients;
    return patients.filter((p) => p.fullName.toLowerCase().includes(q));
  }, [patients, search]);

  function goSessions() {
    setMainView("sessions");
  }

  function printReport() {
    if (!selectedPatient) return;
    const lines = [
      `تقرير الجلسات – ${selectedPatient.fullName}`,
      `عيادة أسنان – ${CLINIC_REGION}`,
      `تاريخ الطباعة: ${formatDateAr(new Date().toISOString().slice(0, 10))}`,
      "",
      ...patientSessions.map((s, i) => {
        return [
          `— الجلسة ${i + 1} – ${formatDateAr(s.date)} ${formatTimeAr(s.time)}`,
          `  النوع: ${s.sessionType}`,
          `  الأعراض: ${s.symptoms}`,
          `  التشخيص: ${s.diagnosis}`,
          `  الإجراءات: ${s.procedures}`,
          `  الطبيب: ${s.doctorName}`,
          "",
        ].join("\n");
      }),
    ];
    const w = window.open("", "_blank");
    if (w) {
      w.document.write(
        `<pre dir="rtl" style="font-family:inherit;font-size:14px;padding:1rem">${lines.join(
          "\n"
        )}</pre>`
      );
      w.document.close();
      w.print();
    }
  }

  async function deleteSession(id: string) {
    if (!confirm("حذف هذه الجلسة نهائياً؟")) return;
    try {
      await apiDeleteSession(id);
      setSessions(await fetchSessions());
    } catch (e) {
      alert(e instanceof Error ? e.message : String(e));
    }
  }

  if (loading && patients.length === 0 && !loadError) {
    return (
      <div className="eng-state-screen">
        <div className="eng-state-panel">
          <div className="eng-spinner" aria-hidden />
          <div className="eng-status-label">sync</div>
          <p>جاري الاتصال بالخادم وتحميل البيانات…</p>
          <p className="eng-muted">
            نفّذ من هذا المجلد: <code>npm install</code> ثم <code>npm run dev</code>
          </p>
        </div>
      </div>
    );
  }

  if (loadError && patients.length === 0) {
    return (
      <div className="eng-state-screen">
        <div className="eng-state-panel">
          <div className="eng-status-label">خطأ اتصال</div>
          <p>تعذر الاتصال بالخادم.</p>
          <p className="eng-muted">{loadError}</p>
          <p className="eng-muted">
            من مجلد «تطبيق عيادة الاسنان»: <code>npm run dev</code>
          </p>
          <button type="button" className="btn btn-primary" onClick={() => void refreshAll()}>
            إعادة المحاولة
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="app-shell eng-app">
      <aside className="eng-sidebar">
        <h1 className="eng-brand eng-brand-ar">تطبيق عيادة الأسنان</h1>
        <p className="eng-brand-sub" style={{ margin: "-0.35rem 0 0", paddingInlineStart: "0.65rem" }}>
          {CLINIC_REGION} — قائمة المرضى
        </p>
        <input
          className="patient-search"
          placeholder="بحث بالاسم…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <ul className="patient-list">
          {filteredPatientList.map((p) => (
            <li key={p.id}>
              <button
                type="button"
                className={p.id === selectedId ? "active" : ""}
                onClick={() => {
                  setSelectedId(p.id);
                  setMainView("profile");
                }}
              >
                {p.fullName}
              </button>
            </li>
          ))}
        </ul>
        <button type="button" className="add-patient-btn" onClick={() => setAddPatientOpen(true)}>
          + إضافة مريض جديد
        </button>
      </aside>

      <main className="eng-workspace">
        {!selectedPatient ? (
          <div className="panel">
            <div className="panel-body empty-hint">
              <div className="eng-status-label" style={{ marginBottom: "0.75rem" }}>
                لا يوجد اختيار
              </div>
              اختر مريضاً من القائمة الجانبية أو استخدم «إضافة مريض جديد».
            </div>
          </div>
        ) : (
          <>
            {mainView === "profile" && (
              <PatientProfilePanel
                patient={selectedPatient}
                onEdit={() => setEditPatientOpen(true)}
                onSessions={goSessions}
              />
            )}
            {mainView === "sessions" && (
              <>
                <SessionsPanel
                  patientName={selectedPatient.fullName}
                  sessions={patientSessions}
                  sessionFilter={sessionFilter}
                  setSessionFilter={setSessionFilter}
                  filterDoctor={filterDoctor}
                  setFilterDoctor={setFilterDoctor}
                  filterProcedure={filterProcedure}
                  setFilterProcedure={setFilterProcedure}
                  onBack={() => setMainView("profile")}
                  onAddSession={() => {
                    setSessionFormMode("add");
                    setEditingSessionId(null);
                  }}
                  onEditSession={(id) => {
                    setSessionFormMode("edit");
                    setEditingSessionId(id);
                  }}
                  onDeleteSession={deleteSession}
                  onPrint={printReport}
                  onViewXray={(s) =>
                    setXrayPreview({
                      label: s.xrayLabel?.trim() || "صورة شعاعية",
                      url: s.xrayPublicUrl ?? null,
                    })
                  }
                />
                {sessionFormMode && (
                  <SessionFormPanel
                    key={`${sessionFormMode}-${editingSessionId ?? "new"}`}
                    mode={sessionFormMode}
                    patientId={selectedPatient.id}
                    patientName={selectedPatient.fullName}
                    existing={
                      sessionFormMode === "edit" && editingSessionId
                        ? sessions.find((s) => s.id === editingSessionId) ?? null
                        : null
                    }
                    onSave={async (rec, xrayFile) => {
                      try {
                        if (sessionFormMode === "add") {
                          await createSession(rec, xrayFile);
                        } else if (editingSessionId) {
                          await updateSession(editingSessionId, rec, xrayFile);
                        }
                        setSessions(await fetchSessions());
                        setSessionFormMode(null);
                        setEditingSessionId(null);
                      } catch (e) {
                        alert(e instanceof Error ? e.message : String(e));
                      }
                    }}
                    onCancel={() => {
                      setSessionFormMode(null);
                      setEditingSessionId(null);
                    }}
                  />
                )}
              </>
            )}
          </>
        )}
      </main>

      {editPatientOpen && selectedPatient && (
        <PatientEditModal
          patient={selectedPatient}
          onSave={async (updated) => {
            try {
              const saved = await updatePatient(updated);
              setPatients((list) => list.map((p) => (p.id === saved.id ? saved : p)));
              setEditPatientOpen(false);
            } catch (e) {
              alert(e instanceof Error ? e.message : String(e));
            }
          }}
          onClose={() => setEditPatientOpen(false)}
        />
      )}

      {addPatientOpen && (
        <PatientAddModal
          onSave={async (data) => {
            try {
              const p = await createPatient(data);
              setPatients((list) => [...list, p]);
              setSelectedId(p.id);
              setAddPatientOpen(false);
              setMainView("profile");
            } catch (e) {
              alert(e instanceof Error ? e.message : String(e));
            }
          }}
          onClose={() => setAddPatientOpen(false)}
        />
      )}

      {xrayPreview !== null && (
        <div className="modal-overlay" role="presentation" onClick={() => setXrayPreview(null)}>
          <div
            className="modal eng-modal-wide"
            role="dialog"
            aria-labelledby="xray-title"
            onClick={(e) => e.stopPropagation()}
          >
            <h2 id="xray-title">معاينة الصورة الشعاعية</h2>
            <div className="modal-body">
              <p style={{ margin: 0, color: "var(--muted)" }}>{xrayPreview.label}</p>
              <XrayPreviewContent url={xrayPreview.url} label={xrayPreview.label} />
            </div>
            <div className="modal-actions">
              <button type="button" className="btn" onClick={() => setXrayPreview(null)}>
                إغلاق
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
