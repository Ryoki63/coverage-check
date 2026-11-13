#!/usr/bin/env python3
# Verification driver only (not part of the submission).
# Measures the limitations written up in the design note (section 5.7): each case runs coverage_check.py on a small
# page built in a temporary folder and prints the script's verdict next to what a careful reader would say.
# A case prints DIFFERS when the script's verdict is no longer the recorded one (the note must then be updated).
import pathlib
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import coverage_check as cc  # noqa: E402

BLUEPRINT = (HERE / "example.md").read_text(encoding="utf-8").split("=== BLUEPRINT ===", 1)[1]
JP_BLUEPRINT = "\n### Human-in-the-Loop Specification\n- \u90e8\u9580\u9577\u304c\u627f\u8a8d\u3059\u308b\n"
NOT_BLUEPRINT = ("\n### Atomic Thinking Step Register\n"
                 "| A1 | Requester approves own request when not on leave | Requester |\n")
PLAIN_BLUEPRINT = ("\n### Atomic Thinking Step Register\n"
                   "| A1 | Requester approves own request | Requester |\n")

# (label, SOP sentence, Blueprint body, what a careful reader says, verdict recorded for the script)
CASES = (
    ("L1 verb differs (reviewed vs approval)",
     "1. Purchase requests of $10,000 or more must be reviewed by the Department Head.",
     BLUEPRINT, "not covered (review is not approval)", "COVERED"),
    ("L2 two obligations in one sentence",
     "1. Purchase requests of $10,000 or more must be logged in the audit trail and must be approved by the Department Head.",
     BLUEPRINT, "half covered (the audit trail is missing)", "COVERED"),
    ("L3 prohibition lost, no negation anywhere (control)",
     "1. Requesters must never approve their own requests.",
     PLAIN_BLUEPRINT, "prohibition lost", "WEAKENED"),
    ("L3 prohibition lost, an unrelated 'not' in the statement",
     "1. Requesters must never approve their own requests.",
     NOT_BLUEPRINT, "prohibition lost", "COVERED"),
    ("L4 Japanese morphology (shouninsha vs shounin)",
     "1. \u627f\u8a8d\u8005\u306f\u90e8\u9580\u9577\u3067\u306a\u3051\u308c\u3070\u306a\u3089\u306a\u3044\u3002",
     JP_BLUEPRINT, "covered (same meaning)", "UNCLASSIFIED"),
)

DATES = (
    ("Gregorian full date (JP)", "2026\u5e7411\u670814\u65e5"),
    ("Gregorian full date (EN)", "14 November 2026"),
    ("ISO date", "2026-11-14"),
    ("US date", "11/14/2026"),
    ("era year", "\u4ee4\u548c8\u5e74\u5ea6"),
    ("era year (Heisei)", "\u5e73\u6210\u301c30\u5e74".replace("\u301c", "")),
    ("bare day of month", "14\u65e5\u307e\u3067\u306b\u63d0\u51fa\u3059\u308b"),
    ("day count (real duration, kept on purpose)", "3\u65e5\u5f8c"),
)
RECORDED_DATE_FACTS = {
    "Gregorian full date (JP)": [], "Gregorian full date (EN)": [], "ISO date": [], "US date": [],
    "era year": ["YEAR EQ 8"], "era year (Heisei)": ["YEAR EQ 30"],
    "bare day of month": ["DAY EQ 14"], "day count (real duration, kept on purpose)": ["DAY EQ 3"],
}


def verdict_of(sop, blueprint, tmp):
    page = "=== SOP ===\n" + sop + "\n\n=== BLUEPRINT ===" + blueprint
    src = pathlib.Path(tmp) / "case.md"
    out = pathlib.Path(tmp) / "case_out.md"
    src.write_text(page, encoding="utf-8")
    r = subprocess.run([sys.executable, str(HERE / "coverage_check.py"), "--input", str(src), "--output", str(out),
                        "--debug"], capture_output=True, text=True)
    for line in r.stderr.splitlines():
        if line.startswith("OB-001-"):
            return line.split()[1]
    return "(no obligation line, exit=%d)" % r.returncode


bad = 0
with tempfile.TemporaryDirectory() as tmp:
    for label, sop, blueprint, reader, recorded in CASES:
        got = verdict_of(sop, blueprint, tmp)
        flag = "ok" if got == recorded else "DIFFERS"
        bad += got != recorded
        print("%-58s script=%-13s reader=%s [%s]" % (label, got, reader, flag))

print("")
print("word forms: key('placed')=%r key('places')=%r | key('approved')=%r key('approval')=%r" % (
    cc.key("placed"), cc.key("places"), cc.key("approved"), cc.key("approval")))
print("")
for label, text in DATES:
    facts = [cc.fact_str(f) for f in cc.numeric_facts(cc.norm(text))[0]]
    flag = "ok" if facts == RECORDED_DATE_FACTS[label] else "DIFFERS"
    bad += facts != RECORDED_DATE_FACTS[label]
    print("%-46s facts=%-16s [%s]" % (label, facts, flag))
print("")
print("cases differing from the recorded result: %d" % bad)
