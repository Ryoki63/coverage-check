#!/usr/bin/env python3
# Verification driver only (not part of the submission).
# Builds K1 material offline, before any PS sign-in.
# Baseline: example.md with its Blueprint repaired so that all 8 obligations are COVERED (checked at run time).
# Each case is a copy of that baseline with ONE Blueprint statement mutated (the mixed case mutates two).
# Scoring is per obligation ID (the SOP is untouched, so the IDs are stable):
#   defect  : the target leaves COVERED, and no other obligation changes
#   control : nothing changes
#   mixed   : the defect target leaves COVERED, the paraphrased one stays COVERED, nothing else changes
# Known limits are run and printed, but not scored (design note section 5.7).
# K1 itself must still repeat this on Blueprint passages that Process Studio generated (design note section 5.9).
import os
import pathlib
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "k1"
PAGE = (HERE / "example.md").read_text(encoding="utf-8")
SOP, BP0 = PAGE.split("=== BLUEPRINT ===", 1)

A3 = "| A3 | Purchasing never places the purchase order before the vendor credit check is complete | Purchasing |"
A7 = "| A7 | Blanket orders are renewed every year unless the spend exceeds $25,000 | Purchasing |"
A11 = "| A11 | Purchase records are retained for 7 years | Finance |"
A12 = "| A12 | Suppliers are screened against the sanctions list before first use | Purchasing |"
H1 = "| H1 | Approval of purchase requests of $10,000 or more | Department Head |"
H2 = "| H2 | Approval of purchase requests of $50,000 or more | CFO |"
H3 = "| H3 | Approval of vendor master changes | CFO |"
H4 = "| H4 | Second quote for purchases of $20,000 or more | Purchasing |"

# Repairs to example.md (which seeds one verdict of each kind) so that the baseline is all COVERED.
REPAIRS = (
    ("| A3 | Purchasing places the purchase order with the vendor | Purchasing |", A3),
    ("| A7 | Blanket orders are renewed every year | Purchasing |", A7),
    ("| A10 | Receiving confirms the goods receipt | Receiving |",
     "| A10 | Receiving confirms the goods receipt | Receiving |\n" + A11 + "\n" + A12),
    ("| H3 | Approval of vendor master changes | Manager |", H3),
    ("| H4 | Second quote for purchases of $50,000 or more | Purchasing |", H4),
)
BP = BP0
for old, new in REPAIRS:
    if old not in BP:
        sys.exit("example.md changed: repair target not found: " + old)
    BP = BP.replace(old, new, 1)

# (case, line to replace, replacement, target obligation, expected verdict, what a reader would say)
DEFECTS = (
    ("d01_drop_numeric", H4, "", "005", "MISSING", "the second-quote duty disappears"),
    ("d02_drop_nonnumeric", A12, "", "008", "MISSING", "the sanctions screening disappears"),
    ("d03_soften_must", H1, "| H1 | Optional approval of purchase requests of $10,000 or more | Department Head |",
     "001", "WEAKENED", "mandatory became optional"),
    ("d04_lose_prohibition", A3,
     "| A3 | Purchasing places the purchase order before the vendor credit check is complete | Purchasing |",
     "003", "WEAKENED", "the prohibition lost its negation"),
    ("d05_change_amount", H1, "| H1 | Approval of purchase requests of $25,000 or more | Department Head |",
     "001", "VALUE_MISMATCH", "10,000 became 25,000"),
    ("d06_change_comparator", H2, "| H2 | Approval of purchase requests of more than $50,000 | CFO |",
     "002", "VALUE_MISMATCH", "or more became more than"),
    ("d07_change_role", H3, "| H3 | Approval of vendor master changes | Manager |",
     "004", "ROLE_MISMATCH", "CFO became Manager"),
    ("d08_drop_exception", A7, "| A7 | Blanket orders are renewed every year | Purchasing |",
     "007", "EXCEPTION_LOST", "the unless-clause disappears"),
    ("d09_exception_value", A7,
     "| A7 | Blanket orders are renewed every year unless the spend exceeds $30,000 | Purchasing |",
     "007", "VALUE_MISMATCH", "the exception keeps its shape but another amount"),
    ("d10_change_period", A11, "| A11 | Purchase records are retained for 5 years | Finance |",
     "006", "VALUE_MISMATCH", "7 years became 5 years"),
)
# controls: same meaning, other wording. Nothing may change.
CONTROLS = (
    ("c01_paraphrase_approval", H1,
     "| H1 | A purchase request of $10,000 or more is approved by the Department Head | Department Head |",
     "001", "paraphrase of an approval"),
    ("c02_paraphrase_exception", A7,
     "| A7 | Blanket orders are renewed every year, except when the spend exceeds $25,000 | Purchasing |",
     "007", "paraphrase of the exception (unless -> except when)"),
    ("c03_paraphrase_retention", A11, "| A11 | Purchase records are kept and retained for 7 years | Finance |",
     "006", "paraphrase of the retention duty"),
)
MIXED = ("m01_mixed", H3, "| H3 | Approval of vendor master changes | Manager |", "004",
         (H1, "| H1 | A purchase request of $10,000 or more is approved by the Department Head | Department Head |"),
         "001")
