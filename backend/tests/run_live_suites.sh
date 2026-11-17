#!/bin/bash
# Runs every live API suite one by one, pausing between files for the 30/min rate limit.
cd /app/backend
for f in tests/test_dedupe_live.py tests/test_family_pattern_live.py tests/test_family_pattern_split_live.py \
         tests/test_family_pattern_cases_report_live.py tests/test_family_pattern_pdf_comparison.py \
         tests/test_family_pattern_protection_live.py tests/test_family_pattern_limit_edges_live.py \
         tests/test_feedback_live.py tests/test_feedback_edges_live.py tests/test_live_api_e2e.py tests/test_api.py tests/test_security_live.py; do
  echo "== $f"
  python -m pytest "$f" -q -n 0 -p no:cacheprovider 2>&1 | grep -E "passed|failed|^FAILED|^E  " | head -8
  sleep 62
done
echo "== DONE"
