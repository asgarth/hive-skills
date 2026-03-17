---
name: hive-developer
description: Build and debug Hive blockchain software with `hive-tx` in JavaScript/TypeScript, including node failover, quorum reads, key-safe signing, and status-aware broadcasting for wallet, content, and custom_json flows.
version: "2026.3.1"
tags: ["hive", "blockchain", "typescript", "hive-tx", "transactions"]
requirements:
  - Node.js >= 22
  - `hive-tx` npm package
triggers:
  - "Build Hive app logic in TypeScript"
  - "Broadcast Hive transactions safely"
  - "Implement Hive failover and quorum reads"
user-invocable: true
argument-hint: [topic]
---

# Hive Developer (hive-tx)

Use this skill for Hive blockchain development in JavaScript/TypeScript.

Default SDK for all examples in this skill: `hive-tx`.

## Quick Reference

| Topic                                                        | Reference File                                         |
| ------------------------------------------------------------ | ------------------------------------------------------ |
| RPC/REST calls, nodes, failover config, quorum reads         | [api-reference.md](api-reference.md)                   |
| Transaction builders for vote/comment/transfer/custom_json   | [operations.md](operations.md)                         |
| Safety patterns: failover, status checks, wait-for-inclusion | [reliability.md](reliability.md)                       |
| Key hierarchy and signing rules                              | [keys-and-auth.md](keys-and-auth.md)                   |
| Polling and real-time patterns                               | [streaming-and-realtime.md](streaming-and-realtime.md) |

## Core Defaults

1. Use `hive-tx` for all chain operations unless user explicitly requires another SDK.
2. Enable multiple RPC nodes using `config.nodes` so failover is automatic.
3. Use `callWithQuorum(...)` for critical reads (authority checks, balances, pre-broadcast validation).
4. Keep read paths retryable; treat broadcast paths as write-once and verify status instead of blind retries.
5. Expose a `waitForInclusion` option and map it to `tx.broadcast(true)`.
6. Use the correct key type per operation (posting for social ops, active for financial/governance ops).

## When to Use

Use this skill when you need to:

- Build or debug Hive blockchain features in JavaScript/TypeScript using `hive-tx`.
- Implement reliable reads with multi-node failover and quorum validation.
- Build transaction flows for content, wallet, or `custom_json` operations.
- Add key-authority-aware signing and transaction status handling.

## When Not to Use

Do not use this skill when:

- The user requires another SDK/stack (for example `dhive`, Python, Rust) as the primary implementation target.
- The task is chain-agnostic API design with no Hive-specific operation details.
- The request is for non-Hive chains or Hive Engine-specific tooling not covered by `hive-tx`.
- The work requires custodial key storage design or secret-management architecture beyond code-level usage patterns.

## Standard Workflow

1. Configure nodes and retry/timeout values.
2. Run critical preflight reads with `callWithQuorum(...)`.
3. Build transaction with one or more `tx.addOperation(...)` calls.
4. Sign with the minimum required key(s).
5. Broadcast with an explicit wait strategy:
   - `tx.broadcast(false)` for fire-and-check-later.
   - `tx.broadcast(true)` to wait until transaction status resolves.
6. Return/record both `tx_id` and `status`.

## Output Requirements

When generating code for transaction broadcasts, include:

1. A node configuration block (`config.nodes`, `config.timeout`, `config.retry`).
2. A helper that accepts `waitForInclusion` and calls `tx.broadcast(waitForInclusion)`.
3. Status-aware handling for at least: `unknown`, `within_irreversible_block`, `expired_irreversible`, `too_old`.
4. A clear key choice for each operation.

## Guardrails

- Never hardcode private keys in source files.
- Keep HIVE/HBD amounts in 3-decimal asset strings (`1.000 HIVE`), and VESTS in 6-decimal strings.
- Sort beneficiaries alphabetically by account name before broadcasting `comment_options`.
- Do not blindly retry failed broadcasts; first verify chain state (by permlink/tx status/account history), then decide whether a retry is safe.
- Treat `unknown` as non-final; surface it clearly and provide a follow-up status-check path.
- Fail fast on key mismatch (`posting` vs `active`) before signing.
- Check RC before high-volume writes and return actionable guidance when RC is low.
- Redact private keys and sensitive memo content from logs, errors, and telemetry.

### Recovery Guidance

- `Missing Posting Authority` or `Missing Active Authority`: switch to the correct key and re-sign.
- `Duplicate transaction check failed`: assume it may already be submitted, verify chain state before any retry.
- `Please wait to transact, or power up`: account is RC-constrained; wait for regeneration or delegate/power up.
- Terminal status `expired_irreversible` or `too_old`: rebuild and rebroadcast only after validating current chain state.
