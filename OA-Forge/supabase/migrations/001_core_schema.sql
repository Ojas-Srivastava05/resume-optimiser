-- ============================================================================
-- OA Forge: Core Schema
-- Phase 1 — Data Architecture
-- Run this in your Supabase SQL Editor
-- ============================================================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- COMPANIES
-- ============================================================================
CREATE TABLE companies (
  id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name        TEXT NOT NULL UNIQUE,
  slug        TEXT NOT NULL UNIQUE,
  logo_url    TEXT,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- ROLES (per company)
-- ============================================================================
CREATE TABLE roles (
  id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id  UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  title       TEXT NOT NULL,            -- e.g. "SWE Intern", "SDE Intern"
  level       TEXT NOT NULL CHECK (level IN ('intern', 'fte', 'new_grad')),
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(company_id, title, level)
);

-- ============================================================================
-- OA TEMPLATES (how a company's OA is structured)
-- ============================================================================
CREATE TABLE oa_templates (
  id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id        UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  role_id           UUID REFERENCES roles(id) ON DELETE SET NULL,
  name              TEXT NOT NULL,            -- e.g. "Amazon SDE Intern OA 2025"
  duration_minutes  INT NOT NULL DEFAULT 90,
  num_coding_q      INT NOT NULL DEFAULT 2,
  num_mcq_q         INT NOT NULL DEFAULT 0,
  difficulty_mix    TEXT,                     -- e.g. "1 Easy-Med + 1 Med-Hard"
  description       TEXT,                     -- how their OA usually works
  created_at        TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- QUESTIONS (the core content)
-- ============================================================================
CREATE TABLE questions (
  id                    UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  slug                  TEXT NOT NULL UNIQUE,
  title                 TEXT NOT NULL,
  type                  TEXT NOT NULL CHECK (type IN ('coding', 'mcq')),
  difficulty            TEXT NOT NULL CHECK (difficulty IN ('Easy', 'Medium', 'Hard')),
  topics                TEXT[] DEFAULT '{}',   -- e.g. {'arrays', 'hash-map', 'two-pointer'}
  statement_html        TEXT NOT NULL,         -- problem statement (your own words)
  constraints_html      TEXT,
  -- Coding-specific fields
  starter_code_json     JSONB,                 -- {"python": "...", "cpp": "...", "javascript": "..."}
  solution_code         TEXT,                  -- reference solution (admin-only, never sent to client)
  starter_function_name TEXT,                  -- e.g. "twoSum" for JS execution
  -- MCQ-specific fields
  mcq_options           JSONB,                 -- ["option A", "option B", "option C", "option D"]
  mcq_correct_index     INT,                   -- 0-indexed
  mcq_explanation       TEXT,
  -- Metadata
  lc_number             INT,                   -- LeetCode problem number if applicable
  lc_slug               TEXT,                   -- e.g. "two-sum" on LC
  gfg_url               TEXT,
  notes                 TEXT,                   -- admin notes
  is_published          BOOLEAN DEFAULT FALSE,
  created_at            TIMESTAMPTZ DEFAULT NOW(),
  updated_at            TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- QUESTION TEST CASES (hidden from user until submit)
-- ============================================================================
CREATE TABLE question_tests (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  question_id   UUID NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
  input         TEXT NOT NULL,
  expected_output TEXT NOT NULL,
  is_sample     BOOLEAN DEFAULT FALSE,  -- visible in UI as example
  explanation   TEXT,
  order_num     INT DEFAULT 0,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- QUESTION COMPANY OCCURRENCES — THE KEY TABLE
-- Links a question to where it was actually asked
-- ============================================================================
CREATE TABLE question_company_occurrences (
  id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  question_id       UUID NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
  company_id        UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  role_id           UUID REFERENCES roles(id) ON DELETE SET NULL,
  year              INT,                      -- 2024, 2025, etc.
  season            TEXT CHECK (season IN ('spring', 'summer', 'fall', 'winter', 'unknown')),
  round_type        TEXT NOT NULL CHECK (round_type IN ('oa', 'phone', 'onsite', 'unknown')),
  source_type       TEXT NOT NULL CHECK (source_type IN (
    'personal',          -- you personally saw it
    'friend_report',     -- trusted friend report
    'lc_discuss',        -- LeetCode Discuss
    'gfg',               -- GeeksforGeeks
    'blind',             -- Blind / Reddit
    'other'
  )),
  source_url        TEXT,                     -- link to source
  source_notes      TEXT,                     -- additional context
  confidence_tier   TEXT NOT NULL CHECK (confidence_tier IN ('A', 'B', 'C')),
  -- A = verified (you personally saw it)
  -- B = corroborated (2+ independent reports)
  -- C = similar (same pattern, label clearly)
  reported_at       TIMESTAMPTZ DEFAULT NOW(),
  verified_by       TEXT                      -- who verified (you, for now)
);

-- ============================================================================
-- OA SESSIONS (mock attempts)
-- ============================================================================
CREATE TABLE oa_sessions (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id         UUID NOT NULL,              -- Supabase Auth user ID
  oa_template_id  UUID REFERENCES oa_templates(id) ON DELETE SET NULL,
  company_id      UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  started_at      TIMESTAMPTZ DEFAULT NOW(),
  ended_at        TIMESTAMPTZ,
  score           INT,
  total_possible  INT,
  status          TEXT DEFAULT 'in_progress' CHECK (status IN ('in_progress', 'completed', 'abandoned')),
  strict_mode     BOOLEAN DEFAULT FALSE       -- only Tier A+B questions
);

-- ============================================================================
-- OA SESSION QUESTIONS (which questions in a mock session)
-- ============================================================================
CREATE TABLE oa_session_questions (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  session_id    UUID NOT NULL REFERENCES oa_sessions(id) ON DELETE CASCADE,
  question_id   UUID NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
  order_num     INT NOT NULL DEFAULT 0,
  user_code     TEXT,
  language      TEXT,
  verdict       TEXT CHECK (verdict IN ('AC', 'WA', 'TLE', 'RE', 'CE', 'pending', NULL)),
  runtime_ms    INT,
  submitted_at  TIMESTAMPTZ
);

-- ============================================================================
-- SUBMISSIONS (all submission history, including outside of mocks)
-- ============================================================================
CREATE TABLE submissions (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id       UUID NOT NULL,
  question_id   UUID NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
  session_id    UUID REFERENCES oa_sessions(id) ON DELETE SET NULL,
  code          TEXT NOT NULL,
  language      TEXT NOT NULL,
  verdict       TEXT NOT NULL CHECK (verdict IN ('AC', 'WA', 'TLE', 'RE', 'CE')),
  runtime_ms    INT,
  tests_passed  INT DEFAULT 0,
  tests_total   INT DEFAULT 0,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- INDEXES for performance
-- ============================================================================
CREATE INDEX idx_questions_slug ON questions(slug);
CREATE INDEX idx_questions_type ON questions(type);
CREATE INDEX idx_questions_difficulty ON questions(difficulty);
CREATE INDEX idx_questions_published ON questions(is_published);
CREATE INDEX idx_occurrences_company ON question_company_occurrences(company_id);
CREATE INDEX idx_occurrences_question ON question_company_occurrences(question_id);
CREATE INDEX idx_occurrences_tier ON question_company_occurrences(confidence_tier);
CREATE INDEX idx_sessions_user ON oa_sessions(user_id);
CREATE INDEX idx_submissions_user ON submissions(user_id);
CREATE INDEX idx_submissions_question ON submissions(question_id);
CREATE INDEX idx_question_tests_question ON question_tests(question_id);

-- ============================================================================
-- ROW LEVEL SECURITY (basic policies)
-- ============================================================================

-- Questions: public read for published, admin write
ALTER TABLE questions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Published questions are viewable by everyone"
  ON questions FOR SELECT
  USING (is_published = TRUE);

-- Question tests: only sample tests visible; hidden tests never sent
ALTER TABLE question_tests ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Sample tests are viewable by everyone"
  ON question_tests FOR SELECT
  USING (is_sample = TRUE);

-- Companies: public read
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Companies are viewable by everyone"
  ON companies FOR SELECT
  USING (TRUE);

-- Roles: public read
ALTER TABLE roles ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Roles are viewable by everyone"
  ON roles FOR SELECT
  USING (TRUE);

-- OA Templates: public read
ALTER TABLE oa_templates ENABLE ROW LEVEL SECURITY;
CREATE POLICY "OA templates are viewable by everyone"
  ON oa_templates FOR SELECT
  USING (TRUE);

-- Occurrences: public read
ALTER TABLE question_company_occurrences ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Occurrences are viewable by everyone"
  ON question_company_occurrences FOR SELECT
  USING (TRUE);

-- Sessions: users see only their own
ALTER TABLE oa_sessions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view their own sessions"
  ON oa_sessions FOR SELECT
  USING (auth.uid() = user_id);
CREATE POLICY "Users can create their own sessions"
  ON oa_sessions FOR INSERT
  WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own sessions"
  ON oa_sessions FOR UPDATE
  USING (auth.uid() = user_id);

-- Submissions: users see only their own
ALTER TABLE submissions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view their own submissions"
  ON submissions FOR SELECT
  USING (auth.uid() = user_id);
CREATE POLICY "Users can create their own submissions"
  ON submissions FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Session questions: through session ownership
ALTER TABLE oa_session_questions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view their session questions"
  ON oa_session_questions FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM oa_sessions
      WHERE oa_sessions.id = oa_session_questions.session_id
      AND oa_sessions.user_id = auth.uid()
    )
  );
