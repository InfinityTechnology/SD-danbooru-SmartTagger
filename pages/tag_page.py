"""数据集打标页：路径 → 扫描已有标 → 弹窗决策 → WD14 引擎 → 进度/日志"""
import os
import subprocess
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QCheckBox, QDoubleSpinBox, QHBoxLayout, QLabel, QLineEdit,
                               QMessageBox, QProgressBar, QPushButton, QSpinBox,
                               QVBoxLayout, QWidget)

from core.tagger import TaggerWorker
from i18n import tr
from widgets import Card, FileGrid, LogPanel, ScrollPage, path_row

IMG_EXTS = (".png", ".jpg", ".jpeg", ".webp", ".bmp")


class TagPage(ScrollPage):
    def __init__(self, model_dir, parent=None):
        super().__init__(parent)
        lay = self.lay
        self.model_dir = model_dir
        self._worker = None
        self._param_labels = {}   # i18n key -> QLabel

        self.title = QLabel(tr("tag_title"))
        self.title.setObjectName("PageTitle")
        lay.addWidget(self.title)

        # ---- 路径 ----
        self.c1 = Card(tr("path_title"))
        row1, self.in_src, self.lbl_src, self.btn_src = path_row(tr("lbl_src"), tr("ph_src"))
        row2, self.in_out, self.lbl_out, self.btn_out = path_row(tr("lbl_out"), tr("ph_out"))
        self.c1.add(row1)
        self.c1.add(row2)
        self.in_src.textChanged.connect(self._rescan)
        lay.addWidget(self.c1)

        # ---- 文件预览 ----
        self.c2 = Card(tr("preview_title"), tr("preview_hint"))
        self.grid = FileGrid()
        self.c2.add(self.grid)
        self.stat = QLabel(tr("no_dir"))
        self.stat.setObjectName("CardDesc")
        self.c2.add(self.stat)
        lay.addWidget(self.c2)

        # ---- 参数 ----
        self.c3 = Card(tr("param_title"))

        p1 = QHBoxLayout()
        p1.setSpacing(12)
        self.lbl_trigger = QLabel(tr("lbl_trigger"))
        self.lbl_trigger.setObjectName("FieldLabel")
        self.lbl_trigger.setFixedWidth(88)
        self.in_trigger = QLineEdit()
        self.in_trigger.setPlaceholderText(tr("ph_trigger"))
        p1.addWidget(self.lbl_trigger)
        p1.addWidget(self.in_trigger, 1)
        self.c3.add_layout(p1)

        p2 = QHBoxLayout()
        p2.setSpacing(16)
        self.spin_g = self._thr_spin(p2, "lbl_general", 0.35)
        self.spin_c = self._thr_spin(p2, "lbl_character", 0.85)
        self.lbl_mc = QLabel(tr("lbl_mincount"))
        self.lbl_mc.setObjectName("FieldLabel")
        self.spin_mc = QSpinBox()
        self.spin_mc.setRange(0, 100000)
        self.spin_mc.setValue(500)
        p2.addWidget(self.lbl_mc)
        p2.addWidget(self.spin_mc)
        p2.addStretch(1)
        self.c3.add_layout(p2)

        p3 = QHBoxLayout()
        p3.setSpacing(16)
        self.chk_bg = QCheckBox(tr("chk_bg"))
        self.chk_bg.setChecked(True)
        self.chk_skip = QCheckBox(tr("chk_skip"))
        self.chk_skip.setChecked(True)
        self.lbl_prefix = QLabel(tr("lbl_prefix"))
        self.lbl_prefix.setObjectName("FieldLabel")
        self.in_prefix = QLineEdit()
        self.in_prefix.setPlaceholderText(tr("ph_prefix"))
        p3.addWidget(self.chk_bg)
        p3.addWidget(self.chk_skip)
        p3.addWidget(self.lbl_prefix)
        p3.addWidget(self.in_prefix, 1)
        self.c3.add_layout(p3)
        lay.addWidget(self.c3)

        # ---- 进度 ----
        self.c4 = Card(tr("progress_title"))
        self.bar = QProgressBar()
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(8)
        self.c4.add(self.bar)
        lay.addWidget(self.c4)

        # ---- 操作栏 ----
        acts = QHBoxLayout()
        self.btn_start = QPushButton(tr("btn_start_tag"))
        self.btn_start.setProperty("primary", True)
        self.btn_start.clicked.connect(self.start)
        self.btn_open = QPushButton(tr("open_export"))
        self.btn_open.setProperty("secondary", True)
        self.btn_open.clicked.connect(self._open_out)
        acts.addWidget(self.btn_start)
        acts.addWidget(self.btn_open)
        acts.addStretch(1)
        lay.addLayout(acts)
        lay.addStretch(1)

    def _thr_spin(self, parent_lay, key, value):
        """阈值标签 + 微调框，标签登记到 _param_labels 便于切语言时刷新"""
        lbl = QLabel(tr(key))
        lbl.setObjectName("FieldLabel")
        s = QDoubleSpinBox()
        s.setRange(0.05, 0.95)
        s.setSingleStep(0.05)
        s.setValue(value)
        s.setFixedWidth(96)
        self._param_labels[key] = lbl
        parent_lay.addWidget(lbl)
        parent_lay.addWidget(s)
        return s

    # ---- 事件 ----
    def _rescan(self):
        folder = self.in_src.text()
        files = self.grid.show_dir(folder, only_unlabeled=False)
        n_img = len(files)
        n_txt = sum(1 for f in files if Path(f).with_suffix(".txt").exists())
        if not n_img:
            self.stat.setText(tr("no_dir"))
            return
        self.stat.setText(tr("stat_imgs", n=n_img, m=n_txt, k=n_img - n_txt))
        if n_txt and not getattr(self, "_asked_exist", False):
            self._asked_exist = True
            ret = QMessageBox.question(
                self, tr("dlg_exist_title"), tr("dlg_exist_body", n=n_txt),
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if ret == QMessageBox.Yes:
                self.chk_skip.setChecked(True)

    def _opts(self, skip_existing):
        return dict(
            trigger=self.in_trigger.text().strip(),
            prefix_tags=self.in_prefix.text().strip(),
            fixed_tags="",
            suffix_tags="",
            general_threshold=self.spin_g.value(),
            character_threshold=self.spin_c.value(),
            thresh=self.spin_g.value(),
            min_count=True,
            min_count_value=self.spin_mc.value(),
            background=self.chk_bg.isChecked(),
            rating=True, artist=True, copyright=True, character=True, deny_exact=True,
            skip_existing=skip_existing,
            ext="txt",
            provider="auto",
        )

    def start(self):
        folder = self.in_src.text().strip()
        if not folder or not Path(folder).is_dir():
            self.in_src.setProperty("err", True)
            self.in_src.style().unpolish(self.in_src)
            self.in_src.style().polish(self.in_src)
            QMessageBox.warning(self, tr("msg_tip"), tr("msg_valid_dir"))
            return
        if self._worker and self._worker.isRunning():
            return
        opts = self._opts(self.chk_skip.isChecked())
        out = self.in_out.text().strip() or None
        self._worker = TaggerWorker(folder, out, Path(self.model_dir), opts)
        self._worker.progress.connect(self._on_prog)
        self._worker.log.connect(self.log_panel.write)
        self._worker.finished_ok.connect(self._on_done)
        self._worker.failed.connect(lambda m: self.log_panel.write("[FAIL] " + m))
        self.btn_start.setText(tr("btn_running"))
        self.btn_start.setEnabled(False)
        self._worker.start()

    def _on_prog(self, done, total):
        self.bar.setMaximum(total)
        self.bar.setValue(done)

    def _on_done(self, done, el):
        self.btn_start.setText(tr("btn_start_tag"))
        self.btn_start.setEnabled(True)
        self.bar.setValue(self.bar.maximum())
        self.log_panel.write(tr("log_done_tag", n=done, t=el))
        self._asked_exist = True
        self._rescan()

    def _open_out(self):
        folder = self.in_out.text().strip() or self.in_src.text().strip()
        if folder and os.path.isdir(folder):
            subprocess.Popen(["explorer", os.path.normpath(folder)])

    # ---- 双语刷新 ----
    def retranslate_ui(self):
        super().retranslate_ui()
        self.title.setText(tr("tag_title"))
        self.c1.set_texts(tr("path_title"))
        self.c2.set_texts(tr("preview_title"), tr("preview_hint"))
        self.c3.set_texts(tr("param_title"))
        self.c4.set_texts(tr("progress_title"))
        self.lbl_src.setText(tr("lbl_src"))
        self.lbl_out.setText(tr("lbl_out"))
        self.in_src.setPlaceholderText(tr("ph_src"))
        self.in_out.setPlaceholderText(tr("ph_out"))
        self.btn_src.setText(tr("browse"))
        self.btn_out.setText(tr("browse"))
        self.lbl_trigger.setText(tr("lbl_trigger"))
        self.in_trigger.setPlaceholderText(tr("ph_trigger"))
        for key, lbl in self._param_labels.items():
            lbl.setText(tr(key))
        self.lbl_mc.setText(tr("lbl_mincount"))
        self.chk_bg.setText(tr("chk_bg"))
        self.chk_skip.setText(tr("chk_skip"))
        self.lbl_prefix.setText(tr("lbl_prefix"))
        self.in_prefix.setPlaceholderText(tr("ph_prefix"))
        self.btn_start.setText(tr("btn_start_tag"))
        self.btn_open.setText(tr("open_export"))
        if not (self._worker and self._worker.isRunning()) and self.in_src.text().strip():
            self._asked_exist = True
            self._rescan()
        else:
            self.stat.setText(tr("no_dir"))
