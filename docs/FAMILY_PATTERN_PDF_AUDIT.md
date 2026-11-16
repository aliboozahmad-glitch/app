# Family-pattern audit: original PDF vs current GENOVA (read-only)

**Status: READ-ONLY AUDIT. No code, data, database records, results or UI were changed.** Waiting for your approval.

- Source: `baby_gender_prediction_rules_fixed.pdf` as uploaded (identical file to `docs/source/family_pattern_rules.pdf`, MD5 `0501b0041e1ad4d4fb5cc57d5def5308`). 3 pages, scanned images with no text layer.
- GENOVA side: `backend/genova/traditional/data/family_pattern_table.json` (version `legacy-family-pattern-2025-12-21`) and the live answer from `family_pattern_analysis()` for each PDF input. The function only reads the table; nothing was saved.
- How the PDF was read: each page was rendered at 5× and every line was read in three independent ways: (1) by eye, (2) fresh Arabic OCR of each line, (3) the earlier transcription `docs/source/pdf_transcription.json`. **All three agree on all 81 entries** for both families and every result. OCR only garbled some case numbers (e.g. 22 → "242", 61 → "01"). Those were checked against the page image, and the numbers run in order.
- Legend: ذكر = boy (M), أنثى = girl (F). Children are listed in birth order as written.

## 1. Exact count of numbered entries in the PDF

| Page | Heading in PDF | Numbers | Entries |
|---|---|---|---|
| 1 | القسم الأول: توقع الطفل الأول والطفل الثاني | 1–29 | 29 |
| 1 | ملاحظة: الأرقام من 30 إلى 40 غير موجودة في النص المرسل. | 30–40 | 0 (absent) |
| 2 | القسم الثاني: توقع طفل واحد (1) | 41–67 | 27 |
| 3 | القسم الثاني: توقع طفل واحد (2) | 68–92 | 25 |
| **Total** | | | **81 numbered entries** |

- Duplicate case numbers in the PDF: **none**.
- Missing case numbers in the PDF: **30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40** (11 numbers). The PDF itself says they are "not in the sent text". The PDF does not say what they contained.
- Duplicate inputs in the PDF, counting wife's family and husband's family separately: **none**. Each of the 81 entries has a different wife + husband combination.
- 81 numbered entries means 81 entries with different inputs. Whether the intended total was 80, 81, 92 or another number is **not stated** in the PDF, and this audit does not assume one.

## 2. Stated percentage ranges (quoted exactly)

> نسب التوقع المذكورة: الطفل الأول بين 70% و90%، والطفل الثاني بين 50% و60%.

Translation: "Stated prediction rates: first child between 70% and 90%, second child between 50% and 60%." This line appears only in the page 1 subtitle. Pages 2 and 3 have the subtitle «القواعد كما وردت في النص المرسل» ("the rules as given in the sent text") and no percentages. The PDF does not say whether these ranges apply to Section 2, which predicts one child. Each page footer says: «تنبيه: هذا الملف يوثق القواعد كما قدمها صاحب المشروع، ولا يثبت دقتها علمياً أو يضمن تحديد جنس الجنين.» ("Warning: this file records the rules as provided by the project owner. It does not prove they are scientifically accurate or guarantee the baby's sex.")

GENOVA today shows **no percentage** for this feature. It uses no random numbers, which follows your earlier instruction.

## 3. Every numbered PDF entry vs GENOVA

Columns: **GENOVA same-number entry** compares with the table row that has the same case number. **GENOVA live answer** is what the app returns today when these exact families are entered. ⚑ marks review flags the app attaches.

