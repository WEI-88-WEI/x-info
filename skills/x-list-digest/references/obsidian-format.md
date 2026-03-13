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
---

# 列表推文汇总｜2026-03-09｜08:12:56~12:33:59

## 全部列表总结
- 先看这几条：A 项目开放第二季积分；B 协议披露奖励分发数字；C 观点指出稳定币结算会继续吃到宏观红利。
- 空投/积分主要在 星、项目；交易线索主要在 看；宏观线索主要在 生态。

## 星

### Alpha 提取
- 美国参议院投票支持在两党住房法案中加入禁止美联储发行 CBDC 的条款。
  - 标签：#macro
  - 用户：Watcher.Guru (@WatcherGuru)
  - 链接：https://x.com/WatcherGuru/status/2032141446032089399

## 看

### Alpha 提取
- Tom Lee（@fundstrat）的 Bitmine 8 小时前似乎又通过 FalconX 买入 30,000 枚 ETH，金额约 6189 万美元。
  - 标签：#btc
  - 用户：Lookonchain (@lookonchain)
  - 链接：https://x.com/lookonchain/status/2032275771927187596
```

## Rules

- Date must be a folder.
- File name must be the time window.
- All displayed dates and times must use Beijing time.
- Group content by alias inside the note.
- Keep only high-signal tagged tweets.
- Do not dump every tweet.
- Put tags, posting user display name plus handle, and original link directly under each item.
- Add a short `全部列表总结` near the top.
- Do not add `总览`、模板化 `摘要`、单独 `标签` 区块或 `重点来源` section.
- Do not append interpretation tails like `这条偏政策...` / `适合放进宏观环境变量里看` after the factual summary.
- For English tweets, translate the useful content into Chinese instead of leaving the main sentence in English.
- Make `星` the most detailed section.
