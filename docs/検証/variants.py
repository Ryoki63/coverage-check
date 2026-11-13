#!/usr/bin/env python3
# Verification driver only (not part of the submission).
# Runs coverage_check.py on variants of example.md and on two malformed inputs, writes the results into this
# folder, and says whether each result is byte-identical to the one stored before this run.
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
# v1 = the first version of the example (HITL rows without the "Approval of" prefix).
# example.md is v2, so the base must be the saved v1, not example.md.
BASE = (HERE / "example_v1_backup.md").read_text(encoding="utf-8")


def swap(text, old, new):
    if old not in text:
        raise SystemExit("pattern not found: %r" % old)
    return text.replace(old, new)


def read_or_none(path):
    return path.read_bytes() if path.exists() else None


def state(before, after):
    if before is None:
        return "new"
    return "identical" if before == after else "CHANGED"


def run(src_name, out_name, text):
    src = HERE / src_name
    out = HERE / out_name
    src_before = read_or_none(src)
    out_before = read_or_none(out)
    src.write_text(text, encoding="utf-8")
    r = subprocess.run(
        [sys.executable, str(HERE / "coverage_check.py"), "--input", str(src), "--output", str(out), "--debug"],
        capture_output=True, text=True)
    print("== %s (exit=%d, input %s, output %s)" % (
        src_name, r.returncode, state(src_before, read_or_none(src)), state(out_before, read_or_none(out))))
    for line in r.stderr.splitlines():
        if line.startswith("generic=") or line.startswith("OB-"):
            print("  " + line)


v1 = BASE
v2 = swap(BASE, "| H1 | Purchase requests of $10,000 or more |", "| H1 | Approval of purchase requests of $10,000 or more |")
v2 = swap(v2, "| H2 | Purchase requests of $50,000 or more |", "| H2 | Approval of purchase requests of $50,000 or more |")
v2 = swap(v2, "| H3 | Vendor master changes |", "| H3 | Approval of vendor master changes |")
v3 = swap(v2, "8. Suppliers must be screened against the sanctions list before first use.",
          "8. Every purchase order must be matched to a supplier invoice before release.")
v4 = swap(v2, "1. Purchase requests of $10,000 or more must be approved by the Department Head.",
          "1. Purchase requests of $10,000 or more must be signed off by the Department Head.")
# v5: a synonym for the o8 obligation appears in the Blueprint (A10), which also shifts the domain-word set.
v5 = swap(v2, "| A10 | Receiving confirms the goods receipt | Receiving |",
          "| A10 | Compliance vets new vendors against the sanctions register | Compliance |")
# Two inputs the script must refuse politely (UNPARSED, exit 0): no delimiter, and no obligation sentence.
NODELIM = "just some text without markers\n"
ZERO = ("=== SOP ===\nThis is a short note.\n\n=== BLUEPRINT ===\n"
        "### Atomic Thinking Step Register\n\nA1 Do a thing\n")

CASES = (
    ("var_v1_no_verb.md", "var_v1_no_verb_out.md", v1),
    ("var_v2_approval.md", "var_v2_approval_out.md", v2),
    ("var_v3_fail_A.md", "var_v3_fail_A_out.md", v3),
    ("var_v4_fail_B.md", "var_v4_fail_B_out.md", v4),
    ("var_v5_synonym.md", "var_v5_out.md", v5),
    ("nodelim.md", "nodelim_out.md", NODELIM),
    ("zero.md", "zero_out.md", ZERO),
)

for src_name, out_name, text in CASES:
    run(src_name, out_name, text)