| # | Pg | Group | Wife's family | Husband's family | PDF result | GENOVA same-number entry | GENOVA live answer | Verdict |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 | S1 · 3+3 | ذكر ذكر أنثى | ذكر ذكر أنثى | 1st ذكر · 2nd ذكر | ✅ ذكر ذكر أنثى / ذكر ذكر أنثى → 1st ذكر · 2nd ذكر | 1st boy (via case 1); 2nd boy (via case 1) | ✅ match |
| 2 | 1 | S1 · 3+3 | ذكر ذكر أنثى | ذكر أنثى أنثى | 1st ذكر · 2nd ذكر | ✅ ذكر ذكر أنثى / ذكر أنثى أنثى → 1st ذكر · 2nd ذكر | 1st boy (via case 2); 2nd boy (via case 2) | ✅ match |
| 3 | 1 | S1 · 3+3 | ذكر ذكر أنثى | أنثى ذكر أنثى | 1st ذكر · 2nd أنثى | ✅ ذكر ذكر أنثى / أنثى ذكر أنثى → 1st ذكر · 2nd أنثى | 1st boy (via case 3); 2nd girl (via case 3) | ✅ match |
| 4 | 1 | S1 · 3+3 | ذكر ذكر أنثى | أنثى ذكر ذكر | 1st ذكر · 2nd أنثى | ✅ ذكر ذكر أنثى / أنثى ذكر ذكر → 1st ذكر · 2nd أنثى | 1st boy (via case 4); 2nd girl (via case 4) | ✅ match |
| 5 | 1 | S1 · 3+3 | ذكر ذكر أنثى | أنثى أنثى ذكر | 1st ذكر · 2nd أنثى | ✅ ذكر ذكر أنثى / أنثى أنثى ذكر → 1st ذكر · 2nd أنثى | 1st boy (via case 5); 2nd girl (via case 5) | ✅ match |
| 6 | 1 | S1 · 3+3 | ذكر ذكر أنثى | ذكر أنثى ذكر | 1st ذكر · 2nd أنثى | ✅ ذكر ذكر أنثى / ذكر أنثى ذكر → 1st ذكر · 2nd أنثى | 1st boy (via case 6); 2nd girl (via case 6) | ✅ match |
| 7 | 1 | S1 · 3+3 | ذكر أنثى أنثى | ذكر أنثى أنثى | 1st ذكر · 2nd أنثى | ✅ ذكر أنثى أنثى / ذكر أنثى أنثى → 1st ذكر · 2nd أنثى | 1st boy (via case 7); 2nd girl (via case 7) | ✅ match |
| 8 | 1 | S1 · 3+3 | ذكر أنثى أنثى | أنثى ذكر أنثى | 1st أنثى · 2nd ذكر | ✅ ذكر أنثى أنثى / أنثى ذكر أنثى → 1st أنثى · 2nd ذكر | 1st girl (via case 8); 2nd boy (via case 8) | ✅ match |
| 9 | 1 | S1 · 3+3 | ذكر أنثى أنثى | أنثى ذكر ذكر | 1st ذكر · 2nd أنثى | ✅ ذكر أنثى أنثى / أنثى ذكر ذكر → 1st ذكر · 2nd أنثى | 1st boy (via case 9); 2nd girl (via case 9) | ✅ match |
| 10 | 1 | S1 · 3+3 | ذكر أنثى أنثى | أنثى أنثى ذكر | 1st أنثى · 2nd ذكر | ✅ ذكر أنثى أنثى / أنثى أنثى ذكر → 1st أنثى · 2nd ذكر | 1st girl (via case 10); 2nd boy (via case 10) | ✅ match |
| 11 | 1 | S1 · 3+3 | ذكر أنثى أنثى | ذكر أنثى ذكر | 1st ذكر · 2nd أنثى | ✅ ذكر أنثى أنثى / ذكر أنثى ذكر → 1st ذكر · 2nd أنثى | 1st boy (via case 11); 2nd girl (via case 11) | ✅ match |
| 12 | 1 | S1 · 3+3 | ذكر أنثى أنثى | ذكر ذكر أنثى | 1st ذكر · 2nd ذكر | ✅ ذكر أنثى أنثى / ذكر ذكر أنثى → 1st ذكر · 2nd ذكر | 1st boy (via case 12); 2nd boy (via case 12) | ✅ match |
| 13 | 1 | S1 · 3+3 | أنثى ذكر أنثى | ذكر ذكر أنثى | 1st ذكر · 2nd أنثى | ✅ أنثى ذكر أنثى / ذكر ذكر أنثى → 1st ذكر · 2nd أنثى | 1st boy (via case 13); 2nd girl (via case 13) | ✅ match |
| 14 | 1 | S1 · 3+3 | أنثى ذكر أنثى | ذكر أنثى أنثى | 1st أنثى · 2nd ذكر | ✅ أنثى ذكر أنثى / ذكر أنثى أنثى → 1st أنثى · 2nd ذكر | 1st girl (via case 14); 2nd boy (via case 14) | ✅ match |
| 15 | 1 | S1 · 3+3 | أنثى ذكر أنثى | أنثى ذكر أنثى | 1st أنثى · 2nd ذكر | ✅ أنثى ذكر أنثى / أنثى ذكر أنثى → 1st أنثى · 2nd ذكر | 1st girl (via case 15); 2nd boy (via case 15) | ✅ match |
| 16 | 1 | S1 · 3+3 | أنثى ذكر أنثى | أنثى ذكر ذكر | 1st أنثى · 2nd ذكر | ✅ أنثى ذكر أنثى / أنثى ذكر ذكر → 1st أنثى · 2nd ذكر | 1st girl (via case 16); 2nd boy (via case 16) | ✅ match |
| 17 | 1 | S1 · 3+3 | أنثى ذكر أنثى | أنثى أنثى ذكر | 1st أنثى · 2nd أنثى | ✅ أنثى ذكر أنثى / أنثى أنثى ذكر → 1st أنثى · 2nd أنثى | 1st girl (via case 17); 2nd girl (via case 17) | ✅ match |
| 18 | 1 | S1 · 3+3 | أنثى ذكر أنثى | ذكر أنثى ذكر | 1st ذكر · 2nd أنثى | ✅ أنثى ذكر أنثى / ذكر أنثى ذكر → 1st ذكر · 2nd أنثى | 1st boy (via case 18); 2nd girl (via case 18) | ✅ match |
| 19 | 1 | S1 · 3+3 | أنثى ذكر ذكر | ذكر ذكر أنثى | 1st ذكر · 2nd أنثى | ✅ أنثى ذكر ذكر / ذكر ذكر أنثى → 1st ذكر · 2nd أنثى | 1st boy (via case 19); 2nd girl (via case 19) | ✅ match |
| 20 | 1 | S1 · 3+3 | أنثى ذكر ذكر | ذكر أنثى أنثى | 1st ذكر · 2nd أنثى | ✅ أنثى ذكر ذكر / ذكر أنثى أنثى → 1st ذكر · 2nd أنثى | 1st boy (via case 20); 2nd girl (via case 20) | ✅ match |
| 21 | 1 | S1 · 3+3 | أنثى ذكر ذكر | أنثى ذكر أنثى | 1st أنثى · 2nd ذكر | ✅ أنثى ذكر ذكر / أنثى ذكر أنثى → 1st أنثى · 2nd ذكر | 1st girl (via case 21); 2nd boy (via case 21) | ✅ match |
| 22 | 1 | S1 · 3+3 | أنثى ذكر ذكر | أنثى ذكر ذكر | 1st أنثى · 2nd ذكر | ✅ أنثى ذكر ذكر / أنثى ذكر ذكر → 1st أنثى · 2nd ذكر | 1st girl (via case 22); 2nd boy (via case 22) | ✅ match |
| 23 | 1 | S1 · 3+3 | أنثى ذكر ذكر | أنثى أنثى ذكر | 1st أنثى · 2nd ذكر | ✅ أنثى ذكر ذكر / أنثى أنثى ذكر → 1st أنثى · 2nd ذكر | 1st girl (via case 23); 2nd boy (via case 23) | ✅ match |
| 24 | 1 | S1 · 3+3 | أنثى ذكر ذكر | ذكر أنثى ذكر | 1st ذكر · 2nd أنثى | ✅ أنثى ذكر ذكر / ذكر أنثى ذكر → 1st ذكر · 2nd أنثى | 1st boy (via case 24); 2nd girl (via case 24) | ✅ match |
| 25 | 1 | S1 · 3+3 | أنثى أنثى ذكر | ذكر ذكر أنثى | 1st ذكر · 2nd أنثى | ✅ أنثى أنثى ذكر / ذكر ذكر أنثى → 1st ذكر · 2nd أنثى | 1st boy (via case 25); 2nd girl (via case 25) | ✅ match |
| 26 | 1 | S1 · 3+3 | أنثى أنثى ذكر | ذكر أنثى أنثى | 1st أنثى · 2nd ذكر | ✅ أنثى أنثى ذكر / ذكر أنثى أنثى → 1st أنثى · 2nd ذكر | 1st girl (via case 26); 2nd boy (via case 26) | ✅ match |
| 27 | 1 | S1 · 3+3 | أنثى أنثى ذكر | أنثى ذكر أنثى | 1st أنثى · 2nd ذكر | ✅ أنثى أنثى ذكر / أنثى ذكر أنثى → 1st أنثى · 2nd ذكر | 1st girl (via case 27); 2nd boy (via case 27) | ✅ match |
| 28 | 1 | S1 · 3+3 | أنثى أنثى ذكر | أنثى ذكر ذكر | 1st أنثى · 2nd ذكر | ✅ أنثى أنثى ذكر / أنثى ذكر ذكر → 1st أنثى · 2nd ذكر | 1st girl (via case 28); 2nd boy (via case 28) | ✅ match |
| 29 | 1 | S1 · 3+3 | أنثى أنثى ذكر | أنثى أنثى ذكر | 1st أنثى · 2nd أنثى | ✅ أنثى أنثى ذكر / أنثى أنثى ذكر → 1st أنثى · 2nd أنثى | 1st girl (via case 29); 2nd girl (via case 29) | ✅ match |
| 41 | 2 | S2 · 2+2 | ذكر ذكر | ذكر ذكر | طفل ذكر | ✅ ذكر ذكر / ذكر ذكر → 1st ذكر · 2nd ذكر | boy (via case 78) ⚑ duplicate_pattern, split_unconfirmed | ⚠️ same result, other case no. |
| 42 | 2 | S2 · 2+2 | ذكر أنثى | ذكر أنثى | طفل ذكر | ✅ ذكر أنثى / ذكر أنثى → 1st ذكر · 2nd ذكر | boy (via case 75) ⚑ duplicate_pattern, split_unconfirmed | ⚠️ same result, other case no. |
| 43 | 2 | S2 · 2+2 | أنثى أنثى | أنثى أنثى | طفل أنثى | ✅ أنثى أنثى / أنثى أنثى → 1st أنثى · 2nd أنثى | girl (via case 69) ⚑ duplicate_pattern, split_unconfirmed | ⚠️ same result, other case no. |
| 44 | 2 | S2 · 2+2 | أنثى ذكر | أنثى ذكر | طفل أنثى | ✅ أنثى ذكر / أنثى ذكر → 1st أنثى · 2nd أنثى | girl (via case 72) ⚑ duplicate_pattern, split_unconfirmed | ⚠️ same result, other case no. |
| 45 | 2 | S2 · 2+2 | أنثى أنثى | ذكر أنثى | طفل أنثى | ✅ أنثى أنثى / ذكر أنثى → 1st أنثى · 2nd أنثى | girl (via case 71) ⚑ duplicate_pattern, split_unconfirmed | ⚠️ same result, other case no. |
| 46 | 2 | S2 · 2+2 | ذكر ذكر | أنثى ذكر | طفل ذكر | ✅ ذكر ذكر / أنثى ذكر → 1st ذكر · 2nd ذكر | boy (via case 76) ⚑ duplicate_pattern, split_unconfirmed | ⚠️ same result, other case no. |
| 47 | 2 | S2 · 2+2 | ذكر أنثى | ذكر ذكر | طفل ذكر | ✅ ذكر أنثى / ذكر ذكر → 1st ذكر · 2nd ذكر | boy (via case 79) ⚑ duplicate_pattern, split_unconfirmed | ⚠️ same result, other case no. |
| 48 | 2 | S2 · 2+2 | أنثى ذكر | ذكر ذكر | طفل ذكر | ✅ أنثى ذكر / ذكر ذكر → 1st ذكر · 2nd ذكر | boy (via case 70) ⚑ duplicate_pattern, split_unconfirmed | ⚠️ same result, other case no. |
| 49 | 2 | S2 · 2+2 | ذكر أنثى | أنثى أنثى | طفل أنثى | ✅ ذكر أنثى / أنثى أنثى → 1st أنثى · 2nd أنثى | girl (via case 77) ⚑ duplicate_pattern, split_unconfirmed | ⚠️ same result, other case no. |
| 50 | 2 | S2 · 2+2 | أنثى ذكر | أنثى أنثى | طفل أنثى | ✅ أنثى ذكر / أنثى أنثى → 1st أنثى · 2nd أنثى | girl (via case 50) | ✅ match |
| 51 | 2 | S2 · 2+2 | ذكر ذكر | ذكر أنثى | طفل ذكر | ✅ ذكر ذكر / ذكر أنثى → 1st ذكر · 2nd ذكر | boy (via case 51) | ✅ match |
| 52 | 2 | S2 · 2+2 | أنثى أنثى | أنثى ذكر | طفل أنثى | ✅ أنثى أنثى / أنثى ذكر → 1st أنثى · 2nd أنثى | girl (via case 73) ⚑ duplicate_pattern, split_unconfirmed | ⚠️ same result, other case no. |
| 53 | 2 | S2 · 1+2 | أنثى | أنثى أنثى | طفل أنثى | ✅ combined list أنثى أنثى أنثى (split not stored) → 1st أنثى · 2nd أنثى | girl (via case 53) ⚑ split_unconfirmed | ✅ match |
| 54 | 2 | S2 · 1+2 | أنثى | ذكر ذكر | طفل ذكر | ✅ combined list أنثى ذكر ذكر (split not stored) → 1st ذكر · 2nd ذكر | boy (via case 54) ⚑ split_unconfirmed | ✅ match |
| 55 | 2 | S2 · 1+2 | أنثى | أنثى ذكر | طفل أنثى | ✅ combined list أنثى أنثى ذكر (split not stored) → 1st أنثى · 2nd أنثى | girl (via case 55) ⚑ split_unconfirmed | ✅ match |
| 56 | 2 | S2 · 1+2 | أنثى | ذكر أنثى | طفل أنثى | ✅ combined list أنثى ذكر أنثى (split not stored) → 1st أنثى · 2nd أنثى | girl (via case 56) ⚑ split_unconfirmed | ✅ match |
| 57 | 2 | S2 · 1+2 | ذكر | أنثى أنثى | طفل أنثى | ✅ combined list ذكر أنثى أنثى (split not stored) → 1st أنثى · 2nd أنثى | girl (via case 57) ⚑ split_unconfirmed | ✅ match |
| 58 | 2 | S2 · 1+2 | ذكر | ذكر ذكر | طفل ذكر | ✅ combined list ذكر ذكر ذكر (split not stored) → 1st ذكر · 2nd ذكر | boy (via case 58) ⚑ split_unconfirmed | ✅ match |
| 59 | 2 | S2 · 1+2 | ذكر | أنثى ذكر | طفل ذكر | ✅ combined list ذكر أنثى ذكر (split not stored) → 1st ذكر · 2nd ذكر | boy (via case 59) ⚑ split_unconfirmed | ✅ match |
| 60 | 2 | S2 · 1+2 | ذكر | ذكر أنثى | طفل ذكر | ✅ combined list ذكر ذكر أنثى (split not stored) → 1st ذكر · 2nd ذكر | boy (via case 60) ⚑ split_unconfirmed | ✅ match |
| 61 | 2 | S2 · 2+1 | أنثى أنثى | أنثى | طفل أنثى | **not in GENOVA** | girl (via case 53) ⚑ split_unconfirmed | ⚠️ same result, other case no. |
| 62 | 2 | S2 · 2+1 | ذكر ذكر | أنثى | طفل ذكر | **not in GENOVA** | boy (via case 60) ⚑ split_unconfirmed | ⚠️ same result, other case no. |
| 63 | 2 | S2 · 2+1 | أنثى ذكر | أنثى | طفل أنثى | **not in GENOVA** | girl (via case 56) ⚑ split_unconfirmed | ⚠️ same result, other case no. |
| 64 | 2 | S2 · 2+1 | ذكر أنثى | أنثى | طفل أنثى | **not in GENOVA** | girl (via case 57) ⚑ split_unconfirmed | ⚠️ same result, other case no. |
| 65 | 2 | S2 · 2+1 | أنثى أنثى | ذكر | طفل أنثى | **not in GENOVA** | girl (via case 55) ⚑ split_unconfirmed | ⚠️ same result, other case no. |
| 66 | 2 | S2 · 2+1 | ذكر ذكر | ذكر | طفل ذكر | **not in GENOVA** | boy (via case 58) ⚑ split_unconfirmed | ⚠️ same result, other case no. |
| 67 | 2 | S2 · 2+1 | أنثى ذكر | ذكر | طفل ذكر | **not in GENOVA** | boy (via case 54) ⚑ split_unconfirmed | ⚠️ same result, other case no. |
| 68 | 3 | S2 · 2+1 | ذكر أنثى | ذكر | طفل ذكر | **not in GENOVA** | boy (via case 59) ⚑ split_unconfirmed | ⚠️ same result, other case no. |
| 69 | 3 | S2 · 1+3 | أنثى | أنثى أنثى أنثى | طفل أنثى | ✅ combined list أنثى أنثى أنثى أنثى (split not stored) → 1st أنثى · 2nd أنثى | girl (via case 69) ⚑ duplicate_pattern, split_unconfirmed | ✅ match |
| 70 | 3 | S2 · 1+3 | أنثى | ذكر ذكر ذكر | طفل ذكر | ✅ combined list أنثى ذكر ذكر ذكر (split not stored) → 1st ذكر · 2nd ذكر | boy (via case 70) ⚑ duplicate_pattern, split_unconfirmed | ✅ match |
| 71 | 3 | S2 · 1+3 | أنثى | أنثى ذكر أنثى | طفل أنثى | ✅ combined list أنثى أنثى ذكر أنثى (split not stored) → 1st أنثى · 2nd أنثى | girl (via case 71) ⚑ duplicate_pattern, split_unconfirmed | ✅ match |
| 72 | 3 | S2 · 1+3 | أنثى | ذكر أنثى ذكر | طفل أنثى | ✅ combined list أنثى ذكر أنثى ذكر (split not stored) → 1st أنثى · 2nd أنثى | girl (via case 72) ⚑ duplicate_pattern, split_unconfirmed | ✅ match |
| 73 | 3 | S2 · 1+3 | أنثى | أنثى أنثى ذكر | طفل أنثى | ✅ combined list أنثى أنثى أنثى ذكر (split not stored) → 1st أنثى · 2nd أنثى | girl (via case 73) ⚑ duplicate_pattern, split_unconfirmed | ✅ match |
| 74 | 3 | S2 · 1+3 | أنثى | ذكر ذكر أنثى | طفل ذكر | ✅ combined list أنثى ذكر ذكر أنثى (split not stored) → 1st ذكر · 2nd ذكر | boy (via case 74) ⚑ split_unconfirmed | ✅ match |
| 75 | 3 | S2 · 1+3 | ذكر | أنثى ذكر أنثى | طفل ذكر | ✅ combined list ذكر أنثى ذكر أنثى (split not stored) → 1st ذكر · 2nd ذكر | boy (via case 75) ⚑ duplicate_pattern, split_unconfirmed | ✅ match |
| 76 | 3 | S2 · 1+3 | ذكر | ذكر أنثى ذكر | طفل ذكر | ✅ combined list ذكر ذكر أنثى ذكر (split not stored) → 1st ذكر · 2nd ذكر | boy (via case 76) ⚑ duplicate_pattern, split_unconfirmed | ✅ match |
| 77 | 3 | S2 · 1+3 | ذكر | أنثى أنثى أنثى | طفل أنثى | ✅ combined list ذكر أنثى أنثى أنثى (split not stored) → 1st أنثى · 2nd أنثى | girl (via case 77) ⚑ duplicate_pattern, split_unconfirmed | ✅ match |
| 78 | 3 | S2 · 1+3 | ذكر | ذكر ذكر ذكر | طفل ذكر | ✅ combined list ذكر ذكر ذكر ذكر (split not stored) → 1st ذكر · 2nd ذكر | boy (via case 78) ⚑ duplicate_pattern, split_unconfirmed | ✅ match |
| 79 | 3 | S2 · 1+3 | ذكر | أنثى ذكر ذكر | طفل ذكر | ✅ combined list ذكر أنثى ذكر ذكر (split not stored) → 1st ذكر · 2nd ذكر | boy (via case 79) ⚑ duplicate_pattern, split_unconfirmed | ✅ match |
| 80 | 3 | S2 · 1+3 | ذكر | ذكر أنثى أنثى | طفل ذكر | ✅ combined list ذكر ذكر أنثى أنثى (split not stored) → 1st ذكر · 2nd ذكر | boy (via case 80) ⚑ split_unconfirmed | ✅ match |
| 81 | 3 | S2 · 3+1 | أنثى أنثى أنثى | أنثى | طفل أنثى | **not in GENOVA** | girl (via case 69) ⚑ duplicate_pattern, split_unconfirmed | ⚠️ same result, other case no. |
| 82 | 3 | S2 · 3+1 | ذكر ذكر ذكر | أنثى | طفل ذكر | **not in GENOVA** | boy (via case 51) ⚑ split_mismatch | ⚠️ same result, other case no. |
| 83 | 3 | S2 · 3+1 | أنثى ذكر أنثى | أنثى | طفل أنثى | **not in GENOVA** | girl (via case 50) ⚑ split_mismatch | ⚠️ same result, other case no. |
| 84 | 3 | S2 · 3+1 | ذكر أنثى ذكر | أنثى | طفل أنثى | **not in GENOVA** | boy (via case 75) ⚑ duplicate_pattern, split_unconfirmed | ❌ **different result** |
| 85 | 3 | S2 · 3+1 | أنثى أنثى ذكر | أنثى | طفل أنثى | **not in GENOVA** | girl (via case 71) ⚑ duplicate_pattern, split_unconfirmed | ⚠️ same result, other case no. |
| 86 | 3 | S2 · 3+1 | ذكر ذكر أنثى | أنثى | طفل ذكر | **not in GENOVA** | boy (via case 80) ⚑ split_unconfirmed | ⚠️ same result, other case no. |
| 87 | 3 | S2 · 3+1 | أنثى ذكر أنثى | ذكر | طفل ذكر | **not in GENOVA** | girl (via case 72) ⚑ duplicate_pattern, split_unconfirmed | ❌ **different result** |
| 88 | 3 | S2 · 3+1 | ذكر أنثى ذكر | ذكر | طفل ذكر | **not in GENOVA** | boy (via case 79) ⚑ duplicate_pattern, split_unconfirmed | ⚠️ same result, other case no. |
| 89 | 3 | S2 · 3+1 | أنثى أنثى أنثى | ذكر | طفل أنثى | **not in GENOVA** | girl (via case 73) ⚑ duplicate_pattern, split_unconfirmed | ⚠️ same result, other case no. |
| 90 | 3 | S2 · 3+1 | ذكر ذكر ذكر | ذكر | طفل ذكر | **not in GENOVA** | boy (via case 78) ⚑ duplicate_pattern, split_unconfirmed | ⚠️ same result, other case no. |
| 91 | 3 | S2 · 3+1 | أنثى ذكر ذكر | ذكر | طفل ذكر | **not in GENOVA** | boy (via case 70) ⚑ duplicate_pattern, split_unconfirmed | ⚠️ same result, other case no. |
| 92 | 3 | S2 · 3+1 | ذكر أنثى أنثى | ذكر | طفل ذكر | **not in GENOVA** | no prediction (not_in_table) | ❌ no answer |

