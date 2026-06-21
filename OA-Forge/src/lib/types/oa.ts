export type ConfidenceTier = "A" | "B" | "C";

export type OACompany = {
	id: string;
	slug: string;
	name: string;
};

export type OAQuestion = {
	id: string;
	slug: string;
	title: string;
	difficulty: string;
	category: string;
	question_order: number;
};

export type OAQuestionWithMeta = OAQuestion & {
	confidence_tier: ConfidenceTier;
	year: number;
	season: string | null;
	source_notes: string | null;
	source_url?: string | null;
};

export type OACompanyReadiness = OACompany & {
	total_questions: number;
	strict_questions: number;
	tier_a: number;
	tier_b: number;
	tier_c: number;
	duration_minutes: number;
	num_questions: number;
	mock_ready: boolean;
	strict_ready: boolean;
	source_leads?: number;
};

export type OATemplate = {
	id: string;
	company_id: string;
	name: string;
	duration_minutes: number;
	num_questions: number;
	strict_tiers: ConfidenceTier[];
};

export type OASession = {
	id: string;
	company_id: string;
	template_id: string | null;
	status: "active" | "completed" | "expired";
	duration_minutes: number;
	started_at: string;
	ended_at: string | null;
};

export type OATestCase = {
	id: string;
	input_text: string;
	expected_output: string;
	is_sample: boolean;
	test_order: number;
};

export type OASessionQuestion = {
	id: string;
	session_id: string;
	question_id: string;
	question_order: number;
	verdict: string | null;
	question: OAQuestion;
};
