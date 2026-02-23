---
name: hive
description: Hive blockchain CLI skill for hive-tx-cli: query accounts/content/RC/feed/replies, upload images, and broadcast publish/reply/edit/vote/transfer/community/social/profile/reward/custom-json operations with correct key usage.
homepage: https://github.com/asgarth/hive-tx-cli
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

## Quick Start

```bash
hive config                    # Interactive configuration
hive status                    # Check configuration status
hive account peakd             # Query an account
hive vote --url https://peakd.com/@author/permlink --weight 100
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

## Troubleshooting

- Auth errors: verify account + private keys, then run `hive status`
- Key mismatch: posting vs active operations are different; switch key type/command
- URL parsing issues: pass explicit `--author` + `--permlink` instead of `--url`
- Broadcast uncertainty: add `--wait` to commands that support it
- Script mode: set `HIVE_JSON_OUTPUT=1` to avoid spinner/UI text

### Node connection issues

- Try different node: `hive config set node https://api.hiveworks.com`
- Check network connectivity

## References

- Hive docs: https://developers.hive.io/
- hive-tx-cli: https://github.com/asgarth/hive-tx-cli