Summary of the 81 PDF entries:

- ✅ Exact match (same number, same inputs, same result, and the live answer comes from that case): **51**: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 50, 51, 53, 54, 55, 56, 57, 58, 59, 60, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80.
- ⚠️ Same result, but the live answer comes from a different case number: **27**: 41, 42, 43, 44, 45, 46, 47, 48, 49, 52, 61, 62, 63, 64, 65, 66, 67, 68, 81, 82, 83, 85, 86, 88, 89, 90, 91.
- ❌ Different result or no answer: **3**: 84, 87, 92.

## 4. Every case currently in GENOVA

GENOVA holds **72 entries**. Duplicate case numbers: **none**. The numbers present are 1–60 and 69–80.

| GENOVA case | Section (as stored) | Wife / Husband (as stored) | 1st | 2nd | In PDF under same number? |
|---|---|---|---|---|---|
| 1 | wife3_husband3 | ذكر ذكر أنثى / ذكر ذكر أنثى | ذكر | ذكر | yes, same inputs and result |
| 2 | wife3_husband3 | ذكر ذكر أنثى / ذكر أنثى أنثى | ذكر | ذكر | yes, same inputs and result |
| 3 | wife3_husband3 | ذكر ذكر أنثى / أنثى ذكر أنثى | ذكر | أنثى | yes, same inputs and result |
| 4 | wife3_husband3 | ذكر ذكر أنثى / أنثى ذكر ذكر | ذكر | أنثى | yes, same inputs and result |
| 5 | wife3_husband3 | ذكر ذكر أنثى / أنثى أنثى ذكر | ذكر | أنثى | yes, same inputs and result |
| 6 | wife3_husband3 | ذكر ذكر أنثى / ذكر أنثى ذكر | ذكر | أنثى | yes, same inputs and result |
| 7 | wife3_husband3 | ذكر أنثى أنثى / ذكر أنثى أنثى | ذكر | أنثى | yes, same inputs and result |
| 8 | wife3_husband3 | ذكر أنثى أنثى / أنثى ذكر أنثى | أنثى | ذكر | yes, same inputs and result |
| 9 | wife3_husband3 | ذكر أنثى أنثى / أنثى ذكر ذكر | ذكر | أنثى | yes, same inputs and result |
| 10 | wife3_husband3 | ذكر أنثى أنثى / أنثى أنثى ذكر | أنثى | ذكر | yes, same inputs and result |
| 11 | wife3_husband3 | ذكر أنثى أنثى / ذكر أنثى ذكر | ذكر | أنثى | yes, same inputs and result |
| 12 | wife3_husband3 | ذكر أنثى أنثى / ذكر ذكر أنثى | ذكر | ذكر | yes, same inputs and result |
| 13 | wife3_husband3 | أنثى ذكر أنثى / ذكر ذكر أنثى | ذكر | أنثى | yes, same inputs and result |
| 14 | wife3_husband3 | أنثى ذكر أنثى / ذكر أنثى أنثى | أنثى | ذكر | yes, same inputs and result |
| 15 | wife3_husband3 | أنثى ذكر أنثى / أنثى ذكر أنثى | أنثى | ذكر | yes, same inputs and result |
| 16 | wife3_husband3 | أنثى ذكر أنثى / أنثى ذكر ذكر | أنثى | ذكر | yes, same inputs and result |
| 17 | wife3_husband3 | أنثى ذكر أنثى / أنثى أنثى ذكر | أنثى | أنثى | yes, same inputs and result |
| 18 | wife3_husband3 | أنثى ذكر أنثى / ذكر أنثى ذكر | ذكر | أنثى | yes, same inputs and result |
| 19 | wife3_husband3 | أنثى ذكر ذكر / ذكر ذكر أنثى | ذكر | أنثى | yes, same inputs and result |
| 20 | wife3_husband3 | أنثى ذكر ذكر / ذكر أنثى أنثى | ذكر | أنثى | yes, same inputs and result |
| 21 | wife3_husband3 | أنثى ذكر ذكر / أنثى ذكر أنثى | أنثى | ذكر | yes, same inputs and result |
| 22 | wife3_husband3 | أنثى ذكر ذكر / أنثى ذكر ذكر | أنثى | ذكر | yes, same inputs and result |
| 23 | wife3_husband3 | أنثى ذكر ذكر / أنثى أنثى ذكر | أنثى | ذكر | yes, same inputs and result |
| 24 | wife3_husband3 | أنثى ذكر ذكر / ذكر أنثى ذكر | ذكر | أنثى | yes, same inputs and result |
| 25 | wife3_husband3 | أنثى أنثى ذكر / ذكر ذكر أنثى | ذكر | أنثى | yes, same inputs and result |
| 26 | wife3_husband3 | أنثى أنثى ذكر / ذكر أنثى أنثى | أنثى | ذكر | yes, same inputs and result |
| 27 | wife3_husband3 | أنثى أنثى ذكر / أنثى ذكر أنثى | أنثى | ذكر | yes, same inputs and result |
| 28 | wife3_husband3 | أنثى أنثى ذكر / أنثى ذكر ذكر | أنثى | ذكر | yes, same inputs and result |
| 29 | wife3_husband3 | أنثى أنثى ذكر / أنثى أنثى ذكر | أنثى | أنثى | yes, same inputs and result |
| 30 | wife3_husband3 | أنثى أنثى ذكر / ذكر أنثى ذكر | أنثى | ذكر | **no, PDF number absent** (from old code only) |
| 31 | wife3_husband3 | ذكر أنثى ذكر / ذكر ذكر أنثى | ذكر | ذكر | **no, PDF number absent** (from old code only) |
| 32 | wife3_husband3 | ذكر أنثى ذكر / ذكر أنثى أنثى | ذكر | أنثى | **no, PDF number absent** (from old code only) |
| 33 | wife3_husband3 | ذكر أنثى ذكر / أنثى ذكر أنثى | ذكر | أنثى | **no, PDF number absent** (from old code only) |
| 34 | wife3_husband3 | ذكر أنثى ذكر / أنثى ذكر ذكر | ذكر | ذكر | **no, PDF number absent** (from old code only) |
| 35 | wife3_husband3 | ذكر أنثى ذكر / أنثى أنثى ذكر | أنثى | ذكر | **no, PDF number absent** (from old code only) |
| 36 | wife3_husband3 | ذكر أنثى ذكر / ذكر أنثى ذكر | ذكر | أنثى | **no, PDF number absent** (from old code only) |
| 37 | one_each | ذكر / أنثى | أنثى | أنثى | **no, PDF number absent** (from old code only) |
| 38 | one_each | أنثى / ذكر | ذكر | ذكر | **no, PDF number absent** (from old code only) |
| 39 | one_each | أنثى / أنثى | أنثى | أنثى | **no, PDF number absent** (from old code only) |
| 40 | one_each | ذكر / ذكر | ذكر | ذكر | **no, PDF number absent** (from old code only) |
| 41 | two_each | ذكر ذكر / ذكر ذكر | ذكر | ذكر | yes, same inputs and result |
| 42 | two_each | ذكر أنثى / ذكر أنثى | ذكر | ذكر | yes, same inputs and result |
| 43 | two_each | أنثى أنثى / أنثى أنثى | أنثى | أنثى | yes, same inputs and result |
| 44 | two_each | أنثى ذكر / أنثى ذكر | أنثى | أنثى | yes, same inputs and result |
| 45 | two_each | أنثى أنثى / ذكر أنثى | أنثى | أنثى | yes, same inputs and result |
| 46 | two_each | ذكر ذكر / أنثى ذكر | ذكر | ذكر | yes, same inputs and result |
| 47 | two_each | ذكر أنثى / ذكر ذكر | ذكر | ذكر | yes, same inputs and result |
| 48 | two_each | أنثى ذكر / ذكر ذكر | ذكر | ذكر | yes, same inputs and result |
| 49 | two_each | ذكر أنثى / أنثى أنثى | أنثى | أنثى | yes, same inputs and result |
| 50 | two_each | أنثى ذكر / أنثى أنثى | أنثى | أنثى | yes, same inputs and result |
| 51 | two_each | ذكر ذكر / ذكر أنثى | ذكر | ذكر | yes, same inputs and result |
| 52 | two_each | أنثى أنثى / أنثى ذكر | أنثى | أنثى | yes, same inputs and result |
| 53 | one_plus_two | combined أنثى أنثى أنثى (split not stored) | أنثى | أنثى | yes, same inputs and result |
| 54 | one_plus_two | combined أنثى ذكر ذكر (split not stored) | ذكر | ذكر | yes, same inputs and result |
| 55 | one_plus_two | combined أنثى أنثى ذكر (split not stored) | أنثى | أنثى | yes, same inputs and result |
| 56 | one_plus_two | combined أنثى ذكر أنثى (split not stored) | أنثى | أنثى | yes, same inputs and result |
| 57 | one_plus_two | combined ذكر أنثى أنثى (split not stored) | أنثى | أنثى | yes, same inputs and result |
| 58 | one_plus_two | combined ذكر ذكر ذكر (split not stored) | ذكر | ذكر | yes, same inputs and result |
| 59 | one_plus_two | combined ذكر أنثى ذكر (split not stored) | ذكر | ذكر | yes, same inputs and result |
| 60 | one_plus_two | combined ذكر ذكر أنثى (split not stored) | ذكر | ذكر | yes, same inputs and result |
| 69 | one_plus_three | combined أنثى أنثى أنثى أنثى (split not stored) | أنثى | أنثى | yes, same inputs and result |
| 70 | one_plus_three | combined أنثى ذكر ذكر ذكر (split not stored) | ذكر | ذكر | yes, same inputs and result |
| 71 | one_plus_three | combined أنثى أنثى ذكر أنثى (split not stored) | أنثى | أنثى | yes, same inputs and result |
| 72 | one_plus_three | combined أنثى ذكر أنثى ذكر (split not stored) | أنثى | أنثى | yes, same inputs and result |
| 73 | one_plus_three | combined أنثى أنثى أنثى ذكر (split not stored) | أنثى | أنثى | yes, same inputs and result |
| 74 | one_plus_three | combined أنثى ذكر ذكر أنثى (split not stored) | ذكر | ذكر | yes, same inputs and result |
| 75 | one_plus_three | combined ذكر أنثى ذكر أنثى (split not stored) | ذكر | ذكر | yes, same inputs and result |
| 76 | one_plus_three | combined ذكر ذكر أنثى ذكر (split not stored) | ذكر | ذكر | yes, same inputs and result |
| 77 | one_plus_three | combined ذكر أنثى أنثى أنثى (split not stored) | أنثى | أنثى | yes, same inputs and result |
| 78 | one_plus_three | combined ذكر ذكر ذكر ذكر (split not stored) | ذكر | ذكر | yes, same inputs and result |
| 79 | one_plus_three | combined ذكر أنثى ذكر ذكر (split not stored) | ذكر | ذكر | yes, same inputs and result |
| 80 | one_plus_three | combined ذكر ذكر أنثى أنثى (split not stored) | ذكر | ذكر | yes, same inputs and result |

