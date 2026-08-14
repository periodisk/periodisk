"""Public registries for supported presentation choices."""

SUPPORTED_LOCALES = ("en_GB", "nb_NO")
SUPPORTED_ELECTRONEGATIVITY_SCALES = ("pauling", "allred-rochow", "allen")


def validate_electronegativity_scale(scale: str) -> str:
    if scale not in SUPPORTED_ELECTRONEGATIVITY_SCALES:
        choices = ", ".join(SUPPORTED_ELECTRONEGATIVITY_SCALES)
        raise ValueError(
            f"Unsupported electronegativity scale: {scale!r}; choose {choices}"
        )
    return scale
