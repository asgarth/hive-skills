#!/usr/bin/env python3
"""
Recursively scan npm ecosystem projects for affected dependency versions.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


LOCKFILE_NAMES = (
    "package-lock.json",
    "npm-shrinkwrap.json",
    "pnpm-lock.yaml",
    "yarn.lock",
)

PROJECT_MARKERS = ("package.json",) + LOCKFILE_NAMES

IGNORED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".idea",
    ".next",
    ".nuxt",
    ".pnpm-store",
    ".turbo",
    ".yarn",
    "coverage",
    "build",
    "dist",
    "out",
    "tmp",
    "vendor",
    "node_modules",
}

PACKAGE_JSON_SECTIONS = (
    "dependencies",
    "devDependencies",
    "optionalDependencies",
    "peerDependencies",
    "resolutions",
    "overrides",
)


@dataclass(frozen=True, order=True)
class SemVer:
    major: int
    minor: int
    patch: int
    prerelease: tuple[object, ...] = ()

    def __str__(self) -> str:
        base = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            return f"{base}-" + ".".join(str(part) for part in self.prerelease)
        return base


@dataclass(frozen=True)
class Finding:
    package: str
    version: str
    project_root: str
    file: str
    manager: str
    evidence: str
    locator: str


def normalize_version_text(raw: str) -> str:
    value = raw.strip()
    if value.startswith("v"):
        value = value[1:]
    return value


def parse_semver(raw: str) -> SemVer:
    value = normalize_version_text(raw)
    value = value.split("+", 1)[0]
    prerelease: tuple[object, ...] = ()
    if "-" in value:
        value, prerelease_part = value.split("-", 1)
        prerelease_items = []
        for item in prerelease_part.split("."):
            prerelease_items.append(int(item) if item.isdigit() else item)
        prerelease = tuple(prerelease_items)
    parts = value.split(".")
    if len(parts) > 3:
        raise ValueError(f"invalid semver: {raw}")
    normalized = []
    for item in parts:
        if item == "":
            raise ValueError(f"invalid semver: {raw}")
        if not item.isdigit():
            raise ValueError(f"invalid semver: {raw}")
        normalized.append(int(item))
    while len(normalized) < 3:
        normalized.append(0)
    return SemVer(
        major=normalized[0],
        minor=normalized[1],
        patch=normalized[2],
        prerelease=prerelease,
    )


def compare_semver(left: SemVer, right: SemVer) -> int:
    left_core = (left.major, left.minor, left.patch)
    right_core = (right.major, right.minor, right.patch)
    if left_core < right_core:
        return -1
    if left_core > right_core:
        return 1
    if not left.prerelease and not right.prerelease:
        return 0
    if not left.prerelease:
        return 1
    if not right.prerelease:
        return -1
    for index in range(max(len(left.prerelease), len(right.prerelease))):
        if index >= len(left.prerelease):
            return -1
        if index >= len(right.prerelease):
            return 1
        left_part = left.prerelease[index]
        right_part = right.prerelease[index]
        if left_part == right_part:
            continue
        if isinstance(left_part, int) and isinstance(right_part, int):
            return -1 if left_part < right_part else 1
        if isinstance(left_part, int):
            return -1
        if isinstance(right_part, int):
            return 1
        return -1 if str(left_part) < str(right_part) else 1
    return 0


def parse_partial_version(raw: str) -> tuple[list[int], bool]:
    value = normalize_version_text(raw).split("+", 1)[0]
    if "-" in value:
        raise ValueError(f"partial versions cannot include prerelease: {raw}")
    parts = value.split(".")
    numbers: list[int] = []
    wildcard = False
    for part in parts:
        lower = part.lower()
        if lower in {"x", "*"}:
            wildcard = True
            break
        if not part.isdigit():
            raise ValueError(f"invalid partial version: {raw}")
        numbers.append(int(part))
    return numbers, wildcard


def semver_with_defaults(numbers: Iterable[int]) -> SemVer:
    values = list(numbers)
    while len(values) < 3:
        values.append(0)
    return SemVer(values[0], values[1], values[2])


def bump_partial(numbers: list[int]) -> SemVer:
    if not numbers:
        raise ValueError("cannot bump empty version")
    values = list(numbers)
    index = len(values) - 1
    values[index] += 1
    while len(values) < 3:
        values.append(0)
    for follow in range(index + 1, 3):
        values[follow] = 0
    return SemVer(values[0], values[1], values[2])


def expand_caret(token: str) -> list[str]:
    numbers, wildcard = parse_partial_version(token[1:])
    if wildcard:
        raise ValueError(f"unsupported caret wildcard: {token}")
    lower = semver_with_defaults(numbers)
    padded = [lower.major, lower.minor, lower.patch]
    if padded[0] > 0:
        upper = SemVer(padded[0] + 1, 0, 0)
    elif padded[1] > 0:
        upper = SemVer(0, padded[1] + 1, 0)
    else:
        upper = SemVer(0, 0, padded[2] + 1)
    return [f">={lower}", f"<{upper}"]


def expand_tilde(token: str) -> list[str]:
    numbers, wildcard = parse_partial_version(token[1:])
    if wildcard:
        raise ValueError(f"unsupported tilde wildcard: {token}")
    lower = semver_with_defaults(numbers)
    if len(numbers) <= 1:
        upper = SemVer(lower.major + 1, 0, 0)
    else:
        upper = SemVer(lower.major, lower.minor + 1, 0)
    return [f">={lower}", f"<{upper}"]


def expand_wildcard(token: str) -> list[str]:
    numbers, wildcard = parse_partial_version(token)
    if not wildcard:
        exact = semver_with_defaults(numbers)
        return [f"={exact}"]
    if not numbers:
        return []
    lower = semver_with_defaults(numbers)
    upper = bump_partial(numbers)
    return [f">={lower}", f"<{upper}"]


def compare_with_operator(version: SemVer, operator: str, reference: SemVer) -> bool:
    comparison = compare_semver(version, reference)
    if operator == "=":
        return comparison == 0
    if operator == ">":
        return comparison > 0
    if operator == ">=":
        return comparison >= 0
    if operator == "<":
        return comparison < 0
    if operator == "<=":
        return comparison <= 0
    raise ValueError(f"unsupported operator: {operator}")


def expand_clause_tokens(clause: str) -> list[str]:
    normalized = clause.strip()
    if not normalized or normalized == "*":
        return []

    hyphen = re.fullmatch(r"(.+?)\s+-\s+(.+)", normalized)
    if hyphen:
        lower = parse_semver(hyphen.group(1).strip())
        upper = parse_semver(hyphen.group(2).strip())
        return [f">={lower}", f"<={upper}"]

    tokens = [item for item in re.split(r"[,\s]+", normalized) if item]
    expanded: list[str] = []
    for token in tokens:
        if token in {"*", "x", "X"}:
            return []
        if token.startswith("^"):
            expanded.extend(expand_caret(token))
        elif token.startswith("~"):
            expanded.extend(expand_tilde(token))
        elif "x" in token.lower() or "*" in token:
            expanded.extend(expand_wildcard(token))
        elif token[0].isdigit() or token[0] == "v":
            expanded.append(f"={parse_semver(token)}")
        else:
            expanded.append(token)
    return expanded


def match_range(version_text: str, expression: str) -> bool:
    version = parse_semver(version_text)
    for alternative in expression.split("||"):
        expanded = expand_clause_tokens(alternative)
        matched = True
        for token in expanded:
            comparator = re.fullmatch(r"(<=|>=|<|>|=)(.+)", token)
            if not comparator:
                raise ValueError(f"invalid comparator token: {token}")
            operator = comparator.group(1)
            reference = parse_semver(comparator.group(2).strip())
            if not compare_with_operator(version, operator, reference):
                matched = False
                break
        if matched:
            return True
    return False


def matches_version(
    version: str,
    exact_versions: set[str],
    range_expressions: list[str],
) -> bool:
    normalized = normalize_version_text(version)
    if normalized in exact_versions:
        return True
    for expression in range_expressions:
        if match_range(normalized, expression):
            return True
    return False


def looks_like_semver_selector(value: str) -> bool:
    stripped = value.strip()
    if not stripped:
        return False
    if stripped.startswith(
        (
            "workspace:",
            "file:",
            "link:",
            "portal:",
            "patch:",
            "git+",
            "github:",
            "gitlab:",
            "bitbucket:",
            "http://",
            "https://",
        )
    ):
        return False
    return True


def is_plain_semver_value(value: str) -> bool:
    return re.fullmatch(
        r"v?\d+(?:\.\d+){0,2}(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?",
        value.strip(),
    ) is not None


def update_lower_bound(
    current: tuple[SemVer, bool] | None,
    candidate: tuple[SemVer, bool],
) -> tuple[SemVer, bool]:
    if current is None:
        return candidate
    comparison = compare_semver(candidate[0], current[0])
    if comparison > 0:
        return candidate
    if comparison < 0:
        return current
    return (candidate[0], current[1] and candidate[1])


def update_upper_bound(
    current: tuple[SemVer, bool] | None,
    candidate: tuple[SemVer, bool],
) -> tuple[SemVer, bool]:
    if current is None:
        return candidate
    comparison = compare_semver(candidate[0], current[0])
    if comparison < 0:
        return candidate
    if comparison > 0:
        return current
    return (candidate[0], current[1] and candidate[1])


def clause_to_interval(clause: str) -> tuple[tuple[SemVer, bool] | None, tuple[SemVer, bool] | None]:
    expanded = expand_clause_tokens(clause)
    lower: tuple[SemVer, bool] | None = None
    upper: tuple[SemVer, bool] | None = None
    for token in expanded:
        comparator = re.fullmatch(r"(<=|>=|<|>|=)(.+)", token)
        if not comparator:
            raise ValueError(f"invalid comparator token: {token}")
        operator = comparator.group(1)
        reference = parse_semver(comparator.group(2).strip())
        if operator == "=":
            lower = update_lower_bound(lower, (reference, True))
            upper = update_upper_bound(upper, (reference, True))
        elif operator == ">":
            lower = update_lower_bound(lower, (reference, False))
        elif operator == ">=":
            lower = update_lower_bound(lower, (reference, True))
        elif operator == "<":
            upper = update_upper_bound(upper, (reference, False))
        elif operator == "<=":
            upper = update_upper_bound(upper, (reference, True))
    return lower, upper


def intervals_overlap(
    left: tuple[tuple[SemVer, bool] | None, tuple[SemVer, bool] | None],
    right: tuple[tuple[SemVer, bool] | None, tuple[SemVer, bool] | None],
) -> bool:
    left_lower, left_upper = left
    right_lower, right_upper = right

    if left_upper and right_lower:
        comparison = compare_semver(left_upper[0], right_lower[0])
        if comparison < 0:
            return False
        if comparison == 0 and not (left_upper[1] and right_lower[1]):
            return False

    if right_upper and left_lower:
        comparison = compare_semver(right_upper[0], left_lower[0])
        if comparison < 0:
            return False
        if comparison == 0 and not (right_upper[1] and left_lower[1]):
            return False

    return True


def ranges_overlap(left_expression: str, right_expression: str) -> bool:
    left_clauses = [clause.strip() for clause in left_expression.split("||")]
    right_clauses = [clause.strip() for clause in right_expression.split("||")]
    for left_clause in left_clauses:
        left_interval = clause_to_interval(left_clause)
        for right_clause in right_clauses:
            right_interval = clause_to_interval(right_clause)
            if intervals_overlap(left_interval, right_interval):
                return True
    return False


def matches_declared_spec(
    declared_spec: str,
    exact_versions: set[str],
    range_expressions: list[str],
) -> bool:
    normalized = declared_spec.strip()
    if normalized in exact_versions:
        return True
    if not looks_like_semver_selector(normalized):
        return False
    for exact_version in exact_versions:
        if match_range(exact_version, normalized):
            return True
    if is_plain_semver_value(normalized):
        normalized_version = normalize_version_text(normalized)
        for expression in range_expressions:
            if match_range(normalized_version, expression):
                return True
    for expression in range_expressions:
        if normalized == expression or ranges_overlap(normalized, expression):
            return True
    return False


def canonicalize_package_name(name: str) -> str:
    return name.strip().lower()


def read_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def add_finding(
    findings: list[Finding],
    seen: set[tuple[str, str, str, str, str, str, str]],
    *,
    package: str,
    version: str,
    project_root: Path,
    file_path: Path,
    manager: str,
    evidence: str,
    locator: str,
) -> None:
    finding = Finding(
        package=package,
        version=normalize_version_text(version),
        project_root=str(project_root.resolve()),
        file=str(file_path.resolve()),
        manager=manager,
        evidence=evidence,
        locator=locator,
    )
    key = (
        finding.package,
        finding.version,
        finding.project_root,
        finding.file,
        finding.manager,
        finding.evidence,
        finding.locator,
    )
    if key not in seen:
        seen.add(key)
        findings.append(finding)


def package_name_from_node_modules_path(raw_path: str) -> str | None:
    parts = [part for part in Path(raw_path).parts if part not in {"", "."}]
    last_name: str | None = None
    index = 0
    while index < len(parts):
        if parts[index] != "node_modules":
            index += 1
            continue
        if index + 1 >= len(parts):
            break
        next_part = parts[index + 1]
        if next_part.startswith("@") and index + 2 < len(parts):
            last_name = f"{next_part}/{parts[index + 2]}"
            index += 3
        else:
            last_name = next_part
            index += 2
    return last_name


def scan_package_json(
    path: Path,
    target_package: str,
    exact_versions: set[str],
    range_expressions: list[str],
    findings: list[Finding],
    seen: set[tuple[str, str, str, str, str, str, str]],
) -> None:
    data = read_json(path)
    if not isinstance(data, dict):
        return
    target = canonicalize_package_name(target_package)

    def visit_mapping(mapping: object, locator: str) -> None:
        if not isinstance(mapping, dict):
            return
        for key, value in mapping.items():
            current = f"{locator}.{key}" if locator else key
            if canonicalize_package_name(str(key)) == target and isinstance(value, str):
                if matches_declared_spec(value, exact_versions, range_expressions):
                    add_finding(
                        findings,
                        seen,
                        package=target_package,
                        version=value,
                        project_root=path.parent,
                        file_path=path,
                        manager="manifest",
                        evidence="declared",
                        locator=current,
                    )
            if isinstance(value, dict):
                visit_mapping(value, current)

    for section in PACKAGE_JSON_SECTIONS:
        visit_mapping(data.get(section), section)


def scan_npm_lock(
    path: Path,
    target_package: str,
    exact_versions: set[str],
    range_expressions: list[str],
    findings: list[Finding],
    seen: set[tuple[str, str, str, str, str, str, str]],
) -> None:
    data = read_json(path)
    if not isinstance(data, dict):
        return
    target = canonicalize_package_name(target_package)

    packages = data.get("packages")
    if isinstance(packages, dict):
        for key, value in packages.items():
            if not isinstance(value, dict):
                continue
            name = value.get("name")
            if not isinstance(name, str):
                inferred = package_name_from_node_modules_path(str(key))
                name = inferred if inferred else ""
            version = value.get("version")
            if (
                isinstance(name, str)
                and isinstance(version, str)
                and canonicalize_package_name(name) == target
                and matches_version(version, exact_versions, range_expressions)
            ):
                locator = "packages.<root>" if key == "" else f"packages.{key}"
                add_finding(
                    findings,
                    seen,
                    package=name,
                    version=version,
                    project_root=path.parent,
                    file_path=path,
                    manager="npm",
                    evidence="locked",
                    locator=locator,
                )

    def walk_dependencies(mapping: object, locator: str) -> None:
        if not isinstance(mapping, dict):
            return
        for name, value in mapping.items():
            if not isinstance(value, dict):
                continue
            version = value.get("version")
            current = f"{locator}.{name}" if locator else str(name)
            if (
                isinstance(version, str)
                and canonicalize_package_name(str(name)) == target
                and matches_version(version, exact_versions, range_expressions)
            ):
                add_finding(
                    findings,
                    seen,
                    package=str(name),
                    version=version,
                    project_root=path.parent,
                    file_path=path,
                    manager="npm",
                    evidence="locked",
                    locator=current,
                )
            walk_dependencies(value.get("dependencies"), f"{current}.dependencies")

    walk_dependencies(data.get("dependencies"), "dependencies")


def parse_pnpm_package_key(raw_key: str) -> tuple[str, str] | None:
    key = raw_key.strip().strip("'\"")
    if key.startswith("/"):
        key = key[1:]
    if "@npm:" in key:
        key = key.split("@npm:", 1)[1]
    key = key.split("(", 1)[0]
    match = re.match(r"^(@[^/]+/[^@]+|[^@]+)@(.+)$", key)
    if not match:
        return None
    return match.group(1), normalize_version_text(match.group(2))


def scan_pnpm_lock(
    path: Path,
    target_package: str,
    exact_versions: set[str],
    range_expressions: list[str],
    findings: list[Finding],
    seen: set[tuple[str, str, str, str, str, str, str]],
) -> None:
    target = canonicalize_package_name(target_package)
    in_packages = False
    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.rstrip("\n")
            if not in_packages:
                if line.strip() == "packages:":
                    in_packages = True
                continue
            if line and not line.startswith(" "):
                break
            entry = re.match(r"^ {2}(.+):\s*$", line)
            if not entry:
                continue
            parsed = parse_pnpm_package_key(entry.group(1))
            if not parsed:
                continue
            package_name, version = parsed
            if (
                canonicalize_package_name(package_name) == target
                and matches_version(version, exact_versions, range_expressions)
            ):
                add_finding(
                    findings,
                    seen,
                    package=package_name,
                    version=version,
                    project_root=path.parent,
                    file_path=path,
                    manager="pnpm",
                    evidence="locked",
                    locator=f"packages.{entry.group(1).strip()}",
                )


def extract_selector_packages(selector: str) -> set[str]:
    token = selector.strip().strip('"').strip("'")
    packages: set[str] = set()
    if "@npm:" in token:
        prefix, suffix = token.split("@npm:", 1)
        if prefix:
            packages.add(prefix)
        token = suffix
    match = re.match(r"^(@[^/]+/[^@]+|[^@]+)@", token)
    if match:
        packages.add(match.group(1))
    return packages


def scan_yarn_lock(
    path: Path,
    target_package: str,
    exact_versions: set[str],
    range_expressions: list[str],
    findings: list[Finding],
    seen: set[tuple[str, str, str, str, str, str, str]],
) -> None:
    target = canonicalize_package_name(target_package)
    header: str | None = None
    block_lines: list[str] = []

    def flush_block() -> None:
        if header is None:
            return
        selectors = [item.strip() for item in header[:-1].split(",") if item.strip()]
        packages = {
            canonicalize_package_name(package)
            for package in (
                candidate
                for selector in selectors
                for candidate in extract_selector_packages(selector)
            )
            if package
        }
        if target not in packages:
            return
        version: str | None = None
        for line in block_lines:
            match = re.match(r'^\s+version(?::)?\s+"?([^"\s]+)"?\s*$', line)
            if match:
                version = normalize_version_text(match.group(1))
                break
        if not version:
            return
        if matches_version(version, exact_versions, range_expressions):
            add_finding(
                findings,
                seen,
                package=target_package,
                version=version,
                project_root=path.parent,
                file_path=path,
                manager="yarn",
                evidence="locked",
                locator=f"selector {header[:-1]}",
            )

    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.rstrip("\n")
            if re.match(r"^[^\s].*:\s*$", line):
                flush_block()
                header = line
                block_lines = []
            elif header is not None:
                block_lines.append(line)
    flush_block()


def scan_installed_package(
    project_root: Path,
    target_package: str,
    exact_versions: set[str],
    range_expressions: list[str],
    findings: list[Finding],
    seen: set[tuple[str, str, str, str, str, str, str]],
) -> None:
    node_modules_root = project_root / "node_modules"
    if not node_modules_root.is_dir():
        return
    target = canonicalize_package_name(target_package)

    for current_root, _, filenames in os.walk(node_modules_root):
        if "package.json" not in filenames:
            continue
        current_path = Path(current_root)
        relative_dir = current_path.relative_to(project_root)
        package_name = package_name_from_node_modules_path(str(relative_dir))
        if canonicalize_package_name(package_name or "") != target:
            continue

        package_json = current_path / "package.json"
        data = read_json(package_json)
        if not isinstance(data, dict):
            continue
        version = data.get("version")
        name = data.get("name", target_package)
        if (
            isinstance(version, str)
            and isinstance(name, str)
            and canonicalize_package_name(name) == target
            and matches_version(version, exact_versions, range_expressions)
        ):
            add_finding(
                findings,
                seen,
                package=name,
                version=version,
                project_root=project_root,
                file_path=package_json,
                manager="filesystem",
                evidence="installed",
                locator=str(package_json.relative_to(project_root)),
            )


def find_project_roots(start_path: Path) -> list[Path]:
    projects: list[Path] = []
    for current_root, dirnames, filenames in os.walk(start_path):
        dirnames[:] = [
            dirname
            for dirname in dirnames
            if dirname not in IGNORED_DIRS and not dirname.startswith(".cache")
        ]
        if any(filename in PROJECT_MARKERS for filename in filenames):
            projects.append(Path(current_root))
    return sorted(projects)


def scan_project(
    project_root: Path,
    target_package: str,
    exact_versions: set[str],
    range_expressions: list[str],
    findings: list[Finding],
    seen: set[tuple[str, str, str, str, str, str, str]],
    warnings: list[str],
) -> None:
    def safe_scan(label: str, callback) -> None:
        try:
            callback()
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"{project_root} [{label}]: {exc}")

    package_json = project_root / "package.json"
    if package_json.is_file():
        safe_scan(
            "package.json",
            lambda: scan_package_json(
                package_json,
                target_package,
                exact_versions,
                range_expressions,
                findings,
                seen,
            ),
        )

    for name in ("package-lock.json", "npm-shrinkwrap.json"):
        lockfile = project_root / name
        if lockfile.is_file():
            safe_scan(
                name,
                lambda lockfile=lockfile: scan_npm_lock(
                    lockfile,
                    target_package,
                    exact_versions,
                    range_expressions,
                    findings,
                    seen,
                ),
            )

    pnpm_lock = project_root / "pnpm-lock.yaml"
    if pnpm_lock.is_file():
        safe_scan(
            "pnpm-lock.yaml",
            lambda: scan_pnpm_lock(
                pnpm_lock,
                target_package,
                exact_versions,
                range_expressions,
                findings,
                seen,
            ),
        )

    yarn_lock = project_root / "yarn.lock"
    if yarn_lock.is_file():
        safe_scan(
            "yarn.lock",
            lambda: scan_yarn_lock(
                yarn_lock,
                target_package,
                exact_versions,
                range_expressions,
                findings,
                seen,
            ),
        )

    safe_scan(
        "node_modules",
        lambda: scan_installed_package(
            project_root,
            target_package,
            exact_versions,
            range_expressions,
            findings,
            seen,
        ),
    )


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Recursively scan npm/pnpm/yarn projects for affected dependency versions.",
    )
    parser.add_argument(
        "start_path",
        nargs="?",
        default=".",
        help="Folder to scan recursively. Defaults to the current directory.",
    )
    parser.add_argument(
        "--package",
        required=True,
        help="Package name to look for, for example axios or @scope/pkg.",
    )
    parser.add_argument(
        "--version",
        action="append",
        default=[],
        help="Exact affected version. Repeat as needed.",
    )
    parser.add_argument(
        "--range",
        dest="ranges",
        action="append",
        default=[],
        help="Affected semver expression, for example '>=1.2.0 <1.2.4' or '^4.2.1'. Repeat as needed.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON output.",
    )
    parser.add_argument(
        "--fail-on-match",
        action="store_true",
        help="Exit with status 1 if any match is found.",
    )
    return parser


def validate_inputs(args: argparse.Namespace) -> tuple[Path, set[str], list[str]]:
    start_path = Path(args.start_path).resolve()
    if not start_path.exists():
        raise SystemExit(f"start path does not exist: {start_path}")
    if not start_path.is_dir():
        raise SystemExit(f"start path is not a directory: {start_path}")

    exact_versions = {normalize_version_text(item) for item in args.version}
    if not exact_versions and not args.ranges:
        raise SystemExit("provide at least one --version or --range selector")

    for version in exact_versions:
        parse_semver(version)
    for expression in args.ranges:
        match_range("0.0.0", expression)

    return start_path, exact_versions, list(args.ranges)


def print_text_report(
    *,
    start_path: Path,
    package_name: str,
    exact_versions: set[str],
    range_expressions: list[str],
    project_roots: list[Path],
    findings: list[Finding],
    warnings: list[str],
) -> None:
    print(f"Scan root: {start_path}")
    print(f"Package: {package_name}")
    selectors = []
    if exact_versions:
        selectors.append("exact=" + ", ".join(sorted(exact_versions)))
    if range_expressions:
        selectors.append("range=" + ", ".join(range_expressions))
    print(f"Selectors: {'; '.join(selectors)}")
    print(f"Projects scanned: {len(project_roots)}")
    print(f"Matches: {len(findings)}")

    if findings:
        for finding in sorted(findings, key=lambda item: (item.project_root, item.file, item.evidence, item.locator)):
            print()
            print(f"[MATCH] {finding.evidence} via {finding.manager}")
            print(f"project: {finding.project_root}")
            print(f"file: {finding.file}")
            print(f"package: {finding.package}@{finding.version}")
            print(f"locator: {finding.locator}")
    else:
        print()
        print("No matching declared, locked, or installed versions were found.")

    if warnings:
        print()
        print("Warnings:")
        for warning in warnings:
            print(f"- {warning}")


def main() -> int:
    parser = build_argument_parser()
    args = parser.parse_args()
    start_path, exact_versions, range_expressions = validate_inputs(args)

    findings: list[Finding] = []
    seen: set[tuple[str, str, str, str, str, str, str]] = set()
    warnings: list[str] = []
    project_roots = find_project_roots(start_path)

    for project_root in project_roots:
        scan_project(
            project_root,
            args.package,
            exact_versions,
            range_expressions,
            findings,
            seen,
            warnings,
        )

    if args.json:
        payload = {
            "scan_root": str(start_path),
            "package": args.package,
            "exact_versions": sorted(exact_versions),
            "ranges": range_expressions,
            "projects_scanned": [str(project) for project in project_roots],
            "findings": [asdict(finding) for finding in findings],
            "warnings": warnings,
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_text_report(
            start_path=start_path,
            package_name=args.package,
            exact_versions=exact_versions,
            range_expressions=range_expressions,
            project_roots=project_roots,
            findings=findings,
            warnings=warnings,
        )

    if warnings:
        return 2
    if args.fail_on_match and findings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
