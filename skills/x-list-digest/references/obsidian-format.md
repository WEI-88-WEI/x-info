# Obsidian Output Format

Each generated note should follow this structure.

```md
---
alias: 星
weight: 5
list_url: https://x.com/i/lists/1855801320558694836
date: 2026-03-09
window: 08:12:56~12:33:59
fetched_count: 30
new_count: 8
tags:
  - airdrop
  - trading
---

# 星｜2026-03-09｜08:12:56~12:33:59

## 总览

2-5 bullets summarizing the window.

## Alpha 提取

- strongest signals only
- note why it matters

## 分类标签

#airdrop #trading #macro

## 重点推文

### 1. <short headline>
- tweet_id: 123
- author: @name
- time: 08:30:00 UTC
- link: https://x.com/.../status/123
- 摘要: ...
- 为什么重要: ...

## 其他推文速览

- `123`: one-line summary
- `456`: one-line summary

## Source Links

- https://x.com/.../status/123
- https://x.com/.../status/456
```

## Naming

Write files to:

`data/<alias>/<YYYY-MM-DD>/<HH:MM:SS~HH:MM:SS>.md`

Examples:

- `data/星/2026-03-09/08:12:56~12:33:59.md`
- `data/看/2026-03-09/12:34:00~15:10:22.md`
