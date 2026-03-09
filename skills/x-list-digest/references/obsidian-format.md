# Obsidian Output Format

Write files using this structure:

`data/<YYYY-MM-DD>/<HH:MM:SS~HH:MM:SS>.md`

Use **Beijing time (UTC+8)** for both folder dates and file time windows.

Example:

```md
---
date: 2026-03-09
window: 08:12:56~12:33:59
timezone: Asia/Shanghai
aliases:
  - 星
  - 看
tags:
  - airdrop
  - trading
---

# 列表推文汇总｜2026-03-09｜08:12:56~12:33:59

## 总览
- 这个时间段内的高价值内容汇总
- 只保留有营养且有标签的内容

## 星（权重 5）
### 摘要
- 详细总结

### Alpha 提取
- 摘要内容
  - 标签：#airdrop #trading
  - 用户：@name
  - 链接：https://x.com/.../status/123
```

## Rules

- Date must be a folder.
- File name must be the time window.
- All displayed dates and times must use Beijing time.
- Group content by alias inside the note.
- Keep only high-signal tagged tweets.
- Do not dump every tweet.
- Put tags, posting user, and original link directly under each Alpha item.
- Do not add a separate `重点来源` section.
- Make `星` the most detailed section.
