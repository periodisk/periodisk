# Scientific data and provenance

This file records the scientific data decisions behind the packaged dataset,
which was initially prepared for release 2026.1 and remains the basis of current
releases. Subsequent changes are recorded in the project
[changelog](../CHANGELOG.md). The packaged JSON is an offline snapshot:
rendering does not access the network or import Mendeleev. Machine-readable
citations and access dates are kept in the
[source registry](../src/periodisk/resources/sources.json).
Oxidation-state selections and their supporting review notes are kept in the
[curation worksheet](../curation/oxidation_states/review.json).

The project's CC BY 4.0 content licence applies only to the project's original
contributions. It does not grant rights in third-party source material. See
[`THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md).

Atomic numbers, symbols, periods, groups, and British English names follow the
IUPAC periodic table dated 4 May 2022.[^iupac-table] Element names are stored
once, in the corresponding locale resource. Bokmål names are a reviewed
project list, with
[Wikipedia](https://no.wikipedia.org/wiki/Periodesystemet),
[Store norske leksikon](https://snl.no/periodesystemet), and
[periodesystemet.no](https://www.periodesystemet.no/) used for comparison.

## Atomic weights

For elements with a standard atomic weight, the dataset-preparation script
uses one value from CIAAW's **Abridged Standard Atomic Weights 2024**
table.[^ciaaw-weights] For example, hydrogen is displayed as `1.0080`.
CIAAW's uncertainty is retained in the JSON but is not printed in the compact
cell.

For other elements, the bracketed number is a mass number from CIAAW's
radioactive-elements table, based on NUBASE2020.[^ciaaw-radioactive][^nubase]
During dataset preparation, the project selects the isotope with the largest
recommended central half-life after normalising the time units. This is not a
standard atomic weight. Overlapping half-life uncertainties can mean that no
single isotope is demonstrably the longest-lived. CIAAW explicitly gives
Tc-97/Tc-98 and Mt-277/Mt-278 as examples. Inspection of CIAAW's published
symmetric one-standard-uncertainty ranges suggests the same caution for the
listed isotope pairs of Sg, Bh, Hs, and Mc (this is a project inference, not
an additional CIAAW determination).

The packaged dataset nevertheless needs one compact value, so the preparation
script consistently chooses the isotope with the largest reported central
half-life. The rendered table therefore displays `[97]` for Tc, `[269]` for
Sg, `[270]` for Bh, `[269]` for Hs, `[277]` for Mt, and `[290]` for Mc. For
these elements, the brackets identify the project's
representative choice. They do not imply that the selected isotope has been
shown conclusively to outlive every listed alternative.

## First ionisation energy

Neutral-atom first ionisation energies are imported from the NIST Atomic
Spectra Database snapshot distributed by Mendeleev 1.2.0. Mendeleev stores the
values in eV.[^nist-asd][^mendeleev] During dataset preparation, the values are
converted to **kJ/mol** using
`1 eV/particle = 96.48533212331002 kJ/mol` and rounded to 0.001 kJ/mol. This
factor follows from the exact post-2019 definitions of the electronvolt and
the Avogadro constant.[^si-brochure] A null value means that the source snapshot
supplied no value (it does not mean zero).

## Electronegativity

Pauling values are the CRC Handbook values distributed by Mendeleev
1.2.0.[^mendeleev][^crc]
Absent values remain absent.

Allen electronegativities are the valence-shell configuration energies, in
eV, distributed by Mendeleev and attributed to Allen's 1989
definition.[^mendeleev][^allen]
For compact display, the dataset-preparation script multiplies them by `0.169`
and rounds to two decimal places. This places the values in a Pauling-like
numerical range but does not convert them into Pauling electronegativities or
change their ordering. Values are available for 71 elements, from H to Rn
with gaps.

Allred–Rochow values are calculated rather than independently tabulated. The
dataset-preparation script applies

$$
\chi_{\mathrm{AR}} = 0.359\frac{Z_{\mathrm{eff}}}{r^2} + 0.744
$$

with $r$ expressed in ångströms, using Slater effective nuclear charges and
Pyykkö single-bond covalent radii from Mendeleev
1.2.0.[^allred-rochow][^slater][^pyykko] Results are rounded to two decimal
places. Because
these are not the radii available to Allred and Rochow in 1958, the output is
labelled as a calculated modern variant, not an experimental measurement.

## Electron configurations

Neutral-atom ground-state configurations are imported from Mendeleev 1.2.0
and displayed in noble-gas abbreviated form. Configurations for Z = 104–118
are labelled as calculated because assignments for these short-lived elements
depend on theoretical evaluation.

An audit against NIST and modern relativistic calculations found two
Mendeleev discrepancies. Ds is overridden as `[Rn] 5f14 6d8 7s2`, following
Hoffman, Lee, and Pershina (2006),[^hoffman] and Rg as `[Rn] 5f14 6d9 7s2`,
following Kaygorodov et al. (2022).[^kaygorodov] The evidence and decisions are
recorded in the
[electron-configuration audit](../curation/electron_configurations/README.md).

## Oxidation states

The printed oxidation states are an editorial teaching selection covering all
118 elements. Mendeleev 1.2.0 supplied the initial candidates, while a
revision-pinned Wikipedia snapshot[^wikipedia-oxidation] was retained for
comparison. Neither list was copied automatically. The final printed lists
record the decisions made during the element-by-element review.

The worksheet contains 210 selected oxidation-state values. Carbon's nine
values are displayed compactly as the range `−4…+4`. For each selected value,
the worksheet records a representative compound or ion, a short inclusion
rationale, and a citation identifier. These identifiers refer to Housecroft
and Sharpe, *Inorganic Chemistry* (2018),[^housecroft] Greenwood and Earnshaw,
*Chemistry of the Elements* (1997),[^greenwood] or the IUPAC 2016 definition
of oxidation state.[^iupac-oxidation]

The selections and their supporting evidence are listed in the
[oxidation-state review table](../curation/oxidation_states/REVIEW_TABLE.md).

The selection is intended for general-chemistry teaching and is not an
inventory of every reported state. Zero is normally omitted. Carbon is the
documented exception and is printed as the range `−4…+4`. An empty list is a
reviewed editorial decision, not missing data. Rn and Db–Og remain blank
because their compound chemistry does not meet the project's inclusion
threshold. Rf(+4), supported by tracer-scale chloride-complex chemistry, is
the sole printed state above the actinoids. The full rules are in the
[curation README](../curation/oxidation_states/README.md).

## Radioactivity

The radioactive symbol means that an element has no stable isotopes, not
merely that radioactive isotopes exist. The flag follows NUBASE2020[^nubase]
and is set for Tc, Pm, and every element from Bi through Og. Bi is included
because Bi-209 is radioactive, despite its extremely long half-life and the
existence of a CIAAW standard atomic weight for naturally occurring bismuth.

## Classifications

Colour categories and split categories are editorial classifications, not
measured properties. Po is shown as both a post-transition metal and a
metalloid. At is shown as both a halogen and a metalloid. Mt, Ds, Rg, Lv, Ts,
and Og are marked as insufficiently characterised, so the renderer gives them
a neutral fill while retaining their conventional families for table
placement and navigation.

## References

[^iupac-table]: IUPAC, [*Periodic Table of the Elements*, release 4 May
    2022](https://iupac.org/what-we-do/periodic-table-of-elements/).

[^ciaaw-weights]: CIAAW, [*Abridged Standard Atomic Weights
    2024*](https://ciaaw.org/abridged-atomic-weights.htm).

[^ciaaw-radioactive]: CIAAW, [*Radioactive
    Elements*](https://ciaaw.org/radioactive-elements.htm).

[^nubase]: F. G. Kondev et al., “The NUBASE2020 evaluation of nuclear physics
    properties,” *Chinese Physics C* **45**, 030001 (2021),
    [doi:10.1088/1674-1137/abddae](https://doi.org/10.1088/1674-1137/abddae).

[^nist-asd]: A. Kramida et al., *NIST Atomic Spectra Database*, version 5.11
    (2023), [doi:10.18434/T4W30F](https://doi.org/10.18434/T4W30F).

[^mendeleev]: L. M. Mentel, [*Mendeleev* 1.2.0 data
    documentation](https://mendeleev.readthedocs.io/en/latest/data.html).

[^allen]: L. C. Allen, “Electronegativity is the average one-electron energy
    of the valence-shell electrons in ground-state free atoms,” *J. Am. Chem.
    Soc.* **111**, 9003–9014 (1989),
    [doi:10.1021/ja00207a003](https://doi.org/10.1021/ja00207a003).

[^allred-rochow]: A. L. Allred and E. G. Rochow, “A scale of
    electronegativity based on electrostatic force,” *J. Inorg. Nucl. Chem.*
    **5**, 264–268 (1958),
    [doi:10.1016/0022-1902(58)80003-2](https://doi.org/10.1016/0022-1902(58)80003-2).

[^slater]: J. C. Slater, “Atomic shielding constants,” *Phys. Rev.* **36**,
    57–64 (1930),
    [doi:10.1103/PhysRev.36.57](https://doi.org/10.1103/PhysRev.36.57).

[^pyykko]: P. Pyykkö and M. Atsumi, “Molecular single-bond covalent radii for
    elements 1–118,” *Chem. Eur. J.* **15**, 186–197 (2009),
    [doi:10.1002/chem.200800987](https://doi.org/10.1002/chem.200800987).

[^hoffman]: D. C. Hoffman, D. M. Lee, and V. Pershina, “Transactinides and the
    future elements,” in *The Chemistry of the Actinide and Transactinide
    Elements* (2006),
    [doi:10.1007/1-4020-3598-5_14](https://doi.org/10.1007/1-4020-3598-5_14).

[^kaygorodov]: M. Y. Kaygorodov et al., “Ionization potentials and electron
    affinities of Rg, Cn, Nh, and Fl superheavy elements,” *Phys. Rev. A*
    **105**, 062805 (2022),
    [doi:10.1103/PhysRevA.105.062805](https://doi.org/10.1103/PhysRevA.105.062805).

[^iupac-oxidation]: P. Karen et al., “Comprehensive definition of oxidation
    state,” *Pure Appl. Chem.* **88**, 831–839 (2016),
    [doi:10.1515/pac-2015-1204](https://doi.org/10.1515/pac-2015-1204).

[^crc]: W. M. Haynes (ed.), *CRC Handbook of Chemistry and Physics*, 95th ed.
    (CRC Press, 2014).

[^housecroft]: C. E. Housecroft and A. G. Sharpe, *Inorganic Chemistry*, 5th
    ed. (Pearson, 2018), ISBN 978-1-292-13414-7.

[^greenwood]: N. N. Greenwood and A. Earnshaw, *Chemistry of the Elements*,
    2nd ed. (Butterworth-Heinemann, 1997), ISBN 978-0-7506-3365-9.

[^wikipedia-oxidation]: Wikipedia contributors, [“Template:List of oxidation
    states of the elements,” revision
    1340524841](https://en.wikipedia.org/w/index.php?title=Template:List_of_oxidation_states_of_the_elements&oldid=1340524841)
    (comparison source, CC BY-SA 4.0).

[^si-brochure]: BIPM, *The International System of Units (SI)*, 9th ed. (2019,
    updated 2026),
    [doi:10.59161/AUEZ1291](https://doi.org/10.59161/AUEZ1291).
