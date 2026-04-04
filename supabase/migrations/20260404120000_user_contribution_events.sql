-- أحداث مساهمة المستخدم (تغذية تدريب المساعدين) — اختياري لرفع النجوم من السحابة لاحقاً
CREATE TABLE IF NOT EXISTS core.user_contribution_events (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL DEFAULT auth.uid(),
  kind text NOT NULL,
  points int NOT NULL DEFAULT 1,
  meta jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE core.user_contribution_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY user_contribution_events_insert_own ON core.user_contribution_events
  FOR INSERT TO authenticated
  WITH CHECK (user_id = auth.uid());

CREATE POLICY user_contribution_events_select_own ON core.user_contribution_events
  FOR SELECT TO authenticated
  USING (user_id = auth.uid());