# known limits (section 5.7): printed for the record, not scored
LIMITS = (
    ("x01_synonyms_only", A12, "| A12 | Vendors are vetted against the embargo register before onboarding | Purchasing |",
     "008", "same meaning, no shared content word: expected to fall to MISSING/UNCLASSIFIED (a false alarm)"),
    ("x02_vague_statement", A7, "| A7 | Blanket orders are handled by Purchasing | Purchasing |",
     "007", "the statement goes vague"),
    ("x03_added_condition", H1,
     "| H1 | Approval of purchase requests of $10,000 or more for capital items only | Department Head |",
     "001", "a narrowing condition is added: word overlap cannot see it (a false COVERED)"),
)


def verdicts(out_bytes):
    found = {}
    for line in out_bytes.decode("utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and cells[0].startswith("OB-"):
            found[cells[0].split("-")[1]] = cells[1]
    return found


def run_case(name, edits):
    bp = BP
    for old, new in edits:
        if old not in bp:
            sys.exit(name + ": line to mutate not found: " + old)
        bp = bp.replace(old, new, 1)
    page = OUT / (name + ".md")
    page.write_bytes((SOP + "=== BLUEPRINT ===" + bp).encode("utf-8"))
    out = OUT / (name + "_out.md")
    r = subprocess.run([sys.executable, str(HERE / "coverage_check.py"), "--input", str(page), "--output", str(out)],
                       capture_output=True, text=True,
                       creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
    return r.returncode, verdicts(out.read_bytes())


def changed_ids(base, got):
    return sorted(k for k in base if got.get(k) != base[k])


OUT.mkdir(exist_ok=True)
code, base = run_case("_baseline", ())
print("baseline: exit=%d %s" % (code, " ".join("%s=%s" % (k, base[k]) for k in sorted(base))))
if code != 0 or len(base) != 8 or any(v != "COVERED" for v in base.values()):
    sys.exit("baseline is not all COVERED; K1 material would not be meaningful")
print("")

hit = 0
for name, old, new, target, expect, reader in DEFECTS:
    code, got = run_case(name, ((old, new),))
    ch = changed_ids(base, got)
    ok = code == 0 and ch == [target]
    hit += ok
    hint = "" if got.get(target) == expect else " (class differs from the guess: %s)" % expect
    print("%-26s %s: COVERED -> %-14s changed=%s  %s%s [%s]" % (
        name, target, got.get(target), ch or "-", reader, hint, "ok" if ok else "NG"))
print("")

false_flag = 0
for name, old, new, target, reader in CONTROLS:
    code, got = run_case(name, ((old, new),))
    ch = changed_ids(base, got)
    ok = code == 0 and not ch
    false_flag += not ok
    print("%-26s %s: COVERED -> %-14s changed=%s  %s [%s]" % (
        name, target, got.get(target), ch or "-", reader, "ok" if ok else "NG"))
print("")

name, old, new, target, extra, kept = MIXED
code, got = run_case(name, ((old, new), extra))
ch = changed_ids(base, got)
mixed_ok = code == 0 and ch == [target]
print("%-26s %s: COVERED -> %-14s %s: %-8s changed=%s  one defect plus one paraphrase [%s]" % (
    name, target, got.get(target), kept, got.get(kept), ch or "-", "ok" if mixed_ok else "NG"))
print("")

for name, old, new, target, reader in LIMITS:
    code, got = run_case(name, ((old, new),))
    ch = changed_ids(base, got)
    print("%-26s %s: COVERED -> %-14s changed=%s  %s [limit, not scored]" % (
        name, target, got.get(target), ch or "-", reader))
print("")
print("defects detected: %d / %d, controls false-flagged: %d / %d, mixed: %s" % (
    hit, len(DEFECTS), false_flag, len(CONTROLS), "ok" if mixed_ok else "NG"))
