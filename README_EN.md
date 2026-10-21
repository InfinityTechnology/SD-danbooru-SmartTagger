# SmartTagger · Intelligent Dataset Tagger

A **LoRA dataset tagging and cleaning tool** for Stable Diffusion / Anima-style base models. It runs WD14 Tagger locally and applies a community-vetted algorithmic filter list — bringing dataset preparation from the command line into a proper GUI.

- **Cross-vendor GPU**: on Windows, `onnxruntime-directml` covers NVIDIA / AMD / Intel in one package — **integrated graphics included**
- **Zero API cost**: fully local inference by default, no cloud calls
- **No console window**: a pure GUI app; installation and runtime logs are embedded in the UI
- **Bilingual + light/dark themes**: 中文 / English and light / dark, one click in the top-right; your choice is remembered
- **Anima-aware**: lowercase tags with spaces instead of underscores; no blanket quality/score stamping

> Validated on real projects: a character LoRA with 2,386 images, and another with 1,734 images.

---

## Features

| Module | Description |
|---|---|
| **Environment** | Auto-detects GPU / Python / packages / model cache on startup; one-click install of missing dependencies to a directory of your choice; one-click model download (~400 MB, fully offline afterwards) |
| **Tag Dataset** | Batch WD14 inference; when existing tag files are found, asks whether to **skip already-tagged images** or **overwrite and rebuild**; trigger word, thresholds, fixed prefix/suffix and filter rules are all configurable |
| **Clean Dataset** | Pure text algorithm — seconds to run, no inference, no VRAM; warns when the number of images and `.txt` files mismatch, and does nothing if you cancel |
| **API (optional)** | OpenAI Chat Completions compatible; completely disabled when no API key is set — no calls, no cost |
| **Built-in File Browser** | Thumbnail grid with green badges marking tagged / untagged images; loaded on a background thread so the UI never freezes |
| **Bilingual & themes** | Instant 中文 / English and light / dark switching (dialogs and palettes included), persisted across sessions |
| **Progress & Logs** | Live progress bar with ETA; all output goes to a fixed log panel on the right |

## Quick Start

### Option 1 — Packaged executable

1. Download `SmartTagger-v1.0-win64.zip` from Releases
2. Extract and double-click `SmartTagger.exe` (first launch unpacks temp files, ~5–10 s)
3. On first run, click **Download Model** on the Environment page — offline afterwards

> `models/` must sit next to the exe. It also works without it; the app will prompt you to download.

### Option 2 — Run from source

```bash
git clone https://github.com/<your-name>/SmartTagger.git
cd SmartTagger
pip install -r requirements.txt
python main.py
```

Python ≥ 3.10. On Windows install `onnxruntime-directml` (covers NVIDIA/AMD/Intel); on other platforms install `onnxruntime`.

## Three-minute walkthrough

1. **Environment** — check the detection result, click **Install Missing Dependencies** and **Download Model**, then **Refresh**
2. **Tag Dataset** — pick a folder → enter a trigger word → click **Start Tagging**
3. **Clean Dataset** — pick a folder → tick the filter rules → click **Start Cleaning**; leave export empty to overwrite in place

Full step-by-step guide: [User Guide](docs/USER_GUIDE_EN.md).

## Tagging parameters

| Parameter | Default | Note |
|---|---|---|
| Trigger word | *(empty)* | Written at the front of every caption; include digits to avoid clashing with existing concepts, e.g. `mylora1919810` |
| Fixed prefix | *(empty)* | Comma separated, e.g. `1boy, solo`; empty = none |
| General threshold | 0.35 | Confidence cut-off for general tags |
| Character threshold | 0.85 | Higher cut-off for character/artist/copyright to avoid false matches |
| Low-frequency threshold | 500 | Danbooru occurrence count below which long-tail tags are dropped |
| Drop backgrounds | On | Removes all `*background` tags so the trigger word doesn't drag a background along |
| Skip already tagged | On | Only processes images without `.txt`; uncheck to rebuild everything |

## Built-in filter list

Shared by both tagging and cleaning (`core/filters.py`):

- **Backgrounds**: wildcard removal of `*background`
- **Rating**: general / sensitive / questionable / explicit
- **Artist / copyright / character names**: prevents style bleed and misidentification
- **Source noise**: watermark, signature, jpeg artifacts, text variants, scan, lowres…
- **Quality & score**: masterpiece, best quality, highres, score_1–10 (an unscored dataset shouldn't be stamped)
- **Variant markers**: parody, alternate costume/hairstyle, virtual youtuber…
- **Long-tail**: filtered by Danbooru occurrence count

Core character traits (hair, eyes, animal ears, mechanical limbs…) are whitelisted and never removed.

## Project layout

```
SmartTagger/
├─ main.py            # Entry point + main window (sidebar, theme & language switching)
├─ i18n.py            # zh/en string table + tr() lookup
├─ theme.py           # Corporate Clean QSS (light + dark)
├─ widgets.py         # Cards / log panel / thumbnail grid / scrollable page base
├─ core/
│  ├─ filters.py      # Community filter list + whitelist
│  ├─ tagger.py       # WD14 tagging engine (QThread)
│  ├─ cleaner.py      # Cleaning engine (QThread)
│  └─ detector.py     # Environment / dependency / model detection
├─ pages/             # Four feature pages
└─ docs/              # User guides (中文 / English)
```

## Tech stack

PySide6 (Qt 6) · onnxruntime-directml · SmilingWolf/wd-vit-tagger-v3 · Pillow / NumPy

## FAQ

**Does it work on integrated graphics?** Yes. DirectML runs on DX12, so Intel/AMD iGPUs work — slower than a discrete GPU, so schedule large batches overnight.

**Why spaces instead of underscores?** Anima and similar models specify lowercase tags with spaces; only `score_*` keeps underscores.

**How long does tagging take?** Roughly 0.3 s per image on CPU at 448 px — about 12 minutes for 2,386 images; DirectML is noticeably faster.

**Does it recurse into subfolders?** The current version processes images directly inside the target folder, not subfolders.

## License

MIT License. WD14 model weights follow the license of the SmilingWolf repository.
