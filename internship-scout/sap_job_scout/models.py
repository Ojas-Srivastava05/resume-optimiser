"""Job model for SAP scout."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SapJob:
    title: str
    company: str
    location: str
    url: str
    source: str
    score: int = 0

    @property
    def key(self) -> str:
        url = self.url.split("?")[0].rstrip("/").lower()
        return f"{self.source}|{self.company}|{self.title}|{url}".lower()
