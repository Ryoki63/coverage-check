=== SOP ===
# Purchasing procedure (excerpt)
1. Purchase requests of $10,000 or more must be approved by the Department Head.
2. Purchase requests of $50,000 or more must be approved by the CFO.
3. Purchase orders must never be placed before the vendor credit check is complete.
4. Vendor master changes must be approved by the CFO.
5. Purchases of $20,000 or more require a second quote.
6. Purchase records must be retained for 7 years.
7. Blanket orders must be renewed every year unless the spend exceeds $25,000.
8. Suppliers must be screened against the sanctions list before first use.
9. Invoices are paid within 30 days of receipt.

=== BLUEPRINT ===
# Purchasing blueprint (excerpt)

### Atomic Thinking Step Register

| # | Step | Role |
|---|---|---|
| A1 | Requester raises a purchase request in the portal | Requester |
| A2 | Requester attaches the business justification | Requester |
| A3 | Purchasing never places the purchase order before the vendor credit check is complete | Purchasing |
| A4 | Purchasing performs the vendor credit check | Purchasing |
| A5 | Emergency orders are reported to the Department Head within 2 business days | Department Head |
| A6 | Manager approves purchase orders | Manager |
| A7 | Blanket orders are renewed every year unless the spend exceeds $25,000 | Purchasing |
| A8 | Supplier invoices are matched to purchase orders | Finance |
| A9 | Finance posts the matched invoice | Finance |
| A10 | Receiving confirms the goods receipt | Receiving |
| A11 | Purchase records are retained for 7 years | Finance |
| A12 | Suppliers are screened against the sanctions list before first use | Purchasing |

### Human-in-the-Loop Specification

| # | Check | Decision owner |
|---|---|---|
| H1 | Approval of purchase requests of $10,000 or more | Department Head |
| H2 | Approval of purchase requests of more than $50,000 | CFO |
| H3 | Approval of vendor master changes | CFO |
| H4 | Second quote for purchases of $20,000 or more | Purchasing |

### Agent Definition Register

| Agent | Responsibility |
|---|---|
| Intake agent | Classifies incoming requests by category and amount |
| Matching agent | Compares invoices with goods receipts |

### Integration with Systems of Record

| System | Interaction |
|---|---|
| ERP | Receives the approved purchase order |
| AP ledger | Receives the posted invoice |

### MCP Tool Register

| Tool | Purpose |
|---|---|
| erp.get_vendor | Reads the vendor master data |
| erp.create_order | Creates the purchase order in the ERP |
