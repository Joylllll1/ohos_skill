#!/usr/bin/env python3
"""Inventory source filenames and verify a HarmonyOS PC migration evidence record."""

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import stat


SCHEMA_VERSION = 1
DEFAULT_MAX_FILES = 5000
PROJECT_FIELDS = (
    "name", "root", "target_os", "target_device", "sdk_api", "abi",
    "upstream_revision", "route",
)
GATE_IDS = (
    "scope", "route_proof", "build", "integration", "device_validation",
    "release_candidate", "submission", "review",
)
GATE_STATUSES = ("pending", "pass", "blocked", "not_applicable")
EVIDENCE_ENVIRONMENTS = ("host", "emulator", "device", "portal", "manual")
OPTIONAL_GATES = ("submission", "review")
REQUIRED_ENVIRONMENTS = {
    "device_validation": ("emulator", "device"),
    "submission": ("portal",),
    "review": ("portal",),
}
SHA256_PATTERN = re.compile(r"[0-9a-fA-F]{64}")

EXCLUDED_DIRECTORIES = (
    ".cache", ".git", ".gradle", ".hg", ".hvigor", ".next", ".svn", ".venv",
    "__pycache__", "build", "dist", "node_modules", "oh_modules", "output",
    "vendor",
)
SOURCE_SUFFIXES = {
    ".asm": "Assembly", ".s": "Assembly",
    ".c": "C", ".h": "C/C++ header",
    ".cc": "C++", ".cpp": "C++", ".cxx": "C++",
    ".hh": "C++", ".hpp": "C++", ".hxx": "C++",
    ".m": "Objective-C or MATLAB", ".mm": "Objective-C++",
    ".cs": "C#", ".fs": "F#", ".vb": "Visual Basic",
    ".ets": "ArkTS", ".ts": "TypeScript", ".tsx": "TypeScript",
    ".js": "JavaScript", ".mjs": "JavaScript", ".cjs": "JavaScript",
    ".jsx": "JavaScript", ".vue": "Vue", ".svelte": "Svelte",
    ".htm": "HTML", ".html": "HTML", ".css": "CSS", ".scss": "SCSS",
    ".py": "Python", ".pyi": "Python", ".pyx": "Cython",
    ".java": "Java", ".kt": "Kotlin", ".kts": "Kotlin", ".groovy": "Groovy",
    ".rs": "Rust", ".go": "Go", ".swift": "Swift", ".dart": "Dart",
    ".f": "Fortran", ".for": "Fortran", ".f90": "Fortran", ".f95": "Fortran",
    ".f03": "Fortran", ".f08": "Fortran",
    ".qml": "QML", ".ui": "UI resource", ".glade": "Glade UI",
    ".rb": "Ruby", ".php": "PHP", ".lua": "Lua", ".tcl": "Tcl",
    ".sh": "Shell", ".bash": "Shell", ".ps1": "PowerShell",
}
MANIFEST_NAMES = {
    "app.json5": "HarmonyOS app/module metadata",
    "module.json5": "HarmonyOS app/module metadata",
    "build-profile.json5": "HarmonyOS build profile",
    "hvigorfile.ts": "Hvigor",
    "hvigor-config.json5": "Hvigor",
    "oh-package.json5": "ohpm",
    "oh-package-lock.json5": "ohpm",
    "cmakelists.txt": "CMake",
    "cmakepresets.json": "CMake",
    "cmakeuserpresets.json": "CMake",
    "configure.ac": "Autotools",
    "configure.in": "Autotools",
    "makefile.am": "Automake",
    "makefile": "Make",
    "gnumakefile": "Make",
    "meson.build": "Meson",
    "meson_options.txt": "Meson",
    "meson.options": "Meson",
    "cargo.toml": "Cargo",
    "cargo.lock": "Cargo",
    "package.json": "JavaScript package manifest",
    "package-lock.json": "npm",
    "npm-shrinkwrap.json": "npm",
    "pnpm-lock.yaml": "pnpm",
    "pnpm-workspace.yaml": "pnpm",
    "yarn.lock": "Yarn",
    "bun.lock": "Bun",
    "bun.lockb": "Bun",
    "tsconfig.json": "TypeScript configuration",
    "tauri.conf.json": "Tauri",
    "tauri.conf.json5": "Tauri",
    "tauri.toml": "Tauri",
    "electron-builder.yml": "Electron Builder",
    "electron-builder.yaml": "Electron Builder",
    "electron-builder.json": "Electron Builder",
    "pyproject.toml": "Python packaging",
    "setup.py": "Python packaging",
    "setup.cfg": "Python packaging or tooling",
    "pipfile": "Pipenv",
    "pipfile.lock": "Pipenv",
    "poetry.lock": "Poetry",
    "uv.lock": "uv",
    "environment.yml": "Conda",
    "environment.yaml": "Conda",
    "build.gradle": "Gradle",
    "build.gradle.kts": "Gradle",
    "settings.gradle": "Gradle",
    "settings.gradle.kts": "Gradle",
    "gradle.properties": "Gradle",
    "pom.xml": "Maven",
    "directory.build.props": "MSBuild",
    "go.mod": "Go modules",
    "go.sum": "Go modules",
    "gemfile": "Bundler",
    "gemfile.lock": "Bundler",
    "composer.json": "Composer",
    "composer.lock": "Composer",
    "pubspec.yaml": "Dart packages",
    "pubspec.lock": "Dart packages",
    "package.swift": "SwiftPM",
}
MANIFEST_SUFFIXES = {
    ".pro": "qmake-style project filename",
    ".pri": "qmake-style project filename",
    ".sln": "Visual Studio solution",
    ".slnx": "Visual Studio solution",
    ".csproj": "MSBuild",
    ".fsproj": "MSBuild",
    ".vbproj": "MSBuild",
    ".vcxproj": "MSBuild",
}


