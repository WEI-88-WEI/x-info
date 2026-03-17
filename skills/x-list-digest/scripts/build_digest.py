#!/usr/bin/env python3
import argparse
import html
import json
import math
import re
import subprocess
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
FETCH = BASE_DIR / "scripts" / "fetch_list.py"
BJ = timezone(timedelta(hours=8))
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
    "airdrop": ["airdrop", "撸毛", "空投", "积分", "wl", "whitelist", "eligible", "tge", "alpha", "任务", "claim", "snapshot", "reward", "campaign"],
    "macro": ["特朗普", "原油", "美股", "加息", "降息", "宏观", "油价", "fed", "cpi", "亚盘", "纳指", "标普", "伊朗", "stablecoin", "稳定币", "流动性"],
    "trading": ["交易", "做多", "做空", "止盈", "止损", "fdv", "polymarket", "perp", "仓位", "套利", "资金费", "开单", "赔率", "entry", "tp", "sl", "breakout"],
    "defi": ["defi", "dex", "tvl", "流动性", "lp", "借贷", "链上", "收益率", "质押", "deposit", "deposits", "bridge", "vault"],
    "ai": ["ai", "openclaw", "gpt", "agent", "模型", "龙虾", "codex", "cursor", "claude"],
    "btc": ["btc", "eth", "ethereum", "比特币", "大饼", "bitcoin", "strategy"],
}
PRIORITY = ["airdrop", "trading", "macro", "defi", "ai", "btc"]
TAG_BONUS = {
    "airdrop": 5,
    "trading": 4,
    "macro": 3,
    "defi": 3,
    "ai": 2,
    "btc": 2,
}
ACTION_TERMS = [
    "claim", "eligible", "snapshot", "deposit", "stake", "bridge", "mint", "launch", "live", "register", "trade",
    "领取", "快照", "开放", "上线", "开始", "截止", "存入", "质押", "桥接", "铸造", "交易", "报名", "奖励",
]
LOW_SIGNAL_PATTERNS = [
    r"^rt @[a-z0-9_]+:",
    r"\bgm\b",
    r"\bgood morning\b",
    r"\blfg\b",
    r"\bsoon\b",
    r"\bwen\b",
    r"\bbullish\b",
    r"\bjust vibes\b",
    r"\bstay tuned\b",
    r"\bloading\b",
]
ANALYSIS_TAIL_PATTERNS = [
    r"[，,；; ]*这条偏[^。；!?！？]*",
    r"[，,；; ]*偏(?:政策|监管|情绪|观点|叙事|宏观)[^。；!?！？]*",
    r"[，,；; ]*适合放进[^。；!?！？]*",
    r"[，,；; ]*放进[^。；!?！？]*里看",
    r"[，,；; ]*环境变量[^。；!?！？]*",
    r"[，,；; ]*重点在于[^。；!?！？]*",
    r"[，,；; ]*值得放进[^。；!?！？]*",
    r"[，,；; ]*可放进[^。；!?！？]*",
]
PHRASE_REPLACEMENTS = [
    (r"\bairdrops?\b", "空投"),
    (r"\bpoints? program\b", "积分计划"),
    (r"\bpoints?\b", "积分"),
    (r"\brecap\b", "回顾"),
    (r"\bdistributed\b", "已分发"),
    (r"\bdistribute\b", "分发"),
    (r"\busers?\b", "用户"),
    (r"\brollups?\b", "Rollup"),
    (r"\bleading\b", "领跑"),
    (r"\bleaderboard\b", "排行榜"),
    (r"\bhas surpassed\b", "已突破"),
    (r"\bsurpassed\b", "突破"),
    (r"\btotal deposits?\b", "总存款"),
    (r"\bdeposits?\b", "存款"),
    (r"\bdeposit(?:ed|ing)?\b", "存入"),
    (r"\bwithdraw(?:al|als)?\b", "提现"),
    (r"\bclaim(?:ing)?\b", "领取"),
    (r"\bwhitelist\b", "白名单"),
    (r"\beligible\b", "符合条件"),
    (r"\bannounc(?:e|ed|es)\b", "宣布"),
    (r"\bintroduc(?:e|ed|es)\b", "推出"),
    (r"\blaunch(?:ed|ing|es)?\b", "上线"),
    (r"\bnow live\b", "现已上线"),
    (r"\bis live\b", "已上线"),
    (r"\blive\b", "上线"),
    (r"\bmainnet\b", "主网"),
    (r"\btestnet\b", "测试网"),
    (r"\bfederal reserve\b", "美联储"),
    (r"\bcentral bank digital currency\b", "CBDC"),
    (r"\bu\.?s\.? senate\b", "美国参议院"),
    (r"\bsenate\b", "参议院"),
    (r"\bfed\b", "美联储"),
    (r"\bcbdc\b", "CBDC"),
    (r"\bbipartisan\b", "两党"),
    (r"\bhousing\b", "住房"),
    (r"\bbill\b", "法案"),
    (r"\bprovision\b", "条款"),
    (r"\bvoted? to include\b", "投票支持加入"),
    (r"\bvoted to\b", "投票支持"),
    (r"\bvote(?:d|s)? for\b", "投票支持"),
    (r"\badd(?:ed|ing)?\b", "加入"),
    (r"\bban on\b", "禁止"),
    (r"\bban(?:ning|ned|s)?\b", "禁止"),
    (r"\breclaims?\b", "重新站上"),
    (r"\bbitcoin\b", "比特币"),
    (r"\bpresident\b", "总统"),
    (r"\bchair\b", "主席"),
    (r"\bjerome powell\b", "鲍威尔"),
    (r"\bsays\b", "表示"),
    (r"\bshould\b", "应"),
    (r"\blower interest rates\b", "降息"),
    (r"\bimmediately\b", "立即"),
    (r"\bwithout waiting for the next fomc meeting\b", "无需等到下次 FOMC 会议"),
    (r"\bbought another\b", "再次买入"),
    (r"\bbought\b", "买入"),
    (r"\bsold\b", "卖出"),
    (r"\bvia\b", "通过"),
    (r"\bit seems that\b", "似乎"),
    (r"\bstablecoins?\b", "稳定币"),
    (r"\btrading\b", "交易"),
    (r"\btraders?\b", "交易者"),
    (r"\bpartnership\b", "合作"),
    (r"\bpartner(?:ed|s)? with\b", "与"),
    (r"\bopen now\b", "现已开放"),
    (r"\bnow open\b", "现已开放"),
    (r"\bopen\b", "开放"),
    (r"\btoday\b", "今日"),
    (r"\btomorrow\b", "明日"),
    (r"\bthis week\b", "本周"),
    (r"\bnext week\b", "下周"),
    (r"\bemail\b", "邮件"),
    (r"\bmessaging apps\b", "消息应用"),
    (r"\bbank cards\b", "银行卡"),
    (r"\bpayments?\b", "支付"),
    (r"\bcoins?\b", "币"),
    (r"\bbills\b", "账单"),
    (r"\btelegraph\b", "电报"),
    (r"\bletters\b", "书信"),
    (r"\bpower(?:ed)? by\b", "由"),
]
MIN_SCORE = 10


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