## 5. Missing and duplicated case numbers

| | PDF | GENOVA |
|---|---|---|
| Numbered entries | 81 | 72 |
| Numbers present | 1–29, 41–92 | 1–60, 69–80 |
| Numbers absent | 30–40 (11) | 61–68 (8), 81–92 (12) → **20 PDF entries not in GENOVA** |
| Numbers only on this side | 61–68, 81–92 | 30–40 (11): 30–36 are 3+3 entries and 37–40 are 1+1 entries, all from the old code |
| Duplicate numbers | none | none |
| Duplicate inputs (wife and husband kept separate) | none | n/a, since 53–60 and 69–80 store only a combined list |

**Overlaps in the combined list.** The old code joins wife + husband into one list, and GENOVA's lookup uses that joined list. Several PDF entries that are different families then become the same list:

| Combined list | PDF entries that produce it | GENOVA entries that produce it |
|---|---|---|
| ذكر ذكر ذكر ذكر | 41, 78, 90 | 41, 78 |
| ذكر أنثى ذكر أنثى | 42, 75, 84 | 42, 75 |
| أنثى أنثى أنثى أنثى | 43, 69, 81 | 43, 69 |
| أنثى ذكر أنثى ذكر | 44, 72, 87 | 44, 72 |
| أنثى أنثى ذكر أنثى | 45, 71, 85 | 45, 71 |
| ذكر ذكر أنثى ذكر | 46, 76 | 46, 76 |
| ذكر أنثى ذكر ذكر | 47, 79, 88 | 47, 79 |
| أنثى ذكر ذكر ذكر | 48, 70, 91 | 48, 70 |
| ذكر أنثى أنثى أنثى | 49, 77 | 49, 77 |
| أنثى ذكر أنثى أنثى | 50, 83 | — |
| ذكر ذكر ذكر أنثى | 51, 82 | — |
| أنثى أنثى أنثى ذكر | 52, 73, 89 | 52, 73 |
| أنثى أنثى أنثى | 53, 61 | — |
| أنثى ذكر ذكر | 54, 67 | — |
| أنثى أنثى ذكر | 55, 65 | — |
| أنثى ذكر أنثى | 56, 63 | — |
| ذكر أنثى أنثى | 57, 64 | — |
| ذكر ذكر ذكر | 58, 66 | — |
| ذكر أنثى ذكر | 59, 68 | — |
| ذكر ذكر أنثى | 60, 62 | — |
| ذكر ذكر أنثى أنثى | 80, 86 | — |

