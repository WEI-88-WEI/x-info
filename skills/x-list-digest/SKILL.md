---
name: x-list-digest
description: Fetch, deduplicate, filter, summarize, and archive tweets from a fixed set of X/Twitter Lists for Obsidian-based research. Use when the user asks things like “帮我获取列表推文”, wants list updates since the last fetch, wants summaries from the configured lists (星, 看, maomao, meme, 生态, 项目, 其他), or wants time-window list digests pushed to GitHub.
---

Use this skill to maintain a repeatable pipeline for the configured X lists.

## Workflow

1. Fetch tweets from the requested alias, or all aliases if the user does not specify one.
2. If this is the first run for an alias or the user wants a rebuild, use bootstrap and fetch the latest 30 tweets.
3. Otherwise, fetch recent tweets and keep only items newer than the alias checkpoint in `data/state.json`.
4. Deduplicate by `tweet_id` globally before writing output.
5. Filter aggressively. Keep only tweets that match the fixed tags and have clear signal quality.
6. Prioritize airdrop info, trading setups, macro signals, and notable project updates for this user.
7. Write files using Beijing time with date folders and time-window filenames: `data/<YYYY-MM-DD>/<HH:MM:SS~HH:MM:SS>.md`.
8. Inside each note, use sections for aliases that produced useful content: 星, 看, maomao, meme, 生态, 项目, 其他.
9. Keep the note lean. Do not add `总览`、模板化 `摘要`、单独 `标签` 区块或 `重点来源` 区块。
10. Add a short `全部列表总结` near the top. Write it as an overall digest of the whole batch, not as a showcase of a few picked tweets.
11. Treat `data/2026-03-20/00:02:42~09:10:19.md` as the canonical reference note for both overall summary style and tweet-level extraction quality.
12. Do not use `先看：` or any similar picked-items intro.
13. Summarize the batch-level picture with concrete content from this batch: actual price moves, policy events, protocol updates, funding flows, trading setups, numbers, and conditions.
14. `全部列表总结` should closely match the reference note: concise, batch-level, and written like a real synthesized briefing rather than pasted tweet excerpts.
15. Prefer a stable 3-paragraph structure when material exists: `交易主线还是围着高波动里的被动应对展开：...` / `宏观和结构性压力仍然在：...` / `机会侧还是有东西可做，但更偏执行型：...`.
16. Each paragraph must stay on its own theme only. Do not mix `交易`/`宏观`/`机会` content into the wrong paragraph.
17. Do not let the same tweet or the same fact pattern appear twice in `全部列表总结`, even if it matches multiple tags.
18. Do not quote or lightly rephrase multiple tweet summaries back-to-back; synthesize them into one coherent paragraph with concrete facts.
19. Keep each paragraph tight: usually 2 concrete points are enough. Prefer fewer, sharper details over long stitched sentences.
20. Aggressively compress: remove chatty lead-ins, self-talk, rhetorical filler, and repeated setup clauses from source tweets before summarizing.
21. Do not let any single summary paragraph become a long run-on sentence packed with tweet fragments.
22. Do not start with bookkeeping or meta-stat lines like `这批内容主要集中在…` or `本次共整理…`.
23. Avoid vague analyst filler like `风险偏好回升` / `值得继续跟` / `情绪改善` unless tied to specific events or numbers from the batch.
24. Do not include alias-distribution lines like `空投/积分主要在…` / `交易主要在…` / `宏观主要在…`.
25. Under each alias, keep only the strongest subset after ranking. Prefer fewer, sharper items over completeness.
26. For each kept tweet, write one compact Chinese summary line. Then put that tweet's tags, posting user display name plus handle, and original link directly under the item.
27. Tweet-level extraction should follow the same standard as the reference note: preserve the concrete fact pattern, strip filler, and rewrite into compact Chinese that can stand alone when read in isolation.
28. Do not emit `判断` or `动作` lines, and do not append interpretive tails like `这条偏政策和监管信号` or `适合放进宏观环境变量里看`.
29. For non-Chinese tweets, rewrite the main content into concise Chinese instead of dumping the English original.
30. If a rewritten summary still leaves obvious English sentence fragments, drop that item rather than emitting mixed-language output.
31. If the source says `bought another 30,000 ETH via FalconX 8 hours ago`, the summary should read like `8 小时前又通过 FalconX 买入 30,000 枚 ETH` rather than leaving the English sentence intact.
32. Commit and push to the GitHub repo after generation when the user asked to save results.

## Output rules

- Always write Markdown in Obsidian-friendly format.
- Date must be a folder.
- File name must be the time window.
- All displayed dates and times must use Beijing time.
- Group content by alias inside the note.
- For alias `星`, allow more detail because it has the highest weight.
- Filter out low-value and off-topic tweets.
- Keep only tweets relevant to these tags when possible: `#airdrop` `#macro` `#trading` `#defi` `#ai` `#btc`.
- Put tags, posting user display name plus handle, and original link directly under each kept item.
- Avoid analyst-sounding filler that could apply to any tweet.
- Prefer concrete facts, numbers, timing, conditions, and changes.

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
