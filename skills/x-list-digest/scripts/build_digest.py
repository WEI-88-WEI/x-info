#!/usr/bin/env python3
import argparse, json, re, subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
FETCH = BASE_DIR / "scripts" / "fetch_list.py"
LISTS = {
    "星": {"weight": 5, "url": "https://x.com/i/lists/1855801320558694836"},
    "看": {"weight": 4, "url": "https://x.com/i/lists/1857245607410442370"},
    "maomao": {"weight": 4, "url": "https://x.com/i/lists/1783528404085821643"},
    "meme": {"weight": 3, "url": "https://x.com/i/lists/1783528771288780849"},
    "生态": {"weight": 4, "url": "https://x.com/i/lists/1783532882629370177"},
    "项目": {"weight": 4, "url": "https://x.com/i/lists/1783529655053778975"},
    "其他": {"weight": 4, "url": "https://x.com/i/lists/1783529697554694355"},
}
TAG_RULES = {
    "airdrop": ["airdrop", "撸毛", "空投", "积分", "wl", "whitelist", "eligible", "tge", "alpha", "任务"],
    "macro": ["特朗普", "原油", "美股", "加息", "降息", "宏观", "油价", "fed", "cpi", "亚盘", "纳指", "标普", "伊朗"],
    "trading": ["交易", "做多", "做空", "止盈", "止损", "fdv", "polymarket", "perp", "仓位", "套利", "资金费", "开单", "赔率"],
    "defi": ["defi", "dex", "tvl", "流动性", "lp", "借贷", "链上", "收益率", "质押"],
    "ai": ["ai", "openclaw", "gpt", "agent", "模型", "龙虾", "codex"],
    "btc": ["btc", "比特币", "大饼", "bitcoin", "strategy"],
}
PRIORITY = ["airdrop", "trading", "macro", "defi", "ai", "btc"]
MIN_SCORE = 12


def run_fetch(alias=None, all_aliases=False, limit=100, bootstrap=False):
    cmd = ["python3", str(FETCH)]
    if all_aliases:
        cmd.append("--all")
    else:
        cmd += ["--alias", alias]
    cmd += ["--limit", str(limit)]
    if bootstrap:
        cmd.append("--bootstrap")
    out = subprocess.check_output(cmd, text=True)
    return json.loads(out)


def classify(text):
    lower = text.lower()
    found = []
    for tag, terms in TAG_RULES.items():
        if any(term.lower() in lower for term in terms):
            found.append(tag)
    return found


def clean(text):
    return re.sub(r"\s+", " ", text or "").strip()


def score_tweet(tweet, tags):
    metrics = tweet.get("metrics", {})
    score = metrics.get("like", 0) + metrics.get("retweet", 0) * 2 + metrics.get("quote", 0) * 2
    if metrics.get("view", 0) > 5000:
        score += 4
    if len(clean(tweet.get("text", ""))) > 100:
        score += 2
    for idx, tag in enumerate(PRIORITY, start=1):
        if tag in tags:
            score += (len(PRIORITY) - idx + 1) * 3
    return score


def summarize(tweet, tags):
    text = clean(tweet.get("text", ""))
    short = text[:180] + ("…" if len(text) > 180 else "")
    why = []
    if "airdrop" in tags:
        why.append("含空投/积分机会")
    if "trading" in tags:
        why.append("含交易或赔率线索")
    if "macro" in tags:
        why.append("带宏观驱动")
    if "defi" in tags:
        why.append("关联 DeFi / 链上生态")
    if "ai" in tags:
        why.append("涉及 AI / Agent")
    if "btc" in tags:
        why.append("涉及 BTC 主线")
    return short, "；".join(why) if why else "有一定信息价值"


def pick_signal_tweets(tweets):
    picked = []
    seen = set()
    for t in tweets:
        tags = classify(t.get("text", ""))
        if not tags:
            continue
        score = score_tweet(t, tags)
        if score < MIN_SCORE:
            continue
        if t["tweet_id"] in seen:
            continue
        seen.add(t["tweet_id"])
        t["tags"] = tags
        t["score"] = score
        picked.append(t)
    picked.sort(key=lambda x: (x["score"], x["created_at"]), reverse=True)
    return picked


