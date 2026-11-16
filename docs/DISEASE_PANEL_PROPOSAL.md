# GENOVA AI — Proposed v1 Disease Panel (DRAFT, NOT VALIDATED)

Status: **PROPOSAL ONLY.** No risk number below goes into the calculation engine until it has been checked against the primary source (exact table, page, population, year) and signed off (see §4).

How to read this:
- **Inheritance pattern**: well established, taken from MedlinePlus Genetics / GeneReviews / OMIM. Safe to use for exact Mendelian calculations when the user enters **lab-confirmed** genotypes.
- **Regional evidence**: candidate figures from the literature, used **only** when a parent's status is unknown (population estimate). Shown as ranges, never as one exact number. Every figure is marked `TO VALIDATE`.

---

## 1. Proposed panel

| # | Condition | Gene(s) | Inheritance | Why included |
|---|---|---|---|---|
| 1 | β-thalassaemia | HBB | Autosomal recessive | User-requested; very common in Mediterranean, Middle East, South Asia |
| 2 | Sickle cell disease | HBB (HbS) | Autosomal recessive | In old app; high frequency in Africa, Gulf (esp. Eastern Province KSA), India |
| 3 | G6PD deficiency | G6PD | X-linked (recessive pattern; heterozygous females can be affected) | User-requested; very common in Gulf |
| 4 | Cystic fibrosis | CFTR | Autosomal recessive | In old app; most common severe AR disease in Europeans |
| 5 | Haemophilia A | F8 | X-linked recessive | In old app |
| 6 | Duchenne muscular dystrophy | DMD | X-linked recessive | In old app |
| 7 | Spinal muscular atrophy (5q) | SMN1 | Autosomal recessive | Common pan-ethnic carrier frequency; included in many screening panels |
| 8 | Phenylketonuria | PAH | Autosomal recessive | Newborn-screened worldwide; high in parts of Europe & Middle East |
| 9 | Tay-Sachs disease | HEXA | Autosomal recessive | Classic population-specific carrier screening example |
| 10 | Red-green colour vision deficiency | OPN1LW / OPN1MW | X-linked recessive | In old app. **Labelled as a trait, not a disease.** |

Kept outside the panel, as a separate "population statistic" card: **Down syndrome** (in the old app). It's chromosomal and mostly *not inherited*. Risk depends on maternal age, from a cited age table.

Alternatives if you want to swap any item: α-thalassaemia (HBA1/HBA2, complex: 4 genes), haemophilia B (F9), familial Mediterranean fever (MEFV), congenital adrenal hyperplasia (CYP21A2).

---

## 2. Per-condition detail

### 1. β-thalassaemia
- **Inheritance:** AR. Two carriers: 1/4 affected, 1/2 carrier, 1/4 non-carrier per pregnancy.
- **Regional evidence (TO VALIDATE):** Haemoglobin-disorder carriers are concentrated in Africa, the Eastern Mediterranean and South-East Asia, and much less common in Northern Europe (Modell & Darlison 2008). Country-level β-thal carrier rates in the Middle East range roughly from low single digits to above 10%, depending on the country and study.
- **Limitations:** Severity varies (major vs intermedia); co-inheritance with HbS or α-thal changes the outcome. Carrier status needs lab testing (CBC + HbA2/HPLC).
- **Sources:**
  - MedlinePlus Genetics — Beta thalassemia: https://medlineplus.gov/genetics/condition/beta-thalassemia/
  - GeneReviews — β-Thalassemia (NBK1426): https://www.ncbi.nlm.nih.gov/books/NBK1426/
  - Modell B, Darlison M. Global epidemiology of haemoglobin disorders. *Bull WHO* 2008;86:480–487. https://pmc.ncbi.nlm.nih.gov/articles/PMC2647473/

### 2. Sickle cell disease
- **Inheritance:** AR (HbSS). HbS combined with β-thal or HbC also causes sickling disease, and the engine will model these combinations.
- **Regional evidence (TO VALIDATE):** HbS carrier frequency is highest in sub-Saharan Africa and is also high in parts of the Gulf (notably Eastern Province of Saudi Arabia), India and the Mediterranean (Modell & Darlison 2008; Saudi premarital screening reports).
- **Limitations:** Clinical severity varies a lot (HbF levels, α-thal co-inheritance).
- **Sources:**
  - MedlinePlus Genetics — Sickle cell disease: https://medlineplus.gov/genetics/condition/sickle-cell-disease/
  - GeneReviews — Sickle Cell Disease (NBK1377): https://www.ncbi.nlm.nih.gov/books/NBK1377/
  - CDC — Sickle cell disease: https://www.cdc.gov/sickle-cell/
  - Modell & Darlison 2008 (above)