def manifest_signal(filename, suffix):
    name = filename.casefold()
    if name.startswith("requirements") and name.endswith(".txt"):
        return "Python requirements"
    return MANIFEST_NAMES.get(name) or MANIFEST_SUFFIXES.get(suffix)


def scan_mode(path, scan_errors):
    try:
        info = path.lstat()
    except OSError as error:
        scan_errors.append(error)
        return 0
    if getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
        return 0
    return info.st_mode


def inventory(root, max_files):
    """Count scanned regular source files and collect manifest paths by filename."""
    file_types = Counter()
    manifests = []
    manifest_signals = set()
    scan_errors = []
    scanned = 0
    truncated = False

    for directory, subdirs, filenames in os.walk(root, onerror=scan_errors.append):
        parent = Path(directory)
        subdirs[:] = [
            name for name in sorted(subdirs)
            if name.casefold() not in EXCLUDED_DIRECTORIES
            and stat.S_ISDIR(scan_mode(parent / name, scan_errors))
        ]
        for name in sorted(filenames):
            path = parent / name
            if not stat.S_ISREG(scan_mode(path, scan_errors)):
                continue

            if scanned == max_files:
                truncated = True
                break
            scanned += 1
            suffix = path.suffix.casefold()
            if suffix in SOURCE_SUFFIXES:
                file_types[suffix] += 1
            signal = manifest_signal(name, suffix)
            if signal:
                manifests.append(path.relative_to(root).as_posix())
                manifest_signals.add(signal)
        if truncated:
            break

    return {
        "root": str(root),
        "files_scanned": scanned,
        "source_file_types": dict(sorted(file_types.items())),
        "manifest_paths": sorted(manifests),
        "stack_signals": {
            "source_languages": sorted({SOURCE_SUFFIXES[ext] for ext in file_types}),
            "build_and_dependency_files": sorted(manifest_signals),
        },
        "exclusions": {
            "directory_names": list(EXCLUDED_DIRECTORIES),
            "symlinks": True,
            "nonregular_files": True,
            "windows_reparse_points": True,
        },
        "max_files": max_files,
        "truncated": truncated,
        "scan_errors": [str(error) for error in scan_errors],
        "scope": (
            "Signals use filename and extension heuristics. Counts describe scanned "
            "regular files. Skipped paths may contain additional source or manifests."
        ),
    }


def init_record(destination):
    """Create a blank record with exclusive file creation."""
    record = {
        "schema_version": SCHEMA_VERSION,
        "project": dict.fromkeys(PROJECT_FIELDS, ""),
        "gates": [
            {"id": gate_id, "status": "pending", "reason": "", "evidence": []}
            for gate_id in GATE_IDS
        ],
    }
    content = json.dumps(record, indent=2) + "\n"
    with destination.open("x", encoding="utf-8", newline="\n") as output:
        output.write(content)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key {key!r}")
        result[key] = value
    return result


def reject_json_constant(value):
    raise ValueError(f"Invalid JSON constant {value!r}")


