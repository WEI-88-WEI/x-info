---
name: x-list-digest
description: Fetch, deduplicate, filter, summarize, and archive tweets from a fixed set of X/Twitter Lists for Obsidian-based research. Use when the user asks things like “帮我获取列表推文”, wants list updates since the last fetch, wants summaries from the configured lists (星, 看, maomao, meme, 生态, 项目, 其他), or wants daily list digests pushed to GitHub.
---

Use this skill to maintain a repeatable pipeline for the configured X lists.

## Fixed lists

Use the aliases and weights from `references/lists.md`.

## Workflow

1. Run `scripts/fetch_list.py` for the requested alias, or for all aliases if the user does not specify one.
2. If this is the first run for an alias or the user wants a rebuild, use bootstrap and fetch the latest 30 tweets.
3. Otherwise, fetch recent tweets and keep only items newer than the alias checkpoint in `data/state.json`.
4. Deduplicate by `tweet_id`.
5. Filter aggressively. Keep only tweets that match the fixed tags and have clear signal quality.
6. Prioritize airdrop info, trading setups, macro signals, and notable project updates for this user.
7. Generate one Obsidian markdown file per date under `data/<YYYY-MM-DD>.md`.
8. Inside the date file, use sections for the aliases that produced useful content: 星, 看, maomao, meme, 生态, 项目, 其他.
9. Do not record every tweet. Write only detailed summaries plus the author and source link for important items.
10. Commit and push to the GitHub repo after generation when the user asked to save results.

## Output rules

- Always write Markdown in Obsidian-friendly format.
- Use one file per date, not one file per alias window.
- Include sections for aliases inside the daily file.
- For alias `星`, write the most detailed summary because it has the highest weight.
- Filter out low-value and off-topic tweets.
- Keep only tweets relevant to these tags when possible: `#airdrop` `#macro` `#trading` `#defi` `#ai` `#btc`.
- For important points, include the posting user and original tweet link.

## File format

Follow `references/obsidian-format.md` exactly.

## Commands

Fetch one alias:

```bash
python3 {baseDir}/scripts/fetch_list.py --alias 星
```

Fetch all aliases:

```bash
python3 {baseDir}/scripts/fetch_list.py --all
```

Build daily digests:

```bash
python3 {baseDir}/scripts/build_digest.py --all
```

Bootstrap and rebuild from the latest 30 tweets:

```bash
python3 {baseDir}/scripts/build_digest.py --all --bootstrap
```

Build daily digests and push to GitHub:

```bash
python3 {baseDir}/scripts/build_digest.py --all --commit
```

## GitHub

Use `build_digest.py --commit` to commit and push only generated daily digest files and the state file.

Do not push unrelated workspace files.
