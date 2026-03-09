# Obsidian Output Format

Write one daily markdown file per date.

Path:

`data/<YYYY-MM-DD>.md`

Example:

```md
---
date: 2026-03-09
aliases:
  - 星
  - 看
  - maomao
  - meme
  - 生态
  - 项目
  - 其他
tags:
  - airdrop
  - trading
  - macro
---

# 列表推文日报｜2026-03-09

## 总览
- 今日最重要的信号
- 只总结有营养的内容

## 星（权重 5）
### 摘要
- 详细总结

### Alpha 提取
- 只写最强信号

### 重点来源
- @name｜https://x.com/.../status/123
- @name2｜https://x.com/.../status/456

### 标签
#airdrop #trading

## 看（权重 4）
...
```

## Rules

- Use one file per date.
- Include sections for the aliases that produced useful tagged tweets on that date.
- Do not dump every tweet.
- Keep only tweets that match the fixed tags and clear signal quality.
- For important points, include the posting user and original link.
- Make `星` the most detailed section.