In the PDF, all entries in the same row of this table give the **same result**, except 84 vs 42/75 and 87 vs 44/72. The overlap is why GENOVA gives a different answer for 84 and 87. The PDF never merges these entries: each one names the wife's family and the husband's family separately.

## 6. Differences between the PDF and GENOVA

**Results that differ today (what a user would see):**

| PDF # | Wife | Husband | PDF says | GENOVA returns today | Why |
|---|---|---|---|---|---|
| 84 | ذكر أنثى ذكر | أنثى | طفل أنثى (girl) | boy, via case 75 | 84 is not in GENOVA. Its combined list equals case 75 (ذكر / أنثى ذكر أنثى → ذكر), and that entry wins. |
| 87 | أنثى ذكر أنثى | ذكر | طفل ذكر (boy) | girl, via case 72 | 87 is not in GENOVA. Its combined list equals case 72 (أنثى / ذكر أنثى ذكر → أنثى), and that entry wins. |
| 92 | ذكر أنثى أنثى | ذكر | طفل ذكر (boy) | no prediction (`not_in_table`) | 92 is not in GENOVA and no other entry has the same combined list. The old app's hidden default was "male". GENOVA records this as `original_fallback` but does not show it as a prediction. |

**Structural differences (results the same, but presented differently):**

1. **20 PDF entries are not in GENOVA as cases:** 61–68 (wife 2 + husband 1) and 81–92 (wife 3 + husband 1). For 17 of them, the live answer happens to match because another entry has the same combined list. The app then shows a different case number and flags `split_unconfirmed` or `split_mismatch`. For 84, 87 and 92 it does not match (see above).
2. **11 GENOVA entries have no PDF counterpart:** 30–36 (3+3) and 37–40 (1+1). They come from the old code. The PDF says only that numbers 30–40 were "not in the sent text". It does not confirm or contradict GENOVA's 30–40.
3. **Family split not stored for 53–60 and 69–80.** GENOVA stores only the joined list. The PDF gives the split explicitly: 53–60 = wife 1 + husband 2, and 69–80 = wife 1 + husband 3. With the split, every one of these entries matches the PDF.
4. **Overlapping 2+2 entries:** for PDF 41–49 and 52 (wife 2 + husband 2), GENOVA's live answer comes from a 1+3 entry with the same joined list. Results are identical, but the case number shown is different and the result is flagged `duplicate_pattern`.
5. **One child vs first/second.** Section 2 (41–92) gives a single result, «طفل ذكر/أنثى». GENOVA asks "first or second child" for every input and returns the same answer for both in Section 2.
6. **Percentages.** The PDF states 70–90% (first child) and 50–60% (second child) on page 1 only. GENOVA shows none.
7. **Section 1 coverage (observation only, not corrected):** the PDF has 5 wife patterns × husband patterns. Wife ذكر أنثى ذكر is absent from 1–29, and wife أنثى أنثى ذكر has 5 husbands, with ذكر أنثى ذكر absent. GENOVA's 30–36 cover exactly those inputs, from the old code.

