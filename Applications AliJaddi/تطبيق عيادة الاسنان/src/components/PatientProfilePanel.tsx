import { CLINIC_REGION } from "../mock";
import type { Patient } from "../types";
import { calcAge, formatDateAr } from "../utils";

export function PatientProfilePanel({
  patient,
  onEdit,
  onSessions,
}: {
  patient: Patient;
  onEdit: () => void;
  onSessions: () => void;
}) {
  const initial = patient.fullName.trim().charAt(0) || "؟";
  return (
    <div className="panel">
      <h2 className="panel-title">تطبيق عيادة الأسنان – ملف المريض · {CLINIC_REGION}</h2>
      <div className="panel-body">
        <div className="avatar-row">
          <div className="avatar" aria-hidden>
            {initial}
          </div>
          <div className="field-grid two" style={{ flex: 1 }}>
            <div className="field">
              <label>الاسم الكامل</label>
              <span className="value">{patient.fullName}</span>
            </div>
            <div className="field">
              <label>تاريخ الميلاد (العمر)</label>
              <span className="value">
                {formatDateAr(patient.birthDate)} (العمر: {calcAge(patient.birthDate)} سنة)
              </span>
            </div>
            <div className="field">
              <label>الجنس</label>
              <span className="value">{patient.gender}</span>
            </div>
            <div className="field">
              <label>رقم الهاتف</label>
              <span className="value">{patient.phone}</span>
            </div>
          </div>
        </div>
        <div className="section-label">معلومات العيادة</div>
        <div className="field-grid two">
          <div className="field">
            <label>تاريخ أول زيارة</label>
            <span className="value">{formatDateAr(patient.firstVisit)}</span>
          </div>
          <div className="field">
            <label>الطبيب المعالج الأساسي</label>
            <span className="value">{patient.primaryDoctor}</span>
          </div>
        </div>
        <div className="actions-row">
          <button type="button" className="btn btn-primary" onClick={onEdit}>
            تعديل المعلومات
          </button>
          <button type="button" className="btn" onClick={onSessions}>
            عرض تاريخ الجلسات
          </button>
        </div>
      </div>
    </div>
  );
}
