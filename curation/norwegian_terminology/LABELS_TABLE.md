# Norwegian label and explanatory-text review

This file is generated from [`labels.json`](labels.json). Do not edit it
directly. See the [curation README](README.md) for the scope and method.

BM denotes Bokmålsordboka. **Not listed** names sources that were searched
but have no entry for the term. A ` / ` marks a rendered line break.

## Labels

| Key | Reviewed text | Decision | Sources | Not listed | Notes |
|---|---|---|---|---|---|
| `title` | Periodesystemet | Retained | [BM: periodesystem](https://ordbokene.no/bm/periodesystem) · [NAOB: periodesystem](https://naob.no/ordbok/periodesystem) · [SNL: periodesystemet](https://snl.no/periodesystemet) | — | Definite form of periodesystem, as in the SNL headword. |
| `accessible_description` | Liggende periodesystem i {page_size}-format med 118 grunnstoffer. Cellefargene viser kjemisk klassifisering. | Retained | — | — | Editorial screen-reader description; reviewed for grammar and consistency with the visible terms. |
| `atomic_number` | Atomnummer | Retained | [BM: atomnummer](https://ordbokene.no/bm/atomnummer) · [NAOB: atomnummer](https://naob.no/ordbok/atomnummer) · [SNL: atomnummer](https://snl.no/atomnummer) | — | Established term in all three sources. |
| `element_symbol` | Atomsymbol | Retained | [BM: atomsymbol](https://ordbokene.no/bm/atomsymbol) · [NAOB: atomsymbol](https://naob.no/ordbok/atomsymbol) · [SNL: atomsymbol](https://snl.no/atomsymbol) · [SNL: kjemisk symbol](https://snl.no/kjemisk_symbol) | — | SNL headword; SNL states that kjemisk symbol is the same. |
| `element_name` | Navn | Retained | — | — | Editorial wording with no specialist term to verify. |
| `atomic_weight` | Relativ atommasse / ([ ] = massetall for isotopen med lengst halveringstid) | Changed (was Atommasse ([ ] = massetall for isotopen med lengst halveringstid)) | [SNL: relativ atommasse](https://snl.no/relativ_atommasse) · [SNL: atommasse](https://snl.no/atommasse) · [BM: massetall](https://ordbokene.no/bm/massetall) · [BM: halveringstid](https://ordbokene.no/bm/halveringstid) | — | SNL defines atommasse as the mass of a single atom, usually in u, and relativ atommasse as the dimensionless isotope-averaged value given in the periodic table. The displayed values are CIAAW standard atomic weights. The bracket explanation moves to a second line so the longer label clears the table. |
| `electronegativity` | Elektronegativitet | Retained | [BM: elektronegativitet](https://ordbokene.no/bm/elektronegativitet) · [NAOB: elektronegativitet](https://naob.no/ordbok/elektronegativitet) · [SNL: elektronegativitet](https://snl.no/elektronegativitet) | — | Established term in all three sources. |
| `first_ionisation_energy` | Første ioniseringsenergi | Retained | [SNL: ioniseringsenergi](https://snl.no/ioniseringsenergi) | BM, NAOB | SNL headword. The alternative ionisasjonsenergi was found in none of Bokmålsordboka, NAOB or SNL. |
| `oxidation_states` | Oksidasjonstall (C: −4…+4 = alle heltall) | Retained | [BM: oksidasjonstall](https://ordbokene.no/bm/oksidasjonstall) · [NAOB: oksidasjonstall](https://naob.no/ordbok/oksidasjonstall) · [SNL: oksidasjonstall](https://snl.no/oksidasjonstall) | — | Established term in all three sources. |
| `electron_configuration` | Elektronkonfigurasjon (grunntilstand; beregnet for Rf–Og) | Retained | [NAOB: elektronkonfigurasjon](https://naob.no/ordbok/elektronkonfigurasjon) · [SNL: elektronkonfigurasjon](https://snl.no/elektronkonfigurasjon) · [NAOB: grunntilstand](https://naob.no/ordbok/grunntilstand) · [SNL: grunntilstand](https://snl.no/grunntilstand) | BM | Both terms are in NAOB and SNL. |
| `radioactive` | Ingen stabile isotoper | Retained | [BM: isotop](https://ordbokene.no/bm/isotop) · [SNL: isotop](https://snl.no/isotop) | — | Plain description; isotop is established. |
| `unknown_chemistry` | Ufullstendig karakterisert | Retained | [BM: karakterisere](https://ordbokene.no/bm/karakterisere) · [NAOB: karakterisere](https://naob.no/ordbok/karakterisere) | — | Editorial status label. |
| `radioactive_sign` | Radioaktivitetssymbol | Retained | — | BM, NAOB, SNL | Editorial compound. No source has a term for the symbol, and none offers an alternative. |
| `sources` | Kilder | Retained | — | — | Editorial wording with no specialist term to verify. |
| `split_classification` | To klassifiseringer | Retained | [BM: klassifisering](https://ordbokene.no/bm/klassifisering) · [NAOB: klassifisering](https://naob.no/ordbok/klassifisering) | — | Editorial legend label. |

## Source notes

| Key | Reviewed text | Decision | Sources | Not listed | Notes |
|---|---|---|---|---|---|
| `atomic_masses` | relative atommasser | Changed (was atommasser) | [SNL: relativ atommasse](https://snl.no/relativ_atommasse) | — | Follows the label change; CIAAW publishes standard atomic weights, which SNL calls relativ atommasse. |
| `ionisation_energies` | ioniseringsenergier | Retained | [SNL: ioniseringsenergi](https://snl.no/ioniseringsenergi) | — | Plural of the SNL headword. |
| `pauling` | CRC Handbook (Pauling-elektronegativitet) | Retained | [SNL: elektronegativitet](https://snl.no/elektronegativitet) | — | Names the source and scale. |
| `allred-rochow` | Allred–Rochow/Pyykkö (beregnet elektronegativitet) | Retained | [SNL: elektronegativitet](https://snl.no/elektronegativitet) | — | Names the source and scale. |
| `allen` | Allen/Mendeleev 1.2.0 (skalert Allen-elektronegativitet) | Changed (was Allen/Mendeleev 1.2.0 (reskalert Allen-elektronegativitet)) | [BM: skalere](https://ordbokene.no/bm/skalere) · [NAOB: skalere](https://naob.no/ordbok/skalere) | — | Reskalere is in neither Bokmålsordboka nor NAOB; skalere is in both. The values are Allen energies multiplied by 0.169. |
| `electron_configurations` | elektronkonfigurasjoner; Ds og Rg fra nyere beregninger | Retained | [SNL: elektronkonfigurasjon](https://snl.no/elektronkonfigurasjon) | — | Names the source and the newer calculations for Ds and Rg. |
| `oxidation_states` | Oksidasjonstall: utvalg bearbeidet fra Mendeleev 1.2.0 | Retained | [SNL: oksidasjonstall](https://snl.no/oksidasjonstall) | — | Names the source and the editorial selection. |

## Units

| Key | Reviewed text | Decision | Sources | Not listed | Notes |
|---|---|---|---|---|---|
| `first_ionisation_energy` | kJ/mol | Retained | — | — | SI unit symbol; language-independent. |
