#!/usr/bin/env python3
# Verification driver only (not part of the submission).
# Load test for coverage_check.py: 300 SOP obligations x 600 Blueprint statements, built in a temporary folder.
# The generator is a fixed linear congruential sequence (no random module), so the input is the same on every run.
# It runs the script twice, prints wall time, exit code, sizes and verdict counts, checks that both outputs are
# byte-identical, and asserts the 300-second per-page limit of the BYOS script mode.
import hashlib
import pathlib
import subprocess
import sys
import tempfile
import time

HERE = pathlib.Path(__file__).resolve().parent
N_SOP = 300
N_BP = 600
BASES = (1000, 5000, 10000, 25000, 50000, 100000)
ROLES = ("CFO", "Department Head", "Controller", "Manager", "Director")
VERDICTS = ("COVERED", "ROLE_MISMATCH", "VALUE_MISMATCH", "WEAKENED", "EXCEPTION_LOST", "MISSING", "UNCLASSIFIED")
LIMIT_SECONDS = 300


def sequence(seed):
    x = seed
    while True:
        x = (x * 1103515245 + 12345) % 2147483648
        yield x >> 8


def build():
    g = sequence(20261103)
    sop = ["=== SOP ===", "# Big SOP"]
    for i in range(N_SOP):
        amount = BASES[next(g) % len(BASES)] + i
        role = ROLES[next(g) % len(ROLES)]
        sop.append("Item %d: Requests of $%d or more must be approved by the %s." % (i, amount, role))
    bp = ["=== BLUEPRINT ===", "# Big Blueprint", "### Human-in-the-Loop Specification"]
    for i in range(N_BP):
        amount = BASES[next(g) % len(BASES)] + i
        role = ROLES[next(g) % len(ROLES)]
        bp.append("- H%d\uff5cApproval of requests of $%d or more\uff5c%s" % (i, amount, role))
    return "\n".join(sop + bp) + "\n"


def run_once(src, out):
    t0 = time.perf_counter()
    r = subprocess.run(
        [sys.executable, str(HERE / "coverage_check.py"), "--input", str(src), "--output", str(out)],
        capture_output=True, text=True)
    return r.returncode, time.perf_counter() - t0


def counts(text):
    found = {}
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and cells[0] in VERDICTS:
            found[cells[0]] = cells[1]
    return found


with tempfile.TemporaryDirectory() as tmp:
    src = pathlib.Path(tmp) / "stress_in.md"
    src.write_text(build(), encoding="utf-8")
    outs = []
    for k in (1, 2):
        out = pathlib.Path(tmp) / ("stress_out_%d.md" % k)
        code, seconds = run_once(src, out)
        print("run %d: exit=%d, %.2f s" % (k, code, seconds))
        assert code == 0, "the script must exit 0"
        assert seconds < LIMIT_SECONDS, "over the %d-second per-page limit" % LIMIT_SECONDS
        outs.append(out.read_bytes())
    print("input : %d bytes, %d obligations, %d statements" % (src.stat().st_size, N_SOP, N_BP))
    print("output: %d bytes, sha256 %s" % (len(outs[0]), hashlib.sha256(outs[0]).hexdigest()))
    print("two runs byte-identical: %s" % (outs[0] == outs[1]))
    print("verdict counts: %s" % counts(outs[0].decode("utf-8")))
    assert outs[0] == outs[1], "the output must not depend on the run"
