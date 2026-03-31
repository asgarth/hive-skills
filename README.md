# AI Agent Skills

This repository contains AI agent skills that extend the capabilities of your AI assistant.

## Available Skills

- **hive-developer**: Build and debug Hive blockchain software with `hive-tx` in JavaScript/TypeScript, including node failover, quorum reads, key-safe signing, and status-aware broadcasting for wallet, content, and `custom_json` flows.

- **hive**: Hive blockchain CLI for querying accounts, content, RC, feed, replies, and broadcasting operations (publish, reply, edit, vote, transfer, etc.).

- **npm-scan**: Recursively scan folders for affected npm ecosystem dependency versions across npm, pnpm, and yarn projects, separating declared, locked, and installed evidence.

- **venice-ai**: Generate and manipulate images and videos using Venice.ai's privacy-first, uncensored AI API.

## Installation

To add skills to your AI agent, run:

```bash
npx skills add https://github.com/asgarth/hive-skills --skill hive-developer
npx skills add https://github.com/asgarth/hive-skills --skill hive
npx skills add https://github.com/asgarth/hive-skills --skill npm-scan
npx skills add https://github.com/asgarth/hive-skills --skill venice-ai
```
