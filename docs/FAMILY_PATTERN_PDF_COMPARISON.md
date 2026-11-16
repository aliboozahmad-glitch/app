# Family-pattern rules: original PDF vs current GENOVA

Status: **COMPARISON ONLY. No code or data has been changed.** Waiting for your approval.

Source PDF: `docs/source/family_pattern_rules.pdf` (3 scanned pages, no text layer). It was read with Arabic OCR (Tesseract), and every entry was also checked against the current table and the scan. The OCR dropped one child in case 71; I checked the image and corrected the transcription. Machine-readable transcription: `docs/source/pdf_transcription.json`.

## 1. Entry counts

| | PDF | Current GENOVA |
|---|---|---|
| Section 1: first + second child, 3 + 3 children | cases 1–29 (29) | cases 1–36 (36) |
| Cases 30–40 | **absent** (PDF note: "الأرقام من 30 إلى 40 غير موجودة في النص المرسل") | 30–36 (3 + 3) and 37–40 (1 + 1): **11 entries from your old code** |
| Section 2: one child, 2 + 2 | 41–52 (12) | 41–52 (12) |
| Section 2: wife 1 + husband 2 | 53–60 (8) | 53–60 (8), family split unknown |
| Section 2: wife 2 + husband 1 | **61–68 (8)** | **missing** |
| Section 2: wife 1 + husband 3 | 69–80 (12) | 69–80 (12), family split unknown |
| Section 2: wife 3 + husband 1 | **81–92 (12)** | **missing** |
| **Total** | **81 entries** (1–29, 41–92) | **72 entries** |

## 2. Result differences

- **Cases 1–29:** all 29 match exactly (families and both results).
- **Cases 41–60 and 69–80:** all 32 match. Your old code stored the same answer for "first" and "second", and the PDF gives one child (`طفل`) with that same answer.
- **Cases 61–68 (wife 2 + husband 1):** not in GENOVA as cases. Today these inputs fall back to the 1 + 2 entry with the same combined list. **All 8 currently give the same answer as the PDF**, but they're labelled with the wrong case number and flagged "split unconfirmed".
- **Cases 81–92 (wife 3 + husband 1):** not in GENOVA as cases. Today these inputs fall back to another entry with the same combined list:

| PDF case | Wife | Husband | PDF result | GENOVA today | Same? |
|---|---|---|---|---|---|
| 81 | أنثى أنثى أنثى | أنثى | أنثى | case 69: أنثى | ✅ |
| 82 | ذكر ذكر ذكر | أنثى | ذكر | case 51: ذكر | ✅ |
| 83 | أنثى ذكر أنثى | أنثى | أنثى | case 50: أنثى | ✅ |
| 84 | ذكر أنثى ذكر | أنثى | أنثى | case 75: ذكر | ❌ **different** |
| 85 | أنثى أنثى ذكر | أنثى | أنثى | case 71: أنثى | ✅ |
| 86 | ذكر ذكر أنثى | أنثى | ذكر | case 80: ذكر | ✅ |
| 87 | أنثى ذكر أنثى | ذكر | ذكر | case 72: أنثى | ❌ **different** |
| 88 | ذكر أنثى ذكر | ذكر | ذكر | case 79: ذكر | ✅ |
| 89 | أنثى أنثى أنثى | ذكر | أنثى | case 73: أنثى | ✅ |
| 90 | ذكر ذكر ذكر | ذكر | ذكر | case 78: ذكر | ✅ |
| 91 | أنثى ذكر ذكر | ذكر | ذكر | case 70: ذكر | ✅ |
| 92 | ذكر أنثى أنثى | ذكر | ذكر | no answer (not in table) | ❌ **different** |

So **3 inputs currently give a different answer from your PDF: cases 84, 87 and 92.**

## 3. Other differences

1. **The PDF settles the family split.** Section 2 states it explicitly: 53–60 are wife 1 + husband 2, 61–68 wife 2 + husband 1, 69–80 wife 1 + husband 3, and 81–92 wife 3 + husband 1. Your old code joined both families into one list, which caused the 2 + 2 / 1 + 3 overlap. **None of the 81 PDF entries conflict with each other** once the wife's and husband's families are kept separate.
2. **The 10 "duplicated patterns" aren't duplicates in the PDF.** For example, 41 (ذكر ذكر + ذكر ذكر) and 78 (ذكر + ذكر ذكر ذكر) are different families. They only collided in the old code's joined list.
3. **Section 2 predicts one child only.** GENOVA's "which child" choice (first or second) should apply only to Section 1.
4. **Confidence ranges.** The PDF header states "الطفل الأول بين 70% و90%، والطفل الثاني بين 50% و60%". The old app picked a random number inside these ranges. GENOVA shows none, as you asked earlier. Should the stated ranges be displayed as text, without random numbers?
5. **Entries 30–40 in GENOVA (from your old code, not the PDF):** 7 more 3 + 3 cases and 4 cases with 1 + 1 children. Per your instruction they haven't been deleted. Should they stay as "from the old app, not in the PDF", or be hidden?

## 4. Proposed change (only after your approval)

- Make the PDF (81 entries) the master table, looked up by **wife's family + husband's family separately**. The exact split removes the overlap; nothing is merged.
- Add cases 61–68 and 81–92 exactly as written in the PDF. This changes the answers for 84, 87 and 92 to match the PDF.
- Keep old-code entries 30–40 marked "old app only" (or hide them, as you prefer).
- Section 2 shows a single-child result. Section 1 keeps first/second.
- No random numbers. The confidence ranges are shown as text only if you approve.
