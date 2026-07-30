"""Data models for international opportunities."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class Opportunity:
	"""One first-world internship / research / summer program."""

	id: str
	name: str
	org: str
	country: str
	region: str  # EU | UK | CH | US | CA | JP | AU | SG | Remote-FirstWorld
	duration: str
	who_can_apply: str
	cost: str
	stipend: str
	typical_deadline_window: str  # human text for Summer 2027 cycle
	url: str
	fit_tags: tuple[str, ...] = ()
	visa_note: str = ""
	priority: int = 2  # 1 = highest fit for Ojas
	status: str = "watch"  # open | watch | closed
	notes: str = ""

	def to_dict(self) -> dict[str, Any]:
		return asdict(self)


@dataclass
class LiveListing:
	"""Optional live ATS / board hit (company intern, first-world location)."""

	company: str
	title: str
	location: str
	country: str
	url: str
	source: str
	fit_tags: list[str] = field(default_factory=list)
