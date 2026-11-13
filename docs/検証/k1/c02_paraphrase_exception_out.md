# Coverage Check

- input_sha256: eafaf18f2c48ce2781611d9c4d06b7bc3ee831ff421ab8cb4d3ce5087c17bf21
- obligations extracted from the SOP: 8
- Blueprint statements: 22
- domain words ignored in the overlap (in 3+ statements and in 25%+ of them): [order purcha]

## Summary

| Verdict | Count | Handled | Open |
|---|---|---|---|
| MISSING | 0 | 0 | 0 |
| WEAKENED | 0 | 0 | 0 |
| EXCEPTION_LOST | 0 | 0 | 0 |
| ROLE_MISMATCH | 0 | 0 | 0 |
| VALUE_MISMATCH | 0 | 0 | 0 |
| UNCLASSIFIED | 0 | 0 | 0 |
| COVERED | 8 | - | - |

- COVERED / obligations extracted: 8 / 8 (100%). A guide only: obligations the script could not extract are outside the denominator, and COVERED can still be wrong.
- COVERED but with an SOP number found only in another statement: 0 (spot-check these first)

## Findings

| ID | Verdict | SOP | Nearest Blueprint statement | Evidence |
|---|---|---|---|---|
| OB-001-ccaca295 | COVERED | Purchase requests of $10,000 or more must be approved by the Department Head. | U13 [Human-in-the-Loop Specification] H1 / Approval of purchase requests of $10,000 or more / Department Head | w=4 t=2 r=1 n=1 [approv depart head reques]; role DEPT_HEAD; USD GE 10000 |
| OB-002-ea4eb040 | COVERED | Purchase requests of $50,000 or more must be approved by the CFO. | U14 [Human-in-the-Loop Specification] H2 / Approval of purchase requests of $50,000 or more / CFO | w=3 t=2 r=1 n=1 [approv cfo reques]; role CFO; USD GE 50000 |
| OB-003-185b1f60 | COVERED | Purchase orders must never be placed before the vendor credit check is complete. | U03 [Atomic Thinking Step Register] A3 / Purchasing never places the purchase order before the vendor credit check is complete / Purchasing | w=3 t=2 r=0 n=0 [check credit placed vendor] |
| OB-004-ab1d7a62 | COVERED | Vendor master changes must be approved by the CFO. | U15 [Human-in-the-Loop Specification] H3 / Approval of vendor master changes / CFO | w=5 t=2 r=1 n=0 [approv cfo change master vendor]; role CFO |
| OB-005-d766b0ae | COVERED | Purchases of $20,000 or more require a second quote. | U16 [Human-in-the-Loop Specification] H4 / Second quote for purchases of $20,000 or more / Purchasing | w=2 t=2 r=0 n=1 [quote second]; USD GE 20000 |
| OB-006-bb131b74 | COVERED | Purchase records must be retained for 7 years. | U11 [Atomic Thinking Step Register] A11 / Purchase records are retained for 7 years / Finance | w=2 t=2 r=0 n=1 [record retain]; YEAR EQ 7 |
| OB-007-98fff216 | COVERED | Blanket orders must be renewed every year unless the spend exceeds $25,000. | U07 [Atomic Thinking Step Register] A7 / Blanket orders are renewed every year, except when the spend exceeds $25,000 / Purchasing | w=3 t=2 r=0 n=0 [blanke renewe year] |
| OB-008-8d7886a0 | COVERED | Suppliers must be screened against the sanctions list before first use. | U12 [Atomic Thinking Step Register] A12 / Suppliers are screened against the sanctions list before first use / Purchasing | w=5 t=2 r=0 n=0 [first list sancti screen suppli] |

## Not extracted (no obligation word, but it carries a number or a role)

- Invoices are paid within 30 days of receipt.

## Stale dispositions

- none

## Machine-readable result

```json
{"input_sha256":"eafaf18f2c48ce2781611d9c4d06b7bc3ee831ff421ab8cb4d3ce5087c17bf21","obligations":8,"statements":22,"results":[{"id":"OB-001-ccaca295","verdict":"COVERED","unit":"U13","disposition":""},{"id":"OB-002-ea4eb040","verdict":"COVERED","unit":"U14","disposition":""},{"id":"OB-003-185b1f60","verdict":"COVERED","unit":"U03","disposition":""},{"id":"OB-004-ab1d7a62","verdict":"COVERED","unit":"U15","disposition":""},{"id":"OB-005-d766b0ae","verdict":"COVERED","unit":"U16","disposition":""},{"id":"OB-006-bb131b74","verdict":"COVERED","unit":"U11","disposition":""},{"id":"OB-007-98fff216","verdict":"COVERED","unit":"U07","disposition":""},{"id":"OB-008-8d7886a0","verdict":"COVERED","unit":"U12","disposition":""}]}
```
