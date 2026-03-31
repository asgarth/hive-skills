#!/usr/bin/env python3
"""
Functional tests for scan_npm_dependency.py.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("scan_npm_dependency.py")


class ScanNpmDependencyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="npm-scan-test-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def run_scan(self, *args: str) -> tuple[int, dict[str, object], str]:
        result = subprocess.run(
            ["python3", str(SCRIPT_PATH), str(self.temp_dir), "--json", *args],
            text=True,
            capture_output=True,
            check=False,
        )
        payload = json.loads(result.stdout)
        return result.returncode, payload, result.stderr

    def test_detects_yarn_modern_npm_selector(self) -> None:
        app = self.temp_dir / "app"
        app.mkdir(parents=True)
        (app / "yarn.lock").write_text(
            '"axios@npm:^1.14.0":\n'
            '  version: 1.14.1\n',
            encoding="utf-8",
        )

        returncode, payload, _ = self.run_scan(
            "--package",
            "axios",
            "--version",
            "1.14.1",
        )

        self.assertEqual(returncode, 0)
        findings = payload["findings"]
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["manager"], "yarn")
        self.assertEqual(findings[0]["version"], "1.14.1")

    def test_detects_transitive_installed_package(self) -> None:
        installed = (
            self.temp_dir
            / "app"
            / "node_modules"
            / "foo"
            / "node_modules"
            / "axios"
        )
        installed.mkdir(parents=True)
        (self.temp_dir / "app" / "package.json").write_text(
            json.dumps({"name": "app", "dependencies": {"foo": "1.0.0"}}, indent=2),
            encoding="utf-8",
        )
        (installed / "package.json").write_text(
            json.dumps({"name": "axios", "version": "1.14.1"}, indent=2),
            encoding="utf-8",
        )

        returncode, payload, _ = self.run_scan(
            "--package",
            "axios",
            "--version",
            "1.14.1",
        )

        self.assertEqual(returncode, 0)
        findings = payload["findings"]
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["evidence"], "installed")
        self.assertEqual(
            findings[0]["locator"],
            "node_modules/foo/node_modules/axios/package.json",
        )

    def test_detects_scoped_package_in_yarn_and_pnpm(self) -> None:
        yarn_app = self.temp_dir / "yarn-app"
        yarn_app.mkdir(parents=True)
        (yarn_app / "yarn.lock").write_text(
            '"@scope/pkg@npm:^2.3.0":\n'
            '  version: 2.3.4\n',
            encoding="utf-8",
        )

        pnpm_app = self.temp_dir / "pnpm-app"
        pnpm_app.mkdir(parents=True)
        (pnpm_app / "pnpm-lock.yaml").write_text(
            "lockfileVersion: \"9.0\"\n"
            "packages:\n"
            "  '@scope/pkg@2.3.4':\n"
            "    resolution: {integrity: sha512-test}\n",
            encoding="utf-8",
        )

        returncode, payload, _ = self.run_scan(
            "--package",
            "@scope/pkg",
            "--version",
            "2.3.4",
        )

        self.assertEqual(returncode, 0)
        findings = payload["findings"]
        self.assertEqual(len(findings), 2)
        managers = {item["manager"] for item in findings}
        self.assertEqual(managers, {"pnpm", "yarn"})

    def test_returns_no_findings_for_clean_fixture(self) -> None:
        app = self.temp_dir / "app"
        app.mkdir(parents=True)
        (app / "package.json").write_text(
            json.dumps({"name": "app", "dependencies": {"left-pad": "1.3.0"}}, indent=2),
            encoding="utf-8",
        )

        returncode, payload, _ = self.run_scan(
            "--package",
            "axios",
            "--version",
            "1.14.1",
        )

        self.assertEqual(returncode, 0)
        self.assertEqual(payload["findings"], [])
        self.assertEqual(payload["warnings"], [])


if __name__ == "__main__":
    unittest.main()
