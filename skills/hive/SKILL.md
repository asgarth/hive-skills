---
name: hive
description: Hive blockchain CLI skill for hive-tx-cli: query accounts/content/RC/feed/replies, upload images, and broadcast publish/reply/edit/vote/transfer/community/social/profile/reward/custom-json operations with correct key usage.
homepage: https://github.com/asgarth/hive-tx-cli
version: "2026.3.1"
tags: ["blockchain", "hive", "cli", "broadcasting"]
requirements:
  - hive
  - Node.js >= 22.0.0
  - npm/pnpm/bun for installation
triggers:
  - "Broadcast Hive blockchain operations"
  - "Post content to Hive blockchain"
  - "Query Hive account or content data"
  - "Transfer HIVE/HP on Hive"
  - "Vote on Hive posts"
profile: "binary-first"
metadata:
  {
    'openclaw':
      {
        'requires': { 'bins': ['hive'] },
        'install': [{ 'id': 'npm', 'kind': 'node', 'package': '@peakd/hive-tx-cli', 'bins': ['hive'], 'label': 'Install hive-tx-cli (npm)' }]
      }
  }
---

# Hive CLI

The `hive` CLI (`@peakd/hive-tx-cli`) is the single entrypoint for this skill. All functionality is accessed through its subcommands. Do not create wrapper scripts that only duplicate CLI invocations.

Use `hive` (`@peakd/hive-tx-cli`) to query Hive state and broadcast common operations.

## Install

```bash
# npm/pnpm/bun
npm install -g @peakd/hive-tx-cli

# One-shot (no install)
bunx @peakd/hive-tx-cli account peakd
```

## Requirements

- Node.js >= 22.0.0

## When to Use

Use this skill when you need to:

- Query Hive blockchain state (accounts, content, RC, feed, rewards)
- Broadcast operations (post, reply, vote, transfer, follow, custom-json)
- Upload images to Hive's image hosting
- Manage community subscriptions
- Claim rewards or delegate HP

## When Not to Use

Do **not** use this skill when:

- Simple read-only queries where raw API calls are faster (use `hive call` directly)
- Operations requiring hardware wallet signing (not supported)
- High-frequency trading scenarios (use specialized tools)
- Operations on chains other than Hive (e.g., Hive Engine tokens require different tools)

## Workflow

Follow this general workflow for safe operations:

1. **Configure keys**: Run `hive config` interactively or set environment variables (`HIVE_ACCOUNT`, `HIVE_POSTING_KEY`, `HIVE_ACTIVE_KEY`)
   ```bash
   hive config                    # Interactive setup
   export HIVE_ACCOUNT="your-username"
   export HIVE_POSTING_KEY="your-posting-private-key"
   ```
2. **Test with query/dry-run**: Verify configuration with `hive status`, query the target account, or use read-only commands first
   ```bash
   hive status                    # Check configuration status
   hive account peakd             # Query target account
   ```
3. **Execute operation**: Run the broadcast command (add `--wait` for commands that support it)
   ```bash
   hive vote --url https://peakd.com/@author/permlink --weight 100 --wait
   ```
4. **Verify**: Confirm the operation succeeded via returned transaction ID or by querying the updated state
   ```bash
   hive content author permlink   # Verify post appeared
   ```

## Quick Start

```bash
hive config                    # Interactive configuration
hive status                    # Check configuration status
hive account peakd             # Query an account
hive vote --url https://peakd.com/@author/permlink --weight 100
```

## Common Use Cases

### Post a new article

```bash
hive publish --permlink my-article --title "My Title" --body "Content here" --tags "hive,development" --wait
hive content your-account my-article  # Verify it appeared
```

### Reply to a post

```bash
hive reply author permlink --body "Great post!" --wait
```

### Vote on content

```bash
hive vote --url https://peakd.com/@author/permlink --weight 100 --wait
```

### Transfer HIVE

```bash
hive transfer --to recipient --amount "1.000 HIVE" --memo "Thanks!" --wait
```

### Claim rewards

```bash
hive claim --wait
```

## Authentication & Keys

- **Posting key**: publish/reply/edit/delete-comment/vote/follow/community subscribe/reblog/claim/custom-json(basic)/upload
- **Active key**: transfer/delegate/profile update/custom-json with `--required-active`, and raw active broadcasts
- Keys stored in `~/.hive-tx-cli/config.json` with 600 permissions
- Environment variables override config values

```bash
hive config                    # Interactive setup
hive config --show             # Show current configuration
hive config --clear            # Clear all configuration
hive config set account <name>
hive config set postingKey <private-key>
hive config set activeKey <private-key>
hive config set node <url>
hive config get account
```

### Environment Variables

```bash
export HIVE_ACCOUNT="your-username"
export HIVE_POSTING_KEY="your-posting-private-key"
export HIVE_ACTIVE_KEY="your-active-private-key"
export HIVE_JSON_OUTPUT=1      # Machine-friendly output + spinner disabled
```

## Guardrails & Warnings

> **⚠️ Active Key Operations**: Commands using `--required-active` or the active key can transfer funds or modify account settings. These operations are irreversible.

> **⚠️ Transfer Risks**: Hive transfers cannot be reversed. Always verify the recipient address and amount before executing.

> **⚠️ Memo Privacy**: Memos are publicly visible on the blockchain. Do not include sensitive information in memos.

> **⚠️ Key Exposure**: Never commit private keys to version control. Use environment variables or a secure config file with 600 permissions.

> **⚠️ Resource Credits (RC)**: Broadcasting operations consumes RC. Ensure sufficient RC before bulk operations. Check with `hive rc <account>`.

### Pre-flight Checklist

Before broadcasting any operation:

- [ ] Account name is correct (check with `hive account <name>`)
- [ ] Key type matches operation (posting vs active)
- [ ] Sufficient RC: `hive rc <account>` shows > 0
- [ ] Amounts/memos verified (transfers cannot be undone)
- [ ] Using `--wait` for commands that support it

## Query Commands

```bash
# Account/state
hive account <username>
hive balance <username>
hive rc <username>
hive props
hive block <number>

# Content (author/permlink or URL)
hive content <author> <permlink>
hive content https://peakd.com/@author/permlink
hive replies <author> <permlink>
hive replies https://peakd.com/@author/permlink
hive feed <account> --limit 10

# Raw API
hive call database_api get_accounts '[["username"]]'
hive call condenser_api get_content_replies '["author","permlink"]' --raw
```

## Broadcast Commands

### Publish, Reply, Edit, Delete

```bash
hive publish --permlink my-post --title "My Post" --body "Body" --tags "hive,cli"
hive publish --permlink my-post --title "My Post" --body-file ./post.md --metadata '{"app":"hive-tx-cli"}'
hive publish --permlink my-reply --title "Re" --body "Reply" --parent-url https://peakd.com/@author/permlink
hive publish --permlink my-post --title "My Post" --body "Body" --burn-rewards
hive publish --permlink my-post --title "My Post" --body "Body" --beneficiaries '[{"account":"foo","weight":1000}]'

hive reply <parent-author> <parent-permlink> --body "Nice post" --wait
hive edit <author> <permlink> --body-file ./updated.md --tags "hive,update"
hive delete-comment --url https://peakd.com/@author/permlink --wait
```

Notes:

- `publish` aliases: `post`, `comment`
- `publish` requires `--title`; use `reply` for standard replies
- `--wait` is available on supported commands to wait for tx confirmation

#### Post Metadata

The `--metadata` option accepts a JSON string with post metadata. All fields are optional.

**Schema:**

- `app`: Application identifier (e.g., "hive-tx-cli/2026.1.1")
- `description`: Short summary of the post content
- `image`: Array of image URLs for the post thumbnail
- `tags`: Array of post tags (should match --tags)
- `users`: Array of mentioned usernames
- `ai_tools`: Object indicating AI involvement in creating content
  - `writing_edit`: AI assisted with writing/editing
  - `media_generation`: AI generated images/media
  - `research`: AI assisted with research
  - `translation`: AI performed translation
  - `post_draft`: AI helped draft the post
  - `other`: Other AI assistance

**Guidelines:**

- Set `app` to the tool you're using
- Include a `description` summarizing the post (1-2 sentences)
- Add `image` URLs when the post contains images
- If the post was created with AI assistance, set appropriate `ai_tools` flags to `true`

**Example:**

```bash
hive post --permlink my-post --title "My Post" --body "Content" --tags "hive,ai" \
  --metadata '{"app":"hive-tx-cli/2026.1.1","description":"A post about Hive and AI tools","image":["https://example.com/image.jpg"],"ai_tools":{"writing_edit":true}}'
```

### Vote, Transfer, Custom JSON, Raw

```bash
hive vote --url https://peakd.com/@author/permlink --weight 100 --wait
hive transfer --to <recipient> --amount "1.000 HIVE" --memo "Thanks" --wait
hive custom-json --id <app-id> --json '{"key":"value"}'
hive custom-json --id <app-id> --json '{"key":"value"}' --required-active myaccount --wait
hive broadcast '[{"type":"vote","value":{"voter":"me","author":"you","permlink":"post","weight":10000}}]' --key-type posting --wait
```

### Social and Community

```bash
hive follow <account>
hive unfollow <account>
hive mute <account>
hive unmute <account>
hive reblog --author <author> --permlink <permlink>

hive community search peakd
hive community info hive-12345
hive community subscribers hive-12345
hive community subscribe hive-12345
hive community unsubscribe hive-12345
```

### Rewards and Profile

```bash
hive claim
hive delegate <account> "100 HP"
hive profile update --name "My Name" --about "Hive user" --location "Earth"
```

## Global Options

```bash
hive --account myaccount vote --author author --permlink permlink --weight 100
hive --node https://api.hive.blog account peakd
```

## Image Uploads

If possible, resize/compress large images before upload.

```bash
hive upload --file ./path/to/image.jpg
hive upload --file ./image.png --host https://images.ecency.com
```

Returns JSON with the uploaded URL.

## Output Contract

When `HIVE_JSON_OUTPUT=1` is set, commands return machine-friendly JSON output.

### Success Output

```json
{
  "success": true,
  "data": { ... },
  "txId": "abc123..."
}
```

### Error Output

```json
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE"
}
```

### Stderr Conditions

- Warnings and informational messages may be printed to stderr
- Progress spinners are disabled in JSON mode

## Troubleshooting

### Common Errors

| Error                         | Cause                        | Resolution                                                    |
| ----------------------------- | ---------------------------- | ------------------------------------------------------------- |
| `Invalid key` or `Auth error` | Wrong key type for operation | Posting key for publish/vote/follow; Active key for transfers |
| `Insufficient RC`             | Not enough Resource Credits  | Wait for RC regeneration or delegate HP                       |
| `Transaction expired`         | Node timing issue            | Retry with `--wait` or switch nodes                           |
| `Account does not exist`      | Typo in username             | Verify account name with `hive account <name>`                |

### Recovery Steps

1. **Auth failures**: Verify keys with `hive status`, check key type matches operation
2. **Broadcast uncertainty**: Always use `--wait` to wait for tx confirmation
3. **RC exhaustion**: Check with `hive rc <account>`, delegate from account with HP

### Node connection issues

- Try different node: `hive config set node https://api.hiveworks.com`
- Check network connectivity

## References

- Hive docs: https://developers.hive.io/
- hive-tx-cli: https://github.com/asgarth/hive-tx-cli
