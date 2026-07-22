from __future__ import annotations

import json

from typer.testing import CliRunner

from nokaman.cli import app


def test_score_command_rich_table_output(tmp_path) -> None:
    """nokaman score --sample shows a rich dimension table per skill."""
    sample_file = tmp_path / "en_writing_a2.json"
    sample_file.write_text(
        json.dumps(
            {
                "id": "en_writing_a2",
                "language": "en",
                "skill": "writing",
                "expected_cefr": "A2",
                "text": "I like English. I study every day. My teacher is nice. I want good job.",
            }
        )
        + "\n"
    )
    result = CliRunner().invoke(
        app,
        ["score", "--sample", str(sample_file)],
    )
    assert result.exit_code == 0, result.output
    # Table headers
    assert "Skill" in result.output
    assert "Score" in result.output
    assert "CEFR" in result.output
    # All six skills present
    for skill in ["vocabulary", "grammar", "reading", "writing", "listening", "speaking"]:
        assert skill in result.output
    # Overall summary line
    assert "Overall" in result.output


def test_score_command_with_plain_text(tmp_path) -> None:
    """nokaman score works with a minimal sample (plain text only)."""
    sample_file = tmp_path / "en_minimal.json"
    sample_file.write_text(
        json.dumps(
            {
                "id": "en_minimal",
                "language": "en",
                "skill": "writing",
                "text": "Hello world.",
            }
        )
        + "\n"
    )
    result = CliRunner().invoke(
        app,
        ["score", "--sample", str(sample_file)],
    )
    assert result.exit_code == 0, result.output
    assert "Skill" in result.output
    assert "vocabulary" in result.output


def test_score_command_plain_fallback(tmp_path) -> None:
    """nokaman score --plain produces plain-text table without Rich formatting."""
    sample_file = tmp_path / "en_plain_test.json"
    sample_file.write_text(
        json.dumps(
            {
                "id": "en_plain_test",
                "language": "en",
                "skill": "writing",
                "expected_cefr": "B1",
                "text": "I have been studying English for three years.",
            }
        )
        + "\n"
    )
    result = CliRunner().invoke(
        app,
        ["score", "--sample", str(sample_file), "--plain"],
    )
    assert result.exit_code == 0, result.output
    # Plain output: no Rich escape codes, has column headers
    assert "Skill" in result.output
    assert "Score" in result.output
    assert "CEFR" in result.output
    assert "vocabulary" in result.output
    assert "Overall" in result.output
    # No Rich markup in output
    assert "[bold]" not in result.output
    assert "[cyan]" not in result.output


def test_eval_batch_writes_nested_output_path(tmp_path) -> None:
    out_path = tmp_path / "data" / "out" / "batch.json"
    result = CliRunner().invoke(
        app,
        ["eval", "batch", "--out", str(out_path), "--json-only"],
    )

    assert result.exit_code == 0, result.output
    assert out_path.exists()
    report = json.loads(out_path.read_text(encoding="utf-8"))
    assert report["n_samples"] >= 1
    assert "by_language" in report
    assert "rows" in report
