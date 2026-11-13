# Coverage Check

- input_sha256: e7ccf52cade51151e9349524120d6218a250f17baae21c0edefbd1001202c3a9
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
| UNCLASSIFIED | 1 | 0 | 1 |
| COVERED | 2 | - | - |

- COVERED / obligations extracted: 2 / 8 (25%). A guide only: obligations the script could not extract are outside the denominator, and COVERED can still be wrong.
- COVERED but with an SOP number found only in another statement: 0 (spot-check these first)

## Findings

| ID | Verdict | SOP | Nearest Blueprint statement | Evidence |
|---|---|---|---|---|
| OB-006-bb131b74 | MISSING | Purchase records must be retained for 7 years. | (none) | w=0 t=2 r=0 n=0 [record retain]; no word, number or role in common with any Blueprint statement |
| OB-003-185b1f60 | WEAKENED | Purchase orders must never be placed before the vendor credit check is complete. | U04 [Atomic Thinking Step Register] A4 / Purchasing performs the vendor credit check / Purchasing | w=3 t=2 r=0 n=0 [check credit placed vendor]; the SOP prohibits, the nearest statement has no negation |
| OB-007-98fff216 | EXCEPTION_LOST | Blanket orders must be renewed every year unless the spend exceeds $25,000. | U07 [Atomic Thinking Step Register] A7 / Blanket orders are renewed every year / Purchasing | w=3 t=2 r=0 n=0 [blanke renewe year]; exception clause "the spend exceeds $25,000" has no counterpart (w=0 t=1 [spend]) |
| OB-004-ab1d7a62 | ROLE_MISMATCH | Vendor master changes must be approved by the CFO. | U13 [Human-in-the-Loop Specification] H3 / Approval of vendor master changes / Manager | w=3 t=2 r=0 n=0 [cfo change master vendor]; SOP role CFO vs Blueprint role MANAGER |
| OB-005-d766b0ae | VALUE_MISMATCH | Purchases of $20,000 or more require a second quote. | U14 [Human-in-the-Loop Specification] H4 / Second quote for purchases of $50,000 or more / Purchasing | w=2 t=2 r=0 n=0 [quote second]; SOP USD GE 20000 vs Blueprint USD GE 50000 |
| OB-008-8d7886a0 | UNCLASSIFIED | Suppliers must be screened against the sanctions list before first use. | U08 [Atomic Thinking Step Register] A8 / Supplier invoices are matched to purchase orders / Finance | w=1 t=2 r=0 n=0 [first list sancti screen suppli]; below the threshold, so the nearest statement is not accepted as the counterpart |
| OB-001-e3a4706b | COVERED | Purchase requests of $10,000 or more must be signed off by the Department Head. | U11 [Human-in-the-Loop Specification] H1 / Approval of purchase requests of $10,000 or more / Department Head | w=2 t=2 r=1 n=1 [depart head signed]; role DEPT_HEAD; USD GE 10000 |
| OB-002-ea4eb040 | COVERED | Purchase requests of $50,000 or more must be approved by the CFO. | U12 [Human-in-the-Loop Specification] H2 / Approval of purchase requests of $50,000 or more / CFO | w=1 t=1 r=1 n=1 [cfo]; role CFO; USD GE 50000 |

## Not extracted (no obligation word, but it carries a number or a role)

- Invoices are paid within 30 days of receipt.

## Stale dispositions

- none

## Machine-readable result

```json
{"input_sha256":"e7ccf52cade51151e9349524120d6218a250f17baae21c0edefbd1001202c3a9","obligations":8,"statements":20,"results":[{"id":"OB-006-bb131b74","verdict":"MISSING","unit":"","disposition":""},{"id":"OB-003-185b1f60","verdict":"WEAKENED","unit":"U04","disposition":""},{"id":"OB-007-98fff216","verdict":"EXCEPTION_LOST","unit":"U07","disposition":""},{"id":"OB-004-ab1d7a62","verdict":"ROLE_MISMATCH","unit":"U13","disposition":""},{"id":"OB-005-d766b0ae","verdict":"VALUE_MISMATCH","unit":"U14","disposition":""},{"id":"OB-008-8d7886a0","verdict":"UNCLASSIFIED","unit":"U08","disposition":""},{"id":"OB-001-e3a4706b","verdict":"COVERED","unit":"U11","disposition":""},{"id":"OB-002-ea4eb040","verdict":"COVERED","unit":"U12","disposition":""}]}
```
