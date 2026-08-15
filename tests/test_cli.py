import periodisk.cli
from periodisk.cli import _parser
from periodisk.settings import SUPPORTED_LOCALES


def test_electronegativity_scale_option_matches_python_api_name() -> None:
    args = _parser().parse_args(
        ["render", "table.svg", "--electronegativity-scale", "allen"]
    )
    assert args.electronegativity_scale == "allen"


def test_release_validation_loads_every_supported_locale(monkeypatch) -> None:
    loaded = []
    monkeypatch.setattr(
        periodisk.cli,
        "load_locale",
        lambda locale: loaded.append(locale),
    )

    assert periodisk.cli.main(["validate", "--release"]) == 0
    assert loaded == list(SUPPORTED_LOCALES)


def test_release_validation_reports_invalid_locale(monkeypatch, capsys) -> None:
    def invalid_locale(locale: str) -> None:
        raise ValueError("missing locale section 'units'")

    monkeypatch.setattr(periodisk.cli, "load_locale", invalid_locale)

    assert periodisk.cli.main(["validate", "--release"]) == 1
    output = capsys.readouterr().out
    for locale in SUPPORTED_LOCALES:
        assert f"{locale}: invalid locale resource" in output
