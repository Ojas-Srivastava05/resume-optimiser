from dataclasses import dataclass, field


@dataclass
class TestCase:
	input_text: str
	output_text: str


@dataclass
class OAQuestion:
	title: str
	slug: str
	difficulty: str
	statement: str
	test_cases: list[TestCase] = field(default_factory=list)
	source_url: str = ""
	source: str = "leetcode"  # leetcode | ramesh_oa


@dataclass
class OADayPlan:
	company_slug: str
	company_name: str
	questions: list[OAQuestion]
	visit_number: int
	queue_position: int
	queue_total: int
