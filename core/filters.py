"""社区共识过滤清单 + Anima 底模规范（清洗引擎与打标引擎共用）"""

# 精确黑名单（原始 tag，下划线形式，匹配时统一 lower）
DENY_EXACT = {
    # 源噪声 / 画质缺陷
    "watermark", "signature", "artist name", "twitter username", "username", "url",
    "text", "english text", "japanese text", "chinese text", "korean text", "symbol",
    "speech bubble", "dialogue", "letterboxed", "multiple views", "out of frame",
    "scan", "scanned", "scanlines", "jpeg artifacts", "compression artifacts",
    "lowres", "thumbnail", "pixelated", "resolution mismatch", "cropped",
    "bad anatomy", "bad hands", "missing fingers", "extra digits", "fewer digits",
    "error", "faulty", "artifacts",
    # 质量 / 分数标签（Anima 官方：别给未评分数据集盖章）
    "masterpiece", "best quality", "high quality", "normal quality", "low quality",
    "worst quality", "highres", "absurdres", "incredibly absurdres",
    "ultra-detailed", "extremely detailed", "very aesthetic", "aesthetic",
    # 变体 / 二创标记（kohya colab 默认黑名单）
    "virtual youtuber", "parody", "style parody",
    "official alternate costume", "official alternate hairstyle", "official alternate hair length",
    "alternate costume", "alternate hairstyle", "alternate hair length", "alternate hair color",
    "cosplay",
}
DENY_EXACT |= {f"score_{i}" for i in range(1, 11)}

# 角色核心特征白名单：任何过滤都不许动
WHITELIST = {
    "1girl", "1boy", "1other", "solo", "no humans", "multiple girls", "multiple boys",
    "animal", "cat", "cat ears", "animal ears", "animal tail", "tail", "cat tail",
    "fur", "furry", "kemonomimi", "kemono", "whiskers", "paw", "paws", "claws",
    "black hair", "green eyes", "green hair", "child", "chibi", "young",
    # 雷古（机器人男孩）核心特征
    "robot", "mechanical arms", "mechanical legs", "android", "cyborg",
    "prosthetic arm", "mechanical parts", "palm cannon", "neck ring", "facial mark",
}

# 可勾选的过滤规则（清洗页 UI 用；第二项为 i18n key，由界面 tr() 取文案）
RULES = [
    ("background",  "rule_background", True),
    ("rating",      "rule_rating",     True),
    ("artist",      "rule_artist",     True),
    ("copyright",   "rule_copyright",  True),
    ("character",   "rule_character",  True),
    ("meta",        "rule_meta",       False),
    ("deny_exact",  "rule_deny_exact", True),
    ("min_count",   "rule_min_count",  True),
]

DEFAULT_MIN_COUNT = 500


def norm(tag: str) -> str:
    return tag.strip().lower().replace(" ", "_")


def build_judge(opts: dict):
    """根据选项生成 judge(name, category, count) -> (keep, reason)
    name 为 Danbooru 原始形式（下划线）；category: 0=general 1=artist 2=copyright
    3=character 4=meta 9=rating；count 为 Danbooru 出现次数。"""
    extra_deny = {norm(t) for t in opts.get("extra_deny", [])}

    def judge(name, category, count):
        n = norm(name)
        if norm(name) in {norm(w) for w in WHITELIST}:
            return True, ""
        if opts.get("deny_exact", True) and n in DENY_EXACT:
            return False, "黑名单"
        if n in extra_deny:
            return False, "自定义黑名单"
        if opts.get("background", True) and n.endswith("background"):
            return False, "背景类"
        if opts.get("rating", True) and category == 9:
            return False, "rating"
        if opts.get("artist", True) and category == 1:
            return False, "画师"
        if opts.get("copyright", True) and category == 2:
            return False, "版权"
        if opts.get("character", True) and category == 3:
            return False, "角色名"
        if opts.get("meta", False) and category == 4:
            return False, "meta"
        if opts.get("min_count", True) and 0 < count < opts.get("min_count_value", DEFAULT_MIN_COUNT):
            return False, f"低频<{opts.get('min_count_value', DEFAULT_MIN_COUNT)}"
        return True, ""

    return judge
