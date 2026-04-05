export type Gender = "ذكر" | "أنثى";

export interface Patient {
  id: string;
  fullName: string;
  birthDate: string;
  gender: Gender;
  phone: string;
  firstVisit: string;
  primaryDoctor: string;
}

export interface SessionRecord {
  id: string;
  patientId: string;
  date: string;
  time: string;
  sessionType: string;
  symptoms: string;
  diagnosis: string;
  procedures: string;
  doctorName: string;
  assistants: string;
  xrayLabel: string | null;
  hasXray: boolean;
  xrayPublicUrl?: string | null;
}

export type SessionFilter = "all" | "doctor" | "procedure";
