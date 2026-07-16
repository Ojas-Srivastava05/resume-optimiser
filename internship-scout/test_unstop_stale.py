#!/usr/bin/env python3
"""Unit tests for Unstop stale-opportunity detection."""

import unittest
from datetime import datetime, timedelta, timezone

from fetchers.unstop_utils import is_expired, normalize_unstop_date, unstop_opportunity_is_stale


class UnstopStaleTests(unittest.TestCase):
    def test_normalize_offset(self):
        self.assertEqual(
            normalize_unstop_date("2023-06-30T00:00:00+05:30"),
            "2023-06-30T00:00:00+0530",
        )

    def test_expired_end_date(self):
        self.assertTrue(is_expired("2023-06-30T00:00:00+05:30"))
        self.assertTrue(is_expired("2025-09-30T10:35:00+05:30"))

    def test_future_end_date(self):
        future = (datetime.now(timezone.utc) + timedelta(days=30)).strftime("%Y-%m-%d")
        self.assertFalse(is_expired(future))

    def test_stale_when_registration_ended(self):
        item = {
            "title": "HackOn With Amazon 6.0",
            "end_date": "2026-07-31T23:59:00+05:30",
            "regnRequirements": {
                "end_regn_dt": "2026-05-28T23:59:35+05:30",
                "remainingDaysArray": {"text": "Ended"},
            },
        }
        self.assertTrue(unstop_opportunity_is_stale(item))

    def test_open_when_registration_active(self):
        item = {
            "title": "Adobe University Hackathon 2026",
            "end_date": "2026-10-16T16:00:15+05:30",
            "regnRequirements": {
                "end_regn_dt": "2026-08-08T23:59:31+05:30",
                "remainingDaysArray": {"text": " days left"},
            },
        }
        self.assertFalse(unstop_opportunity_is_stale(item))

    def test_stale_closed_internship(self):
        item = {
            "title": "Backend Internship",
            "end_date": "2023-06-30T00:00:00+05:30",
            "regnRequirements": {
                "end_regn_dt": "2023-06-30T00:00:00+05:30",
                "remainingDaysArray": {"text": "Ended"},
            },
        }
        self.assertTrue(unstop_opportunity_is_stale(item))

    def test_stale_myntra_rampup(self):
        item = {
            "title": "Myntra RampUp - SDE Internship",
            "end_date": "2025-09-30T10:35:00+05:30",
            "regnRequirements": {
                "end_regn_dt": "2025-09-17T23:59:00+05:30",
                "remainingDaysArray": {"text": "Ended"},
            },
        }
        self.assertTrue(unstop_opportunity_is_stale(item))


if __name__ == "__main__":
    raise SystemExit(unittest.main())
