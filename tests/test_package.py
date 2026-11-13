"""Package-level checks using synthetic fixtures and isolated output directories."""
import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/sop-blueprint-coverage/scripts"
EXAMPLE = ROOT / "docs/検証/example.md"
GOLDEN = "a779368fa0f9aee49190fbb512dfce5d83e31445d06b2288142742bb5f7c1b8c"
TOOLS = "run_skill_script list_temp_files read_temp_file write_temp_file save_output_file list_domains get_blueprint_markdown stage_blueprint_to_temp list_skill_files read_skill_file"


def run(script, args, cwd, seed="0"):
    env = dict(os.environ, PYTHONHASHSEED=seed, PYTHONDONTWRITEBYTECODE="1")
    return subprocess.run([sys.executable, "-X", "utf8", str(script)] + args,
                          cwd=str(cwd), env=env, capture_output=True, text=True,
                          encoding="utf-8", timeout=300,
                          creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)


class PackageTests(unittest.TestCase):
    def test_golden_both_entrypoints_and_hash_seeds(self):
        with tempfile.TemporaryDirectory() as folder:
            temp = Path(folder)
            for name in ("generate_coverage.py", "coverage.py"):
                for seed in ("0", "7"):
                    output = temp / "coverage.md"
                    result = run(SCRIPTS / name, ["--input", str(EXAMPLE), "--output", str(output)], temp, seed)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    raw = output.read_bytes()
                    self.assertEqual(hashlib.sha256(raw).hexdigest(), GOLDEN)
                    self.assertNotIn(b"\r", raw)
                    payload = json.loads(raw.decode("utf-8").split("```json\n", 1)[1].split("```", 1)[0])
                    self.assertEqual(payload["obligations"], 8)
            self.assertEqual(sorted(p.name for p in temp.iterdir()), ["coverage.md"])

    def test_k1_defects_controls_mixed_and_known_limits(self):
        # The existing driver writes fixtures beside itself. Copy it into a temp
        # directory with each packaged entrypoint so tracked files stay untouched.
        with tempfile.TemporaryDirectory() as folder:
            temp = Path(folder)
            shutil.copyfile(ROOT / "docs/検証/k1_cases.py", temp / "k1_cases.py")
            shutil.copyfile(EXAMPLE, temp / "example.md")
            shutil.copyfile(SCRIPTS / "coverage.py", temp / "coverage.py")
            for name in ("coverage.py", "generate_coverage.py"):
                shutil.copyfile(SCRIPTS / name, temp / "coverage_check.py")
                result = run(temp / "k1_cases.py", [], temp)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout.strip().splitlines()[-1],
                                 "defects detected: 10 / 10, controls false-flagged: 0 / 3, mixed: ok")
                self.assertNotIn("[NG]", result.stdout)
                self.assertIn("x03_added_condition", result.stdout)
                for report in (temp / "k1").glob("*_out.md"):
                    self.assertNotIn(b"\r", report.read_bytes())

    def test_unparsed_and_unreadable_input_contract(self):
        cases = ("", "ordinary text", "=== SOP ===\nMust approve.\n",
                 "=== SOP ===\nplain text\n=== BLUEPRINT ===\n- Approval\n",
                 "=== SOP ===\nRecords must be retained.\n=== BLUEPRINT ===\n")
        with tempfile.TemporaryDirectory() as folder:
            temp = Path(folder)
            for name in ("generate_coverage.py", "coverage.py"):
                for text in cases:
                    source = temp / "input.md"
                    source.write_bytes(text.encode("utf-8"))
                    output = temp / "unparsed.md"
                    result = run(SCRIPTS / name, ["--input", str(source), "--output", str(output)], temp)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    report = output.read_text(encoding="utf-8")
                    self.assertIn("## UNPARSED", report)
                    self.assertNotIn("| COVERED |", report)
                absent_output = temp / (name + ".md")
                result = run(SCRIPTS / name, ["--input", str(temp / "absent.md"), "--output", str(absent_output)], temp)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(absent_output.exists())
                self.assertIn("cannot read input", result.stderr)

    def test_manifest_layout_and_distributed_script_constraints(self):
        manifest = json.loads((SCRIPTS / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(set(manifest), {"scripts"})
        scripts = {p.name for p in SCRIPTS.glob("*.py")}
        self.assertEqual(set(manifest["scripts"]), scripts)
        self.assertEqual(scripts, {"generate_coverage.py", "coverage.py"})
        for entry in manifest["scripts"].values():
            self.assertEqual(entry["arguments"], {
                "--input": {"type": "input_path", "required": True},
                "--output": {"type": "output_path", "required": True}})
        skill = (SCRIPTS.parent / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("run_as_batch: yes\n", skill)
        self.assertIn("allowed-tools: " + TOOLS + "\n", skill)
        self.assertTrue(all(p.is_dir() for p in SCRIPTS.parent.parent.iterdir()))
        allowed_imports = {"argparse", "hashlib", "re", "sys", "pathlib", "coverage"}
        for path in SCRIPTS.glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), feature_version=(3, 9))
            for node in ast.walk(tree):
                self.assertNotIsInstance(node, ast.JoinedStr, path.name)
                if isinstance(node, ast.Import):
                    self.assertTrue(all(n.name in allowed_imports for n in node.names))
                if isinstance(node, ast.ImportFrom):
                    self.assertIn(node.module, allowed_imports)
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        self.assertNotIn(node.func.id, {"eval", "exec", "compile", "__import__"})
                    if isinstance(node.func, ast.Attribute):
                        self.assertNotEqual(node.func.attr, "compile")
        # Classification remains byte-for-byte the prototype, apart from labels.
        source = (ROOT / "docs/検証/coverage_check.py").read_text(encoding="utf-8")
        expected = source.replace("Coverage Check (prototype)", "Coverage Check").replace(
            "coverage check (prototype)", "coverage check")
        self.assertEqual((SCRIPTS / "coverage.py").read_text(encoding="utf-8"), expected)


if __name__ == "__main__":
    unittest.main()
