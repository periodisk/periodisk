# Oxidation-state curation

This directory records how oxidation states were selected for the compact
general-chemistry table. Curation is separate from the runtime package:
rendering uses the reviewed offline dataset and makes no network requests.

The element-by-element review is complete for release 2026.1: all 118 records
are marked `reviewed`, and the selected values have been applied to the runtime
dataset.

## Scope and selection policy

The selection is editorial and is not intended to enumerate every reported
oxidation state. Include a state when a named compound or ion demonstrates it
and it is useful for introductory inorganic, aqueous, environmental,
industrial, periodic-trend, or redox chemistry.

Normally exclude states known only from isolated atoms, unusual matrices,
extreme conditions, transient intermediates, or theoretical predictions. Do
not infer states for insufficiently characterised superheavy elements.

Additional rules are:

- treat Mendeleev `main` and `additional` values as candidates, not approved
  facts;
- permit a documented override when a selected state is absent from the
  Mendeleev lists;
- prefer no more than five states per element;
- normally omit zero, because every element already has state zero in its
  elemental form;
- sort selected states numerically and remove duplicates; and
- require a representative species and a teaching rationale for every
  selected value.

Carbon is the compact-display exception: every integer from −4 through +4 is
retained and rendered as `−4…+4`. Nitrogen's six-value teaching selection is
the exception to the preferred five-state limit.

The optional `principal` list is reserved for a possible future edition that
emphasises a smaller subset typographically. It is currently empty and is not
rendered.

## Sources and limitations

Mendeleev 1.2.0 supplied the initial candidates. The revision-pinned Wikipedia
snapshot in `wikipedia.json` was retained for comparison; neither source was
copied automatically into the final `print` lists.

[Chemdex](https://winter.group.shef.ac.uk/chemdex/) was consulted informally
during the exploratory review, but its distributions were not imported,
stored, or cited as support for the final selections. No documented bulk
export or clear database-reuse licence was identified, so the project did not
use Chemdex as a curation or runtime data source.

The worksheet contains 210 selected oxidation-state values; carbon's nine
values are displayed compactly as the range `−4…+4`. For each selected value,
the worksheet records a representative compound or ion, a short inclusion
rationale, and a citation identifier. These identifiers refer to Housecroft
and Sharpe, *Inorganic Chemistry* (2018), Greenwood and Earnshaw, *Chemistry of
the Elements* (1997), or the IUPAC 2016 definition of oxidation state.

The citations are broad rather than page-specific. They should be treated as
intended supporting references, not as confirmation that each source was
checked for the exact representative species. The records document teaching
choices; they do not establish the frequency of a state or constitute an
independent literature review. See the repository-level
[`DATA_SOURCES.md`](../../docs/DATA_SOURCES.md) for full citations.

## Worksheet

`review.json` contains one record per element. It preserves the Mendeleev and
Wikipedia comparison lists alongside the selected `print` list, support
records, notes, status, reviewer, and review date. Its format is defined by
`review.schema.json`; registered citation details are in `sources.json`.

[`REVIEW_TABLE.md`](REVIEW_TABLE.md) is a generated, browser-friendly view of
the worksheet. It contains an element-by-state matrix linked to a detailed
table of representatives, inclusion rationales, and citations. Regenerate it
after changing the worksheet with:

```console
python scripts/render_oxidation_review_markdown.py
```

A selected value uses its signed integer as the support-record key:

```json
"print": [2, 3, 6],
"evidence": {
  "2": {
    "representative": "FeO",
    "reason": "Common iron(II) chemistry",
    "source": "reference-id"
  }
}
```

Validate the completed worksheet with:

```console
python scripts/validate_oxidation_review.py --complete
```

## Refreshing comparison data

Refresh the Wikipedia snapshot explicitly when required, then regenerate the
comparison fields while preserving review decisions:

```console
python scripts/collect_wikipedia_oxidation_states.py
python scripts/generate_oxidation_review.py
```

The collector uses the MediaWiki API. For a reproducible offline run, save an
API response and pass it with `--input`. Use the generator's `--fresh` option
only when intentionally discarding all existing review decisions.

## Applying decisions

Apply reviewed values to the runtime dataset with:

```console
python scripts/apply_oxidation_review.py --complete
```

Use `--dry-run` to validate without writing. Applied values cite
`curated-oxidation-states-2026.1`; the supporting review notes remain in
`review.json`.
