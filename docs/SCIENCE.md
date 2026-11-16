# Science & methods (engine v1.0.0)

Rules enforced by `backend/tests/test_scientific_integrity.py`:
- No random numbers anywhere in `genova/genetics` (source scan).
- Every probability is an exact `fractions.Fraction`; every outcome group sums to exactly 1.
- Same input gives the same output.
- Every result carries references that exist in `references.json` and starts its limitations with "not a diagnosis".
- Regional data entries need a source; `validated` entries need `reviewed_by`. Only validated entries are used.

| Calculator | Tier | Method | Source |
|---|---|---|---|
| Single gene | established | Punnett square, equal gamete probability | MedlinePlus inheritance patterns |
| Blood type | established | ABO (A,B,O) × RhD (D,d), independent loci. Phenotype input gives ranges over compatible genotypes and a possible/impossible list | MedlinePlus blood typing; Dean 2005 (NCBI) |
| Carrier risk, confirmed statuses | established | AR or X-linked Punnett | MedlinePlus, GeneReviews per condition |
| Carrier risk, unknown status | established (conditional) | One exact scenario per possible genotype of the untested parent | as above |
| Carrier risk, population | population_estimate | Scenarios weighted by a **validated** regional carrier frequency. **Currently disabled: all regional data is draft.** | regional source per entry |
| Height | statistical_estimate | Tanner: sons (M+F+13)/2, daughters (M+F−13)/2, ±8.5 cm | Tanner 1970; MedlinePlus |
| Eye / hair colour | uncertain_estimate | Qualitative bands only, every colour listed as possible | MedlinePlus eye/hair colour |
| Boy / girl | population_statistic | 105 boys per 100 girls at birth | Our World in Data / UN WPP; MedlinePlus |

Known simplifications (shown to users): complete penetrance, no de novo mutation, no rare ABO variants (Bombay, cis-AB, weak D), G6PD heterozygous females shown as "variable", and no family-history Bayesian priors yet.

Legacy logic **not** carried over (see audit): random "confidence" values, the family birth-order sex table, keyword-count disease percentages, and averaged trait scores.
