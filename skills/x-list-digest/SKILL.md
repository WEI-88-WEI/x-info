---
name: x-list-digest
description: Fetch, deduplicate, filter, and archive tweets from a fixed set of X/Twitter Lists for Obsidian-based research. Use when the user asks things like “帮我获取列表推文”, wants list updates since the last fetch, wants per-tweet notes from the configured lists (星, 看, maomao, meme, 生态, 项目, 其他), or wants time-window list digests pushed to GitHub.
---

Use this skill to maintain a repeatable pipeline for the configured X lists.

## Workflow

1. Fetch tweets from the requested alias, or all aliases if the user does not specify one.
2. If this is the first run for an alias or the user wants a rebuild, use bootstrap and fetch the latest 30 tweets.
3. Otherwise, fetch recent tweets and keep only items newer than the alias checkpoint in `data/state.json`.
4. Deduplicate by `tweet_id`.
5. Filter aggressively. Keep only tweets that match the fixed tags and have clear signal quality.
6. Prioritize airdrop info, trading setups, macro signals, and notable project updates for this user.
7. Write files using Beijing time with date folders and time-window filenames: `data/<YYYY-MM-DD>/<HH:MM:SS~HH:MM:SS>.md`.
8. Inside each note, use sections for aliases that produced useful content: 星, 看, maomao, meme, 生态, 项目, 其他.
9. Do not add overview, executive summary, recap, or other top-level summary blocks.
10. Do not add any separate tags section, summary section, or `重点来源` section.
11. For each kept tweet, write one standalone item with the useful content, then put that tweet's tags, posting user, and original link directly under that item.
12. Do not duplicate metadata elsewhere in the note.
13. Commit and push to the GitHub repo after generation when the user asked to save results.

## Output rules

- Always write Markdown in Obsidian-friendly format.
- Date must be a folder.
- File name must be the time window.
- All displayed dates and times must use Beijing time.
- Group content by alias inside the note.
- Do not add top-level overview or summary sections.
- For alias `星`, allow more detail per tweet because it has the highest weight.
- Filter out low-value and off-topic tweets.
- Keep only tweets relevant to these tags when possible: `#airdrop` `#macro` `#trading` `#defi` `#ai` `#btc`.
- Put tags, posting user, and original link directly under each kept tweet item.
- Do not add a separate tags block at the end or beginning of the note.

## Commands

Build time-window digests:

```bash
python3 {baseDir}/scripts/build_digest.py --all
```

Bootstrap and rebuild from the latest 30 tweets:

```bash
python3 {baseDir}/scripts/build_digest.py --all --bootstrap
```

Build time-window digests and push to GitHub:

```bash
python3 {baseDir}/scripts/build_digest.py --all --commit
```

## GitHub

Use `build_digest.py --commit` to commit and push only generated digest files and the state file.

Do not push unrelated workspace files.
