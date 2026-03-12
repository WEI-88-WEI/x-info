# x-info

X/Twitter list intelligence for OpenClaw.

This repo contains an OpenClaw skill focused on turning noisy X/Twitter list timelines into a compact, decision-oriented research feed.

## Included skill

- `skills/x-list-digest`

---

## What this repo is for

This repo is built for a specific workflow:

- monitor a fixed set of X/Twitter lists
- pull fresh tweets from those lists
- filter out low-signal content
- keep the strongest items for a crypto-native operator
- rewrite them into readable Chinese notes
- archive the result as Obsidian-friendly markdown
- push the latest digest data back to GitHub

It is **not** trying to be a full X archive.
It is a **high-signal list digest pipeline**.

---

## Who this is optimized for

The current skill behavior is optimized for a user with this profile:

- crypto native
- cares about airdrops and qualification windows
- cares about trading setups and market transmission
- wants macro events translated into actionable watchpoints
- follows DeFi mechanism changes, yield / vault / points systems, and onchain capital rotation
- cares about AI / agent infrastructure when it has real strategy value
- wants BTC-related context, but not BTC-only content

That user profile affects the ranking, filtering, and summary style.

---

## What the skill does

When asked things like:

- `帮我获取列表推文`
- `获取今天的列表推文`
- `推 github`
- `重新抓取并总结`

`skills/x-list-digest` is designed to:

1. fetch tweets from the configured X lists
2. deduplicate by `tweet_id`
3. rank tweets by signal quality
4. penalize low-value content such as:
   - reposts / RT-heavy items
   - slogan-like AI marketing posts
   - vague brand content
   - low-specificity commentary
   - multiple tweets saying nearly the same thing
5. prioritize tweets with:
   - clear opportunity windows
   - metrics / numbers / caps / points / FDV / OI / vault changes
   - macro-to-market transmission clues
   - DeFi mechanism changes or capital flow signals
   - meaningful BTC context
6. generate a compact markdown digest in Beijing time
7. add a top-level `全部列表总结`
8. write per-list `Alpha 提取` items in **conclusion mode**, not raw tweet-copy mode
9. show each source as:
   - display name
   - handle
   - original link
10. add concise Chinese translation for non-Chinese tweets
11. write output into `skills/x-list-digest/data/`
12. optionally sync the latest data back to GitHub

---

## Current output philosophy

The digest is intentionally opinionated.

### It tries to do this

- be fast to scan
- preserve decision value
- reduce timeline noise
- convert scattered tweets into readable conclusions
- help the user decide what is worth:
  - watching
  - digging deeper on
  - participating in

### It avoids doing this

- dumping full list timelines
- keeping low-information engagement bait
- repeating the same theme too many times
- bloated markdown full of template filler
- acting like a neutral archive when a ranked digest is more useful

---

## Output structure

A generated digest usually contains:

- frontmatter metadata
- one file per Beijing-time date / time window
- `全部列表总结`
- per-alias sections such as:
  - 星
  - 看
  - maomao
  - meme
  - 生态
  - 项目
  - 其他
- inside each alias section:
  - `Alpha 提取`
  - concise conclusion-style items
  - optional `为什么重要`
  - optional `你该怎么用`
  - translation for non-Chinese tweets
  - tags
  - display name + handle
  - original X link

The current system prefers:

- **fewer, stronger items**
- not full coverage for coverage’s sake

---

## Global summary behavior

The `全部列表总结` block is meant to answer questions like:

- which lists were most information-dense today?
- what is the real cross-list market narrative?
- where are the highest-quality opportunities?
- where is the noise concentrated?
- what deserves active watching next?

This summary is written from the user’s point of view, not as a neutral newsroom recap.

---

## Translation behavior

For tweets whose main content is not Chinese, the skill adds a concise Chinese translation.

This translation is meant to be:

- readable
- compressed
- decision-oriented

It is **not** intended to be a perfect sentence-by-sentence literary translation.
The goal is: the user should understand why the tweet matters without needing to open X.

---

## Configured list aliases

The current skill is configured around these aliases:

- 星
- 看
- maomao
- meme
- 生态
- 项目
- 其他

These aliases are treated as stable buckets for digest generation.

---

## Output paths

Generated files live under:

- `skills/x-list-digest/data/<YYYY-MM-DD>/<HH:MM:SS~HH:MM:SS>.md`
- `skills/x-list-digest/data/state.json`

### `state.json`

`state.json` stores checkpoint state for each alias so the skill can:

- know what has already been seen
- fetch incrementally on later runs
- avoid repeatedly re-processing the same tweets

---

## Typical workflow used in practice

A common operator flow is:

1. clear old `data`
2. fetch fresh tweets from all configured lists
3. rebuild the latest digest
4. keep only the current digest file and `state.json`
5. commit and push the refreshed data to GitHub

In short:

- clear
- fetch
- filter
- summarize
- archive
- push

---

## GitHub sync behavior

This repo is commonly used as a lightweight distribution layer for the latest digest output.

Typical sync behavior:

- remove stale digest data
- write the newly generated digest
- keep `state.json`
- commit only the intended digest data update
- push to `main`

This keeps the repo aligned with the most recent curated output instead of accumulating a lot of stale intermediate files.

---

## Why the repo may not contain every tweet

That is intentional.

The skill is designed to optimize for:

- signal density
- user relevance
- downstream actionability

So if a tweet is missing, common reasons are:

- it was too low-signal
- it duplicated a stronger tweet
- it was generic AI / branding noise
- it lacked relevance to the user’s focus areas
- it lost in ranking against stronger items in the same alias bucket

---

## Design principles behind the skill

The current implementation follows a few practical rules:

### 1. Signal > completeness

A digest is more useful than a dump.

### 2. Conclusions > excerpts

Users care more about:

- what happened
- why it matters
- what to watch

than raw tweet text.

### 3. Relevance > popularity

A viral post is not automatically useful.

### 4. Chinese readability matters

The user should be able to read the digest directly, without bouncing back and forth into X.

### 5. Cross-list synthesis matters

The best signal often appears only after combining multiple lists, not from reading one tweet in isolation.

---

## Example use cases

This repo / skill is a good fit when you want to:

- get today’s strongest list signals in one pass
- monitor airdrop opportunities without reading every post manually
- track macro-driven market narratives through curated X lists
- keep a research notebook in Obsidian-ready markdown
- push the latest digest to GitHub for later reading or automation

---

## Repository layout

```text
x-info/
├── README.md
└── skills/
    └── x-list-digest/
        ├── SKILL.md
        ├── scripts/
        │   ├── fetch_list.py
        │   └── build_digest.py
        ├── references/
        └── data/
            ├── state.json
            └── <YYYY-MM-DD>/
                └── <HH:MM:SS~HH:MM:SS>.md
```

---

## Notes

This repo reflects an actively iterated workflow.
The output format, ranking rules, translation behavior, and summary style may continue to evolve as the digest gets tuned for better signal quality.
