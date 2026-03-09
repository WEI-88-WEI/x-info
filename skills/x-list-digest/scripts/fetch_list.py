#!/usr/bin/env python3
import argparse, json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
STATE_PATH = DATA_DIR / "state.json"
LISTS = {
    "星": {"weight": 5, "url": "https://x.com/i/lists/1855801320558694836"},
    "看": {"weight": 4, "url": "https://x.com/i/lists/1857245607410442370"},
    "maomao": {"weight": 4, "url": "https://x.com/i/lists/1783528404085821643"},
    "meme": {"weight": 3, "url": "https://x.com/i/lists/1783528771288780849"},
    "生态": {"weight": 4, "url": "https://x.com/i/lists/1783532882629370177"},
    "项目": {"weight": 4, "url": "https://x.com/i/lists/1783529655053778975"},
    "其他": {"weight": 4, "url": "https://x.com/i/lists/1783529697554694355"},
}

XREACH = os.environ.get("XREACH_BIN", "xreach")
AUTH = os.environ.get("X_AUTH_TOKEN")
CT0 = os.environ.get("X_CT0")
AGENT_REACH_CONFIG = Path.home() / ".agent-reach" / "config.yaml"


def load_tokens():
    global AUTH, CT0
    if AUTH and CT0:
        return
    if not AGENT_REACH_CONFIG.exists():
        return
    for line in AGENT_REACH_CONFIG.read_text().splitlines():
        if line.startswith("twitter_auth_token:") and not AUTH:
            AUTH = line.split(":", 1)[1].strip()
        elif line.startswith("twitter_ct0:") and not CT0:
            CT0 = line.split(":", 1)[1].strip()


def load_state():
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())
    return {"aliases": {}}


def save_state(state):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2))


def parse_time(s):
    return datetime.strptime(s, "%a %b %d %H:%M:%S %z %Y").astimezone(timezone.utc)


def run_xreach(url, limit=100):
    cmd = [XREACH]
    if AUTH:
        cmd += ["--auth-token", AUTH]
    if CT0:
        cmd += ["--ct0", CT0]
    cmd += ["list-tweets", url, "-n", str(limit), "--json"]
    out = subprocess.check_output(cmd, text=True)
    return json.loads(out)


def normalize_items(items):
    rows = []
    for item in items:
        created = parse_time(item["createdAt"])
        rows.append({
            "tweet_id": item["id"],
            "created_at": created.isoformat(),
            "text": item.get("text", ""),
            "author": item.get("user", {}).get("screenName", ""),
            "author_name": item.get("user", {}).get("name", ""),
            "lang": item.get("lang"),
            "link": f"https://x.com/{item.get('user', {}).get('screenName', 'i')}/status/{item['id']}",
            "metrics": {
                "reply": item.get("replyCount", 0),
                "retweet": item.get("retweetCount", 0),
                "like": item.get("likeCount", 0),
                "quote": item.get("quoteCount", 0),
                "view": item.get("viewCount", 0),
            },
        })
    rows.sort(key=lambda r: (r["created_at"], r["tweet_id"]))
    return rows


def filter_new(alias, rows, state, bootstrap=False):
    alias_state = state["aliases"].get(alias, {})
    last_id = alias_state.get("latest_tweet_id")
    last_ts = alias_state.get("latest_created_at")
    if bootstrap:
        return rows[-30:]
    if not last_id and not last_ts:
        return rows[-30:]
    fresh = []
    for row in rows:
        if last_ts and row["created_at"] <= last_ts:
            continue
        if last_id and row["tweet_id"] == last_id:
            continue
        fresh.append(row)
    seen = set()
    uniq = []
    for row in fresh:
        if row["tweet_id"] in seen:
            continue
        seen.add(row["tweet_id"])
        uniq.append(row)
    return uniq


def checkpoint(alias, new_rows, state):
    if not new_rows:
        return
    latest = max(new_rows, key=lambda r: (r["created_at"], r["tweet_id"]))
    state["aliases"][alias] = {
        "latest_tweet_id": latest["tweet_id"],
        "latest_created_at": latest["created_at"],
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def main():
    load_tokens()
    ap = argparse.ArgumentParser()
    ap.add_argument("--alias")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--limit", type=int, default=100)
    ap.add_argument("--bootstrap", action="store_true")
    args = ap.parse_args()

    targets = list(LISTS.keys()) if args.all else [args.alias]
    if not targets or targets == [None]:
        print("Specify --alias or --all", file=sys.stderr)
        sys.exit(2)

    state = load_state()
    result = {"generated_at": datetime.now(timezone.utc).isoformat(), "aliases": {}}

    for alias in targets:
        meta = LISTS[alias]
        payload = run_xreach(meta["url"], args.limit)
        rows = normalize_items(payload.get("items", []))
        new_rows = filter_new(alias, rows, state, bootstrap=args.bootstrap)
        checkpoint(alias, new_rows, state)
        result["aliases"][alias] = {
            "weight": meta["weight"],
            "url": meta["url"],
            "fetched_count": len(rows),
            "new_count": len(new_rows),
            "window_start": new_rows[0]["created_at"][11:19] if new_rows else None,
            "window_end": new_rows[-1]["created_at"][11:19] if new_rows else None,
            "tweets": new_rows,
        }

    save_state(state)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
