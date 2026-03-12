# x-info

X/Twitter list intelligence for OpenClaw.

## Included skill

- `skills/x-list-digest`

## What it does

When asked `帮我获取列表推文`, the skill is designed to:

1. fetch tweets from the configured X lists
2. deduplicate by `tweet_id`
3. rank and filter for signal quality instead of dumping every tweet
4. prioritize content relevant to this user's profile: airdrops, trading setups, macro drivers, DeFi changes, AI infra, and BTC context
5. write Obsidian-compatible markdown notes in Beijing time
6. generate a short `全部列表总结` across all lists
7. write each alpha item in a conclusion-oriented style instead of raw tweet excerpts
8. include user display name plus handle for every item
9. add concise Chinese translations for non-Chinese tweets
10. optionally commit and push the generated digest data to GitHub

## Output style

The current digest format is optimized for reading speed and decision usefulness:

- lean structure, with low-information boilerplate removed
- stronger per-list filtering instead of full timeline dumps
- conclusion-first alpha items
- cross-list synthesis near the top of the note
- only the current generated data window is intended to be pushed to GitHub

## Configured list aliases

- 星
- 看
- maomao
- meme
- 生态
- 项目
- 其他

## Output location

Generated notes live under:

- `skills/x-list-digest/data/<YYYY-MM-DD>/<HH:MM:SS~HH:MM:SS>.md`
- `skills/x-list-digest/data/state.json`

## Typical workflow

1. clear old `data`
2. fetch fresh list tweets
3. generate the daily digest markdown
4. keep the current digest and `state.json`
5. push updated data to GitHub
