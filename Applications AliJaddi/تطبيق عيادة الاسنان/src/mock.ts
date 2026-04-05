import type { Patient, SessionRecord } from "./types";

export const DOCTORS = ["د. لمياء حسن", "د. علي كاظم", "د. رنا مهدي"] as const;
export const ASSISTANTS_OPTIONS = ["زينب (مساعدة)", "سجاد", "نور", "كرار"] as const;
export const CLINIC_REGION = "العراق";
export const SESSION_TYPES = [
  "فحص أولي",
  "متابعة",
  "طارئ",
  "تجميلي",
  "جراحة",
] as const;
export const PROCEDURE_TAGS = ["حشو", "خلع", "تنظيف", "تبييض", "أخرى"] as const;

export const initialPatients: Patient[] = [
  {
    id: "p1",
    fullName: "علي كريم الجبوري",
    birthDate: "1990-03-15",
    gender: "ذكر",
    phone: "07901234567",
    firstVisit: "2024-01-10",
    primaryDoctor: "د. لمياء حسن",
  },
  {
    id: "p2",
    fullName: "سارة طارق الدليمي",
    birthDate: "1985-07-22",
    gender: "أنثى",
    phone: "07809998877",
    firstVisit: "2023-11-05",
    primaryDoctor: "د. علي كاظم",
  },
  {
    id: "p3",
    fullName: "محمد فاضل العبيدي",
    birthDate: "1978-12-01",
    gender: "ذكر",
    phone: "07705554433",
    firstVisit: "2024-06-20",
    primaryDoctor: "د. لمياء حسن",
  },
];

export const initialSessions: SessionRecord[] = [
  {
    id: "s1",
    patientId: "p1",
    date: "2024-01-15",
    time: "10:30",
    sessionType: "فحص أولي",
    symptoms: "ألم في الضرس الخلفي، حساسية للبارد",
    diagnosis: "تسوس عميق في الضرس 36",
    procedures: "حشو مركب + أشعة حول الذروة",
    doctorName: "د. لمياء حسن",
    assistants: "",
    xrayLabel: "أشعة حول الذروة",
    hasXray: true,
  },
  {
    id: "s2",
    patientId: "p1",
    date: "2024-03-10",
    time: "09:00",
    sessionType: "متابعة",
    symptoms: "لا أعراض، فحص دوري",
    diagnosis: "التهاب دواعم سن خفيف",
    procedures: "تنظيف عميق + تلميع",
    doctorName: "د. علي كاظم",
    assistants: "زينب (مساعدة)",
    xrayLabel: null,
    hasXray: false,
  },
  {
    id: "s3",
    patientId: "p1",
    date: "2024-08-22",
    time: "14:00",
    sessionType: "طارئ",
    symptoms: "تورم باللثة، ألم شديد ليلاً",
    diagnosis: "خراج حول الذروة",
    procedures: "تصريف خراج، مضاد حيوي، أشعة بانورامية",
    doctorName: "د. لمياء حسن",
    assistants: "نور، سجاد",
    xrayLabel: "بانورامية",
    hasXray: true,
  },
];
