# Electron-configuration curation

Reviewed 2026-08-12. Scope: neutral gaseous atoms, Z = 104–118.

These configurations are calculated assignments, not direct electron counts.
The compact notation also hides spin–orbit splitting and configuration mixing.

## Decisions

| Z | Element | Reviewed configuration | Decision |
|---:|:---:|---|---|
| 104 | Rf | `[Rn]5f¹⁴6d²7s²` | Retain Mendeleev; agrees with NIST[^nist] |
| 105 | Db | `[Rn]5f¹⁴6d³7s²` | Retain Mendeleev; agrees with NIST[^nist] |
| 106 | Sg | `[Rn]5f¹⁴6d⁴7s²` | Retain Mendeleev; agrees with NIST[^nist] |
| 107 | Bh | `[Rn]5f¹⁴6d⁵7s²` | Retain Mendeleev; agrees with NIST[^nist] |
| 108 | Hs | `[Rn]5f¹⁴6d⁶7s²` | Retain Mendeleev; agrees with NIST[^nist] |
| 109 | Mt | `[Rn]5f¹⁴6d⁷7s²` | Retain Mendeleev[^dzuba-mt] |
| 110 | Ds | `[Rn]5f¹⁴6d⁸7s²` | Override Mendeleev[^hoffman] |
| 111 | Rg | `[Rn]5f¹⁴6d⁹7s²` | Override Mendeleev[^kaygorodov] |
| 112 | Cn | `[Rn]5f¹⁴6d¹⁰7s²` | Retain Mendeleev[^kaygorodov] |
| 113 | Nh | `[Rn]5f¹⁴6d¹⁰7s²7p¹` | Retain Mendeleev[^kaygorodov] |
| 114 | Fl | `[Rn]5f¹⁴6d¹⁰7s²7p²` | Retain Mendeleev[^kaygorodov] |
| 115 | Mc | `[Rn]5f¹⁴6d¹⁰7s²7p³` | Retain Mendeleev[^hoffman] |
| 116 | Lv | `[Rn]5f¹⁴6d¹⁰7s²7p⁴` | Retain Mendeleev[^lv-ts] |
| 117 | Ts | `[Rn]5f¹⁴6d¹⁰7s²7p⁵` | Retain Mendeleev[^lv-ts] |
| 118 | Og | `[Rn]5f¹⁴6d¹⁰7s²7p⁶` | Retain Mendeleev[^oganesson] |

Mendeleev 1.2.0 gives `[Rn]5f¹⁴6d⁹7s¹` for Ds and
`[Rn]5f¹⁴6d¹⁰7s¹` for Rg. Modern relativistic calculations instead favour the
`7s²` assignments shown above. These two overrides are applied in the packaged
dataset and its preparation script. Their provenance cites the supporting
publications rather than Mendeleev.

All configurations from Rf to Og are labelled as calculated in the printed
legend and as predicted in the data records.

## References

[^nist]: NIST, [*Ground Levels and Ionization Energies for the Neutral Atoms*,
    Rf–Hs](https://www.nist.gov/pml/ground-levels-and-ionization-energies-neutral-atoms),
    [doi:10.18434/T42P4C](https://doi.org/10.18434/T42P4C).

[^dzuba-mt]: V. A. Dzuba et al., theoretical spectra of Sg, Bh, Hs, and Mt
    (2019), [arXiv:1902.06819](https://arxiv.org/abs/1902.06819).

[^hoffman]: D. C. Hoffman, D. M. Lee, and V. Pershina, “Transactinides and the
    Future Elements,” in *The Chemistry of the Actinide and Transactinide
    Elements*, 3rd ed. (2006),
    [doi:10.1007/1-4020-3598-5_14](https://doi.org/10.1007/1-4020-3598-5_14).

[^kaygorodov]: M. Y. Kaygorodov et al., “Ionization potentials and electron
    affinities of Rg, Cn, Nh, and Fl superheavy elements,” *Physical Review A*
    **105**, 062805 (2022),
    [doi:10.1103/PhysRevA.105.062805](https://doi.org/10.1103/PhysRevA.105.062805).

[^lv-ts]: “Electronic structure calculation for superheavy elements
    Livermorium and Tennessine and their lighter analogs” (2025),
    [arXiv:2505.22895](https://arxiv.org/abs/2505.22895).

[^oganesson]: V. A. Dzuba et al., “Atomic structure calculations of
    superheavy noble element oganesson,” *Physical Review A* **98**, 042504
    (2018), [arXiv:1809.02325](https://arxiv.org/abs/1809.02325).
