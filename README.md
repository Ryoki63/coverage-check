# SOP to Blueprint Coverage Check

Process Studio Skillathon 2026 entry by Ryoki Kojima (IBM Consulting, Japan). Coverage Check helps reviewers check whether an SOP's mandatory steps, prohibitions, thresholds, approvers, and exceptions survived into a Blueprint. The deterministic report quotes source duties and candidate Blueprint statements, explains the evidence, and orders findings for review.

**COVERED is a heuristic match, not proof.** Duties the script cannot extract are outside its ratio. Review unextracted sentences and known false-positive/false-negative cases as well as flagged findings. No time-saving figure has been measured in Process Studio.

## Package and status

```text
skills/sop-blueprint-coverage/
  SKILL.md
  scripts/
    generate_coverage.py  # Analyze alpha wrapper
    coverage.py           # shared engine and combined-page chat entrypoint
    manifest.json         # both scripts, nested argument declarations
tests/                    # local package verification; not scanned by BYOS
docs/検証/                # synthetic fixtures and prototype engine
```

This is the alpha package. Beta full-Blueprint staging, uploaded SOP discovery, and separate-file argument design remain pending PS K0. Neither entrypoint currently accepts `--sop` or `--blueprint`.

Local synthetic baseline: 10/10 defects detected, 0/3 paraphrase controls false-flagged, mixed case correct. These hand-crafted cases are not PS K1, which requires three PS-generated Blueprints. Added narrowing conditions can still be missed; synonym-only paraphrases can be falsely flagged. K3 time measurement and K4 comparison are pending. Local execution does not establish PS Security passed, sandbox compatibility, Global instance selection, or successful Analyze delivery.

## Local verification

Python 3.9+ and its standard library are sufficient. Use `python3` on macOS/Linux if needed; on this Windows PC `python` is available (`py` is not).

```sh
python -X utf8 -m unittest discover -s tests -v
python -X utf8 docs/検証/k1_cases.py
python -X utf8 skills/sop-blueprint-coverage/scripts/generate_coverage.py --input docs/検証/example.md --output coverage.md
python -X utf8 -c "import hashlib,pathlib; print(hashlib.sha256(pathlib.Path('coverage.md').read_bytes()).hexdigest())"
```

Expected SHA-256: `a779368fa0f9aee49190fbb512dfce5d83e31445d06b2288142742bb5f7c1b8c`. Reports are written as UTF-8 bytes with LF, avoiding Windows `write_text` CRLF conversion. The package tests use temporary directories and do not rewrite tracked fixtures. The original K1 driver regenerates `docs/検証/k1/`; run it only when intentionally refreshing those synthetic files.

Input is one Markdown page delimited by `=== SOP ===` and `=== BLUEPRINT ===`, optionally `=== DISPOSITION ===`. Missing markers or unextractable content produce an UNPARSED report, not a pass. Unreadable input fails.

## Process Studio installation and verification

1. Connect this repository as a BYOS source with branch `main`, folder `skills`. Keep tests and proposal documents outside the scanned folder.
2. Use a dedicated token if one is required. Never paste credentials into this repository or a chat.
3. Sync in Settings → Skills → My Skills; inspect Security passed. Assign and save the skill in Main → Project Skills.
4. Verify Global selection, then Analyze a synthetic/public combined page. Check the actual report and delivery. Next verify full Blueprint staging and SOP attachment discovery for beta K0 before extending the interface.

Global PS inputs must be synthetic or public. Never store customer data or PS-generated IBM Confidential Blueprints in this repository or GitHub. Reports quoting such Blueprints also remain in temporary authorized workspaces. Local tests use synthetic fixtures only.

## Provenance

The shared engine preserves the prototype's classification behavior in `docs/検証/coverage_check.py`. Packaging follows the Process Studio BYOS batch-skill conventions as checked on 2026-11-11, including `run_as_batch: yes`. The prototype's only behavior change is LF output serialization for Windows parity.