### 3. G6PD deficiency
- **Inheritance:** X-linked. Hemizygous males with a deficient allele are deficient. Heterozygous females can range from normal to fully deficient, because of X-inactivation. So **female risk is shown as a range, not an exact %.**
- **Regional evidence (TO VALIDATE):** Saudi studies vary widely by region and method. Examples: about 9% of males / 4% of females nationally (Ann Saudi Med 2001), much higher in the Eastern Province (Qatif and Al-Hassa studies), and lower in Al-Qassim. Other Gulf states (UAE, Oman, Kuwait) report wide ranges. Global distribution follows historic malaria regions (Howes et al. 2012, *PLoS Med*).
- **Limitations:** Mostly symptom-free until triggered (fava beans, some medicines, infections). Severity depends on the variant (e.g. Mediterranean vs A−).
- **Sources:**
  - MedlinePlus Genetics — G6PD deficiency: https://medlineplus.gov/genetics/condition/glucose-6-phosphate-dehydrogenase-deficiency/
  - Howes RE et al. G6PD deficiency prevalence and estimates of affected populations in malaria endemic countries. *PLoS Med* 2012;9(11):e1001339.
  - Saudi regional studies (Ann Saudi Med 2001 doi:10.5144/0256-4947.2001.174; Eastern Province newborn screening studies).

### 4. Cystic fibrosis
- **Inheritance:** AR.
- **Regional evidence (TO VALIDATE):** About 1 in 25 carriers in people of Northern/Western European ancestry (range ~1/20–1/32 by country; Ireland higher). Middle East data are sparse and use different mutation spectra, so they need a separate validated source. Lower in East Asia and sub-Saharan Africa.
- **Limitations:** Carrier panels detect a variable share of CFTR variants depending on ancestry, so a negative carrier test leaves a residual risk.
- **Sources:**
  - MedlinePlus Genetics — Cystic fibrosis: https://medlineplus.gov/genetics/condition/cystic-fibrosis/
  - GeneReviews — CFTR-Related Disorders (NBK1250): https://www.ncbi.nlm.nih.gov/books/NBK1250/
  - WHO Human Genetics Programme, The molecular genetic epidemiology of cystic fibrosis (2004): https://iris.who.int/handle/10665/68702

### 5. Haemophilia A
- **Inheritance:** X-linked recessive. Carrier mother × unaffected father: each son 1/2 affected, each daughter 1/2 carrier.
- **Regional evidence:** 1 in 4,000 to 1 in 5,000 males worldwide (MedlinePlus, verified June 2026). Region choice doesn't change it.
- **Limitations:** About 1/3 of cases are new mutations with no family history. Some carrier females have mild bleeding.
- **Sources:**
  - MedlinePlus Genetics — Hemophilia: https://medlineplus.gov/genetics/condition/hemophilia/
  - GeneReviews — Hemophilia A (NBK1404): https://www.ncbi.nlm.nih.gov/books/NBK1404/
  - CDC — Hemophilia: https://www.cdc.gov/hemophilia/

### 6. Duchenne muscular dystrophy
- **Inheritance:** X-linked recessive.
- **Regional evidence:** Duchenne **and Becker together** affect 1 in 3,500–5,000 newborn males worldwide (MedlinePlus, verified June 2026). The Duchenne-only figure needs a separate source. No strong regional variation.
- **Limitations:** About 1/3 of cases are new mutations. A mother can carry it in her eggs only (gonadal mosaicism), so recurrence risk isn't zero even if her blood test is negative.
- **Sources:**
  - MedlinePlus Genetics — Duchenne and Becker muscular dystrophy: https://medlineplus.gov/genetics/condition/duchenne-and-becker-muscular-dystrophy/
  - GeneReviews — Dystrophinopathies (NBK1119): https://www.ncbi.nlm.nih.gov/books/NBK1119/

### 7. Spinal muscular atrophy (5q)
- **Inheritance:** AR.
- **Regional evidence (TO VALIDATE):** Pan-ethnic carrier frequency about 1/54 in a large US study (Sugarman et al. 2012, *Eur J Hum Genet*). Ethnic-specific values were about 1/47 to 1/72.
- **Limitations:** Some carriers (2 SMN1 copies on one chromosome) aren't detected by standard testing, so a negative test leaves a residual risk. SMN2 copy number affects severity.
- **Sources:**
  - MedlinePlus Genetics — Spinal muscular atrophy: https://medlineplus.gov/genetics/condition/spinal-muscular-atrophy/
  - GeneReviews — Spinal Muscular Atrophy (NBK1352): https://www.ncbi.nlm.nih.gov/books/NBK1352/
  - Sugarman EA et al. Pan-ethnic carrier screening and prenatal diagnosis for SMA. *Eur J Hum Genet* 2012;20:27–32. https://www.nature.com/articles/ejhg2011134

