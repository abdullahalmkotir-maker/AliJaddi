import { useState, type FormEvent } from "react";
import { DOCTORS } from "../mock";
import type { Gender, Patient } from "../types";

export function PatientEditModal({
  patient,
  onSave,
  onClose,
}: {
  patient: Patient;
  onSave: (p: Patient) => void | Promise<void>;
  onClose: () => void;
}) {
  const [fullName, setFullName] = useState(patient.fullName);
  const [birthDate, setBirthDate] = useState(patient.birthDate);
  const [gender, setGender] = useState<Gender>(patient.gender);
  const [phone, setPhone] = useState(patient.phone);
  const [firstVisit, setFirstVisit] = useState(patient.firstVisit);
  const [primaryDoctor, setPrimaryDoctor] = useState(patient.primaryDoctor);

  async function submit(e: FormEvent) {
    e.preventDefault();
    await onSave({
      ...patient,
      fullName,
      birthDate,
      gender,
      phone,
      firstVisit,
      primaryDoctor,
    });
  }

  return (
    <div className="modal-overlay" role="presentation" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>تعديل بيانات المريض</h2>
        <form className="modal-body form-grid" onSubmit={(e) => void submit(e)}>
          <div className="form-field">
            <label>الاسم الكامل</label>
            <input value={fullName} onChange={(e) => setFullName(e.target.value)} required />
          </div>
          <div className="form-field">
            <label>تاريخ الميلاد</label>
            <input
              type="date"
              value={birthDate}
              onChange={(e) => setBirthDate(e.target.value)}
              required
            />
          </div>
          <div className="form-field">
            <label>الجنس</label>
            <select value={gender} onChange={(e) => setGender(e.target.value as Gender)}>
              <option value="ذكر">ذكر</option>
              <option value="أنثى">أنثى</option>
            </select>
          </div>
          <div className="form-field">
            <label>الهاتف</label>
            <input value={phone} onChange={(e) => setPhone(e.target.value)} required />
          </div>
          <div className="form-field">
            <label>تاريخ أول زيارة</label>
            <input
              type="date"
              value={firstVisit}
              onChange={(e) => setFirstVisit(e.target.value)}
              required
            />
          </div>
          <div className="form-field">
            <label>الطبيب الأساسي</label>
            <select value={primaryDoctor} onChange={(e) => setPrimaryDoctor(e.target.value)}>
              {DOCTORS.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </div>
          <div className="modal-actions" style={{ borderTop: "none", padding: "1rem 0 0" }}>
            <button type="button" className="btn" onClick={onClose}>
              إلغاء
            </button>
            <button type="submit" className="btn btn-primary">
              حفظ
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export function PatientAddModal({
  onSave,
  onClose,
}: {
  onSave: (p: Omit<Patient, "id">) => void | Promise<void>;
  onClose: () => void;
}) {
  const today = new Date().toISOString().slice(0, 10);
  const [fullName, setFullName] = useState("");
  const [birthDate, setBirthDate] = useState("1990-01-01");
  const [gender, setGender] = useState<Gender>("ذكر");
  const [phone, setPhone] = useState("");
  const [firstVisit, setFirstVisit] = useState(today);
  const [primaryDoctor, setPrimaryDoctor] = useState<string>(DOCTORS[0]);

  async function submit(e: FormEvent) {
    e.preventDefault();
    await onSave({
      fullName,
      birthDate,
      gender,
      phone: phone || "—",
      firstVisit,
      primaryDoctor,
    });
  }

  return (
    <div className="modal-overlay" role="presentation" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>إضافة مريض جديد</h2>
        <form className="modal-body form-grid" onSubmit={(e) => void submit(e)}>
          <div className="form-field">
            <label>الاسم الكامل</label>
            <input value={fullName} onChange={(e) => setFullName(e.target.value)} required />
          </div>
          <div className="form-field">
            <label>تاريخ الميلاد</label>
            <input
              type="date"
              value={birthDate}
              onChange={(e) => setBirthDate(e.target.value)}
              required
            />
          </div>
          <div className="form-field">
            <label>الجنس</label>
            <select value={gender} onChange={(e) => setGender(e.target.value as Gender)}>
              <option value="ذكر">ذكر</option>
              <option value="أنثى">أنثى</option>
            </select>
          </div>
          <div className="form-field">
            <label>الهاتف</label>
            <input
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="مثال: 07901234567"
            />
          </div>
          <div className="form-field">
            <label>تاريخ أول زيارة</label>
            <input
              type="date"
              value={firstVisit}
              onChange={(e) => setFirstVisit(e.target.value)}
              required
            />
          </div>
          <div className="form-field">
            <label>الطبيب الأساسي</label>
            <select value={primaryDoctor} onChange={(e) => setPrimaryDoctor(e.target.value)}>
              {DOCTORS.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </div>
          <div className="modal-actions" style={{ borderTop: "none", padding: "1rem 0 0" }}>
            <button type="button" className="btn" onClick={onClose}>
              إلغاء
            </button>
            <button type="submit" className="btn btn-primary">
              حفظ
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
