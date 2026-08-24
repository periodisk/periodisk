from pathlib import Path

from scripts.render_examples import (
    DEFAULT_OUTPUT_ROOT,
    example_outputs,
    render_examples,
)


def test_canonical_example_inventory_matches_tracked_files() -> None:
    expected = {
        output.relative_to(DEFAULT_OUTPUT_ROOT) for output, _, _ in example_outputs()
    }
    tracked = {
        output.relative_to(DEFAULT_OUTPUT_ROOT)
        for output in DEFAULT_OUTPUT_ROOT.glob("*/*/*")
        if output.suffix in {".pdf", ".svg"}
    }
    assert tracked == expected


def test_committed_svg_examples_are_current(tmp_path: Path) -> None:
    generated = render_examples(tmp_path, formats=("svg",))
    assert len(generated) == 4
    for output in generated:
        relative_path = output.relative_to(tmp_path)
        assert output.read_bytes() == (DEFAULT_OUTPUT_ROOT / relative_path).read_bytes()
