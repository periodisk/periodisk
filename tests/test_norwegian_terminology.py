import json
from copy import deepcopy
from pathlib import Path

from scripts.render_norwegian_classification_review_markdown import (
    render as render_classifications,
)
from scripts.render_norwegian_name_review_markdown import render
from scripts.validate_norwegian_classification_review import BROAD_INCLUDES
from scripts.validate_norwegian_classification_review import (
    validate as validate_classifications,
)
from scripts.validate_norwegian_name_review import validate

ROOT = Path(__file__).parents[1]
REVIEW_PATH = ROOT / "curation/norwegian_terminology/review.json"
ELEMENTS_PATH = ROOT / "src/periodisk/resources/elements.json"
LOCALE_PATH = ROOT / "src/periodisk/resources/locales/nb_NO.json"


def _resources() -> tuple[dict, dict, dict]:
    return tuple(
        json.loads(path.read_text(encoding="utf-8"))
        for path in (REVIEW_PATH, ELEMENTS_PATH, LOCALE_PATH)
    )


def test_review_is_complete_and_matches_runtime_names() -> None:
    review, elements, locale = _resources()

    assert validate(review, elements, locale) == []
    assert [record["atomic_number"] for record in review["elements"]] == list(
        range(1, 119)
    )


def test_review_validation_detects_a_runtime_name_mismatch() -> None:
    review, elements, locale = _resources()
    edited = deepcopy(review)
    edited["elements"][0]["reviewed_name"] = "changed"

    assert "elements[0].reviewed_name must match nb_NO.json" in validate(
        edited, elements, locale
    )


def test_review_validation_accepts_a_changed_name_matching_the_locale() -> None:
    review, elements, locale = _resources()
    edited_review = deepcopy(review)
    edited_locale = deepcopy(locale)
    edited_review["elements"][0]["decision"] = "changed"
    edited_review["elements"][0]["reviewed_name"] = "vannstoff"
    edited_locale["element_names"]["H"] = "vannstoff"

    assert validate(edited_review, elements, edited_locale) == []


def test_review_validation_rejects_an_unresolved_decision() -> None:
    review, elements, locale = _resources()
    edited = deepcopy(review)
    edited["elements"][0]["decision"] = "unresolved"

    assert (
        "elements[0].decision must be retained or changed in a completed audit"
        in validate(edited, elements, locale)
    )


def test_review_validation_applies_the_json_schema() -> None:
    review, elements, locale = _resources()
    edited = deepcopy(review)
    edited["elements"][0]["unexpected"] = True
    del edited["elements"][1]["notes"]

    errors = validate(edited, elements, locale)
    assert any(
        error.startswith("review.elements[0]:") and "unexpected" in error
        for error in errors
    )
    assert any(
        error.startswith("review.elements[1]:") and "'notes'" in error
        for error in errors
    )


def test_review_validation_detects_an_invalid_source_url() -> None:
    review, elements, locale = _resources()
    edited = deepcopy(review)
    edited["elements"][0]["sources"]["naob"]["url"] = "http://example.com"

    assert "elements[0].sources.naob.url must use https://naob.no" in validate(
        edited, elements, locale
    )


def test_generated_review_table_is_current() -> None:
    review, _, _ = _resources()
    generated = (ROOT / "curation/norwegian_terminology/REVIEW_TABLE.md").read_text(
        encoding="utf-8"
    )

    assert generated == render(review)


# Classification-term review

CLASSIFICATIONS_PATH = ROOT / "curation/norwegian_terminology/classifications.json"


def _classification_resources() -> tuple[dict, dict, dict]:
    return tuple(
        json.loads(path.read_text(encoding="utf-8"))
        for path in (CLASSIFICATIONS_PATH, ELEMENTS_PATH, LOCALE_PATH)
    )


def test_classification_review_is_complete_and_matches_runtime_terms() -> None:
    review, elements, locale = _classification_resources()

    assert validate_classifications(review, elements, locale) == []


def test_classification_review_detects_a_runtime_term_mismatch() -> None:
    review, elements, locale = _classification_resources()
    edited = deepcopy(locale)
    edited["classifications"]["halogen"] = "Saltdannere"

    assert "terms[6].reviewed_term must match nb_NO.json" in validate_classifications(
        review, elements, edited
    )


def test_classification_review_detects_changed_membership() -> None:
    review, elements, locale = _classification_resources()
    edited = deepcopy(elements)
    zinc = next(element for element in edited["elements"] if element["symbol"] == "Zn")
    zinc["classifications"] = ["post-transition-metal"]

    errors = validate_classifications(review, edited, locale)
    assert "terms[2].members must match elements.json" in errors
    assert "terms[3].members must match elements.json" in errors


def test_classification_review_requires_previous_term_for_changes() -> None:
    review, elements, locale = _classification_resources()
    edited = deepcopy(review)
    del edited["terms"][5]["previous_term"]

    errors = validate_classifications(edited, elements, locale)
    assert any(
        error.startswith("review.terms[5]:") and "previous_term" in error
        for error in errors
    )


def test_classification_review_rejects_a_cited_source_marked_not_listed() -> None:
    review, elements, locale = _classification_resources()
    edited = deepcopy(review)
    edited["terms"][0]["not_listed"] = ["snl"]

    assert (
        "terms[0].not_listed must not include cited sources: snl"
        in validate_classifications(edited, elements, locale)
    )


def test_documented_broad_mapping_matches_the_renderer() -> None:
    from periodisk._render_svg import _display_categories
    from periodisk.data import load_elements

    single = {
        element.classifications[0]: element
        for element in load_elements()
        if len(element.classifications) == 1
    }
    for broad, detailed_keys in BROAD_INCLUDES.items():
        for key in detailed_keys:
            assert _display_categories(single[key], "broad") == (broad,)


def test_generated_classification_table_is_current() -> None:
    review, _, _ = _classification_resources()
    generated = (
        ROOT / "curation/norwegian_terminology/CLASSIFICATIONS_TABLE.md"
    ).read_text(encoding="utf-8")

    assert generated == render_classifications(review)
