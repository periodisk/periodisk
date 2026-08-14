from periodisk.cli import _parser


def test_electronegativity_scale_option_matches_python_api_name() -> None:
    args = _parser().parse_args(
        ["render", "table.svg", "--electronegativity-scale", "allen"]
    )
    assert args.electronegativity_scale == "allen"
