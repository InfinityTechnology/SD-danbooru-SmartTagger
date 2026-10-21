"""WD14 打标引擎 —— QThread 后台工作器，支持 CPU / DirectML / CUDA"""
import csv
import time
from pathlib import Path

import numpy as np
from PySide6.QtCore import QThread, Signal

from .filters import build_judge

IMAGE_SIZE = 448
IMG_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tiff"}

# 默认模型缓存目录（软件根目录下）
MODEL_REPO = "SmilingWolf/wd-vit-tagger-v3"
MODEL_FILES = ["model.onnx", "selected_tags.csv"]


def load_tags(csv_path: Path):
    tags = []
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        for row in csv.reader(f):
            if len(row) < 3:
                continue
            if row[0].strip().lower() in ("tag_id", "name"):
                continue
            if len(row) >= 4 and row[0].strip().isdigit():
                name, cat_s, cnt_s = row[1], row[2], row[3]
            else:
                name, cat_s, cnt_s = row[0], row[1], row[2] if len(row) > 2 else "0"
            try:
                cat = int(cat_s)
            except ValueError:
                continue
            tags.append((name, cat, int(cnt_s) if cnt_s.strip().isdigit() else 0))
    return tags


def preprocess(pil_img, size=IMAGE_SIZE):
    from PIL import Image
    arr = np.array(pil_img.convert("RGB"))[:, :, ::-1]
    h, w = arr.shape[:2]
    s = max(h, w)
    arr = np.pad(arr, (((s - h) // 2, s - h - (s - h) // 2), ((s - w) // 2, s - w - (s - w) // 2), (0, 0)),
                 mode="constant", constant_values=255)
    if s != size:
        arr = np.array(Image.fromarray(arr).resize((size, size), Image.LANCZOS))
    return arr.astype(np.float32)


class TaggerWorker(QThread):
    progress = Signal(int, int)          # done, total
    log = Signal(str)
    finished_ok = Signal(int, float)     # done, elapsed
    failed = Signal(str)

    def __init__(self, input_dir, out_dir, model_dir, opts):
        super().__init__()
        self.input_dir = Path(input_dir)
        self.out_dir = Path(out_dir) if out_dir else None   # None = 写回源目录
        self.model_dir = Path(model_dir)
        self.opts = opts
        self._stop = False

    def stop(self):
        self._stop = True

    def _pick_provider(self):
        import onnxruntime as ort
        prefer = self.opts.get("provider", "auto")
        avail = ort.get_available_providers()
        order = {
            "auto":    ["DmlExecutionProvider", "CUDAExecutionProvider", "CPUExecutionProvider"],
            "dml":     ["DmlExecutionProvider", "CPUExecutionProvider"],
            "cuda":    ["CUDAExecutionProvider", "CPUExecutionProvider"],
            "cpu":     ["CPUExecutionProvider"],
        }.get(prefer, avail)
        for p in order:
            if p in avail:
                return [p, "CPUExecutionProvider"]
        return ["CPUExecutionProvider"]

    def run(self):
        try:
            self._run()
        except Exception as e:
            self.failed.emit(str(e))

    def _run(self):
        from PIL import Image
        import onnxruntime as ort

        opts = self.opts
        onnx_path = self.model_dir / "model.onnx"
        csv_path = self.model_dir / "selected_tags.csv"
        if not onnx_path.exists() or not csv_path.exists():
            self.failed.emit(f"模型文件缺失：{self.model_dir}（请先在「环境与依赖」页下载模型）")
            return

        out_root = self.out_dir or self.input_dir
        files = sorted(p for p in self.input_dir.glob("*") if p.suffix.lower() in IMG_EXTS and p.is_file())
        total0 = len(files)
        if opts.get("skip_existing", True):
            before = len(files)
            files = [p for p in files if not (out_root / p.stem).with_suffix("." + opts.get("ext", "txt")).exists()]
            self.log.emit(f"跳过已打标 {before - len(files)} 张，剩余 {len(files)} 张")
        if not files:
            self.log.emit("没有需要处理的图片。")
            self.finished_ok.emit(0, 0.0)
            return

        tags = load_tags(csv_path)
        judge = build_judge(opts)
        providers = self._pick_provider()
        self.log.emit(f"推理后端: {providers[0]}")
        sess = ort.InferenceSession(str(onnx_path), providers=providers)
        input_name = sess.get_inputs()[0].name

        def split_block(s):
            return [x.strip() for x in (s or "").split(",") if x.strip()]

        prefix = split_block(opts.get("prefix_tags"))
        fixed = split_block(opts.get("fixed_tags"))
        suffix = split_block(opts.get("suffix_tags"))
        trigger = opts.get("trigger", "").strip()
        fixed_norm = {n.lower().replace("_", " ") for n in prefix + fixed + suffix + ([trigger] if trigger else [])}

        g_t, g_c, c_t, m_t, r_t = (opts.get("general_threshold", 0.35), opts.get("thresh", 0.35),
                                   opts.get("character_threshold", 0.85), opts.get("meta_threshold", 0.35), 0.35)
        bs = opts.get("batch_size", 8)
        ext = "." + opts.get("ext", "txt").lstrip(".")
        t0, done = time.time(), 0

        for i in range(0, len(files), bs):
            if self._stop:
                self.log.emit("[STOP] 用户中止")
                break
            batch, valid = [], []
            for p in files[i:i + bs]:
                try:
                    with Image.open(p) as im:
                        im.load()
                    batch.append(preprocess(Image.open(p)))
                    valid.append(p)
                except Exception as e:
                    self.log.emit(f"[WARN] 跳过损坏图片 {p.name}: {e}")
            if not batch:
                continue
            probs = sess.run(None, {input_name: np.stack(batch)})[0]

            for p, row in zip(valid, probs):
                labels, dropped = [], []
                for idx, (name, cat, cnt) in enumerate(tags):
                    prob = float(row[idx])
                    if cat == 0 and prob < g_t: continue
                    if cat in (1, 2, 3) and prob < c_t: continue
                    if cat == 4 and prob < m_t: continue
                    if cat == 9 and prob < r_t: continue
                    if prob < opts.get("thresh", 0.35): continue
                    ok, _ = judge(name, cat, cnt)
                    if ok:
                        labels.append(name)
                    else:
                        dropped.append(name)
                labels = [n.replace("_", " ") for n in labels]
                labels = [n for n in labels if n.lower() not in fixed_norm]
                final = prefix + ([trigger] if trigger else []) + fixed + labels + suffix
                out_path = (self.out_dir / p.name if self.out_dir else p).with_suffix(ext)
                out_path.write_text(", ".join(final), encoding="utf-8")
                done += 1
                if done % 20 == 0 or done == len(files):
                    el = time.time() - t0
                    self.progress.emit(done, len(files))
                    self.log.emit(f"[INFO] {done}/{len(files)}  {el:.0f}s  剩余 {el/max(done,1)*(len(files)-done):.0f}s")
        self.finished_ok.emit(done, time.time() - t0)
