# Coverage Check

- input_sha256: 763ac0d1344675f9281140f38203e4f1fe0908b260586b2871199655d2f42924
- obligations extracted from the SOP: 8
- Blueprint statements: 20
- domain words ignored in the overlap (in 3+ statements and in 25%+ of them): [approv order purcha reques]

## Summary

| Verdict | Count | Handled | Open |
|---|---|---|---|
| MISSING | 1 | 0 | 1 |
| WEAKENED | 1 | 0 | 1 |
| EXCEPTION_LOST | 1 | 0 | 1 |
| ROLE_MISMATCH | 1 | 0 | 1 |
| VALUE_MISMATCH | 1 | 0 | 1 |
| UNCLASSIFIED | 0 | 0 | 0 |
| COVERED | 3 | - | - |

- COVERED / obligations extracted: 3 / 8 (38%). A guide only: obligations the script could not extract are outside the denominator, and COVERED can still be wrong.
- COVERED but with an SOP number found only in another statement: 0 (spot-check these first)

## Findings

| ID | Verdict | SOP | Nearest Blueprint statement | Evidence |
|---|---|---|---|---|
| OB-006-bb131b74 | MISSING | Purchase records must be retained for 7 years. | (none) | w=0 t=2 r=0 n=0 [record retain]; no word, number or role in common with any Blueprint statement |
| OB-003-185b1f60 | WEAKENED | Purchase orders must never be placed before the vendor credit check is complete. | U04 [Atomic Thinking Step Register] A4 / Purchasing performs the vendor credit check / Purchasing | w=3 t=2 r=0 n=0 [check credit placed vendor]; the SOP prohibits, the nearest statement has no negation |
| OB-007-98fff216 | EXCEPTION_LOST | Blanket orders must be renewed every year unless the spend exceeds $25,000. | U07 [Atomic Thinking Step Register] A7 / Blanket orders are renewed every year / Purchasing | w=3 t=2 r=0 n=0 [blanke renewe year]; exception clause "the spend exceeds $25,000" has no counterpart (w=0 t=1 [spend]) |
| OB-004-ab1d7a62 | ROLE_MISMATCH | Vendor master changes must be approved by the CFO. | U13 [Human-in-the-Loop Specification] H3 / Approval of vendor master changes / Manager | w=3 t=2 r=0 n=0 [cfo change master vendor]; SOP role CFO vs Blueprint role MANAGER |
| OB-005-d766b0ae | VALUE_MISMATCH | Purchases of $20,000 or more require a second quote. | U14 [Human-in-the-Loop Specification] H4 / Second quote for purchases of $50,000 or more / Purchasing | w=2 t=2 r=0 n=0 [quote second]; SOP USD GE 20000 vs Blueprint USD GE 50000 |
| OB-001-ccaca295 | COVERED | Purchase requests of $10,000 or more must be approved by the Department Head. | U11 [Human-in-the-Loop Specification] H1 / Approval of purchase requests of $10,000 or more / Department Head | w=2 t=2 r=1 n=1 [depart head]; role DEPT_HEAD; USD GE 10000 |
| OB-002-ea4eb040 | COVERED | Purchase requests of $50,000 or more must be approved by the CFO. | U12 [Human-in-the-Loop Specification] H2 / Approval of purchase requests of $50,000 or more / CFO | w=1 t=1 r=1 n=1 [cfo]; role CFO; USD GE 50000 |
| OB-008-fd0ef31f | COVERED | Every purchase order must be matched to a supplier invoice before release. | U08 [Atomic Thinking Step Register] A8 / Supplier invoices are matched to purchase orders / Finance | w=3 t=2 r=0 n=0 [invoic matche releas suppli] |

## Not extracted (no obligation word, but it carries a number or a role)

- Invoices are paid within 30 days of receipt.

## Stale dispositions

- none

## Machine-readable result

```json
{"input_sha256":"763ac0d1344675f9281140f38203e4f1fe0908b260586b2871199655d2f42924","obligations":8,"statements":20,"results":[{"id":"OB-006-bb131b74","verdict":"MISSING","unit":"","disposition":""},{"id":"OB-003-185b1f60","verdict":"WEAKENED","unit":"U04","disposition":""},{"id":"OB-007-98fff216","verdict":"EXCEPTION_LOST","unit":"U07","disposition":""},{"id":"OB-004-ab1d7a62","verdict":"ROLE_MISMATCH","unit":"U13","disposition":""},{"id":"OB-005-d766b0ae","verdict":"VALUE_MISMATCH","unit":"U14","disposition":""},{"id":"OB-001-ccaca295","verdict":"COVERED","unit":"U11","disposition":""},{"id":"OB-002-ea4eb040","verdict":"COVERED","unit":"U12","disposition":""},{"id":"OB-008-fd0ef31f","verdict":"COVERED","unit":"U08","disposition":""}]}
```