def clean(text):
    text = html.unescape(text or "")
    text = text.replace("\u00a0", " ")
    text = text.replace("\u2022", " • ")
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def contains_term(text, term):
    haystack = text.lower()
    needle = term.lower()
    if re.search(r"[\u4e00-\u9fff]", needle):
        return needle in haystack
    pattern = rf"(?<![a-z0-9_]){re.escape(needle)}(?![a-z0-9_])"
    return re.search(pattern, haystack) is not None


def has_any_term(text, terms):
    return any(contains_term(text, term) for term in terms)


def classify(text):
    lower = clean(text).lower()
    found = []
    for tag, terms in TAG_RULES.items():
        if has_any_term(lower, terms):
            found.append(tag)
    return found


def normalize_for_similarity(text):
    text = clean(text).lower()
    text = re.sub(r"^rt @[a-z0-9_]+:\s*", "", text)
    text = re.sub(r"@[a-z0-9_]+", "", text)
    text = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", text)
    return text[:96]


def is_chinese_dominant(text):
    cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
    latin = len(re.findall(r"[A-Za-z]", text))
    return cjk >= max(6, latin // 2)


def has_excess_english(text):
    cleaned = re.sub(r"@[A-Za-z0-9_]+", "", text)
    cleaned = re.sub(r"\b[A-Za-z_]+\.[A-Za-z0-9_()]+\b", "", cleaned)
    cleaned = re.sub(r"\b[A-Z]{2,}\b", "", cleaned)
    cjk = len(re.findall(r"[\u4e00-\u9fff]", cleaned))
    english_words = re.findall(r"\b[A-Za-z]{4,}\b", cleaned)
    english_chars = sum(len(word) for word in english_words)
    return len(english_words) >= 4 and english_chars > cjk


def looks_low_signal(text):
    simple = clean(text)
    if not simple:
        return True
    if len(simple) < 28 and not re.search(r"\d", simple):
        return True
    if re.fullmatch(r"[\W_]+", simple):
        return True
    lower = simple.lower()
    return any(re.search(pattern, lower) for pattern in LOW_SIGNAL_PATTERNS)


def specificity_bonus(text):
    bonus = 0
    if re.search(r"\d", text):
        bonus += 2
    if re.search(r"[$%]|\b\d+(?:\.\d+)?[kmb]?\b", text, re.I):
        bonus += 1
    if re.search(r"\$[A-Z0-9]{2,10}\b", text):
        bonus += 1
    if has_any_term(text.lower(), [term for term in ACTION_TERMS if term.isascii()]):
        bonus += 2
    if has_any_term(text, [term for term in ACTION_TERMS if not term.isascii()]):
        bonus += 2
    if len(text) >= 80:
        bonus += 1
    return bonus


def score_tweet(tweet, tags):
    text = clean(tweet.get("text", ""))
    metrics = tweet.get("metrics", {})
    score = int(
        math.log1p(metrics.get("like", 0)) * 1.0
        + math.log1p(metrics.get("retweet", 0)) * 1.4
        + math.log1p(metrics.get("quote", 0)) * 1.4
        + math.log1p(metrics.get("reply", 0)) * 0.6
        + math.log1p(metrics.get("view", 0)) * 0.4
    )
    score += sum(TAG_BONUS.get(tag, 0) for tag in tags)
    score += specificity_bonus(text)
    if len(tags) >= 2:
        score += 1
    if looks_low_signal(text):
        score -= 5
    if text.startswith("RT @"):
        score -= 4
    if len(text) < 50:
        score -= 2
    return score


def strip_prefix_noise(text):
    text = re.sub(r"^RT @[A-Za-z0-9_]+:\s*", "", text)
    text = re.sub(r"^(?:JUST IN|NEW|BREAKING|NEWS|UPDATE)\s*[:：\-]\s*", "", text, flags=re.I)
    text = re.sub(r"^[🇺🇸🇨🇳🇯🇵🇪🇺🇬🇧🇭🇰🇸🇬\s]+", "", text)
    return text.strip()


def apply_phrase_replacements(text):
    updated = text
    for pattern, replacement in PHRASE_REPLACEMENTS:
        updated = re.sub(pattern, replacement, updated, flags=re.I)
    updated = updated.replace("&", "和")
    updated = updated.replace("/", " / ")
    updated = updated.replace("→", " -> ")
    updated = re.sub(r"\s*•\s*", "；", updated)
    updated = re.sub(r"\s*\|\s*", "；", updated)
    updated = re.sub(r"\s*[-–—]\s*", "；", updated)
    updated = re.sub(r"\s+", " ", updated)
    updated = re.sub(r"\s*([，。；：！？])\s*", r"\1", updated)
    return updated.strip()


def smart_truncate(text, limit=170):
    if len(text) <= limit:
        return text
    cut = text[:limit]
    last = max(cut.rfind(sep) for sep in ["；", "。", "，", ",", ":", " "])
    if last >= limit * 0.55:
        cut = cut[:last]
    return cut.rstrip("；，,: ") + "…"


def normalize_clause(clause):
    clause = clause.strip(" ;；，,。")
    clause = re.sub(r"^[\-•·]+\s*", "", clause)
    clause = re.sub(r"\s+", " ", clause)
    return clause.strip()


def format_decimal(value):
    text = f"{value:.2f}"
    return text.rstrip("0").rstrip(".")


def translate_money(value_text):
    value_text = value_text.strip()
    match = re.fullmatch(r"\$?([\d,]+(?:\.\d+)?)([KMB])?", value_text, re.I)
    if not match:
        return value_text.replace("$", "")
    number = float(match.group(1).replace(",", ""))
    suffix = (match.group(2) or "").upper()
    if suffix == "K":
        number *= 1_000
    elif suffix == "M":
        number *= 1_000_000
    elif suffix == "B":
        number *= 1_000_000_000
    if number >= 100_000_000:
        return f"{format_decimal(number / 100_000_000)} 亿美元"
    if number >= 10_000:
        return f"{format_decimal(number / 10_000)} 万美元"
    return f"{format_decimal(number)} 美元"


def translate_relative_time(text):
    unit_map = {
        "minute": "分钟",
        "minutes": "分钟",
        "hour": "小时",
        "hours": "小时",
        "day": "天",
        "days": "天",
        "week": "周",
        "weeks": "周",
        "month": "个月",
        "months": "个月",
    }
    match = re.fullmatch(r"(\d+)\s+(minute|minutes|hour|hours|day|days|week|weeks|month|months)", text.strip(), re.I)
    if not match:
        return text.strip()
    amount, unit = match.groups()
    return f"{amount} {unit_map[unit.lower()]}"


def prettify_entity(text):
    text = text.strip()
    text = re.sub(r"#([A-Za-z0-9_]+)", r"\1", text)
    text = re.sub(r"([A-Za-z0-9._'’ \-]+)\(@([A-Za-z0-9_]+)\)", r"\1（@\2）", text)
    text = re.sub(r"([A-Za-z0-9._（）@\-]+)(?:'s|’s)\s+", r"\1 的 ", text)
    text = re.sub(r"）\s+的\s+", "）的 ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip(" ;；，,。")


def translate_common_templates(text):
    compact = normalize_clause(text)

    senate_cbdc_pattern = re.match(
        r"(?i)(?:just in:\s*)?(?:🇺🇸\s*)?(?:u\.?s\.?\s+)?senate\s+votes\s+to\s+include\s+(?:a\s+)?(?:ban\s+on|banning)\s+(?:federal\s+reserve|fed)\s+central\s+bank\s+digital\s+currency\s+in\s+(?:a\s+)?bipartisan\s+housing\s+bill\.?$",
        compact,
    )
    if senate_cbdc_pattern:
        return "美国参议院投票支持在两党住房法案中加入禁止美联储发行 CBDC 的条款。"

    bitcoin_reclaim_pattern = re.match(
        r"(?i)(?:just in:\s*)?(?:🇺🇸\s*)?bitcoin\s+reclaims?\s+\$?(?P<price>[\d,]+(?:\.\d+)?)\.?$",
        compact,
    )
    if bitcoin_reclaim_pattern:
        price = bitcoin_reclaim_pattern.group("price")
        return f"比特币重新站上 {price} 美元。"

    crosschain_bridge_pattern = re.match(
        r"(?is)(?:crosschain|cross-chain)\s+payments?\s+should\s+feel\s+native\.\s+with\s+(?P<kit>[A-Za-z0-9 ._\-]+),\s+developers\s+can\s+move\s+(?P<asset>\$?[A-Za-z0-9]+)\s+from\s+(?P<src>[A-Za-z0-9._@\-]+)\s+to\s+(?P<dst>[A-Za-z0-9._@\-]+)\s+in\s+a\s+single\s+(?P<call>[A-Za-z0-9_().]+)\s+call\s+so\s+builders\s+can\s+focus\s+on\s+shipping\..*$",
        compact,
    )
    if crosschain_bridge_pattern:
        kit = prettify_entity(crosschain_bridge_pattern.group("kit"))
        asset = crosschain_bridge_pattern.group("asset").lstrip("$")
        src = prettify_entity(crosschain_bridge_pattern.group("src"))
        dst = prettify_entity(crosschain_bridge_pattern.group("dst"))
        call = crosschain_bridge_pattern.group("call")
        return f"{kit} 支持开发者通过一次 {call} 调用，把 {asset} 从 {src} 转到 {dst}，让跨链支付更接近原生体验。"

    claw_network_pattern = re.match(
        r"(?is)early\s+v\.?1\s+alpha\s+skill\s+to\s+connect\s+your\s+claw\s+to\s+send\s+a\s+message\s+and\s+find\s+other\s+agents\s+on\s+an\s+open\s+secure\s+network\.\s+please\s+give\s+us\s+feedback!?$",
        compact,
    )
    if claw_network_pattern:
        return "推出早期 v1 alpha skill，可让 Claw 在开放且安全的网络上发送消息并发现其他 agents，欢迎反馈。"

    bill_autofill_pattern = re.match(
        r"(?is)the\s+most\s+tedious\s+part\s+of\s+paying\s+a\s+bill\s+is(?:\s+not|n't)\s+the\s+payment\.\s+it'?s\s+everything\s+before\s+it\.\s+upload\s+or\s+forward\s+a\s+bill\s+to\s+(?P<product>[A-Za-z0-9._@\-]+)\.\s+ai\s+reads\s+it\s+and\s+prefills\s+every\s+detail\..*$",
        compact,
    )
    if bill_autofill_pattern:
        product = prettify_entity(bill_autofill_pattern.group("product"))
        return f"支付账单最麻烦的不是付款本身，而是前置准备；把账单上传或转发给 {product} 后，AI 会读取内容并预填所有细节。"

    trade_kit_pattern = re.match(
        r"(?is)your\s+trading\s+strategy\s+doesn'?t\s+need\s+a\s+day\s+off\.\s+agent\s+trade\s+kit[；;,.\s]+(?P<tools>\d+)\s+tools\.\s+24\s*/\s*7\s+execution\.\s+no\s+vacation\s+days\.?$",
        compact,
    )
    if trade_kit_pattern:
        tools = trade_kit_pattern.group("tools")
        return f"Agent Trade Kit 提供 {tools} 个工具，支持 24/7 执行，主打让交易策略不用休息。"

    trump_rates_pattern = re.match(
        r"(?i)(?:just in:\s*)?(?:🇺🇸\s*)?president\s+trump\s+says\s+(?:federal\s+reserve|fed)\s+chair\s+jerome\s+powell\s+should\s+lower\s+interest\s+rates\s+'?immediately'?(?:\s+without\s+waiting\s+for\s+the\s+next\s+fomc\s+meeting)?\.?$",
        compact,
    )
    if trump_rates_pattern:
        return "特朗普表示，美联储主席鲍威尔应立即降息，无需等到下次 FOMC 会议。"

    buy_pattern = re.match(
        r"(?i)(?:it seems that\s+)?(?P<buyer>.+?)\s+bought another\s+(?P<amount>[\d,]+(?:\.\d+)?)\s+(?P<asset>\$?[A-Za-z0-9]+)\s*\((?P<value>\$?[\d,]+(?:\.\d+)?[KMB]?)\)\s+via\s+(?P<venue>#?[A-Za-z0-9_]+)\s+(?P<time>\d+\s+(?:minutes?|hours?|days?|weeks?|months?))\s+ago\.?$",
        compact,
    )
    if buy_pattern:
        buyer = prettify_entity(buy_pattern.group("buyer"))
        amount = buy_pattern.group("amount")
        asset = buy_pattern.group("asset").lstrip("$")
        venue = prettify_entity(buy_pattern.group("venue"))
        relative_time = translate_relative_time(buy_pattern.group("time"))
        value = translate_money(buy_pattern.group("value"))
        return f"{buyer} {relative_time}前似乎又通过 {venue} 买入 {amount} 枚 {asset}，金额约 {value}。"

    sell_pattern = re.match(
        r"(?i)(?:it seems that\s+)?(?P<seller>.+?)\s+sold\s+(?P<amount>[\d,]+(?:\.\d+)?)\s+(?P<asset>\$?[A-Za-z0-9]+)\s*\((?P<value>\$?[\d,]+(?:\.\d+)?[KMB]?)\)\s+(?:via\s+(?P<venue>#?[A-Za-z0-9_]+)\s+)?(?P<time>\d+\s+(?:minutes?|hours?|days?|weeks?|months?))\s+ago\.?$",
        compact,
    )
    if sell_pattern:
        seller = prettify_entity(sell_pattern.group("seller"))
        amount = sell_pattern.group("amount")
        asset = sell_pattern.group("asset").lstrip("$")
        relative_time = translate_relative_time(sell_pattern.group("time"))
        value = translate_money(sell_pattern.group("value"))
        venue = sell_pattern.group("venue")
        venue_part = f"通过 {prettify_entity(venue)} " if venue else ""
        return f"{seller} {relative_time}前{venue_part}卖出 {amount} 枚 {asset}，金额约 {value}。"

    return None


def strip_analysis_tail(text):
    cleaned = text
    for pattern in ANALYSIS_TAIL_PATTERNS:
        cleaned = re.sub(pattern, "", cleaned)
    cleaned = re.sub(r"[，,；;]\s*$", "", cleaned).strip()

    clauses = []
    for clause in re.split(r"[；;]|(?<=[。！？!?])\s*", cleaned):
        normalized = normalize_clause(clause)
        if not normalized:
            continue
        clauses.append(normalized)
    return "；".join(clauses) if clauses else normalize_clause(cleaned)


def summarize(tweet, tags):
    text = strip_prefix_noise(clean(tweet.get("text", "")))
    if not text:
        return "信息量不足。"

    english_heavy = tweet.get("lang") not in ("zh", "zh-cn", "zh-tw") and not is_chinese_dominant(text)
    if english_heavy:
        translated = translate_common_templates(text)
        working = translated or apply_phrase_replacements(text)
    else:
        working = text

    working = strip_analysis_tail(working)
    working = re.sub(r"\s*\n\s*", "；", working)
    working = re.sub(r"\s*•\s*", "；", working)
    working = re.sub(r"\s+", " ", working)

    raw_clauses = re.split(r"[；;]|(?<=[。！？!?])\s+", working)
    clauses = []
    seen = set()
    for clause in raw_clauses:
        normalized = normalize_clause(clause)
        if not normalized:
            continue
        signature = normalized.lower()
        if signature in seen:
            continue
        seen.add(signature)
        clauses.append(normalized)

    if not clauses:
        clauses = [normalize_clause(working)]

    picked = []
    for clause in clauses:
        picked.append(clause)
        joined = "；".join(picked)
        if len(joined) >= 120 or len(picked) >= 3:
            break

    summary = strip_analysis_tail("；".join(picked).strip())
    if not summary:
        summary = strip_analysis_tail(text)

    if not re.search(r"[。！？!?]$", summary):
        summary += "。"
    return smart_truncate(summary)


def to_bj_parts(created_at_iso):
    dt = datetime.fromisoformat(created_at_iso).astimezone(BJ)
    return dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M:%S")


def decorate_tweet(alias, tweet):
    tags = classify(tweet.get("text", ""))
    if not tags:
        return None
    score = score_tweet(tweet, tags)
    if score < MIN_SCORE:
        return None
    summary = summarize(tweet, tags)
    if tweet.get("lang") not in ("zh", "zh-cn", "zh-tw") and has_excess_english(summary):
        return None
    bj_date, bj_time = to_bj_parts(tweet["created_at"])
    decorated = dict(tweet)
    decorated.update({
        "alias": alias,
        "tags": tags,
        "score": score,
        "summary": summary,
        "bj_date": bj_date,
        "bj_time": bj_time,
        "signature": normalize_for_similarity(tweet.get("text", "")),
    })
    return decorated


def prefer_candidate(candidate, existing):
    if existing is None:
        return True
    left = (LISTS[candidate["alias"]]["weight"], candidate["score"], len(candidate["tags"]), candidate["created_at"], candidate["alias"])
    right = (LISTS[existing["alias"]]["weight"], existing["score"], len(existing["tags"]), existing["created_at"], existing["alias"])
    return left > right


def select_alias_tweets(alias, tweets):
    ranked = sorted(
        tweets,
        key=lambda x: (x["score"], LISTS[x["alias"]]["weight"], x["created_at"], x["tweet_id"]),
        reverse=True,
    )
    limit = 5 if alias == "星" else 3
    selected = []
    seen_signatures = set()
    for tweet in ranked:
        signature = tweet.get("signature") or tweet["tweet_id"]
        if signature in seen_signatures:
            continue
        seen_signatures.add(signature)
        selected.append(tweet)
        if len(selected) >= limit:
            break
    return selected


def build_groups(data):
    best_by_tweet_id = {}
    for alias in LISTS:
        payload = data.get("aliases", {}).get(alias, {})
        for tweet in payload.get("tweets", []):
            decorated = decorate_tweet(alias, tweet)
            if not decorated:
                continue
            current = best_by_tweet_id.get(decorated["tweet_id"])
            if prefer_candidate(decorated, current):
                best_by_tweet_id[decorated["tweet_id"]] = decorated

    groups = defaultdict(lambda: {"aliases": defaultdict(list)})
    for tweet in best_by_tweet_id.values():
        groups[tweet["bj_date"]]["aliases"][tweet["alias"]].append(tweet)
    return groups


def unique_tags(tweets):
    tags = []
    for tweet in tweets:
        for tag in tweet["tags"]:
            if tag not in tags:
                tags.append(tag)
    return tags


def user_label(tweet):
    handle = tweet.get("author") or "unknown"
    name = clean(tweet.get("author_name", ""))
    if name and name.lower() != handle.lower():
        return f"{name} (@{handle})"
    return f"@{handle}"


def strip_terminal_punct(text):
    return text.rstrip("。；，,;:！？!? ")


def build_global_summary(selected_by_alias, all_selected):
    alias_count = len(selected_by_alias)
    total_count = len(all_selected)

    tag_counts = defaultdict(int)
    alias_tag_counts = defaultdict(set)
    for tweet in all_selected:
        for tag in tweet["tags"]:
            tag_counts[tag] += 1
            alias_tag_counts[tag].add(tweet["alias"])

    ranked_tags = [tag for tag, _ in sorted(tag_counts.items(), key=lambda item: (item[1], TAG_BONUS.get(item[0], 0)), reverse=True)]
    label_map = {
        "airdrop": "空投/积分",
        "trading": "交易",
        "macro": "宏观",
        "defi": "DeFi/链上",
        "ai": "AI",
        "btc": "BTC/ETH",
    }

    summary_lines = []
    if ranked_tags:
        top_labels = [label_map[tag] for tag in ranked_tags[:3]]
        summary_lines.append(f"这批内容主要集中在{'、'.join(top_labels)}，本次共整理 {total_count} 条高信号内容，覆盖 {alias_count} 个列表。")

    market_parts = []
    if "btc" in tag_counts:
        market_parts.append("BTC/ETH 反弹与风险偏好回升是最强主线")
    if "macro" in tag_counts:
        market_parts.append("宏观侧围绕油价、政策与流动性预期继续驱动市场情绪")
    if "trading" in tag_counts:
        market_parts.append("交易讨论明显偏向顺势和短线节奏")
    if market_parts:
        summary_lines.append("；".join(market_parts) + "。")

    opportunity_parts = []
    if "airdrop" in tag_counts:
        opportunity_parts.append("空投/积分仍有可跟进线索")
    if "defi" in tag_counts:
        opportunity_parts.append("链上资金流和协议数据值得继续跟")
    if "ai" in tag_counts:
        opportunity_parts.append("AI 相关内容有增量但整体不如交易与宏观强")
    if opportunity_parts:
        summary_lines.append("机会侧：" + "；".join(opportunity_parts) + "。")

    return summary_lines[:3]


def alias_section(alias, tweets):
    lines = [f"## {alias}", "", "### Alpha 提取"]
    for tweet in select_alias_tweets(alias, tweets):
        lines += [
            f"- {tweet['summary']}",
            f"  - 标签：{' '.join('#' + tag for tag in tweet['tags'])}",
            f"  - 用户：{user_label(tweet)}",
            f"  - 链接：{tweet['link']}",
        ]
    lines.append("")
    return lines


def write_window_file(date_key, group):
    selected_by_alias = {}
    for alias in LISTS:
        tweets = group["aliases"].get(alias, [])
        selected = select_alias_tweets(alias, tweets)
        if selected:
            selected_by_alias[alias] = selected

    aliases_present = list(selected_by_alias.keys())
    if not aliases_present:
        return None, []

    all_selected = [tweet for tweets in selected_by_alias.values() for tweet in tweets]
    start = min(tweet["bj_time"] for tweet in all_selected)
    end = max(tweet["bj_time"] for tweet in all_selected)
    body = [
        "---",
        f"date: {date_key}",
        f"window: {start}~{end}",
        "timezone: Asia/Shanghai",
        "aliases:",
    ]
    for alias in aliases_present:
        body.append(f"  - {alias}")
    body += ["---", "", f"# 列表推文汇总｜{date_key}｜{start}~{end}", "", "## 全部列表总结"]
    for line in build_global_summary(selected_by_alias, all_selected):
        body.append(f"- {line}")
    for alias in aliases_present:
        body += [""] + alias_section(alias, group["aliases"][alias])

    out_dir = DATA_DIR / date_key
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{start}~{end}.md"
    out_path.write_text("\n".join(body).rstrip() + "\n")
    return out_path, unique_tags(all_selected)


def git_commit_push(paths):
    repo = BASE_DIR.parents[1]
    rels = [str(Path(path).relative_to(repo)) for path in paths]
    subprocess.check_call(["git", "-C", str(repo), "add", *rels])
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    subprocess.check_call(["git", "-C", str(repo), "commit", "-m", f"Update X list digests ({stamp})"])
    subprocess.check_call(["git", "-C", str(repo), "push"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--alias")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--commit", action="store_true")
    ap.add_argument("--bootstrap", action="store_true")
    args = ap.parse_args()

    data = run_fetch(alias=args.alias, all_aliases=args.all, bootstrap=args.bootstrap)
    groups = build_groups(data)
    generated = []
    summary = {"errors": data.get("errors", {})}

    for date_key, group in sorted(groups.items()):
        out_path, tags = write_window_file(date_key, group)
        if out_path:
            generated.append(out_path)
            summary[date_key] = {
                "file": str(out_path),
                "aliases": [alias for alias in LISTS if alias in group["aliases"] and group["aliases"][alias]],
                "tags": tags,
                "window": out_path.stem,
            }

    if args.commit and generated:
        generated.append(DATA_DIR / "state.json")
        git_commit_push(generated)

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