## 7. Unclear or ambiguous items (quoted exactly, not resolved)

No entry is illegible: all 81 lines are printed text and were read the same way three times. The items below are unclear in **meaning**, so each is marked UNCLEAR, quoted, and shown with a page image. No decision has been made on any of them.

**U1 · UNCLEAR: Numbers 30–40**

> ملاحظة: الأرقام من 30 إلى 40 غير موجودة في النص المرسل.

![U1](audit_images/family_pattern_pdf/p1_note_30_40_missing.png)

The PDF does not say whether 30–40 were deleted, never existed, or were lost. GENOVA has its own 30–40 from the old code.

**U2 · UNCLEAR: Percentage ranges**

> نسب التوقع المذكورة: الطفل الأول بين 70% و90%، والطفل الثاني بين 50% و60%.

![U2](audit_images/family_pattern_pdf/p1_header_percentages.png)

Printed only on page 1. It is not stated whether the ranges apply to Section 2 (one child), or whether they should be shown at all.

**U3 · UNCLEAR: Section 2 headings «(1)» and «(2)»**

> القسم الثاني: توقع طفل واحد (1) / القسم الثاني: توقع طفل واحد (2)

![U3](audit_images/family_pattern_pdf/p2_section2_heading_1.png)

![U3b](audit_images/family_pattern_pdf/p3_section2_heading_2.png)

