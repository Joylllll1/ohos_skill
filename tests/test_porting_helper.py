import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


HELPER = (
    Path(__file__).resolve().parents[1]
    / "skills" / "harmonyos-pc-porting" / "scripts" / "porting_helper.py"
)
GATE_IDS = (
    "scope", "route_proof", "build", "integration", "device_validation",
    "release_candidate", "submission", "review",
)
PROJECT_FIELDS = {
    "name", "root", "target_os", "target_device", "sdk_api", "abi",
    "upstream_revision", "route",
}


class PortingHelperTest(unittest.TestCase):
    def setUp(self):
        work = tempfile.TemporaryDirectory()
        self.addCleanup(work.cleanup)
        self.work = Path(work.name)
        self.root = self.work / "project"
        self.root.mkdir()
        self.record_path = self.work / "record.json"

    def run_helper(self, *args, code=0):
        result = subprocess.run(
            [sys.executable, str(HELPER), *map(str, args)],
            capture_output=True, text=True, timeout=10, check=False,
        )
        self.assertEqual(
            result.returncode, code,
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        return result

    def file(self, relative, content=b"fixture"):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return path

    def symlink(self, path, target, directory=False):
        try:
            path.symlink_to(target, target_is_directory=directory)
        except (NotImplementedError, OSError) as error:
            self.skipTest(f"Symlinks unavailable: {error}")

    def blank_record(self):
        self.run_helper("init", self.record_path)
        return json.loads(self.record_path.read_text(encoding="utf-8"))

    def check_record(self, record, code=0):
        self.record_path.write_text(json.dumps(record), encoding="utf-8")
        return self.read_check_output(code)

    def read_check_output(self, code):
        result = self.run_helper("check", self.record_path, "--root", self.root, code=code)
        return json.loads(result.stdout)

    def gate(self, record, gate_id):
        return next(gate for gate in record["gates"] if gate["id"] == gate_id)

    def evidence(self, relative, environment):
        content = f"{environment} fixture for {relative}".encode()
        self.file(relative, content)
        return {
            "path": relative,
            "sha256": hashlib.sha256(content).hexdigest(),
            "environment": environment,
        }

    def test_inventory_gives_filename_signals_and_skips_excluded_trees(self):
        manifests = [
            "AppScope/app.json5", "entry/src/main/module.json5", "build-profile.json5",
            "CMakeLists.txt", "meson.build", "configure.ac", "bridge/Cargo.toml",
            "client/package.json", "desktop.pro", "pyproject.toml", "requirements-dev.txt",
        ]
        secret = b"fixture secret must never appear in inventory output"
        for name in manifests:
            self.file(name, secret)
        for name in ("entry/Page.ets", "solver.f90", "solver.cpp", "solver.h", "bridge/lib.rs"):
            self.file(name)
        excluded = (
            ".git", "node_modules", "oh_modules", "build", "output", "dist", ".venv", "vendor",
        )
        for directory in excluded:
            self.file(f"nested/{directory}/app.json5")
            self.file(f"nested/{directory}/ignored.ets")

        output = self.run_helper("inventory", self.root).stdout
        self.assertNotIn(secret.decode(), output)
        report = json.loads(output)
        self.assertEqual(report["manifest_paths"], sorted(manifests))
        self.assertEqual(
            report["source_file_types"],
            {".cpp": 1, ".ets": 1, ".f90": 1, ".h": 1, ".rs": 1},
        )
        self.assertEqual(report["files_scanned"], len(manifests) + 5)
        self.assertFalse(report["truncated"])
        self.assertTrue(set(excluded).issubset(report["exclusions"]["directory_names"]))
        self.assertIn("Fortran", report["stack_signals"]["source_languages"])
        self.assertIn("CMake", report["stack_signals"]["build_and_dependency_files"])

    def test_inventory_excludes_symlinks_even_when_the_target_is_inside(self):
        outside = self.work / "outside"
        outside.mkdir()
        (outside / "app.json5").write_text("fixture", encoding="utf-8")
        source = self.file("real.cpp")
        self.symlink(self.root / "linked_dir", outside, directory=True)
        self.symlink(self.root / "package.json", outside / "app.json5")
        self.symlink(self.root / "copy.cpp", source)

        report = json.loads(self.run_helper("inventory", self.root).stdout)
        self.assertEqual(report["manifest_paths"], [])
        self.assertEqual(report["source_file_types"], {".cpp": 1})
        self.assertEqual(report["files_scanned"], 1)
        self.assertTrue(report["exclusions"]["symlinks"])

    def test_inventory_limit_is_deterministic_and_exact(self):
        self.file("z.py")
        self.file("a.c")
        self.file("middle/pyproject.toml")

        scan = self.run_helper("inventory", self.root, "--max-files", 2).stdout
        self.assertEqual(scan, self.run_helper("inventory", self.root, "--max-files", 2).stdout)
        limited = json.loads(scan)
        self.assertTrue(limited["truncated"])
        self.assertEqual(limited["files_scanned"], 2)
        self.assertEqual(limited["max_files"], 2)
        self.assertEqual(limited["source_file_types"], {".c": 1, ".py": 1})
        self.assertEqual(limited["manifest_paths"], [])

        exact = json.loads(self.run_helper("inventory", self.root, "--max-files", 3).stdout)
        self.assertFalse(exact["truncated"])
        self.assertEqual(exact["manifest_paths"], ["middle/pyproject.toml"])

    def test_init_builds_blank_record_and_refuses_overwrite(self):
        record = self.blank_record()
        self.assertEqual(record["schema_version"], 1)
        self.assertEqual(record["project"], dict.fromkeys(PROJECT_FIELDS, ""))
        self.assertEqual(
            record["gates"],
            [{"id": gate_id, "status": "pending", "reason": "", "evidence": []}
             for gate_id in GATE_IDS],
        )
        original = self.record_path.read_bytes()
        self.run_helper("init", self.record_path, code=2)
        self.assertEqual(self.record_path.read_bytes(), original)

    def test_init_refuses_dangling_destination_symlink(self):
        missing = self.work / "missing.json"
        self.symlink(self.record_path, missing)
        self.run_helper("init", self.record_path, code=2)
        self.assertTrue(self.record_path.is_symlink())
        self.assertFalse(missing.exists())

    def test_valid_incomplete_record_reports_gaps_and_next_gate(self):
        record = self.blank_record()
        record["project"]["name"] = "Example"
        del record["project"]["route"]
        record["gates"].reverse()
        scope = self.gate(record, "scope")
        scope.update(
            status="blocked",
            reason="Waiting for upstream revision.",
            evidence=[self.evidence("notes/scope.txt", "manual")],
        )

        result = self.check_record(record)
        self.assertEqual(result["evidence_integrity"], "pass")
        self.assertEqual(set(result["project_metadata_gaps"]), PROJECT_FIELDS - {"name"})
        self.assertEqual(result["next_gate"], {"id": "scope", "status": "blocked"})
        self.assertEqual(tuple(gate["id"] for gate in result["gates"]), GATE_IDS)
        self.assertEqual(self.gate(result, "scope")["verified_evidence_count"], 1)
        self.assertEqual(self.gate(result, "route_proof")["status"], "pending")

    def test_pending_evidence_still_requires_digest_match(self):
        record = self.blank_record()
        evidence = self.evidence("notes/scope.txt", "manual")
        self.gate(record, "scope")["evidence"] = [evidence]
        evidence["sha256"] = evidence["sha256"].upper()
        self.assertEqual(self.check_record(record)["evidence_integrity"], "pass")

        self.file(evidence["path"], b"changed")
        report = self.check_record(record, code=1)
        self.assertEqual(report["evidence_integrity"], "fail")
        scope = self.gate(report, "scope")
        self.assertEqual(scope["verified_evidence_count"], 0)
        self.assertIn("SHA-256 digest mismatch", " ".join(scope["issues"]))

    def test_blocked_stage_reports_handoff_reason_and_keeps_other_blockers(self):
        record = self.blank_record()
        build = self.gate(record, "build")
        build.update(status="blocked", reason="  ")
        invalid = self.check_record(record, code=1)
        self.assertIn("blocked requires a reason", " ".join(self.gate(invalid, "build")["issues"]))
        self.assertIsNone(invalid["next_gate"])

        build["reason"] = "docs/porting-plan.md H1: install SDK, then check compiler version"
        release = self.gate(record, "release_candidate")
        release.update(status="blocked", reason="docs/porting-plan.md H2: publisher role pending")
        valid = self.check_record(record)
        self.assertEqual(self.gate(valid, "build")["reason"], build["reason"])
        # Resolving one prerequisite must not erase another manually recorded wait.
        build.update(status="pending", reason="H1 resolved: SDK installation checked")
        resumed = self.check_record(record)
        self.assertEqual(self.gate(resumed, "release_candidate")["status"], "blocked")
        self.assertEqual(self.gate(resumed, "release_candidate")["reason"], release["reason"])

    def test_declared_pass_requires_evidence(self):
        record = self.blank_record()
        self.gate(record, "scope")["status"] = "pass"

        report = self.check_record(record, code=1)
        scope = self.gate(report, "scope")
        self.assertEqual(scope["status"], "pass")
        self.assertIn("pass requires evidence", scope["issues"])
        self.assertEqual(report["evidence_integrity"], "fail")
        self.assertEqual(self.gate(report, "route_proof")["status"], "pending")
        self.assertIsNone(report["next_gate"])

    def test_device_and_portal_gates_require_matching_environment(self):
        record = self.blank_record()
        environments = {
            "device_validation": "device",
            "submission": "portal",
            "review": "portal",
        }
        for gate in record["gates"]:
            gate["status"] = "pass"
            gate["evidence"] = [self.evidence(f"notes/{gate['id']}.txt", "host")]

        report = self.check_record(record, code=1)
        for gate_id, required in environments.items():
            gate = self.gate(report, gate_id)
            self.assertEqual(gate["verified_evidence_count"], 1)
            label = "emulator or device" if gate_id == "device_validation" else required
            self.assertIn(f"pass requires verified {label} evidence", gate["issues"])
            self.gate(record, gate_id)["evidence"].append(
                self.evidence(f"notes/{gate_id}-{required}.txt", required)
            )
        valid = self.check_record(record)
        self.assertEqual(valid["evidence_integrity"], "pass")
        self.assertIsNone(valid["next_gate"])

    def test_emulator_evidence_satisfies_runtime_gate_without_physical_device(self):
        record = self.blank_record()
        self.gate(record, "device_validation").update(
            status="pass", reason="Planned core flow validated on target emulator.",
            evidence=[self.evidence("notes/emulator.txt", "emulator")],
        )
        report = self.check_record(record)
        self.assertEqual(report["evidence_integrity"], "pass")
        self.assertEqual(self.gate(report, "device_validation")["issues"], [])

    def test_not_applicable_needs_reason_and_is_limited_to_store_gates(self):
        record = self.blank_record()
        self.gate(record, "device_validation").update(
            status="not_applicable", reason="No device available."
        )
        self.gate(record, "submission")["status"] = "not_applicable"
        report = self.check_record(record, code=1)
        self.assertIn("this gate requires a result", self.gate(report, "device_validation")["issues"])
        self.assertIn("not_applicable requires a reason", self.gate(report, "submission")["issues"])

        self.gate(record, "device_validation")["status"] = "pending"
        self.gate(record, "submission")["reason"] = "Store distribution is outside scope."
        self.gate(record, "review").update(
            status="not_applicable", reason="Store distribution is outside scope."
        )
        self.assertEqual(self.check_record(record)["evidence_integrity"], "pass")

    def test_check_refuses_absolute_and_traversing_evidence_paths(self):
        outside = self.work / "outside.txt"
        outside.write_bytes(b"fixture")
        record = self.blank_record()
        scope = self.gate(record, "scope")
        for path in ("../outside.txt", str(outside), "C:/outside.txt", "..\\outside.txt"):
            with self.subTest(path=path):
                scope["evidence"] = [
                    {"path": path, "sha256": hashlib.sha256(b"fixture").hexdigest(),
                     "environment": "manual"}
                ]
                report = self.check_record(record, code=1)
                self.assertIn(
                    "project-root-relative", " ".join(self.gate(report, "scope")["issues"])
                )

    def test_check_rejects_symlink_escapes_and_accepts_internal_symlink(self):
        outside = self.work / "outside"
        outside.mkdir()
        (outside / "log.txt").write_bytes(b"fixture")
        source = self.evidence("notes/log.txt", "manual")
        self.symlink(self.root / "linked_dir", outside, directory=True)
        self.symlink(self.root / "linked_file.txt", outside / "log.txt")
        self.symlink(self.root / "internal.txt", self.root / source["path"])

        record = self.blank_record()
        scope = self.gate(record, "scope")
        for path in ("linked_dir/log.txt", "linked_file.txt"):
            with self.subTest(path=path):
                scope["evidence"] = [
                    {"path": path, "sha256": hashlib.sha256(b"fixture").hexdigest(),
                     "environment": "manual"}
                ]
                report = self.check_record(record, code=1)
                self.assertIn("resolves outside", " ".join(self.gate(report, "scope")["issues"]))
        scope["evidence"] = [dict(source, path="internal.txt")]
        self.assertEqual(self.check_record(record)["evidence_integrity"], "pass")

    def test_check_rejects_missing_and_nonregular_files(self):
        (self.root / "directory").mkdir()
        paths = ("missing.txt", "directory")
        if hasattr(os, "mkfifo"):
            os.mkfifo(self.root / "pipe.txt")
            paths += ("pipe.txt",)
        record = self.blank_record()
        self.gate(record, "scope")["evidence"] = [
            {"path": path, "sha256": "a" * 64, "environment": "manual"}
            for path in paths
        ]

        report = self.check_record(record, code=1)
        scope = self.gate(report, "scope")
        self.assertEqual(scope["verified_evidence_count"], 0)
        self.assertEqual(len(scope["issues"]), len(paths))
        self.assertIn("regular file", scope["issues"][1])

    def test_check_rejects_malformed_evidence_fields(self):
        record = self.blank_record()
        self.gate(record, "scope")["evidence"] = [
            None,
            {"path": "", "sha256": "z" * 64, "environment": ["host"]},
        ]
        report = self.check_record(record, code=1)
        issues = self.gate(report, "scope")["issues"]
        self.assertIn("evidence[0] must be an object", issues)
        self.assertTrue(any("path must be" in issue for issue in issues))
        self.assertTrue(any("sha256 must be" in issue for issue in issues))
        self.assertTrue(any("environment must be" in issue for issue in issues))

    def test_check_rejects_invalid_json(self):
        for invalid in ('{"schema_version":', '{"a": 1, "a": 2}', '{"a": NaN}', "[]"):
            with self.subTest(invalid=invalid):
                self.record_path.write_text(invalid, encoding="utf-8")
                report = self.read_check_output(code=1)
                self.assertEqual(report["evidence_integrity"], "fail")
                self.assertTrue(report["issues"])

    def test_check_detects_invalid_schema_and_exact_gate_ids(self):
        record = self.blank_record()
        record["schema_version"] = True
        record["project"] = []
        record["gates"][-1]["id"] = "build"
        record["gates"].append({"id": ["unknown"]})
        self.gate(record, "scope").update(status={"pending": True}, reason=9, evidence={})

        report = self.check_record(record, code=1)
        issues = " ".join(report["issues"])
        self.assertIn("schema_version must be the integer 1", issues)
        self.assertIn("project must be an object", issues)
        self.assertIn("repeats gate 'build'", issues)
        self.assertIn("unknown or missing ID", issues)
        self.assertIn("gate is missing", self.gate(report, "review")["issues"])
        self.assertEqual(len(self.gate(report, "scope")["issues"]), 3)
        self.assertIsNone(report["next_gate"])

    def test_cli_errors_use_exit_code_two(self):
        self.run_helper("inventory", self.root, "--max-files", 0, code=2)
        self.run_helper("inventory", self.root / "missing", code=2)
        self.run_helper("check", self.record_path, "--root", self.root, code=2)


if __name__ == "__main__":
    unittest.main()
