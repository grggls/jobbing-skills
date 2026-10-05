"""Domain model for document generation.

CompanyData holds the content of one tailored CV and cover letter. It reads
and writes applications/{Slug}/{Slug}.json (camelCase keys).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Document generation types
# ---------------------------------------------------------------------------


@dataclass
class Job:
    """A single job entry on a CV."""

    title: str
    company: str
    dates: str = ""
    bullets: list[str] = field(default_factory=list)


@dataclass
class Education:
    """A single education entry on a CV."""

    degree: str
    school: str
    detail: str = ""


@dataclass
class CVData:
    """All data needed to render a CV PDF."""

    name: str
    location: str
    email: str
    github: str
    linkedin: str
    summary: list[str]
    core_skills: list[str]
    key_achievements: list[str]
    jobs: list[Job]
    earlier_experience: list[Job] = field(default_factory=list)
    education: list[Education] = field(default_factory=list)
    skills: dict[str, str] = field(default_factory=dict)


@dataclass
class CLData:
    """All data needed to render a cover letter PDF."""

    date: str
    recipient: str
    company: str
    greeting: str
    paragraphs: list[str]
    closing: str
    name: str
    email: str
    linkedin: str


@dataclass
class CompanyData:
    """Container for one company's complete document data.

    Reads and writes the existing JSON schema (camelCase keys) used by
    all 49 company directories. No migration needed.
    """

    company_upper: str
    cv: CVData
    cl: CLData

    @classmethod
    def from_json_file(cls, path: str | Path) -> CompanyData:
        """Load from the existing JSON format (companies/{co}/{co}.json)."""
        with open(path) as f:
            data = json.load(f)

        cv_data = data["cv"]
        cv = CVData(
            name=cv_data["name"],
            location=cv_data["location"],
            email=cv_data["email"],
            github=cv_data["github"],
            linkedin=cv_data["linkedin"],
            summary=cv_data["summary"],
            core_skills=cv_data["coreSkills"],
            key_achievements=cv_data["keyAchievements"],
            jobs=[
                Job(
                    title=j["title"],
                    company=j["company"],
                    dates=j.get("dates", ""),
                    bullets=j.get("bullets", []),
                )
                for j in cv_data["jobs"]
            ],
            earlier_experience=[
                Job(
                    title=j["title"],
                    company=j["company"],
                    dates=j.get("dates", ""),
                    bullets=j.get("bullets", []),
                )
                for j in cv_data.get("earlierExperience", [])
            ],
            education=[
                Education(
                    degree=e["degree"],
                    school=e["school"],
                    detail=e.get("detail", ""),
                )
                for e in cv_data.get("education", [])
            ],
            skills=cv_data.get("skills", {}),
        )

        cl_data = data["cl"]
        cl = CLData(
            date=cl_data["date"],
            recipient=cl_data["recipient"],
            company=cl_data["company"],
            greeting=cl_data["greeting"],
            paragraphs=cl_data["paragraphs"],
            closing=cl_data["closing"],
            name=cl_data["name"],
            email=cl_data["email"],
            linkedin=cl_data["linkedin"],
        )

        return cls(company_upper=data["companyUpper"], cv=cv, cl=cl)

    def to_json_file(self, path: str | Path) -> None:
        """Write in the existing JSON format for backward compatibility."""
        data = {
            "companyUpper": self.company_upper,
            "cv": {
                "name": self.cv.name,
                "location": self.cv.location,
                "email": self.cv.email,
                "github": self.cv.github,
                "linkedin": self.cv.linkedin,
                "summary": self.cv.summary,
                "coreSkills": self.cv.core_skills,
                "keyAchievements": self.cv.key_achievements,
                "jobs": [
                    {
                        "title": j.title,
                        "company": j.company,
                        **({"dates": j.dates} if j.dates else {}),
                        "bullets": j.bullets,
                    }
                    for j in self.cv.jobs
                ],
                **(
                    {
                        "earlierExperience": [
                            {
                                "title": j.title,
                                "company": j.company,
                                **({"dates": j.dates} if j.dates else {}),
                                "bullets": j.bullets,
                            }
                            for j in self.cv.earlier_experience
                        ]
                    }
                    if self.cv.earlier_experience
                    else {}
                ),
                **(
                    {
                        "education": [
                            {
                                "degree": e.degree,
                                "school": e.school,
                                **({"detail": e.detail} if e.detail else {}),
                            }
                            for e in self.cv.education
                        ]
                    }
                    if self.cv.education
                    else {}
                ),
                **({"skills": self.cv.skills} if self.cv.skills else {}),
            },
            "cl": {
                "date": self.cl.date,
                "recipient": self.cl.recipient,
                "company": self.cl.company,
                "greeting": self.cl.greeting,
                "paragraphs": self.cl.paragraphs,
                "closing": self.cl.closing,
                "name": self.cl.name,
                "email": self.cl.email,
                "linkedin": self.cl.linkedin,
            },
        }

        with open(path, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
