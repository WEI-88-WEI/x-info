---
name: x-list-digest
description: Fetch, deduplicate, analyze, tag, and archive tweets from a fixed set of X/Twitter Lists for Obsidian-based research. Use when the user asks things like “帮我获取列表推文”, wants list updates since the last fetch, wants summaries from the configured lists (星, 看, maomao, meme, 生态, 项目, 其他), or wants new tweets archived and pushed to GitHub.
---

Use this skill to maintain a repeatable pipeline for the configured X lists.

## Fixed lists

Use the aliases and weights from `references/lists.md`.

## Workflow

1. Run `scripts/fetch_list.py` for the requested alias, or for all aliases if the user does not specify one.
2. If this is the first run for an alias on a given day, fetch the latest 30 tweets.
3. Otherwise, fetch recent tweets and keep only items newer than the alias checkpoint in `data/state.json`.
4. Deduplicate by `tweet_id`.
5. Analyze only the new tweets. Prioritize airdrop info, trading setups, macro signals, and notable project updates for this user.
6. Assign tags from this fixed set when relevant: `#airdrop` `#macro` `#trading` `#defi` `#ai` `#btc`.
7. Generate Obsidian markdown files under `data/<alias>/<YYYY-MM-DD>/<HH:MM:SS~HH:MM:SS>.md`.
8. Update `data/state.json` with the newest tweet id and timestamp processed for each alias.
9. Commit and push to the GitHub repo after generation when the user asked to save results.

## Output rules

- Always write Markdown in Obsidian-friendly format.
- Preserve the list-based directory structure.
- Start each note with frontmatter.
- Include: alias, list URL, weight, window start/end, fetched count, new count, tags, and source tweet links.
- For alias `星`, write the most detailed summary because it has the highest weight.
- Surface an `Alpha 提取` section with only the strongest takeaways.
- Keep tweet ids in the note body for traceability.

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

Build one digest note:

```bash
python3 {baseDir}/scripts/build_digest.py --alias 星
```

Bootstrap one alias with the latest 30 tweets when you need the first note or want to rebuild the latest window:

```bash
python3 {baseDir}/scripts/build_digest.py --alias 星 --bootstrap
```

Build all digest notes and push to GitHub:

```bash
python3 {baseDir}/scripts/build_digest.py --all --commit
```

## GitHub

Use `build_digest.py --commit` to commit and push only generated digest files and the state file.

Do not push unrelated workspace files.
