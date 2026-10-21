"""数据集清洗页：算法批量读取 txt，按共识清单过滤，不动图片不跑推理"""
from pathlib import Path

from PySide6.QtWidgets import (QCheckBox, QHBoxLayout, QLabel, QMessageBox, QPushButton,
                               QSpinBox, QVBoxLayout, QWidget)

from core.cleaner import CleanWorker
from core.filters import RULES, DEFAULT_MIN_COUNT
from i18n import tr
from widgets import Card, LogPanel, ScrollPage, path_row

IMG_EXTS = (".png", ".jpg", ".jpeg", ".webp", ".bmp")


class CleanPage(ScrollPage):
    def __init__(self, model_dir, parent=None):
        super().__init__(parent)
        lay = self.lay
        self.model_dir = model_dir
        self._worker = None
        self._mismatch = False
        self._stat = (0, 0)
        self.chk_map = {}

        self.title = QLabel(tr("clean_title"))
        self.title.setObjectName("PageTitle")
        lay.addWidget(self.title)

        self.c1 = Card(tr("path_title"))
        row1, self.in_src, self.lbl_src, self.btn_src = path_row(
            tr("lbl_src"), tr("ph_clean_src"))
        row2, self.in_out, self.lbl_out, self.btn_out = path_row(
            tr("lbl_out"), tr("ph_out_clean"))
        self.c1.add(row1)
        self.c1.add(row2)
        self.in_src.textChanged.connect(self._rescan)
        lay.addWidget(self.c1)

        self.stat = QLabel(tr("no_dir"))
        self.stat.setObjectName("CardDesc")
        lay.addWidget(self.stat)

        self.c2 = Card(tr("rules_title"), tr("rules_desc"))
        for key, i18n_key, default in RULES:
            chk = QCheckBox(tr(i18n_key))
            chk.setChecked(default)
            if key == "min_count":
                self.spin_mc = QSpinBox()
                self.spin_mc.setRange(0, 100000)
                self.spin_mc.setValue(DEFAULT_MIN_COUNT)
                self.spin_mc.setFixedWidth(120)
                h = QHBoxLayout()
                h.addWidget(chk, 1)
                h.addWidget(self.spin_mc)
                self.c2.add_layout(h)
            else:
                self.c2.add(chk)
            self.chk_map[key] = (chk, i18n_key)
        lay.addWidget(self.c2)

        acts = QHBoxLayout()
        self.btn_start = QPushButton(tr("btn_start_clean"))
        self.btn_start.setProperty("primary", True)
        self.btn_start.clicked.connect(self.start)
        acts.addWidget(self.btn_start)
        acts.addStretch(1)
        lay.addLayout(acts)
        lay.addStretch(1)

    def _rescan(self):
        folder = Path(self.in_src.text().strip())
        if not folder.is_dir():
            self.stat.setText(tr("no_dir"))
            return
        imgs = [p for p in folder.iterdir() if p.suffix.lower() in IMG_EXTS]
        txts = list(folder.glob("*.txt"))
        self._stat = (len(imgs), len(txts))
        self._mismatch = (len(imgs) != len(txts))
        self.stat.setText(tr("stat_clean", n=len(imgs), m=len(txts)))

    def _opts(self):
        o = {k: chk.isChecked() for k, (chk, _) in self.chk_map.items()}
        o["min_count_value"] = self.spin_mc.value()
        o["extra_deny"] = []
        return o

    def start(self):
        folder = self.in_src.text().strip()
        if not folder or not Path(folder).is_dir():
            QMessageBox.warning(self, tr("msg_tip"), tr("msg_valid_dir"))
            return
        if not list(Path(folder).glob("*.txt")):
            QMessageBox.information(self, tr("msg_tip"), tr("msg_no_txt"))
            return
        if self._mismatch:
            ret = QMessageBox.question(
                self, tr("dlg_mismatch_title"), tr("dlg_mismatch_body"),
                QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
            if ret != QMessageBox.Ok:
                self.log_panel.write(tr("log_stopped"))
                return
        if self._worker and self._worker.isRunning():
            return
        out = self.in_out.text().strip() or None
        self._worker = CleanWorker(folder, out, Path(self.model_dir), self._opts())
        self._worker.progress.connect(
            lambda d, t: self.log_panel.write(tr("log_prog", d=d, t=t)))
        self._worker.log.connect(self.log_panel.write)
        self._worker.failed.connect(lambda m: self.log_panel.write("[FAIL] " + m))
        self.btn_start.setText(tr("btn_running"))
        self.btn_start.setEnabled(False)

        def done(files, removed, el):
            self.btn_start.setText(tr("btn_start_clean"))
            self.btn_start.setEnabled(True)
            self.log_panel.write(tr("log_done_clean", n=files, m=removed, t=el))

        self._worker.finished_ok.connect(done)
        self._worker.start()

    def retranslate_ui(self):
        super().retranslate_ui()
        self.title.setText(tr("clean_title"))
        self.c1.set_texts(tr("path_title"))
        self.c2.set_texts(tr("rules_title"), tr("rules_desc"))
        self.lbl_src.setText(tr("lbl_src"))
        self.lbl_out.setText(tr("lbl_out"))
        self.in_src.setPlaceholderText(tr("ph_clean_src"))
        self.in_out.setPlaceholderText(tr("ph_out_clean"))
        self.btn_src.setText(tr("browse"))
        self.btn_out.setText(tr("browse"))
        for chk, i18n_key in self.chk_map.values():
            chk.setText(tr(i18n_key))
        if not (self._worker and self._worker.isRunning()):
            self.btn_start.setText(tr("btn_start_clean"))
        if self.in_src.text().strip():
            self.stat.setText(tr("stat_clean", n=self._stat[0], m=self._stat[1]))
        else:
            self.stat.setText(tr("no_dir"))
