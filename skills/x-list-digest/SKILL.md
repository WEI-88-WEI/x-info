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
10. Treat `data/2026-03-20/00:02:42~09:10:19.md` as the canonical reference note.
11. Add `全部列表总结` near the top and keep it to exactly 3 bullets when material exists.
12. The 3 bullets must use these fixed openings: `交易主线还是围着高波动里的被动应对展开：` / `宏观和结构性压力仍然在：` / `机会侧还是有东西可做，但更偏执行型：`.
13. Each summary bullet must contain only 1-2 hard facts from this batch: concrete prices, policy events, protocol updates, flows, numbers, project names, or explicit actions.
14. Do not use bookkeeping or filler such as `今天信息密度最高的列表`、`跨列表主线`、`噪音主要集中在`、`值得关注`、`情绪改善`、`风险偏好回升`.
15. Do not quote or lightly stitch together multiple tweet summaries; synthesize the batch into concise briefing prose that matches the reference note.
16. `全部列表总结` is forbidden from reusing long raw tweet clauses verbatim. Convert selected items into your own compressed prose first, then synthesize.
17. Each bullet must stay on its own theme. Do not mix `交易` / `宏观` / `机会` content into the wrong bullet.
18. Do not let the same tweet or fact pattern appear twice in `全部列表总结`.
19. Aggressively compress: remove chatty lead-ins, self-talk, rhetorical filler, repost framing, and repeated setup clauses.
20. Drop obvious noise from both the overall summary and alias sections, including personal life updates, blogger recommendations, generic motivation, sports metaphors, and broad career/AI hot-take lists.
21. Under each alias, keep only the strongest subset after ranking. Prefer fewer, sharper items over completeness.
22. For each kept tweet, write one compact Chinese summary line that can stand alone when read in isolation.
21. Tweet-level extraction must follow the same standard as the reference note: preserve the concrete fact pattern, strip filler, and avoid analyst-sounding tails.
22. Do not emit `判断` or `动作` lines, and do not append interpretive tails like `这条偏政策和监管信号` or `适合放进宏观环境变量里看`.
23. For non-Chinese tweets, rewrite the main content into concise Chinese instead of dumping the English original.
24. If a rewritten summary still leaves obvious English sentence fragments, drop that item rather than emitting mixed-language output.
25. If the source says `bought another 30,000 ETH via FalconX 8 hours ago`, the summary should read like `8 小时前又通过 FalconX 买入 30,000 枚 ETH`.
26. Commit and push to the GitHub repo after generation when the user asked to save results.

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
