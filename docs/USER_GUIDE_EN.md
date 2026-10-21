# SmartTagger User Guide

> This guide matches **v1.0**. The UI supports **Chinese / English** and **light / dark themes** — switch anytime from the top-right buttons; your choice is remembered.

## Contents

1. [Install & First Launch](#1-install--first-launch)
2. [Interface Overview](#2-interface-overview)
3. [Step 1 — Environment & Dependencies](#3-step-1--environment--dependencies)
4. [Step 2 — Tag a Dataset](#4-step-2--tag-a-dataset)
5. [Step 3 — Clean a Dataset](#5-step-3--clean-a-dataset)
6. [API Integration (Optional)](#6-api-integration-optional)
7. [Parameter Reference](#7-parameter-reference)
8. [FAQ](#8-faq)

---

## 1. Install & First Launch

### Option A: Run the packaged exe (recommended)

1. Download `SmartTagger-v1.0-win64.zip` from Releases
2. Extract to any folder (avoid non-ASCII characters in the path)
3. Double-click `SmartTagger.exe`

> First launch unpacks temp files — 5–10 seconds is normal. It's a **single-file portable app**: no registry writes, delete the folder to uninstall.

### Option B: Run from source

```bash
git clone https://github.com/<your-name>/SmartTagger.git
cd SmartTagger
pip install -r requirements.txt
python main.py
```

Python ≥ 3.10. On Windows install `onnxruntime-directml` (NVIDIA / AMD / Intel in one package); on Linux / macOS use `onnxruntime`.

---

## 2. Interface Overview

```
┌──────────────────────────────────────────────────────┐
│  logo  SmartTagger v1.0      [中文] [☀Light] [status] │  ← language / theme / env status
├──────────┬─────────────────────────────┬─────────────┤
│ Environ. │                             │   Console   │
│ Tag      │        Page content         │  (embedded, │
│ Clean    │    (scrollable, cards)      │   no cmd    │
│ API      │                             │   window)   │
└──────────┴─────────────────────────────┴─────────────┘
```

- **`EN / 中文` button (top-right)**: switch UI language instantly across all pages
- **`🌙 Dark / ☀ Light` button**: switch theme — easy on the eyes for overnight runs
- **Console (right dock)**: every detect / install / tagging log line lands here; **no separate terminal window ever opens**
- **Status chip**: green = ready with GPU acceleration (e.g. `Ready · Dml`); yellow = missing deps or CPU-only mode

---

## 3. Step 1 — Environment & Dependencies

The app opens here and runs a detection automatically.

### Reading the table

| Item | Meaning |
|---|---|
| OS / Python | Base runtime |
| GPU | Detected adapter (integrated graphics work too) |
| onnxruntime | Inference runtime, always required |
| onnxruntime-directml | Unified Windows GPU backend (NVIDIA / AMD / Intel) |
| PySide6 / huggingface_hub | UI & model-download dependencies |
| Provider | `DmlExecutionProvider` = GPU acceleration active |
| WD14 model | The tagging engine itself (~400 MB) |

### Three actions

1. **Missing packages** → click **Install Missing**. Installs into the current Python env by default; type a custom install location first if you prefer a portable folder.
2. **Model not downloaded** → check the folder under *WD14 Model Cache* and click **Download Model** (~400 MB once, **fully offline afterwards**).
3. Click **Refresh** after installing; once the chip turns green, move on.

> If the exe ships with a `models/` folder, it shows "cached" immediately.

---

## 4. Step 2 — Tag a Dataset

### 4.1 Pick folders

- **Input folder**: where your images are (png / jpg / jpeg / webp / bmp; one directory level, no recursion)
- **Output folder**: empty = txt files written next to images; set = tags collected elsewhere

Once a folder is chosen:

- The **File Preview** card shows a thumbnail grid — **green badge = already tagged**
- The status line reads `N images · M tag files · K untagged`
- If existing tag files are found, a dialog asks: **Yes = skip tagged images** (recommended for incremental datasets); No = ignore, untick *Skip tagged* later for a full redo

### 4.2 Set options

| Option | How to set |
|---|---|
| **Trigger word** | Your LoRA's unique summon word, prepended to every caption. Add digits to avoid clashing with base-model concepts, e.g. `mylora1919810` |
| **Fixed prefix** | Tags true in every image, comma separated, e.g. `1boy, solo`. Tags you write here get absorbed by the trigger — never put character traits here |
| **General threshold 0.35** | Lower = more/noisier tags, higher = leaner. Lower if clothing/actions are missing, raise if captions get dirty |
| **Character threshold 0.85** | Prevents mis-identified character names from leaking into captions; usually leave as-is |
| **Min count 500** | Tags rarer than this on Danbooru are dropped (the base model likely doesn't know them) |
| **Drop backgrounds** | Removes every `*background` tag so the trigger doesn't learn backgrounds too |
| **Skip tagged** | Only process images without a txt |

### 4.3 Run

Click **Start Tagging**. The progress bar advances live and the console streams results. On completion the log shows `[DONE] N images in Xs` and badges refresh.

**Spot-check 10–20 captions** afterwards: read the txt against the image and confirm the character's traits (hair / eyes / outfit / signature items) are present. Not happy? Adjust and rerun with *Skip tagged* unticked.

### 4.4 Output format

```
mylora1919810, 1girl, solo, black hair, long hair, green eyes, school uniform, standing, outdoors
```

- Lowercase, spaces instead of underscores (Anima base-model convention); `score_*` is the only underscore form — and it's filtered by default
- Order: trigger → fixed prefix → WD14 tags

---

## 5. Step 3 — Clean a Dataset

Cleaning is a **pure text algorithm**: finishes in seconds, no inference, no VRAM. It reads each txt, removes tags per rules, and writes back.

1. Pick the folder (empty output = overwrite in place)
2. Tick the rules (defaults follow community consensus):

| Rule | Effect |
|---|---|
| Remove `*background` | All background tags |
| Remove rating tags | general / sensitive / explicit |
| Remove artist tags | avoids style bleed |
| Remove copyright/series tags | avoids work-concept pollution |
| Remove detected character names | your character should be the trigger word, not someone else's name |
| Remove meta tags | monochrome, comic… (optional) |
| Remove source noise & quality/score tags | built-in blacklist: watermark, lowres, masterpiece, score_1~10… |
| Remove low-frequency tags | default 500, shared with the tagging page |

3. Click **Start Cleaning**. If **image count ≠ txt count** (or filenames don't pair up), a confirmation dialog appears — **Cancel** changes nothing so you can inspect the dataset first.

> **Whitelist protection**: core character traits (1girl, hair/eye colors, animal ears, mechanical limbs…) are never removed by any rule. For custom characters edit `WHITELIST` in `core/filters.py`.

---

## 6. API Integration (Optional)

The local engine covers most cases at **zero cost**. Use cloud APIs only when you need a vision-language model for fine-grained captions (complex interactions, composition narration).

- Fill in the API base URL (OpenAI Chat Completions compatible, e.g. a proxy endpoint or `https://api.openai.com/v1`), API key, and model name (e.g. `qwen-vl-max`)
- Click **Test Connection**
- **Empty key = feature fully disabled, zero calls made**; the key is stored locally only

---

## 7. Parameter Reference

### Tuning thresholds

| Symptom | Fix |
|---|---|
| Clothing / action tags missing | Lower general threshold (0.35 → 0.25) |
| Captions noisy | Raise general threshold (0.35 → 0.45) |
| Other characters' names appear | Raise character threshold; keep "Remove character names" on |
| Captions full of obscure words | Raise min count (500 → 800) |

### Tag or Clean?

- **No tags yet** → use the Tag page; filters already apply there, one pass does it
- **Have hand-refined txt files** → use the Clean page; it only deletes, never adds or rewrites your manual work

---

## 8. FAQ

**Q: Does integrated graphics work?**
Yes. DirectML runs on DX12 — Intel / AMD iGPUs supported, just slower than dGPUs. Queue large batches overnight.

**Q: Why spaces instead of underscores?**
Anima base-model convention: lowercase tags, spaces for underscores; only `score_*` keeps underscores.

**Q: I have 600 hand-refined captions — will they be overwritten?**
No. Keep *Skip tagged* ticked; only untagged images are processed. The Clean page only deletes, never rewrites.

**Q: Characters with two canonical forms (e.g. black & white hair)?**
WD14 emits `black hair` / `white hair` per image. Keep both in one dataset — each caption carries its own traits.

**Q: Subdirectories?**
Not in this version; consolidate images into one folder first.

**Q: Where are settings stored?**
Windows registry `HKEY_CURRENT_USER\Software\SmartTagger` (language / theme / paths). Delete the key to reset.

**Q: Can I add my own blacklist?**
Edit `DENY_EXACT` in `core/filters.py` (source run), or edit and repackage.

---

*For anything else, please open an Issue.*