### 8. Phenylketonuria (PKU)
- **Inheritance:** AR.
- **Regional evidence (TO VALIDATE):** Global birth prevalence about 1:23,930 (Hillert et al. 2020, *AJHG*), about 1:10,000 in Europe, and higher in some countries (e.g. Italy, Ireland, Turkey, Iran, Jordan). The carrier frequency would be *derived* from prevalence (Hardy-Weinberg), and the report will say that it's derived.
- **Limitations:** Newborn screening and diet make outcomes very good. Severity varies by PAH variant.
- **Sources:**
  - MedlinePlus Genetics — Phenylketonuria: https://medlineplus.gov/genetics/condition/phenylketonuria/
  - GeneReviews — Phenylalanine Hydroxylase Deficiency (NBK1504): https://www.ncbi.nlm.nih.gov/books/NBK1504/
  - Hillert A et al. The genetic landscape and epidemiology of phenylketonuria. *Am J Hum Genet* 2020;107:234–250. https://pubmed.ncbi.nlm.nih.gov/32668217/

### 9. Tay-Sachs disease
- **Inheritance:** AR.
- **Regional evidence (TO VALIDATE):** Carrier frequency about 1/27–1/30 in Ashkenazi Jewish ancestry, versus about 1/250–1/300 in the general population. Also elevated in some other founder populations.
- **Limitations:** Ancestry-specific. For most GENOVA users the default population estimate will be low.
- **Sources:**
  - MedlinePlus Genetics — Tay-Sachs disease: https://medlineplus.gov/genetics/condition/tay-sachs-disease/
  - GeneReviews — Hexosaminidase A Deficiency (NBK1218): https://www.ncbi.nlm.nih.gov/books/NBK1218/
  - NHGRI — Tay-Sachs disease: https://www.genome.gov/Genetic-Disorders/Tay-Sachs-Disease

### 10. Red-green colour vision deficiency (trait)
- **Inheritance:** X-linked recessive.
- **Regional evidence:** About 1 in 12 men and 1 in 200 women of Northern European ancestry. Also common in East Asian populations and less common in most others (MedlinePlus, verified June 2026). Other regions are TO VALIDATE.
- **Limitations:** A trait, not a disease. Several subtypes exist.
- **Sources:**
  - MedlinePlus Genetics — Color vision deficiency: https://medlineplus.gov/genetics/condition/color-vision-deficiency/

### Separate card: Down syndrome (not part of the carrier panel)
- Chromosomal (trisomy 21), mostly sporadic. Risk rises with maternal age. A small share are inherited translocations, and this will be stated.
- Source to validate: Morris JK et al. Comparison of models of maternal age-specific risk for Down syndrome live births. *Prenat Diagn* 2003. MedlinePlus Genetics — Down syndrome: https://medlineplus.gov/genetics/condition/down-syndrome/

---

## 3. What the engine will and won't do

- **Will:** compute exact Mendelian outcomes from confirmed genotypes (AR, X-linked). Combine them with a *validated* regional carrier range only when a parent's status is unknown. Show assumptions, residual risk and sources.
- **Won't:** use any figure marked `TO VALIDATE`, or give a single "your risk is X%" without stating the tier and the range. It also won't model a disease that has no validated source.

## 4. Validation process (before any figure goes live)

1. For each figure: record the primary source, exact table/page, population, sample size, year and method in `backend/app/genetics/data/frequencies.json`.
2. A second reviewer re-checks each entry against the source. A qualified genetic counsellor or clinical geneticist is strongly recommended; this must be you or someone you appoint.
3. Automated tests fail if any entry lacks a source, a population label or a reviewed-by field.
4. Each entry has `status: draft | validated`. Only `validated` entries are used in calculations. Draft regions show "No validated data for this region yet. Please get carrier testing."
5. Data are versioned. Every report prints the data version used.

## 5. Link check (June 2026)

| Source | Status |
|---|---|
| All 12 MedlinePlus Genetics pages | ✅ Opened, correct titles |
| Nature, Sugarman 2012 (SMA) | ✅ Opened, correct title |
| NHGRI genome.gov Tay-Sachs | ✅ Opened |
| PubMed 32668217 (Hillert 2020) | ✅ Reachable |
| NCBI GeneReviews (8 chapters), PMC Modell 2008, CDC, WHO IRIS | ⚠️ These sites block automated checks. Each needs a manual check during validation. |
