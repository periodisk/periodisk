# Norwegian element-name curation

This directory records the review of the 118 Bokmål element names displayed by
Periodisk. The review was completed on 24 August 2026. All existing names were
retained.

## Scope and sources

Each name was checked manually against entries in:

- [Bokmålsordboka](https://ordbokene.no/), maintained by the Language Council
  of Norway and the University of Bergen
- [Det Norske Akademis ordbok (NAOB)](https://naob.no/)
- [Store norske leksikon (SNL)](https://snl.no/oversikt_over_grunnstoffene)
- [Nynorskordboka](https://ordbokene.no/), as a supplementary record of the
  corresponding Nynorsk headword

Bokmålsordboka is the primary spelling authority for the `nb_NO` locale. NAOB
and SNL were used for corroboration and for specialist names not necessarily
covered in every general dictionary. Nynorsk forms do not determine the
Bokmål decision, but they were recorded for possible future localisation.

The links in the worksheet point to the entries actually inspected. A few
sources use disambiguated URLs even though the displayed headword is identical
to the Periodisk name.

## Files

[`review.json`](review.json) is the structured audit record. It contains one
record per element in atomic-number order, including the reviewed name, source
headwords and URLs, decision, and notes. Its format is described by
[`review.schema.json`](review.schema.json).

[`REVIEW_TABLE.md`](REVIEW_TABLE.md) is a generated, browser-friendly view of
the audit. Regenerate it after changing the JSON record with:

```console
python scripts/render_norwegian_name_review_markdown.py
```

Validate the record against the runtime locale and element dataset with:

```console
python scripts/validate_norwegian_name_review.py
```

## Runtime data

The review record documents the decision but is not read during rendering.
The runtime source of truth remains
`src/periodisk/resources/locales/nb_NO.json`. Tests ensure that every retained
name in the audit matches that locale resource, avoiding a second independent
copy of the displayed vocabulary.
