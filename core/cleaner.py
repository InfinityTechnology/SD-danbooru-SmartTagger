"""数据集清洗引擎 —— 纯文本算法，不跑推理，秒级"""
import csv
import time
from collections import Counter
from pathlib import Path

from PySide6.QtCore import QThread, Signal

from .filters import build_judge

IMG_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tiff"}


def load_category_map(csv_path: Path):
    """从模型标签表读 category 与 count；模型不存在则返回空映射（按 general 处理）"""
    cat_map, cnt_map = {}, {}
    if not csv_path.exists():
        return cat_map, cnt_map
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        for row in csv.reader(f):
            if len(row) < 3 or row[0].strip().lower() in ("tag_id", "name"):
                continue
            if len(row) >= 4 and row[0].strip().isdigit():
                name, cat_s, cnt_s = row[1], row[2], row[3]
            else:
                name, cat_s, cnt_s = row[0], row[1], row[2] if len(row) > 2 else "0"
            try:
                cat_map[name] = int(cat_s)
            except ValueError:
                continue
            cnt_map[name] = int(cnt_s) if cnt_s.strip().isdigit() else 0
    return cat_map, cnt_map


class CleanWorker(QThread):
    progress = Signal(int, int)
    log = Signal(str)
    finished_ok = Signal(int, int, float)   # files, removed_tags, elapsed
    failed = Signal(str)

    def __init__(self, input_dir, out_dir, model_dir, opts):
        super().__init__()
        self.input_dir = Path(input_dir)
        self.out_dir = Path(out_dir) if out_dir else None   # None = 原地覆盖
        self.model_dir = Path(model_dir)
        self.opts = opts
        self._stop = False

    def stop(self):
        self._stop = True

    def run(self):
        try:
            self._run()
        except Exception as e:
            self.failed.emit(str(e))

    def _run(self):
        opts = self.opts
        cat_map, cnt_map = load_category_map(self.model_dir / "selected_tags.csv")
        judge = build_judge(opts)
        txts = sorted(self.input_dir.glob("*.txt"))
        if not txts:
            self.failed.emit("目标目录下没有找到 .txt 标签文件。")
            return
        out_root = self.out_dir or self.input_dir
        out_root.mkdir(parents=True, exist_ok=True)
        removed = Counter()
        t0, done = time.time(), 0
        for f in txts:
            if self._stop:
                self.log.emit("[STOP] 用户中止")
                break
            raw = f.read_text(encoding="utf-8")
            tags = [t.strip() for t in raw.split(",") if t.strip()]
            if not tags:
                continue
            kept = []
            for t in tags:
                # 还原 Danbooru 原始形式去查 category/count
                probe = t.lower().replace(" ", "_")
                cat = cat_map.get(probe, cat_map.get(t, 0))
                cnt = cnt_map.get(probe, cnt_map.get(t, 0))
                ok, reason = judge(probe, cat, cnt)
                if ok:
                    kept.append(t)
                else:
                    removed[f"{t} [{reason}]"] += 1
            # 触发词等固定前缀不重排，只按原顺序保留
            out_path = (out_root / f.name) if self.out_dir else f
            out_path.write_text(", ".join(kept), encoding="utf-8")
            done += 1
            if done % 200 == 0 or done == len(txts):
                self.progress.emit(done, len(txts))
                self.log.emit(f"[INFO] 清洗 {done}/{len(txts)}")
        top = "\n".join(f"  {t} ×{c}" for t, c in removed.most_common(15))
        self.log.emit(f"[DONE] 清洗完成：{done} 个文件，移除标签 {sum(removed.values())} 次\n{top}")
        self.finished_ok.emit(done, sum(removed.values()), time.time() - t0)
