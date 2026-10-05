"""Tests for jobbing.models — CV/cover-letter dataclasses and JSON round-trip."""

from __future__ import annotations

import json
from pathlib import Path

from jobbing.models import CLData, CompanyData, CVData, Education, Job


class TestCompanyDataRoundTrip:
    def _sample_data(self) -> CompanyData:
        cv = CVData(
            name="Jane",
            location="Berlin",
            email="jane@example.com",
            github="github.com/jane",
            linkedin="linkedin.com/in/jane",
            summary=["Summary line"],
            core_skills=["Python", "Go"],
            key_achievements=["Built platform"],
            jobs=[
                Job(
                    title="Senior Engineer",
                    company="Acme",
                    dates="2024-present",
                    bullets=["Did things"],
                ),
            ],
            earlier_experience=[
                Job(title="Engineer", company="OldCo", dates="2020-2024", bullets=["Stuff"]),
            ],
            education=[Education(degree="MSc", school="MIT", detail="CS")],
            skills={"Languages": "Python, Go"},
        )
        cl = CLData(
            date="2026-03-08",
            recipient="Hiring Manager",
            company="Acme",
            greeting="Dear Hiring Manager",
            paragraphs=["I am writing to apply."],
            closing="Sincerely",
            name="Jane",
            email="jane@example.com",
            linkedin="linkedin.com/in/jane",
        )
        return CompanyData(company_upper="ACME", cv=cv, cl=cl)

    def test_round_trip(self, tmp_path: Path) -> None:
        original = self._sample_data()
        path = tmp_path / "acme.json"

        original.to_json_file(path)
        loaded = CompanyData.from_json_file(path)

        assert loaded.company_upper == "ACME"
        assert loaded.cv.name == "Jane"
        assert loaded.cv.core_skills == ["Python", "Go"]
        assert len(loaded.cv.jobs) == 1
        assert loaded.cv.jobs[0].title == "Senior Engineer"
        assert len(loaded.cv.earlier_experience) == 1
        assert len(loaded.cv.education) == 1
        assert loaded.cv.skills == {"Languages": "Python, Go"}
        assert loaded.cl.paragraphs == ["I am writing to apply."]

    def test_json_uses_camel_case(self, tmp_path: Path) -> None:
        original = self._sample_data()
        path = tmp_path / "acme.json"
        original.to_json_file(path)

        with open(path) as f:
            raw = json.load(f)

        assert "companyUpper" in raw
        assert "coreSkills" in raw["cv"]
        assert "keyAchievements" in raw["cv"]
        assert "earlierExperience" in raw["cv"]

    def test_minimal_cv(self, tmp_path: Path) -> None:
        """Round-trip with no optional CV fields (earlier_experience, education, skills)."""
        cv = CVData(
            name="Jane",
            location="Berlin",
            email="g@e.com",
            github="gh",
            linkedin="li",
            summary=["s"],
            core_skills=["Python"],
            key_achievements=["a"],
            jobs=[Job(title="E", company="C", bullets=["b"])],
        )
        cl = CLData(
            date="2026-01-01",
            recipient="HM",
            company="C",
            greeting="Hi",
            paragraphs=["p"],
            closing="Thanks",
            name="Jane",
            email="g@e.com",
            linkedin="li",
        )
        data = CompanyData(company_upper="C", cv=cv, cl=cl)
        path = tmp_path / "minimal.json"
        data.to_json_file(path)
        loaded = CompanyData.from_json_file(path)

        assert loaded.cv.earlier_experience == []
        assert loaded.cv.education == []
        assert loaded.cv.skills == {}
