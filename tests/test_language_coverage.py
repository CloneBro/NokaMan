from __future__ import annotations

import json

from typer.testing import CliRunner

from nokaman.cli import app
from nokaman.data.coverage import language_skill_coverage


def test_language_skill_coverage_counts_samples() -> None:
    report = language_skill_coverage()
    rows = {row["code"]: row for row in report["languages"]}

    assert report["skills"] == [
        "vocabulary",
        "grammar",
        "reading",
        "writing",
        "listening",
        "speaking",
    ]
    # English checks (baseline)
    assert rows["en"]["total"] >= 1
    assert rows["en"]["skills"]["writing"] >= 1
    assert rows["en"]["has_rubric"] is True
    # Vietnamese: should have rubric and at least 4 writing samples (now A1, A2, B1, B2, C1 = 5)
    assert rows["vi"]["has_rubric"] is True
    assert rows["vi"]["skills"]["writing"] >= 4
    # Spanish: should have rubric (now added) and at least 4 writing samples (A1, A2, B1, B2, C1 = 5)
    assert rows["es"]["has_rubric"] is True
    assert rows["es"]["skills"]["writing"] >= 4


def test_languages_coverage_json_command() -> None:
    result = CliRunner().invoke(app, ["languages", "coverage", "--json"])
    assert result.exit_code == 0, result.output
    report = json.loads(result.output)
    rows = {row["code"]: row for row in report["languages"]}
    # Japanese check (existing)
    assert rows["ja"]["skills"]["writing"] >= 1
    assert rows["ja"]["has_rubric"] is True
    # Vietnamese and Spanish checks (new)
    assert rows["vi"]["skills"]["writing"] >= 4
    assert rows["vi"]["has_rubric"] is True
    assert rows["es"]["skills"]["writing"] >= 4
    assert rows["es"]["has_rubric"] is True