def build_daily_sections(data):
    daily = defaultdict(lambda: defaultdict(list))
    for alias, payload in data["aliases"].items():
        picked = pick_signal_tweets(payload.get("tweets", []))
        for t in picked:
            dt = t["created_at"][:10]
            daily[dt][alias].append(t)
    return daily


def alias_section(alias, tweets):
    weight = LISTS[alias]["weight"]
    tags = []
    for t in tweets:
        for tag in t["tags"]:
            if tag not in tags:
                tags.append(tag)
    top_n = 5 if alias == "星" else 3
    top = tweets[:top_n]
    lines = [f"## {alias}（权重 {weight}）", "", "### 摘要"]
    lines.append(f"- 本组共筛出 {len(tweets)} 条有效信号，已过滤无营养内容。")
    if "airdrop" in tags:
        lines.append("- 重点关注空投/积分相关机会。")
    if "trading" in tags:
        lines.append("- 有可跟踪的交易/赔率/仓位线索。")
    if "macro" in tags:
        lines.append("- 有宏观事件驱动，需结合市场风险偏好观察。")
    lines += ["", "### Alpha 提取"]
    for t in top:
        short, why = summarize(t, t["tags"])
        lines.append(f"- {short}（{why}）")
    lines += ["", "### 重点来源"]
    for t in top:
        lines.append(f"- @{t['author']}｜{t['link']}")
    lines += ["", "### 标签", " ".join('#' + t for t in tags), ""]
    return lines, tags


def write_daily_file(date_key, alias_map):
    aliases_present = [a for a in LISTS if a in alias_map and alias_map[a]]
    if not aliases_present:
        return None, []
    all_tags = []
    body = ["---", f"date: {date_key}", "aliases:"]
    for alias in aliases_present:
        body.append(f"  - {alias}")
    body.append("tags:")
    section_blocks = []
    for alias in aliases_present:
        section, tags = alias_section(alias, alias_map[alias])
        section_blocks.append(section)
        for tag in tags:
            if tag not in all_tags:
                all_tags.append(tag)
    for tag in all_tags:
        body.append(f"  - {tag}")
    body += ["---", "", f"# 列表推文日报｜{date_key}", "", "## 总览"]
    body.append(f"- 当日共覆盖 {len(aliases_present)} 个列表：{'、'.join(aliases_present)}。")
    if "airdrop" in all_tags:
        body.append("- 已优先保留空投/积分相关内容。")
    if "trading" in all_tags:
        body.append("- 已优先保留交易和赔率相关内容。")
    if "macro" in all_tags:
        body.append("- 已提炼宏观驱动信息。")
    body.append("- 无营养、无标签、低信号推文已过滤，不再逐条罗列。")
    for section in section_blocks:
        body += [""] + section
    out_path = DATA_DIR / f"{date_key}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(body) + "\n")
    return out_path, all_tags


def git_commit_push(paths):
    repo = BASE_DIR.parents[1]
    rels = [str(Path(p).relative_to(repo)) for p in paths]
    subprocess.check_call(["git", "-C", str(repo), "add", *rels])
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    subprocess.check_call(["git", "-C", str(repo), "commit", "-m", f"Refine X daily digest format ({stamp})"])
    subprocess.check_call(["git", "-C", str(repo), "push"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--alias")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--commit", action="store_true")
    ap.add_argument("--bootstrap", action="store_true")
    args = ap.parse_args()
    data = run_fetch(alias=args.alias, all_aliases=args.all, bootstrap=args.bootstrap)
    daily = build_daily_sections(data)
    generated = []
    summary = {"errors": data.get("errors", {})}
    for date_key, alias_map in sorted(daily.items()):
        out_path, tags = write_daily_file(date_key, alias_map)
        if out_path:
            generated.append(out_path)
            summary[date_key] = {
                "file": str(out_path),
                "aliases": [a for a in LISTS if a in alias_map and alias_map[a]],
                "tags": tags,
            }
    if args.commit and generated:
        generated.append(DATA_DIR / "state.json")
        git_commit_push(generated)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
