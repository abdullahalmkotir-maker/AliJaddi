import type { Patient, SessionRecord } from "./types";

async function handle<T>(r: Response): Promise<T> {
  if (!r.ok) {
    const t = await r.text();
    throw new Error(t || r.statusText || "طلب غير ناجح");
  }
  if (r.status === 204) return undefined as T;
  return r.json() as Promise<T>;
}

export async function fetchPatients(): Promise<Patient[]> {
  const r = await fetch("/api/patients");
  return handle<Patient[]>(r);
}

export async function fetchSessions(): Promise<SessionRecord[]> {
  const r = await fetch("/api/sessions");
  return handle<SessionRecord[]>(r);
}

export async function createPatient(p: Omit<Patient, "id">): Promise<Patient> {
  const r = await fetch("/api/patients", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(p),
  });
  return handle<Patient>(r);
}

export async function updatePatient(p: Patient): Promise<Patient> {
  const r = await fetch(`/api/patients/${encodeURIComponent(p.id)}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(p),
  });
  return handle<Patient>(r);
}

export type SessionWriteBody = Omit<SessionRecord, "id" | "xrayPublicUrl">;

function appendSessionFields(fd: FormData, data: SessionWriteBody) {
  fd.append("patientId", data.patientId);
  fd.append("date", data.date);
  fd.append("time", data.time);
  fd.append("sessionType", data.sessionType);
  fd.append("symptoms", data.symptoms);
  fd.append("diagnosis", data.diagnosis);
  fd.append("procedures", data.procedures);
  fd.append("doctorName", data.doctorName);
  fd.append("assistants", data.assistants);
  fd.append("hasXray", data.hasXray ? "1" : "0");
  if (data.xrayLabel) fd.append("xrayLabel", data.xrayLabel);
}

export async function createSession(
  data: SessionWriteBody,
  xrayFile: File | null
): Promise<SessionRecord> {
  if (xrayFile) {
    const fd = new FormData();
    appendSessionFields(fd, data);
    fd.append("xray", xrayFile);
    const r = await fetch("/api/sessions", { method: "POST", body: fd });
    return handle<SessionRecord>(r);
  }
  const r = await fetch("/api/sessions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return handle<SessionRecord>(r);
}

export async function updateSession(
  id: string,
  data: SessionWriteBody,
  xrayFile: File | null
): Promise<SessionRecord> {
  if (xrayFile) {
    const fd = new FormData();
    appendSessionFields(fd, data);
    fd.append("xray", xrayFile);
    const r = await fetch(`/api/sessions/${encodeURIComponent(id)}`, {
      method: "PUT",
      body: fd,
    });
    return handle<SessionRecord>(r);
  }
  const r = await fetch(`/api/sessions/${encodeURIComponent(id)}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return handle<SessionRecord>(r);
}

export async function deleteSession(id: string): Promise<void> {
  const r = await fetch(`/api/sessions/${encodeURIComponent(id)}`, { method: "DELETE" });
  await handle<void>(r);
}