def metadata_gaps(project, issues):
    if not isinstance(project, dict):
        issues.append("project must be an object")
        return list(PROJECT_FIELDS)

    gaps = []
    for field in PROJECT_FIELDS:
        value = project.get(field, "")
        if not isinstance(value, str):
            issues.append(f"project.{field} must be a string")
        elif not value.strip():
            gaps.append(field)
    return gaps


def index_gates(gates, issues):
    if not isinstance(gates, list):
        issues.append("gates must be an array")
        return {}

    result = {}
    for index, gate in enumerate(gates):
        if not isinstance(gate, dict):
            issues.append(f"gates[{index}] must be an object")
            continue
        gate_id = gate.get("id")
        if gate_id not in GATE_IDS:
            issues.append(f"gates[{index}] has an unknown or missing ID")
        elif gate_id in result:
            issues.append(f"gates[{index}] repeats gate {gate_id!r}")
        else:
            result[gate_id] = gate
    return result


def evidence_location(root, reference):
    """Resolve a portable relative path and constrain its target to the scan root."""
    path = PurePosixPath(reference)
    if (
        path.is_absolute() or ".." in path.parts or "\\" in reference
        or PureWindowsPath(reference).drive or "\0" in reference
    ):
        raise ValueError("path must be project-root-relative with no parent traversal")
    resolved = (root / path).resolve(strict=True)
    try:
        relative_path = resolved.relative_to(root)
    except ValueError:
        raise ValueError("path resolves outside the project root") from None
    return resolved, relative_path


def open_evidence(root, relative_path):
    """Open a resolved path using directory descriptors when available."""
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NONBLOCK", 0)
    if (
        os.open not in os.supports_dir_fd or not hasattr(os, "O_NOFOLLOW")
        or not hasattr(os, "O_DIRECTORY")
    ):
        return os.open(root / relative_path, flags)

    flags |= os.O_NOFOLLOW
    directory_flags = flags | os.O_DIRECTORY
    directory_fd = os.open(root, directory_flags)
    try:
        for component in relative_path.parts[:-1]:
            child_fd = os.open(component, directory_flags, dir_fd=directory_fd)
            os.close(directory_fd)
            directory_fd = child_fd
        return os.open(relative_path.name, flags, dir_fd=directory_fd)
    finally:
        os.close(directory_fd)


