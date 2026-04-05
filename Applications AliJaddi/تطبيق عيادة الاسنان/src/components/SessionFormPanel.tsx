import { useState, type FormEvent } from "react";
import { ASSISTANTS_OPTIONS, DOCTORS, PROCEDURE_TAGS, SESSION_TYPES } from "../mock";
import type { SessionRecord } from "../types";

export function SessionFormPanel({
  mode,
  patientId,
  patientName,
  existing,
  onSave,
  onCancel,
}: {
  mode: "add" | "edit";
  patientId: string;
  patientName: string;
  existing: SessionRecord | null;
  onSave: (
    r: Omit<SessionRecord, "id" | "xrayPublicUrl">,
    xrayFile: File | null
  ) => Promise<void>;
  onCancel: () => void;
}) {
  const today = new Date().toISOString().slice(0, 10);
  const [date, setDate] = useState(existing?.date ?? today);
  const [time, setTime] = useState(existing?.time ?? "14:00");
  const [sessionType, setSessionType] = useState(existing?.sessionType ?? SESSION_TYPES[0]);
  const [symptoms, setSymptoms] = useState(existing?.symptoms ?? "");
  const [diagnosis, setDiagnosis] = useState(existing?.diagnosis ?? "");
  const [procedures, setProcedures] = useState(existing?.procedures ?? "");
  const [selectedTags, setSelectedTags] = useState<Set<string>>(() => {
    const s = new Set<string>();
    if (existing?.procedures) {
      PROCEDURE_TAGS.forEach((t) => {
        if (existing.procedures.includes(t)) s.add(t);
      });
    }
    return s;
  });
  const [doctorName, setDoctorName] = useState(existing?.doctorName ?? DOCTORS[0]);
  const [assistantPick, setAssistantPick] = useState<string>(ASSISTANTS_OPTIONS[0]);
  const [assistantsList, setAssistantsList] = useState<string[]>(() => {
    if (!existing?.assistants) return [];
    return existing.assistants.split("،").map((x) => x.trim()).filter(Boolean);
  });
  const [hasXray, setHasXray] = useState(existing?.hasXray ?? false);
  const [xrayLabel, setXrayLabel] = useState(existing?.xrayLabel ?? "");
  const [xrayFileName, setXrayFileName] = useState("");
  const [xrayFile, setXrayFile] = useState<File | null>(null);
  const [saving, setSaving] = useState(false);

  function toggleTag(tag: string) {
    setSelectedTags((prev) => {
      const next = new Set(prev);
      if (next.has(tag)) next.delete(tag);
      else next.add(tag);
      return next;
    });
  }

  function addAssistant() {
    if (!assistantPick) return;
    if (assistantsList.includes(assistantPick)) return;
    setAssistantsList((a) => [...a, assistantPick]);
  }

  async function submit(e: FormEvent) {
    e.preventDefault();
    const fromTags = [...selectedTags].join(" + ");
    const extra = procedures.trim();
    const proceduresFinal = [fromTags, extra].filter(Boolean).join(" — ");
    const payload: Omit<SessionRecord, "id" | "xrayPublicUrl"> = {
      patientId,
      date,
      time,
      sessionType,
      symptoms,
      diagnosis,
      procedures: proceduresFinal,
      doctorName,
      assistants: assistantsList.join("، "),
      xrayLabel:
        hasXray && xrayLabel.trim()
          ? xrayLabel.trim()
          : xrayFileName
            ? xrayFileName
            : null,
      hasXray: hasXray || Boolean(xrayFile) || Boolean(xrayFileName),
    };
    setSaving(true);
    try {
      await onSave(payload, xrayFile);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="panel" style={{ marginTop: "1rem" }}>
      <h2 className="panel-title">
        {mode === "add" ? "إضافة جلسة جديدة" : "تعديل الجلسة"} — {patientName}
      </h2>
      <div className="panel-body">
        <form className="form-grid" onSubmit={submit}>
          <details className="form-collapse" open>
            <summary>الموعد</summary>
            <div className="form-collapse-body">
              <div className="form-row two">
                <div className="form-field">
                  <label htmlFor="sess-date">تاريخ الجلسة</label>
                  <input
                    id="sess-date"
                    type="date"
                    value={date}
                    onChange={(e) => setDate(e.target.value)}
                    required
                  />
                </div>
                <div className="form-field">
                  <label htmlFor="sess-time">الوقت</label>
                  <input
                    id="sess-time"
                    type="time"
                    value={time}
                    onChange={(e) => setTime(e.target.value)}
                    required
                  />
                </div>
              </div>
              <div className="form-field">
                <label htmlFor="sess-type">نوع الجلسة</label>
                <select
                  id="sess-type"
                  value={sessionType}
                  onChange={(e) => setSessionType(e.target.value)}
                >
                  {SESSION_TYPES.map((t) => (
                    <option key={t} value={t}>
                      {t}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </details>

          <details className="form-collapse" open>
            <summary>السريري</summary>
            <div className="form-collapse-body">
              <div className="form-field">
                <label htmlFor="sess-symptoms">الأعراض</label>
                <textarea
                  id="sess-symptoms"
                  value={symptoms}
                  onChange={(e) => setSymptoms(e.target.value)}
                  placeholder="وصف الأعراض…"
                />
              </div>
              <div className="form-field">
                <label htmlFor="sess-diagnosis">التشخيص</label>
                <textarea
                  id="sess-diagnosis"
                  value={diagnosis}
                  onChange={(e) => setDiagnosis(e.target.value)}
                  placeholder="التشخيص الطبي…"
                />
              </div>
              <div className="form-field">
                <span className="form-field-label" id="sess-proc-chips-label">
                  الإجراءات (اختيار سريع)
                </span>
                <div className="procedure-chips" role="group" aria-labelledby="sess-proc-chips-label">
                  {PROCEDURE_TAGS.map((t) => (
                    <button
                      key={t}
                      type="button"
                      className={selectedTags.has(t) ? "selected" : ""}
                      onClick={() => toggleTag(t)}
                    >
                      {t}
                    </button>
                  ))}
                </div>
              </div>
              <div className="form-field">
                <label htmlFor="sess-procedures">نص الإجراءات</label>
                <textarea
                  id="sess-procedures"
                  value={procedures}
                  onChange={(e) => setProcedures(e.target.value)}
                  placeholder="تفاصيل إضافية للإجراءات…"
                />
              </div>
            </div>
          </details>

          <details className="form-collapse">
            <summary>الفريق</summary>
            <div className="form-collapse-body">
              <div className="form-field">
                <label htmlFor="sess-doctor">الطبيب المعالج</label>
                <select
                  id="sess-doctor"
                  value={doctorName}
                  onChange={(e) => setDoctorName(e.target.value)}
                >
                  {DOCTORS.map((d) => (
                    <option key={d} value={d}>
                      {d}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-field">
                <span className="form-field-label" id="sess-assist-label">
                  المساعدون
                </span>
                <div className="assistants-row" role="group" aria-labelledby="sess-assist-label">
                  <select
                    aria-label="اختيار مساعد"
                    value={assistantPick}
                    onChange={(e) => setAssistantPick(e.target.value)}
                  >
                    {ASSISTANTS_OPTIONS.map((a) => (
                      <option key={a} value={a}>
                        {a}
                      </option>
                    ))}
                  </select>
                  <button type="button" className="btn" onClick={addAssistant}>
                    + إضافة مساعد آخر
                  </button>
                </div>
                {assistantsList.length > 0 ? (
                  <p style={{ margin: "0.5rem 0 0", fontSize: "0.9rem" }}>
                    {assistantsList.join("، ")}
                  </p>
                ) : null}
              </div>
            </div>
          </details>

          <details className="form-collapse">
            <summary>الأشعة</summary>
            <div className="form-collapse-body">
              <div className="form-field">
                <label
                  htmlFor="sess-xray-check"
                  style={{ display: "flex", alignItems: "center", cursor: "pointer" }}
                >
                  <input
                    id="sess-xray-check"
                    type="checkbox"
                    checked={hasXray}
                    onChange={(e) => setHasXray(e.target.checked)}
                    style={{ marginInlineEnd: 8 }}
                  />
                  توجد صورة شعاعية
                </label>
                {hasXray ? (
                  <>
                    <label htmlFor="sess-xray-desc" style={{ marginTop: 8, display: "block" }}>
                      وصف نوع الأشعة
                    </label>
                    <input
                      id="sess-xray-desc"
                      placeholder="مثال: بانورامية"
                      value={xrayLabel}
                      onChange={(e) => setXrayLabel(e.target.value)}
                    />
                    <label htmlFor="sess-xray-file" style={{ display: "block", marginTop: 8 }}>
                      رفع ملف (اختياري)
                    </label>
                    <input
                      id="sess-xray-file"
                      type="file"
                      accept="image/*,.pdf"
                      style={{ display: "block", marginTop: 4 }}
                      onChange={(e) => {
                        const f = e.target.files?.[0] ?? null;
                        setXrayFile(f);
                        setXrayFileName(f?.name ?? "");
                      }}
                    />
                  </>
                ) : null}
              </div>
            </div>
          </details>

          <div className="actions-row" style={{ marginTop: 0, borderTop: "none", paddingTop: 0 }}>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? "جاري الحفظ…" : "حفظ"}
            </button>
            <button type="button" className="btn" onClick={onCancel} disabled={saving}>
              إلغاء
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
