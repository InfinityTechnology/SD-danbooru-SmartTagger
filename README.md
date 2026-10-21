# SmartTagger · 智能打标工具

面向 Stable Diffusion / Anima 等底模的 **LoRA 数据集打标与清洗工具**。基于 WD14 Tagger 本地推理，配合社区共识的算法过滤清单，把「数据集准备」这件事从命令行搬进图形界面。

- **跨平台 GPU**：Windows 上通过 `onnxruntime-directml` 一套包通吃 NVIDIA / AMD / Intel，**核显也能跑**
- **零 API 成本**：默认全程本地推理，不调用任何云端接口
- **无黑窗**：纯 GUI 应用，安装与运行日志全部内嵌在界面里
- **中英双语 + 浅色/深色主题**：右上角一键切换，选择自动记住，深夜炼丹不刺眼
- **贴合 Anima 规范**：标签小写、空格代下划线；不滥盖质量/分数标签

> 已在真实项目验证：罗小黑 Character LoRA（2386 张）、雷古 Character LoRA（1734 张）。

---

## 功能

| 模块 | 说明 |
|---|---|
| **环境与依赖** | 启动时自动检测 GPU / Python / 依赖包 / 模型缓存；缺失项一键安装，安装位置可指定；模型一键下载（约 400MB，之后完全离线） |
| **数据集打标** | WD14 批量推理；扫描到已有标签文件时弹窗询问「跳过只打未标」或「覆盖重制」；触发词、阈值、固定前后缀、过滤规则全部可配 |
| **数据集清洗** | 纯文本算法，秒级处理（不跑推理、零显存）；图片与 txt 数量不匹配时先弹窗确认，取消则不做任何改动 |
| **API 接入（备选）** | 兼容 OpenAI Chat Completions 格式；不填 API Key 时功能完全关闭，不产生任何调用 |
| **内嵌文件浏览器** | 缩略图网格，绿色角标标识「已打标 / 待打标」，后台线程加载不卡界面 |
| **双语与主题** | 中文 / English 与浅色 / 深色主题即时切换（含弹窗与调色板），选择持久化 |
| **进度与日志** | 实时进度条 + 预计剩余时间；所有输出进右侧固定日志栏 |

## 快速开始

### 方式一：直接运行打包好的 exe

1. 到 Releases 下载 `SmartTagger-v1.0-win64.zip`
2. 解压后双击 `SmartTagger.exe`（首次启动需解压临时文件，约 5–10 秒）
3. 首次使用在「环境与依赖」页点「下载模型」，之后完全离线

> `models/` 需与 exe 同级目录。不带模型也能运行，程序会提示下载。

### 方式二：源码运行

```bash
git clone https://github.com/<your-name>/SmartTagger.git
cd SmartTagger
pip install -r requirements.txt
python main.py
```

Python ≥ 3.10。Windows 装 `onnxruntime-directml`（N/A/I 全支持），其他平台装 `onnxruntime`。

## 三分钟上手

1. **环境与依赖** —— 打开就看检测结果，缺什么点「一键安装缺失依赖」，模型点「下载模型」，装完点「刷新检测」
2. **数据集打标** —— 选目标文件夹 → 填触发词 → 点「开始打标」
3. **数据集清洗** —— 选目录 → 勾选过滤规则 → 点「开始清洗」；导出留空则原地覆盖

完整图文步骤见 [使用教程](docs/使用教程.md)。

## 打标参数速查

| 参数 | 默认 | 说明 |
|---|---|---|
| 触发词 | 空 | 写在每个 caption 最前；建议带数字避免与底模已有概念冲突，如 `wodelora1919810` |
| 固定前缀 | 空 | 逗号分隔，如 `1boy, solo`；留空则不加 |
| 通用阈值 | 0.35 | general 类标签置信度门槛 |
| 角色阈值 | 0.85 | 角色/画师/版权类门槛，调高避免误判角色名 |
| 低频阈值 | 500 | Danbooru 出现次数低于此值的长尾标签丢弃（底模大概率不认识） |
| 通配删背景 | 开 | 删除所有 `*background` 标签，避免触发词把背景一起带出来 |
| 跳过已打标 | 开 | 只处理没有 txt 的图片；取消勾选则全部重制覆盖 |

## 内置过滤清单

清洗与打标共用同一套规则（`core/filters.py`）：

- **背景类**：通配删除 `*background`
- **rating**：general / sensitive / questionable / explicit
- **画师 / 版权 / 角色名**：避免画风污染与误判污染
- **源噪声**：watermark、signature、jpeg artifacts、各类 text、scan、lowres…
- **质量与分数**：masterpiece、best quality、highres、score_1~10（未评分数据集不该被盖章）
- **变体标记**：parody、alternate costume / hairstyle、virtual youtuber…
- **低频长尾**：按 Danbooru 出现次数过滤

角色核心特征（发色、瞳色、兽耳、机械肢体等）在白名单中，任何规则都不会误删。

## 目录结构

```
SmartTagger/
├─ main.py            # 入口 + 主窗口（侧边导航 + 多页切换 + 主题/语言切换）
├─ i18n.py            # 中英双语字符串表 + tr() 取词
├─ theme.py           # Corporate Clean QSS（浅色 + 深色）
├─ widgets.py         # 卡片 / 日志面板 / 缩略图网格 / 滚动页面基类
├─ core/
│  ├─ filters.py      # 社区共识过滤清单 + 白名单
│  ├─ tagger.py       # WD14 打标引擎（QThread）
│  ├─ cleaner.py      # 清洗引擎（QThread）
│  └─ detector.py     # 环境 / 依赖 / 模型检测与安装
├─ pages/             # 四个功能页
└─ docs/              # 使用教程（中文 / English）
```

## 技术栈

PySide6（Qt 6） · onnxruntime-directml · SmilingWolf/wd-vit-tagger-v3 · Pillow / NumPy

## 常见问题

**核显能跑吗？** 能。DirectML 走 DX12，Intel / AMD 核显可用，只是比独显慢，2000 张量级建议夜间跑。

**为什么标签是空格不是下划线？** Anima 等底模官方规范：标签小写、空格代下划线，只有 `score_*` 保留下划线。

**打标要多久？** CPU 单张约 0.3 秒（448px）。2386 张约 12 分钟；开 DirectML 后显著更快。

**能处理子目录吗？** 当前版本处理目标目录下的一层图片，不递归子目录。

## 许可

MIT License。WD14 模型权重遵循 SmilingWolf 仓库的许可条款。