def evidence_sha256(root, reference):
    resolved, relative_path = evidence_location(root, reference)
    initial_stat = resolved.lstat()
    if not stat.S_ISREG(initial_stat.st_mode):
        raise ValueError("path must identify a regular file")

    fd = open_evidence(root, relative_path)
    try:
        opened_stat = os.fstat(fd)
        if not stat.S_ISREG(opened_stat.st_mode):
            raise ValueError("path must identify a regular file")
        if not os.path.samestat(initial_stat, opened_stat):
            raise ValueError("file changed while being opened")
        if resolved.resolve(strict=True) != resolved:
            raise ValueError("path changed while being opened")

        digest = hashlib.sha256()
        with os.fdopen(fd, "rb", closefd=False) as evidence_file:
            for chunk in iter(lambda: evidence_file.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
    finally:
        os.close(fd)


def verify_evidence(entry, root):
    if not isinstance(entry, dict):
        return ["must be an object"]

    issues = []
    path = entry.get("path")
    expected = entry.get("sha256")
    if not isinstance(path, str) or not path.strip():
        issues.append("path must be a nonempty string")
    if not isinstance(expected, str) or not SHA256_PATTERN.fullmatch(expected):
        issues.append("sha256 must be a 64-digit hexadecimal digest")
    if entry.get("environment") not in EVIDENCE_ENVIRONMENTS:
        issues.append("environment must be host, emulator, device, portal, or manual")
    if issues:
        return issues

    try:
        actual = evidence_sha256(root, path)
    except (OSError, RuntimeError, ValueError) as error:
        return [f"{path!r}: {error}"]
    if actual != expected.lower():
        return [f"{path!r}: SHA-256 digest mismatch"]
    return []


def check_gate(gate_id, gate, root):
    report = {
        "id": gate_id,
        "status": None,
        "reason": None,
        "evidence_count": 0,
        "verified_evidence_count": 0,
        "issues": [],
    }
    issues = report["issues"]
    if gate is None:
        issues.append("gate is missing")
        return report

    status = gate.get("status")
    reason = gate.get("reason")
    entries = gate.get("evidence")
    if status in GATE_STATUSES:
        report["status"] = status
    else:
        issues.append("status must be pending, pass, blocked, or not_applicable")
    if not isinstance(reason, str):
        issues.append("reason must be a string")
    else:
        report["reason"] = reason
        if status == "blocked" and not reason.strip():
            issues.append("blocked requires a reason")
    if status == "not_applicable":
        if gate_id not in OPTIONAL_GATES:
            issues.append("this gate requires a result")
        if isinstance(reason, str) and not reason.strip():
            issues.append("not_applicable requires a reason")
    if not isinstance(entries, list):
        issues.append("evidence must be an array")
        return report

    report["evidence_count"] = len(entries)
    verified_environments = set()
    for index, entry in enumerate(entries):
        entry_issues = verify_evidence(entry, root)
        if entry_issues:
            issues.extend(f"evidence[{index}] {issue}" for issue in entry_issues)
        else:
            report["verified_evidence_count"] += 1
            verified_environments.add(entry["environment"])

    if status == "pass":
        if not entries:
            issues.append("pass requires evidence")
        required = REQUIRED_ENVIRONMENTS.get(gate_id)
        if required and not verified_environments.intersection(required):
            issues.append(f"pass requires verified {' or '.join(required)} evidence")
    return report


def check_record(record_path, root):
    """Validate the record and report the next gate when integrity checks pass."""
    report = {
        "evidence_integrity": "fail",
        "project_metadata_gaps": [],
        "gates": [],
        "issues": [],
        "next_gate": None,
        "verification_scope": (
            "Record schema, recorded environment labels, referenced file paths, and "
            "SHA-256 digests. Gate statuses are declarations from the record."
        ),
    }
    issues = report["issues"]
    try:
        with record_path.open(encoding="utf-8-sig") as source:
            record = json.load(
                source, object_pairs_hook=unique_object,
                parse_constant=reject_json_constant,
            )
    except (OSError, RecursionError, ValueError) as error:
        issues.append(f"Could not read record as JSON: {error}")
        return report
    if not isinstance(record, dict):
        issues.append("record must be an object")
        return report
    version = record.get("schema_version")
    if type(version) is not int or version != SCHEMA_VERSION:
        issues.append(f"schema_version must be the integer {SCHEMA_VERSION}")

    report["project_metadata_gaps"] = metadata_gaps(record.get("project"), issues)
    indexed = index_gates(record.get("gates"), issues)
    gates = [check_gate(gate_id, indexed.get(gate_id), root) for gate_id in GATE_IDS]
    report["gates"] = gates
    if issues or any(gate["issues"] for gate in gates):
        return report
    report["evidence_integrity"] = "pass"
    for gate in gates:
        if gate["status"] in ("pending", "blocked"):
            report["next_gate"] = {"id": gate["id"], "status": gate["status"]}
            break
    return report


def positive_integer(value):
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("expected a positive integer") from None
    if number < 1:
        raise argparse.ArgumentTypeError("expected a positive integer")
    return number


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    scan = commands.add_parser("inventory", help="scan regular file names and extensions")
    scan.add_argument("root", type=Path, help="project directory to scan")
    scan.add_argument(
        "--max-files", type=positive_integer, default=DEFAULT_MAX_FILES,
        help="maximum regular files included in the inventory (default: %(default)s)",
    )
    init = commands.add_parser("init", help="create a new blank JSON workflow record")
    init.add_argument("destination", type=Path, metavar="DEST")
    check = commands.add_parser("check", help="verify record structure and evidence integrity")
    check.add_argument("record", type=Path, metavar="RECORD")
    check.add_argument("--root", type=Path, required=True, help="project evidence root")

    args = parser.parse_args()
    try:
        if args.command == "init":
            init_record(args.destination)
            print(json.dumps({"created": str(args.destination), "schema_version": SCHEMA_VERSION}))
            return 0
        root = args.root.resolve(strict=True)
        if not root.is_dir():
            parser.error("ROOT must be a directory")
        if args.command == "check" and not args.record.is_file():
            parser.error("RECORD must be an existing regular file")
    except (OSError, RuntimeError, ValueError) as error:
        parser.error(str(error))

    if args.command == "inventory":
        result = inventory(root, args.max_files)
        exit_code = int(bool(result["scan_errors"]))
    else:
        result = check_record(args.record, root)
        exit_code = int(result["evidence_integrity"] == "fail")
    print(json.dumps(result, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
