import { CLINIC_REGION, DOCTORS, PROCEDURE_TAGS } from "../mock";
import type { SessionRecord, SessionFilter } from "../types";
import { formatDateAr, formatTimeAr } from "../utils";

export function SessionsPanel({
  patientName,
  sessions,
  sessionFilter,
  setSessionFilter,
  filterDoctor,
  setFilterDoctor,
  filterProcedure,
  setFilterProcedure,
  onBack,
  onAddSession,
  onEditSession,
  onDeleteSession,
  onPrint,
  onViewXray,
}: {
  patientName: string;
  sessions: SessionRecord[];
  sessionFilter: SessionFilter;
  setSessionFilter: (f: SessionFilter) => void;
  filterDoctor: string;
  setFilterDoctor: (d: (typeof DOCTORS)[number]) => void;
  filterProcedure: string;
  setFilterProcedure: (p: string) => void;
  onBack: () => void;
  onAddSession: () => void;
  onEditSession: (id: string) => void;
  onDeleteSession: (id: string) => void;
  onPrint: () => void;
  onViewXray: (s: SessionRecord) => void;
}) {
  return (
    <div className="panel">
      <h2 className="panel-title">
        الجلسات السابقة للمريض: {patientName} · {CLINIC_REGION}
      </h2>
      <div className="panel-body">
        <div className="filter-bar">
          <span style={{ color: "var(--muted)", fontSize: "0.9rem" }}>فلتر:</span>
          <button
            type="button"
            className={`chip ${sessionFilter === "all" ? "active" : ""}`}
            onClick={() => setSessionFilter("all")}
          >
            كل الجلسات
          </button>
          <button
            type="button"
            className={`chip ${sessionFilter === "doctor" ? "active" : ""}`}
            onClick={() => setSessionFilter("doctor")}
          >
            حسب الطبيب
          </button>
          <button
            type="button"
            className={`chip ${sessionFilter === "procedure" ? "active" : ""}`}
            onClick={() => setSessionFilter("procedure")}
          >
            حسب الإجراء
          </button>
          {sessionFilter === "doctor" && (
            <select
              className="filter-select"
              value={filterDoctor}
              onChange={(e) => setFilterDoctor(e.target.value as (typeof DOCTORS)[number])}
            >
              {DOCTORS.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          )}
          {sessionFilter === "procedure" && (
            <select
              className="filter-select"
              value={filterProcedure}
              onChange={(e) => setFilterProcedure(e.target.value)}
            >
              {PROCEDURE_TAGS.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
              <option value="أشعة">أشعة</option>
              <option value="تلميع">تلميع</option>
            </select>
          )}
          <button type="button" className="btn" style={{ marginInlineStart: "auto" }} onClick={onBack}>
            ← ملف المريض
          </button>
        </div>

        {sessions.length === 0 ? (
          <p className="empty-hint">لا توجد جلسات مطابقة للفلتر.</p>
        ) : (
          sessions.map((s, idx) => (
            <article key={s.id} className="session-card">
              <h3>
                الجلسة رقم {idx + 1} – {formatDateAr(s.date)} {formatTimeAr(s.time)}
              </h3>
              <div className="session-inner">
                <dl>
                  <div>
                    <dt>نوع الجلسة</dt>
                    <dd>{s.sessionType}</dd>
                  </div>
                  <div>
                    <dt>الأعراض</dt>
                    <dd>{s.symptoms}</dd>
                  </div>
                  <div>
                    <dt>التشخيص</dt>
                    <dd>{s.diagnosis}</dd>
                  </div>
                  <div>
                    <dt>الإجراءات</dt>
                    <dd>{s.procedures}</dd>
                  </div>
                  <div>
                    <dt>الطبيب المعالج</dt>
                    <dd>{s.doctorName}</dd>
                  </div>
                  {s.assistants ? (
                    <div>
                      <dt>المساعدون</dt>
                      <dd>{s.assistants}</dd>
                    </div>
                  ) : null}
                  <div>
                    <dt>الصور الشعاعية</dt>
                    <dd>
                      {s.hasXray ? (
                        <button
                          type="button"
                          className="btn"
                          style={{ marginTop: 4 }}
                          onClick={() => onViewXray(s)}
                        >
                          عرض الصورة
                          {s.xrayLabel ? ` (${s.xrayLabel})` : ""}
                        </button>
                      ) : (
                        <span style={{ color: "var(--muted)" }}>لا توجد</span>
                      )}
                    </dd>
                  </div>
                </dl>
              </div>
              <div className="session-actions">
                <button type="button" className="btn" onClick={() => onEditSession(s.id)}>
                  تعديل
                </button>
                <button type="button" className="btn btn-danger" onClick={() => onDeleteSession(s.id)}>
                  حذف
                </button>
              </div>
            </article>
          ))
        )}

        <div className="actions-row">
          <button type="button" className="btn btn-primary" onClick={onAddSession}>
            إضافة جلسة جديدة
          </button>
          <button type="button" className="btn" onClick={onPrint}>
            طباعة التقرير
          </button>
        </div>
      </div>
    </div>
  );
}
