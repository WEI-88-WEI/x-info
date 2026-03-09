# Obsidian Output Format

Write files using this structure:

`data/<YYYY-MM-DD>/<HH:MM:SS~HH:MM:SS>.md`

Example:

```md
---
date: 2026-03-09
window: 08:12:56~12:33:59
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
- 最强信号

### 重点来源
- @name｜https://x.com/.../status/123

### 标签
#airdrop #trading
```

## Rules

- Date must be a folder.
- File name must be the time window.
- Group content by alias inside the note.
- Keep only high-signal tagged tweets.
- Do not dump every tweet.
- For important points, include the posting user and original link.
- Make `星` the most detailed section.
