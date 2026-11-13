---
name: sop-blueprint-coverage
description: Compare SOP obligations with Blueprint statements and report possible omissions, weakened duties, changed values, roles, and exceptions with evidence.
run_as_batch: yes
allowed-tools: run_skill_script list_temp_files read_temp_file write_temp_file save_output_file list_domains get_blueprint_markdown stage_blueprint_to_temp list_skill_files read_skill_file
---

# SOP to Blueprint Coverage Check

## Purpose

Help a process reviewer check whether mandatory steps, prohibitions, thresholds, approvers, and exceptions in an SOP survived into a Blueprint. Produce a deterministic report with quoted SOP text, the nearest Blueprint statement, and the evidence used. Review the whole report, including sentences the script did not extract.

## When to use

Use after drafting a Blueprint and before accepting it as a faithful account of the SOP. This is a lexical review aid; it does not certify compliance, approve a redesign, or establish that every source obligation was extracted.

## Inputs

The currently implemented alpha mode takes ONE UTF-8 Markdown page:

```text
=== SOP ===
<SOP text>
=== BLUEPRINT ===
<full Blueprint Markdown>
=== DISPOSITION ===
<optional review dispositions>
```

Use explicit obligation words such as must, require, never, or their supported Japanese equivalents. The optional DISPOSITION section records reviewer handling against the full obligation ID; it does not change the underlying verdict. Preserve source text and stable IDs. Do not invent a Blueprint or silently substitute a truncated excerpt.

In Analyze, `generate_coverage.py` automatically processes each combined page with `--input` and `--output`. The worker runs it once per page with a 300-second limit and collects one output. Missing markers or unparseable content produce an UNPARSED report explaining that nothing was checked.

For a chat invocation on an already combined page, discover its exact temporary filename with `list_temp_files`, invoke the declared `coverage.py` through `run_skill_script` with `--input` and a fresh `--output` filename, then deliver the existing report with `save_output_file`. Use the tool's actual schema, rather than inventing tool argument names.

The intended beta flow is `list_domains` → `stage_blueprint_to_temp` for the FULL Blueprint → `list_temp_files` for the attached `uploaded_<name>` SOP → a declared helper → `save_output_file`. The deployment's full staging and upload behavior remains unverified. The separate-file flags `--sop` and `--blueprint` are NOT implemented or declared yet: do not invoke them. Confirm beta K0 and the staged format before enabling that flow. `get_blueprint_markdown` returns only an excerpt (about 4,000 characters), so it cannot substitute for the full Blueprint.

Only pass file paths, never document bodies, as script arguments. Values must be at most 4,096 characters, with no newlines. Use declared flags once each, with at most 64 invocation tokens.

## Outputs

One UTF-8 Markdown report (LF line endings), normally `coverage.md`, containing the input SHA-256, extracted obligation and Blueprint statement counts, summary, findings with quotes and evidence, unextracted sentences carrying numbers or roles, stale dispositions, and embedded JSON. No second JSON file is required. Unreadable input fails with a nonzero exit code; it is not a successful check. Do not deliver an old report after a failed invocation.

## How to read the report

| Verdict | Review action |
|---|---|
| MISSING | Check whether a source duty has no lexical counterpart. |
| WEAKENED | Check a lost prohibition or mandatory duty made optional. |
| EXCEPTION_LOST | Check whether an exception clause lost its counterpart. |
| ROLE_MISMATCH | Check missing or changed approvers and responsible roles. |
| VALUE_MISMATCH | Check amounts, comparison operators, periods, and exception values. |
| UNCLASSIFIED | Review manually; the counterpart could not be accepted confidently. |
| COVERED | Confirm the quoted evidence; this is a heuristic match, not proof. |

Findings are sorted in the order above, then by obligation sequence. Review notes on COVERED rows too: a number may have been found only in another statement. The COVERED ratio uses only extracted obligations as its denominator. It is not a completeness score for the entire SOP. A disposition marks handling without turning an unresolved finding into COVERED.

## Customization

To adapt roles, obligation words, or synonyms, edit the bundled `coverage.py` and rerun the synthetic controls, defect cases, and known limitations outside `skills/`. The alpha wrapper uses the same engine. Do not generate new executable code at runtime. Local changes are not evidence of Process Studio compatibility until synchronized, assigned, and exercised there.

## Limitations

- Lexical matching can miss equivalent wording, produce false alarms, or incorrectly label a narrowed duty COVERED when an added condition shares the same words.
- Duties without supported obligation words may not be extracted. Some are listed for manual review; others remain outside the report.
- Tables, headings, and role dictionaries affect matching. Verify that ingestion preserves the full Markdown.
- The synthetic defect baseline is not a PS-generated Blueprint test and does not establish PS K1 success. Security scan, sandbox execution, beta staging, and batch behavior must be verified in Process Studio.
- Use synthetic or public data in Global Process Studio. Never use customer data. A PS-generated Blueprint marked IBM Confidential must remain in a temporary workspace; never put it in a repository, GitHub, or shared fixture folder. Reports containing its quoted text require the same handling. Remove temporary confidential material when finished, using the authorized local procedure.
- Scripts use Python 3.9+ standard library and the bundled engine only. No network, subprocess, f-string, or `re.compile` is used in the distributed scripts. No dependency installation is needed.

## Local run

From the [repository](https://github.com/Ryoki63/coverage-check) root (Windows uses `python`; macOS/Linux can use `python3`). The synthetic fixtures and tests sit outside the BYOS-scanned `skills/` folder:

```sh
python -X utf8 skills/sop-blueprint-coverage/scripts/generate_coverage.py --input docs/検証/example.md --output coverage.md
python -X utf8 skills/sop-blueprint-coverage/scripts/coverage.py --input docs/検証/example.md --output coverage.md
python -X utf8 -m unittest discover -s tests -v
```

`tests/` and the synthetic source fixtures are outside the BYOS-scanned `skills/` folder. The golden example report's SHA-256 begins with `a779368f` on LF output.
