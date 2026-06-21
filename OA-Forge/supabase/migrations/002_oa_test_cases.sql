-- Test cases table + expanded seed (mirrors remote migration)

CREATE TABLE IF NOT EXISTS oa_test_cases (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  question_id UUID NOT NULL REFERENCES oa_questions(id) ON DELETE CASCADE,
  input_text TEXT NOT NULL,
  expected_output TEXT NOT NULL,
  is_sample BOOLEAN NOT NULL DEFAULT false,
  test_order INT NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE oa_test_cases ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "oa_test_cases_public_read" ON oa_test_cases;
CREATE POLICY "oa_test_cases_public_read" ON oa_test_cases FOR SELECT USING (true);

CREATE INDEX IF NOT EXISTS idx_oa_test_cases_question ON oa_test_cases(question_id);
