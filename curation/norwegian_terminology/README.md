# Norwegian terminology curation

This directory records the review of the Bokmål terms displayed by Periodisk:

- the 118 element names, reviewed on 24 August 2026; all existing names were
  retained
- the ten detailed and four broad classification terms, reviewed on
  17 November 2026; the detailed `Ikke-metaller` label became
  `Andre ikke-metaller`, and all other terms were retained
- the scientific labels, source notes, and units, reviewed on 18 November
  2026; `Atommasse` became `Relativ atommasse` and `reskalert` became
  `skalert`, and all other text was retained

## Element names

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

## Classification terms

Classification terms were reviewed for both wording and scope: the term must
be established Norwegian usage, and the elements it colours must match how the
sources define it. The sources were:

- Bokmålsordboka, NAOB, and SNL for the Norwegian terms
- [IUPAC *Nomenclature of Inorganic Chemistry* (2005)](https://iupac.org/wp-content/uploads/2016/07/Red_Book_2005.pdf),
  section IR-3.5, for collective names and their membership; its lists predate
  the naming of tennessine and oganesson
- the IUPAC Gold Book definition of *transition element*, cited through ChEBI
  because the Gold Book site blocks automated access
- Norwegian and English Wikipedia for comparison and for categories without an
  authoritative definition

Many general dictionaries have no entry for specialist collective names. A
source listed under `not_listed` was searched and has no entry; that is
recorded as absence of evidence, not as a rejection. `Andre metaller` has no
authoritative Norwegian or IUPAC source and is recorded as an editorial label.

## Labels and explanatory text

Labels were checked against Bokmålsordboka, NAOB, and SNL. Where the
displayed values are a specific quantity, the label must name that quantity:
the table shows CIAAW standard atomic weights, which SNL calls *relativ
atommasse*, whereas *atommasse* is the mass of a single atom. Plain
descriptive or structural text, such as `Navn` and `Kilder`, is recorded as
editorial.

## Files

| Record | Schema | Generated table | Validator |
|---|---|---|---|
| [`review.json`](review.json) (element names) | [`review.schema.json`](review.schema.json) | [`REVIEW_TABLE.md`](REVIEW_TABLE.md) | `scripts/validate_norwegian_name_review.py` |
| [`classifications.json`](classifications.json) | [`classifications.schema.json`](classifications.schema.json) | [`CLASSIFICATIONS_TABLE.md`](CLASSIFICATIONS_TABLE.md) | `scripts/validate_norwegian_classification_review.py` |
| [`labels.json`](labels.json) | [`labels.schema.json`](labels.schema.json) | [`LABELS_TABLE.md`](LABELS_TABLE.md) | `scripts/validate_norwegian_label_review.py` |

Regenerate the tables after changing a JSON record with:

```console
python scripts/render_norwegian_name_review_markdown.py
python scripts/render_norwegian_classification_review_markdown.py
python scripts/render_norwegian_label_review_markdown.py
```

Validate the records against the runtime locale and element dataset with:

```console
python scripts/validate_norwegian_name_review.py
python scripts/validate_norwegian_classification_review.py
python scripts/validate_norwegian_label_review.py
```

The classification validator also checks that each detailed term's recorded
members match `elements.json`, and that each broad term's recorded detailed
categories match the renderer's mapping.

## Runtime data

The review records document decisions but are not read during rendering.
The runtime source of truth remains
`src/periodisk/resources/locales/nb_NO.json`. Tests ensure that every reviewed
term matches that locale resource, avoiding a second independent copy of the
displayed vocabulary.
