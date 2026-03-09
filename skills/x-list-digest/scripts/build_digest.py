#!/usr/bin/env python3
import argparse, json, re, subprocess
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
    "airdrop": ["airdrop", "撸毛", "空投", "积分", "wl", "whitelist", "eligible", "tge"],
    "macro": ["特朗普", "原油", "美股", "加息", "降息", "宏观", "油价", "fed", "cpi", "亚盘"],
    "trading": ["交易", "做多", "做空", "止盈", "止损", "fdv", "polymarket", "perp", "仓位", "套利", "ap y", "资金费"],
    "defi": ["defi", "dex", "tvl", "流动性", "lp", "借贷", "链上"],
    "ai": ["ai", "openclaw", "gpt", "agent", "模型", "龙虾"],
    "btc": ["btc", "比特币", "大饼", "bitcoin"],
}
PRIORITY = ["airdrop", "trading", "macro", "defi", "ai", "btc"]


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


def score_tweet(tweet):
    text = tweet.get("text", "")
    tags = classify(text)
    metrics = tweet.get("metrics", {})
    score = metrics.get("like", 0) + metrics.get("retweet", 0) * 2 + metrics.get("quote", 0) * 2
    for i, tag in enumerate(PRIORITY[::-1], start=1):
        if tag in tags:
            score += i * 5
    if len(text) > 180:
        score += 3
    return score, tags


def summarize_tweet(tweet, tags):
    text = re.sub(r"\s+", " ", tweet.get("text", "")).strip()
    short = text[:140] + ("…" if len(text) > 140 else "")
    why = []
    if "airdrop" in tags:
        why.append("涉及空投/积分机会")
    if "trading" in tags:
        why.append("包含交易或赔率信息")
    if "macro" in tags:
        why.append("带有宏观或事件驱动影响")
    if "defi" in tags:
        why.append("关联链上/DeFi 生态")
    if "ai" in tags:
        why.append("涉及 AI / Agent 方向")
    if "btc" in tags:
        why.append("和 BTC 相关")
    if not why:
        why.append("属于列表中的一般动态")
    return short, "；".join(why)


def build_note(alias, payload):
    meta = LISTS[alias]
    tweets = payload["tweets"]
    if not tweets:
        return None, None
    dt = tweets[0]["created_at"][:10]
    start = payload["window_start"]
    end = payload["window_end"]
    scored = []
    all_tags = []
    for t in tweets:
        score, tags = score_tweet(t)
        t["tags"] = tags
        scored.append((score, t))
        all_tags.extend(tags)
    scored.sort(key=lambda x: x[0], reverse=True)
    top = [t for _, t in scored[: (6 if alias == "星" else 4)]]
    tag_list = []
    for tag in PRIORITY:
        if tag in all_tags and tag not in tag_list:
            tag_list.append(tag)
    overview = []
    if "airdrop" in all_tags:
        overview.append("空投/积分相关信息活跃，值得优先关注可执行机会。")
    if "trading" in all_tags:
        overview.append("交易与赔率类推文较多，适合提取短线情绪和策略线索。")
    if "macro" in all_tags:
        overview.append("出现宏观或事件驱动内容，需要和市场风险偏好联动看。")
    if not overview:
        overview.append("本时间窗以常规信息流更新为主。")
    overview.append(f"新增 {len(tweets)} 条，重点覆盖 {alias} 列表。")
    alpha = []
    for t in top[:3 if alias != '星' else 5]:
        short, why = summarize_tweet(t, t['tags'])
        alpha.append(f"- {short}（{why}）")
    title = f"{alias}｜{dt}｜{start}~{end}"
    tags_inline = " ".join(f"#{t}" for t in tag_list)
    lines = [
        "---",
        f"alias: {alias}",
        f"weight: {meta['weight']}",
        f"list_url: {meta['url']}",
        f"date: {dt}",
        f"window: {start}~{end}",
        f"fetched_count: {payload['fetched_count']}",
        f"new_count: {payload['new_count']}",
        "tags:",
    ]
    for tag in tag_list:
        lines.append(f"  - {tag}")
    lines += [
        "---",
        "",
        f"# {title}",
        "",
        "## 总览",
    ]
    for item in overview:
        lines.append(f"- {item}")
    lines += ["", "## Alpha 提取"]
    lines += alpha or ["- 暂无明显 Alpha。"]
    lines += ["", "## 分类标签", "", tags_inline or "#airdrop", "", "## 重点推文"]
    for idx, t in enumerate(top, start=1):
        short, why = summarize_tweet(t, t['tags'])
        lines += [
            "",
            f"### {idx}. {short}",
            f"- tweet_id: {t['tweet_id']}",
            f"- author: @{t['author']}",
            f"- time: {t['created_at'][11:19]} UTC",
            f"- link: {t['link']}",
            f"- 标签: {' '.join('#'+x for x in t['tags']) if t['tags'] else '无'}",
            f"- 摘要: {short}",
            f"- 为什么重要: {why}",
        ]
    lines += ["", "## 其他推文速览", ""]
    remainder = [t for t in tweets if t not in top]
    for t in remainder[:20]:
        short, _ = summarize_tweet(t, t['tags'])
        lines.append(f"- `{t['tweet_id']}`: {short}")
    lines += ["", "## Source Links", ""]
    for t in tweets:
        lines.append(f"- {t['link']}")
    out_dir = DATA_DIR / alias / dt
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{start}~{end}.md"
    out_path.write_text("\n".join(lines) + "\n")
    return out_path, tag_list


def git_commit_push(paths):
    repo = BASE_DIR.parents[1]
    rels = [str(Path(p).relative_to(repo)) for p in paths]
    subprocess.check_call(["git", "-C", str(repo), "add", *rels])
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    subprocess.check_call(["git", "-C", str(repo), "commit", "-m", f"Add X list digest notes ({stamp})"])
    subprocess.check_call(["git", "-C", str(repo), "push"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--alias")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--commit", action="store_true")
    ap.add_argument("--bootstrap", action="store_true")
    args = ap.parse_args()
    data = run_fetch(alias=args.alias, all_aliases=args.all, bootstrap=args.bootstrap)
    generated = []
    summary = {}
    for alias, payload in data["aliases"].items():
        out_path, tags = build_note(alias, payload)
        summary[alias] = {
            "new_count": payload["new_count"],
            "file": str(out_path) if out_path else None,
            "tags": tags or [],
        }
        if out_path:
            generated.append(out_path)
    if args.commit and generated:
        generated.append(DATA_DIR / "state.json")
        git_commit_push(generated)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
