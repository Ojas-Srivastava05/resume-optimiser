#!/usr/bin/env python3
"""Unit tests for relaxed CS-adjacent internship filters."""

import unittest

from filters import is_relevant


class FilterRelaxationTests(unittest.TestCase):
    def test_classic_swe_intern_still_matches(self):
        self.assertTrue(
            is_relevant(
                "Software Engineering Intern",
                "Microsoft",
                "Hyderabad, India",
                require_priority=False,
            )
        )

    def test_applied_sciences_intern(self):
        self.assertTrue(
            is_relevant(
                "Applied Sciences Intern",
                "Microsoft",
                "India, Multiple Locations",
                require_priority=False,
            )
        )

    def test_technology_program_intern(self):
        self.assertTrue(
            is_relevant(
                "Technology Program Intern",
                "Wells Fargo",
                "Bengaluru",
                require_priority=False,
            )
        )

    def test_summer_analyst_soft_tech(self):
        self.assertTrue(
            is_relevant(
                "Summer Analyst",
                "Goldman Sachs",
                "Mumbai, India",
                require_priority=False,
            )
        )

    def test_sdet_intern(self):
        self.assertTrue(
            is_relevant(
                "SDET Intern",
                "Amazon",
                "Bangalore",
                require_priority=False,
            )
        )

    def test_computer_science_intern(self):
        self.assertTrue(
            is_relevant(
                "Computer Science Intern",
                "Qualcomm",
                "Hyderabad",
                require_priority=False,
            )
        )

    def test_marketing_still_blocked(self):
        self.assertFalse(
            is_relevant(
                "Marketing Intern",
                "Google",
                "Bangalore, India",
                require_priority=False,
            )
        )

    def test_wrong_batch_blocked(self):
        self.assertFalse(
            is_relevant(
                "SDE Internship - Batch of 2026",
                "Myntra",
                "Bangalore",
                require_priority=False,
            )
        )

    def test_prompt_engineering_no_longer_hard_blocked(self):
        # Was previously excluded; AI-adjacent roles should pass
        self.assertTrue(
            is_relevant(
                "Prompt Engineering Intern",
                "Microsoft",
                "Bengaluru, India",
                require_priority=False,
            )
        )


if __name__ == "__main__":
    raise SystemExit(unittest.main())
