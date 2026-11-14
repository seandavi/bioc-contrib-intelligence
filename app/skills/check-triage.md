---
label: Check triage
description: Explain the current BiocCheck / R CMD check findings and whether justifications hold.
---
Triage the current check results.

1. Call get_check_log for bioc-checks and for any platform that isn't OK.
2. Group findings: ERROR / WARNING / NOTE. For each: what the tool says (quote it), what it means in plain language, where in the code (search_code / read_file, cite with line permalinks), and what the fix usually is.
3. If the submitter justified a finding in the thread, say whether the justification addresses it. Never soften or re-derive what the tools reported: the tools' verdict stands; you only explain it.
4. Separate "must fix before acceptance" (ERRORs, WARNINGs, NOTEs Bioconductor requires fixing) from "recommended".
Reply in chat with the triage. Only touch the draft if the reviewer asks you to.
