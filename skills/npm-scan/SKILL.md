---
name: npm-scan
description: Recursively scan a folder tree for affected npm, pnpm, and yarn dependency versions. Use when the user asks to check whether a compromised package version is installed anywhere, scan all subfolders, or verify a package range from an advisory.
version: "2026.3.31"
tags: ["npm", "pnpm", "yarn", "security", "supply-chain", "dependency-scanning"]
requirements:
  - Python 3.9+
---

# NPM Supply Chain Scan

Use the bundled scanner to walk a starting directory recursively and inspect JavaScript/TypeScript projects that use `npm`, `pnpm`, or `yarn`.

The script reports three evidence types separately:

- `declared`: the package is referenced in `package.json`
- `locked`: the affected version is present in a lockfile
- `installed`: the affected version exists in `node_modules/<package>/package.json`

Treat `locked` or `installed` as stronger evidence than `declared`.

## When to Use

Use this skill when you have incident details such as:

- package name
- affected exact versions
- affected semver range
- disclosure URL and date

Typical trigger requests:

- "Check whether `axios@1.14.1` is installed anywhere under this monorepo."
- "Scan this directory recursively for `chalk` versions matching `<5.6.0`."
- "Use the latest npm compromise details and tell me if any affected versions are present."

## When Not to Use

Do not use this skill when:

- the user wants package remediation, upgrades, or lockfile rewrites rather than detection
- the user needs vulnerability severity scoring, CVE enrichment, or SBOM generation
- the package manager is outside the npm ecosystem
- the target path is a single published package tarball instead of a checked-out folder tree

## Trigger Phrases

Positive triggers:

- "scan this repo for affected axios versions"
- "check whether `@scope/pkg` is installed anywhere under this folder"
- "look for `lodash` versions matching `>=4.17.0 <4.17.21`"
- "search all subfolders for a compromised npm package"

Negative triggers:

- "upgrade axios everywhere"
- "generate an SBOM"
- "fix the vulnerability automatically"
- "audit this Python environment"

## Required Inputs

Collect these before running the scan:

1. Package name, for example `axios` or `@scope/pkg`
2. At least one affected version selector:
   - exact versions with `--version`
   - semver expressions with `--range`
3. Starting folder to scan recursively

Use exact versions when an incident report lists them explicitly. Use ranges when the advisory publishes affected windows such as `>=1.2.0 <1.2.5`.

Default operating choices:

- starting folder: current directory if the user does not provide one
- output mode: text for human review, `--json` for machine consumption
- selectors: prefer exact `--version` values when the incident names specific compromised releases

## Workflow

1. Read the incident source and extract the package name, affected versions/ranges, and date.
2. Run `scripts/scan_npm_dependency.py` from the chosen starting folder.
3. Review the output by evidence type:
   - `installed`: package exists on disk under `node_modules`
   - `locked`: package resolves to the affected version in a lockfile
   - `declared`: a manifest references the package, but installation is not proven
4. If matches are found, report the project roots and file paths. Keep remediation separate from detection unless the user asks for both.

## Script-First Policy

Use the bundled scanner as the primary path. Do not replace it with ad hoc `find`, `awk`, `perl`, or `grep` pipelines unless the user explicitly asks for a one-off custom investigation that the script cannot cover.

## Quick Start

Exact-version incident:

```bash
python scripts/scan_npm_dependency.py /path/to/root \
  --package axios \
  --version 1.14.1 \
  --version 0.30.4
```

Range-based incident:

```bash
python scripts/scan_npm_dependency.py /path/to/root \
  --package some-package \
  --range ">=2.4.0 <2.4.3"
```

Machine-readable output:

```bash
python scripts/scan_npm_dependency.py . \
  --package axios \
  --version 1.14.1 \
  --json
```

CI-style failure on detection:

```bash
python scripts/scan_npm_dependency.py . \
  --package axios \
  --version 1.14.1 \
  --version 0.30.4 \
  --fail-on-match
```

Run the functional tests:

```bash
python scripts/test_scan_npm_dependency.py
```

## Script Behavior

The scanner:

- walks the starting directory recursively
- skips common heavy or irrelevant directories such as `.git`, `node_modules`, `.yarn/cache`, and build output folders
- treats each directory containing `package.json` and/or a supported lockfile as a project root candidate
- scans `package-lock.json`, `npm-shrinkwrap.json`, `pnpm-lock.yaml`, and `yarn.lock`
- checks local `node_modules/<package>/package.json` when present

The scanner supports common npm semver syntax in `--range`, including exact versions, comparator sets, `||`, `^`, `~`, and `x`/`*` wildcards.

For `package.json`, a `declared` match is reported when the declared dependency spec itself is affected, can resolve to one of the affected exact versions you supplied, or overlaps with an affected range you supplied.

Installed-package detection is recursive within each discovered project's `node_modules`, so nested or transitive installs such as `node_modules/foo/node_modules/<package>` are checked too.

## Interpretation Rules

- `declared` only: the project references the package, but the currently installed or resolved version is not proven from that evidence alone
- `locked`: the affected version is resolved in the dependency graph captured by the lockfile
- `installed`: the affected version is currently present on disk in `node_modules`

If the incident is known to remove or hide evidence after install, still rely on lockfiles even when `installed` is absent.

## Output Contract

When reporting results, include:

- scanned root path
- package name and selectors used
- number of project roots scanned
- matches grouped by `declared`, `locked`, and `installed`
- file paths and locators for each match
- any warnings emitted by the scanner

If no matches are found, state that explicitly instead of implying a clean bill of health.

## Guardrails

- Do not claim a package is installed based on a `declared` finding alone.
- Treat `locked` and `installed` as evidence, not proof of runtime execution.
- Keep the incident source URL and disclosure date in the final report when available.
- If the user asks for "latest" incident details, verify them from the source before scanning.
- Do not auto-remediate or delete packages unless the user asks for remediation work.
- Keep the scan non-destructive: do not modify manifests, lockfiles, or `node_modules` during detection.

## Anti-Patterns

- do not collapse `declared`, `locked`, and `installed` into a single undifferentiated result
- do not skip lockfiles just because `node_modules` is absent
- do not assume a root-level `node_modules/<package>` check is sufficient for transitive installs
- do not rely on one package manager format when the folder tree may contain multiple project types

## Troubleshooting

Error: `provide at least one --version or --range selector`
Cause: the scan was started without affected versions or ranges
Solution: rerun with one or more `--version` and/or `--range` arguments

Error: `start path does not exist` or `start path is not a directory`
Cause: the root path is wrong or not mounted in the current environment
Solution: verify the absolute path and rerun from a readable directory

Problem: scan finishes with warnings
Cause: one or more manifests or lockfiles could not be parsed
Solution: inspect the warning paths, confirm file format, and rerun after fixing or excluding the broken project

Problem: only `declared` matches are found
Cause: the dependency may not currently be installed, or lockfiles may be absent
Solution: treat the result as weaker evidence and inspect install state or lockfiles before escalating

## References

- `references/axios-march-2026.md`: example incident extraction based on the March 30-31, 2026 axios compromise disclosed by Aikido
- `scripts/scan_npm_dependency.py`: recursive scanner for npm, pnpm, and yarn projects
- `scripts/test_scan_npm_dependency.py`: functional tests covering positive and negative scan cases