These look like page continuation labels. It is not stated whether «طفل واحد» means "the next child" or "first child only".

**U4 · UNCLEAR: Entries 84 and 87 (conflict with the old code's joined lookup)**

> التوقع 84: عائلة الزوجة: ذكر أنثى ذكر | عائلة الزوج: أنثى | النتيجة: طفل أنثى — التوقع 87: عائلة الزوجة: أنثى ذكر أنثى | عائلة الزوج: ذكر | النتيجة: طفل ذكر

![U4](audit_images/family_pattern_pdf/line_84.png)

![U4b](audit_images/family_pattern_pdf/line_87.png)

Clear in the PDF. Each gives the opposite result to an earlier entry with the same joined list (75 and 72).

**U5 · UNCLEAR: Entry 92 (no GENOVA counterpart)**

> التوقع 92: عائلة الزوجة: ذكر أنثى أنثى | عائلة الزوج: ذكر | النتيجة: طفل ذكر

![U5](audit_images/family_pattern_pdf/line_92.png)

Clear in the PDF. GENOVA has no entry for it.

**U6 · UNCLEAR: Entry 81 vs 61 (checked because they look alike at low zoom)**

> التوقع 81: عائلة الزوجة: أنثى أنثى أنثى | عائلة الزوج: أنثى | النتيجة: طفل أنثى — التوقع 61: عائلة الزوجة: أنثى أنثى | عائلة الزوج: أنثى | النتيجة: طفل أنثى

![U6](audit_images/family_pattern_pdf/line_81.png)

![U6b](audit_images/family_pattern_pdf/line_61.png)

At full zoom, 81 has **three** children in the wife's family and 61 has **two**, so they are not duplicates. Both images are included so you can check.

## 8. Comparison with the earlier report

`docs/FAMILY_PATTERN_PDF_COMPARISON.md` has been left unchanged. This fresh audit agrees with all of its entry values, and finds the same 3 differing results (84, 87, 92) and the same 81-entry count. In addition, this report lists every entry, both sides of the comparison, and the unclear items with images.

## 9. Nothing has been changed

No code, table data, database records, prediction results or UI were modified. The only new files are this report and the evidence images in `docs/audit_images/family_pattern_pdf/`. **Waiting for your approval before any change.**
