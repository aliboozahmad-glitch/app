# Family-pattern table: owner review sheet

Status: **PENDING YOUR REVIEW.** Nothing below has been changed. GENOVA uses your table exactly as the old app did, and every case listed here shows an "owner review pending" note on the result.

Source: `baby-gender-backend/gender_prediction_logic.py`, table `PREDICTION_TABLE_EN` (checked identical to the Arabic `PREDICTION_TABLE`), 72 entries.
Notation: M = boy, F = girl. Pattern = wife's family children, then husband's family children, in birth order. Result = first child / second child.

## A. The 10 duplicated patterns
Each pattern is written twice: once in the "2 + 2" section (cases 41–52) and once in the "1 + 3" section (cases 69–80). **All 10 pairs give the same answer**, so results never conflict. GENOVA uses the later entry, like your old app did.

| Pattern (4 children) | Cases | Result | Please confirm |
|---|---|---|---|
| M-M-M-M | 41 & 78 | M / M | is it meant for 2+2, for 1+3, or for both? |
| M-F-M-F | 42 & 75 | M / M | is it meant for 2+2, for 1+3, or for both? |
| F-F-F-F | 43 & 69 | F / F | is it meant for 2+2, for 1+3, or for both? |
| F-M-F-M | 44 & 72 | F / F | is it meant for 2+2, for 1+3, or for both? |
| F-F-M-F | 45 & 71 | F / F | is it meant for 2+2, for 1+3, or for both? |
| M-M-F-M | 46 & 76 | M / M | is it meant for 2+2, for 1+3, or for both? |
| M-F-M-M | 47 & 79 | M / M | is it meant for 2+2, for 1+3, or for both? |
| F-M-M-M | 48 & 70 | M / M | is it meant for 2+2, for 1+3, or for both? |
| M-F-F-F | 49 & 77 | F / F | is it meant for 2+2, for 1+3, or for both? |
| F-F-F-M | 52 & 73 | F / F | is it meant for 2+2, for 1+3, or for both? |

## B. "1 child + 2 children" section (cases 53–60): which family has 1 child?
The old app joined both families into one list, so it can't tell "wife 1 + husband 2" from "wife 2 + husband 1". Today GENOVA gives this answer for both splits and flags it.

| Case | Pattern (3 children) | Result | Wife 1 + husband 2? | Wife 2 + husband 1? |
|---|---|---|---|---|
| 53 | F-F-F | F / F | ☐ | ☐ |
| 54 | F-M-M | M / M | ☐ | ☐ |
| 55 | F-F-M | F / F | ☐ | ☐ |
| 56 | F-M-F | F / F | ☐ | ☐ |
| 57 | M-F-F | F / F | ☐ | ☐ |
| 58 | M-M-M | M / M | ☐ | ☐ |
| 59 | M-F-M | M / M | ☐ | ☐ |
| 60 | M-M-F | M / M | ☐ | ☐ |

## C. "1 child + 3 children" section (cases 69–80): which family has 1 child?
The same problem applies. In addition, a "2 + 2" family enters the same 4-child list, so it also gets these answers.

| Case | Pattern (4 children) | Result | Wife 1 + husband 3? | Wife 3 + husband 1? | Also 2 + 2? |
|---|---|---|---|---|---|
| 69 | F-F-F-F | F / F | ☐ | ☐ | ☐ |
| 70 | F-M-M-M | M / M | ☐ | ☐ | ☐ |
| 71 | F-F-M-F | F / F | ☐ | ☐ | ☐ |
| 72 | F-M-F-M | F / F | ☐ | ☐ | ☐ |
| 73 | F-F-F-M | F / F | ☐ | ☐ | ☐ |
| 74 | F-M-M-F | M / M | ☐ | ☐ | ☐ |
| 75 | M-F-M-F | M / M | ☐ | ☐ | ☐ |
| 76 | M-M-F-M | M / M | ☐ | ☐ | ☐ |
| 77 | M-F-F-F | F / F | ☐ | ☐ | ☐ |
| 78 | M-M-M-M | M / M | ☐ | ☐ | ☐ |
| 79 | M-F-M-M | M / M | ☐ | ☐ | ☐ |
| 80 | M-M-F-F | M / M | ☐ | ☐ | ☐ |

## D. Other points to confirm
1. **Case numbers 61–68 don't exist.** The section header says "53–68", but only 53–60 are written, so the table has 72 cases, not 80. Were 8 cases lost, or is the header wrong?
2. **Patterns not in the table.** The old app returned "boy" (with a random %) for any pattern it didn't know. GENOVA currently shows "not in your table" and doesn't give an answer. Should it show "boy" instead?
3. **3rd and later children.** The old app picked boy or girl at random. GENOVA covers only the 1st and 2nd child, which is what the table defines.
4. **Combinations never covered:** families with 5 children in total (2 + 3 or 3 + 2), plus any pattern missing from a section (for example, 3 + 3 has 36 of the 64 possible patterns). Should any of them be added? If so, please give the results.

Reply with your answers, for example "Case 53 = wife 1 + husband 2". I'll then update only the cases you confirm.
