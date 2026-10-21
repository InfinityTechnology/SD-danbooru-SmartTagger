"""轻量 i18n：中 / 英双语切换
页面实现 retranslate_ui()，语言切换时由主窗口统一调用刷新。
"""
from PySide6.QtCore import QObject, Signal

_current = "zh"

STRINGS = {
    # ---- 通用 ----
    "app_name":      {"zh": "智能打标工具", "en": "SmartTagger"},
    "local_hint":    {"zh": "本地推理 · 零 API 成本", "en": "Local inference · zero API cost"},
    "lang_switch":   {"zh": "EN", "en": "中文"},
    "theme_to_dark": {"zh": "🌙 深色", "en": "🌙 Dark"},
    "theme_to_light":{"zh": "☀ 浅色", "en": "☀ Light"},
    "browse":        {"zh": "浏览", "en": "Browse"},
    "refresh":       {"zh": "刷新检测", "en": "Refresh"},
    "open_export":   {"zh": "打开导出目录", "en": "Open output folder"},
    "log_title":     {"zh": "运行日志", "en": "Console"},
    "log_hint":      {"zh": "所有输出内嵌在此，不弹出独立控制台窗口。",
                      "en": "All output is embedded here — no separate console window."},
    "no_dir":        {"zh": "未选择目录", "en": "No folder selected"},
    "msg_valid_dir": {"zh": "请先选择有效的目标文件夹", "en": "Please select a valid target folder"},
    "msg_stopped":   {"zh": "用户取消，未做任何处理", "en": "Cancelled — nothing was changed"},
    "select_folder": {"zh": "选择文件夹", "en": "Select folder"},
    "select_install":{"zh": "选择安装位置", "en": "Select install location"},

    # ---- 导航 ----
    "nav_env":       {"zh": "环境与依赖", "en": "Environment"},
    "nav_tag":       {"zh": "数据集打标", "en": "Tag Dataset"},
    "nav_clean":     {"zh": "数据集清洗", "en": "Clean Dataset"},
    "nav_api":       {"zh": "API 接入", "en": "API"},

    # ---- 状态 ----
    "status_detect": {"zh": "检测环境中…", "en": "Detecting…"},
    "status_ready":  {"zh": "环境就绪", "en": "Ready"},
    "status_cpu":    {"zh": "GPU 不可用 · CPU 模式", "en": "No GPU · CPU mode"},
    "status_missing":{"zh": "依赖缺失 · 请一键安装", "en": "Missing deps · install"},
    "status_nomodel":{"zh": " · 模型未下载", "en": " · model missing"},

    # ---- 环境页 ----
    "env_title":     {"zh": "环境与依赖", "en": "Environment & Dependencies"},
    "env_card":      {"zh": "设备与环境检测", "en": "Device & Environment"},
    "env_card_desc": {"zh": "启动时自动检测 GPU、Python 与依赖情况；缺什么装什么，可指定安装位置。",
                      "en": "Detects GPU, Python and packages on startup; install what's missing to a folder you choose."},
    "col_item":      {"zh": "检测项", "en": "Item"},
    "col_status":    {"zh": "状态", "en": "Status"},
    "pip_ph":        {"zh": "依赖安装位置（留空 = 安装到当前 Python 环境）",
                      "en": "Install location (empty = current Python env)"},
    "btn_install":   {"zh": "一键安装缺失依赖", "en": "Install Missing"},
    "model_card":    {"zh": "WD14 模型缓存", "en": "WD14 Model Cache"},
    "model_desc":    {"zh": "本地打标引擎使用 SmilingWolf/wd-vit-tagger-v3，首次使用需下载约 400MB，之后完全离线。",
                      "en": "Uses SmilingWolf/wd-vit-tagger-v3. ~400 MB on first use, fully offline afterwards."},
    "model_dir":     {"zh": "模型目录", "en": "Model folder"},
    "btn_download":  {"zh": "下载模型", "en": "Download Model"},

    # ---- 打标页 ----
    "tag_title":     {"zh": "数据集打标", "en": "Tag Dataset"},
    "path_title":    {"zh": "路径设置", "en": "Paths"},
    "lbl_src":       {"zh": "目标文件夹", "en": "Input folder"},
    "ph_src":        {"zh": "选择要打标的图片目录", "en": "Folder with images to tag"},
    "lbl_out":       {"zh": "导出文件夹", "en": "Output folder"},
    "ph_out":        {"zh": "留空则写入目标文件夹", "en": "Empty = write into input folder"},
    "ph_out_clean":  {"zh": "留空 = 原地覆盖原有 txt", "en": "Empty = overwrite in place"},
    "ph_clean_src":  {"zh": "包含待清洗 .txt 的数据集目录", "en": "Dataset folder containing .txt files"},
    "preview_title": {"zh": "文件预览", "en": "File Preview"},
    "preview_hint":  {"zh": "绿色角标 = 已有标签文件；扫描结果实时更新。",
                      "en": "Green badge = already tagged; rescan happens live."},
    "param_title":   {"zh": "打标参数", "en": "Tagging Options"},
    "lbl_trigger":   {"zh": "触发词", "en": "Trigger word"},
    "ph_trigger":    {"zh": "为你的模型指定在日后装载使用时“召唤”它的专属提示词，为了避免和你的本底模型学习参数冲突，可加些数字。如 wodelora1919810",
                      "en": "A unique word that summons your model later. Add digits to avoid clashing with the base model's concepts, e.g. mylora1919810"},
    "lbl_general":   {"zh": "通用阈值", "en": "General thr."},
    "lbl_character": {"zh": "角色阈值", "en": "Character thr."},
    "lbl_mincount":  {"zh": "低频阈值", "en": "Min count"},
    "chk_bg":        {"zh": "通配删背景", "en": "Drop backgrounds"},
    "chk_skip":      {"zh": "跳过已打标", "en": "Skip tagged"},
    "lbl_prefix":    {"zh": "固定前缀", "en": "Fixed prefix"},
    "ph_prefix":     {"zh": "逗号分隔，如 1boy, solo；留空则不加（触发词自动置于最前）",
                      "en": "Comma separated, e.g. 1boy, solo; empty = none (trigger goes first)"},
    "progress_title":{"zh": "处理进度", "en": "Progress"},
    "btn_start_tag": {"zh": "开始打标", "en": "Start Tagging"},
    "btn_running":   {"zh": "运行中…", "en": "Running…"},
    "dlg_exist_title":{"zh": "检测到已有标签文件", "en": "Existing tag files found"},
    "dlg_exist_body": {"zh": "目标目录中已有 {n} 个 .txt 打标文件。\n\n「Yes」= 只处理未打标的图片（跳过已有的）\n「No」 = 忽略，稍后手动调整选项",
                       "en": "Found {n} existing .txt tag files.\n\n「Yes」= only process untagged images (skip existing)\n「No」= ignore, adjust options manually later"},
    "stat_imgs":     {"zh": "{n} 张图片 · {m} 个标签文件 · {k} 待打标",
                      "en": "{n} images · {m} tag files · {k} untagged"},

    # ---- 清洗页 ----
    "clean_title":   {"zh": "数据集清洗", "en": "Clean Dataset"},
    "rules_title":   {"zh": "过滤规则", "en": "Filter Rules"},
    "rules_desc":    {"zh": "按社区共识与 Anima 底模规范预置；白名单保护角色核心特征，规则之间互不冲突。",
                      "en": "Preset from community consensus and Anima conventions; a whitelist protects core character traits."},
    "btn_start_clean":{"zh": "开始清洗", "en": "Start Cleaning"},
    "dlg_mismatch_title": {"zh": "数据集数量不匹配", "en": "Dataset count mismatch"},
    "dlg_mismatch_body":  {"zh": "扫描发现标签文件数量与图片数量不一致（或文件名未成对匹配）。\n\n确认继续清洗？点「Cancel」返回自行检查数据集。",
                           "en": "Tag file count doesn't match image count (or filenames don't pair up).\n\nContinue? Click Cancel to inspect the dataset yourself."},
    "msg_no_txt":    {"zh": "目标目录下没有找到 .txt 标签文件。", "en": "No .txt tag files found in the target folder."},
    "stat_clean":    {"zh": "{n} 张图片 · {m} 个标签文件", "en": "{n} images · {m} tag files"},

    # ---- 过滤规则 ----
    "rule_background": {"zh": "通配删除 *background 背景类标签", "en": "Remove all *background tags"},
    "rule_rating":     {"zh": "删除 rating（general/sensitive/explicit）", "en": "Remove rating tags"},
    "rule_artist":     {"zh": "删除画师标签（防画风污染）", "en": "Remove artist tags (avoid style bleed)"},
    "rule_copyright":  {"zh": "删除版权/作品标签", "en": "Remove copyright/series tags"},
    "rule_character":  {"zh": "删除 WD14 判出的角色名（防误判污染）", "en": "Remove detected character names"},
    "rule_meta":       {"zh": "删除 meta 类标签（monochrome/comic 等）", "en": "Remove meta tags (monochrome/comic…)"},
    "rule_deny_exact": {"zh": "删除源噪声与质量分数标签（黑名单）", "en": "Remove source noise & quality/score tags"},
    "rule_min_count":  {"zh": "删除 Danbooru 低频长尾标签（阈值可调）", "en": "Remove low-frequency Danbooru tags"},

    # ---- API 页 ----
    "api_title":     {"zh": "API 接入", "en": "API Integration"},
    "api_card":      {"zh": "云端 AI 接入（备选功能）", "en": "Cloud AI (optional)"},
    "api_desc":      {"zh": "本地引擎已覆盖绝大多数场景且零成本；仅在需要视觉语言模型细粒度描述时才使用云端 API。\n兼容 OpenAI Chat Completions 接口格式。不填写 API Key 时此功能完全关闭，不会产生任何调用。",
                      "en": "The local engine covers most cases at zero cost — use cloud APIs only for fine-grained VLM captions.\nOpenAI Chat Completions compatible. Leaving the key empty disables the feature entirely."},
    "lbl_base":      {"zh": "API 地址", "en": "API base URL"},
    "ph_base":       {"zh": "如 https://api.openai.com/v1", "en": "e.g. https://api.openai.com/v1"},
    "lbl_key":       {"zh": "API Key", "en": "API key"},
    "ph_key":        {"zh": "sk-...（仅保存在本机，不会上传）", "en": "sk-... (stored locally, never uploaded)"},
    "lbl_model":     {"zh": "模型名称", "en": "Model name"},
    "ph_model":      {"zh": "如 qwen-vl-max / gpt-4o-mini", "en": "e.g. qwen-vl-max / gpt-4o-mini"},
    "api_test":      {"zh": "连接测试", "en": "Connection Test"},
    "btn_test":      {"zh": "测试连接", "en": "Test Connection"},
    "btn_testing":   {"zh": "测试中…", "en": "Testing…"},
    "msg_fill_all":  {"zh": "API 地址 / Key / 模型名称需全部填写才会发起测试。",
                      "en": "Fill in API URL, key and model name before testing."},
    "log_testing":   {"zh": "正在测试连接…", "en": "Testing connection…"},
    "log_busy":      {"zh": "上一次测试还在进行中", "en": "Previous test still running"},
    "api_ok":        {"zh": "连接成功", "en": "connected"},

    # ---- 提示 / 结果 ----
    "msg_tip":       {"zh": "提示", "en": "Notice"},
    "log_stopped":   {"zh": "[STOP] 用户取消，未做任何处理", "en": "[STOP] Cancelled — nothing was changed"},
    "log_done_tag":  {"zh": "[DONE] 完成 {n} 张，用时 {t:.0f}s", "en": "[DONE] {n} images in {t:.0f}s"},
    "log_done_clean":{"zh": "[DONE] 清洗 {n} 个文件，移除 {m} 个标签，用时 {t:.1f}s",
                      "en": "[DONE] Cleaned {n} files, removed {m} tags in {t:.1f}s"},
    "log_prog":      {"zh": "[INFO] {d}/{t}", "en": "[INFO] {d}/{t}"},
    "log_model_ok":  {"zh": "[DONE] 模型就绪", "en": "[DONE] Model ready"},
    "rules_default": {"zh": "规则", "en": "Rule"},
}


class I18N(QObject):
    langChanged = Signal(str)

    def __init__(self):
        super().__init__()
        self.lang = _current

    def set_lang(self, lang):
        global _current
        _current = lang
        self.lang = lang
        self.langChanged.emit(lang)


i18n = I18N()


def tr(key, **kw):
    s = STRINGS.get(key, {}).get(_current, STRINGS.get(key, {}).get("zh", key))
    return s.format(**kw) if kw else s
