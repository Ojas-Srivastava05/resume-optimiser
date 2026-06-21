-- OA Forge initial schema (applied to Supabase project mwvohdvtxwltzkyuboaz)
-- See README for table descriptions

CREATE TABLE IF NOT EXISTS oa_companies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS oa_roles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id UUID NOT NULL REFERENCES oa_companies(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  level TEXT NOT NULL DEFAULT 'intern',
  UNIQUE(company_id, title)
);

CREATE TABLE IF NOT EXISTS oa_questions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  difficulty TEXT NOT NULL,
  category TEXT NOT NULL,
  question_order INT NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS oa_question_occurrences (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  question_id UUID NOT NULL REFERENCES oa_questions(id) ON DELETE CASCADE,
  company_id UUID NOT NULL REFERENCES oa_companies(id) ON DELETE CASCADE,
  role_id UUID REFERENCES oa_roles(id) ON DELETE SET NULL,
  year INT NOT NULL,
  season TEXT,
  round_type TEXT NOT NULL DEFAULT 'oa',
  confidence_tier TEXT NOT NULL CHECK (confidence_tier IN ('A', 'B', 'C')),
  source_notes TEXT,
  source_url TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_oa_occurrence_unique
  ON oa_question_occurrences(question_id, company_id, year, season, round_type);

CREATE TABLE IF NOT EXISTS oa_templates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id UUID NOT NULL REFERENCES oa_companies(id) ON DELETE CASCADE,
  role_id UUID REFERENCES oa_roles(id) ON DELETE SET NULL,
  name TEXT NOT NULL,
  duration_minutes INT NOT NULL DEFAULT 90,
  num_questions INT NOT NULL DEFAULT 2,
  strict_tiers TEXT[] DEFAULT ARRAY['A','B'],
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_oa_templates_company_name
  ON oa_templates(company_id, name);

CREATE TABLE IF NOT EXISTS oa_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id UUID NOT NULL REFERENCES oa_companies(id) ON DELETE CASCADE,
  template_id UUID REFERENCES oa_templates(id) ON DELETE SET NULL,
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'completed', 'expired')),
  duration_minutes INT NOT NULL,
  started_at TIMESTAMPTZ DEFAULT now(),
  ended_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS oa_session_questions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID NOT NULL REFERENCES oa_sessions(id) ON DELETE CASCADE,
  question_id UUID NOT NULL REFERENCES oa_questions(id) ON DELETE CASCADE,
  question_order INT NOT NULL,
  verdict TEXT,
  completed_at TIMESTAMPTZ,
  UNIQUE(session_id, question_order)
);
