import json
from copy import deepcopy
from pathlib import Path

import pytest

from scripts.apply_oxidation_review import CURATED_SOURCE, apply_review
from scripts.render_oxidation_review_markdown import render
from scripts.validate_oxidation_review import validate

ROOT = Path(__file__).parents[1]


def test_review_worksheet_covers_all_elements_in_order() -> None:
    review = json.loads(
        (ROOT / "curation/oxidation_states/review.json").read_text(encoding="utf-8")
    )
    records = review["elements"]
    assert len(records) == 118
    assert [record["atomic_number"] for record in records] == list(range(1, 119))
    assert len({record["symbol"] for record in records}) == 118
    assert all("wikipedia_main" in record for record in records)
    assert all("wikipedia_additional" in record for record in records)
    assert all("principal" in record for record in records)


def test_wikipedia_snapshot_is_revision_pinned_and_complete() -> None:
    snapshot = json.loads(
        (ROOT / "curation/oxidation_states/wikipedia.json").read_text(encoding="utf-8")
    )
    assert snapshot["revision"] == 1340524841
    assert f"oldid={snapshot['revision']}" in snapshot["permanent_url"]
    assert snapshot["license"] == "CC BY-SA 4.0"
    assert [record["atomic_number"] for record in snapshot["elements"]] == list(
        range(1, 119)
    )
    iron = next(record for record in snapshot["elements"] if record["symbol"] == "Fe")
    assert iron["main"] == [2, 3]
    assert 6 in iron["states"]


def test_initial_review_candidates_follow_policy() -> None:
    review = json.loads(
        (ROOT / "curation/oxidation_states/review.json").read_text(encoding="utf-8")
    )
    for record in review["elements"]:
        if record["symbol"] == "C":
            assert record["print"] == list(range(-4, 5))
        else:
            assert 0 not in record["print"]
        assert record["print"] == sorted(record["print"])
        assert set(record["principal"]).issubset(record["print"])
        assert len(record["print"]) <= 5 or record["symbol"] in {"C", "N"}
        if record["status"] == "reviewed":
            assert set(record["evidence"]) == {str(state) for state in record["print"]}


def test_evidence_references_registered_curation_sources() -> None:
    review = json.loads(
        (ROOT / "curation/oxidation_states/review.json").read_text(encoding="utf-8")
    )
    sources = json.loads(
        (ROOT / "curation/oxidation_states/sources.json").read_text(encoding="utf-8")
    )["sources"]
    for record in review["elements"]:
        for evidence in record["evidence"].values():
            assert evidence["source"] in sources


def test_completed_worksheet_is_structurally_valid_and_complete() -> None:
    review = json.loads(
        (ROOT / "curation/oxidation_states/review.json").read_text(encoding="utf-8")
    )
    assert validate(review) == []
    assert validate(review, True) == []
    assert all(record["status"] == "reviewed" for record in review["elements"])


def test_apply_review_updates_only_reviewed_records() -> None:
    review = json.loads(
        (ROOT / "curation/oxidation_states/review.json").read_text(encoding="utf-8")
    )
    elements = json.loads(
        (ROOT / "src/periodisk/resources/elements.json").read_text(encoding="utf-8")
    )
    edited = deepcopy(review)
    for record in edited["elements"]:
        record["status"] = "pending"
        record["reviewer"] = ""
        record["reviewed_date"] = None
        record["evidence"] = {}
    hydrogen = edited["elements"][0]
    hydrogen.update(
        {
            "status": "reviewed",
            "reviewer": "Test reviewer",
            "reviewed_date": "2026-08-12",
            "evidence": {
                "-1": {
                    "representative": "NaH",
                    "reason": "Representative saline hydride",
                    "source": "test-source",
                },
                "1": {
                    "representative": "H2O",
                    "reason": "Dominant general-chemistry state",
                    "source": "test-source",
                },
            },
        }
    )

    updated, applied = apply_review(elements, edited)
    assert applied == ["H"]
    assert updated["elements"][0]["oxidation_states"]["source"] == CURATED_SOURCE
    assert updated["elements"][0]["oxidation_states"]["value"]["main"] == [-1, 1]
    assert (
        updated["elements"][1]["oxidation_states"]
        == elements["elements"][1]["oxidation_states"]
    )


def test_complete_application_rejects_pending_worksheet() -> None:
    review = json.loads(
        (ROOT / "curation/oxidation_states/review.json").read_text(encoding="utf-8")
    )
    elements = json.loads(
        (ROOT / "src/periodisk/resources/elements.json").read_text(encoding="utf-8")
    )
    incomplete = deepcopy(review)
    incomplete["elements"][-1].update(
        {
            "status": "pending",
            "reviewer": "",
            "reviewed_date": None,
            "evidence": {},
        }
    )
    with pytest.raises(ValueError, match="review is not complete"):
        apply_review(elements, incomplete, require_complete=True)


def test_complete_application_accepts_completed_worksheet() -> None:
    review = json.loads(
        (ROOT / "curation/oxidation_states/review.json").read_text(encoding="utf-8")
    )
    elements = json.loads(
        (ROOT / "src/periodisk/resources/elements.json").read_text(encoding="utf-8")
    )

    _, applied = apply_review(elements, review, require_complete=True)
    assert len(applied) == 118


def test_generated_review_table_is_current() -> None:
    review = json.loads(
        (ROOT / "curation/oxidation_states/review.json").read_text(encoding="utf-8")
    )
    sources = json.loads(
        (ROOT / "curation/oxidation_states/sources.json").read_text(encoding="utf-8")
    )["sources"]
    generated = (ROOT / "curation/oxidation_states/REVIEW_TABLE.md").read_text(
        encoding="utf-8"
    )

    assert generated == render(review, sources)
