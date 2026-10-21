"""环境与依赖页：自动检测 + 一键安装 + 模型下载"""
from pathlib import Path

from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtWidgets import (QHBoxLayout, QHeaderView, QLabel, QLineEdit, QPushButton,
                               QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

from core import detector
from i18n import tr
from widgets import Card, LogPanel, ScrollPage

APP_DIR = Path(__file__).resolve().parent.parent


class EnvWorker(QThread):
    """后台跑检测/安装/下载，日志发回界面"""
    log = Signal(str)
    table = Signal(list)
    done = Signal(str)

    def __init__(self, task, model_dir, pip_target=""):
        super().__init__()
        self.task = task
        self.model_dir = model_dir
        self.pip_target = pip_target

    def run(self):
        if self.task == "detect":
            self.table.emit(detector.full_report(self.model_dir))
            self.done.emit("detect")
        elif self.task == "install":
            detector.install_missing(self.pip_target or "", log=self.log.emit)
            self.table.emit(detector.full_report(self.model_dir))
            self.done.emit("install")
        elif self.task == "model":
            ok = detector.download_model(self.model_dir, log=self.log.emit)
            self.table.emit(detector.full_report(self.model_dir))
            self.done.emit("model-ok" if ok else "model-fail")


class EnvPage(ScrollPage):
    def __init__(self, model_dir, parent=None):
        super().__init__(parent)
        lay = self.lay
        self.model_dir = model_dir
        self._worker = None

        self.title = QLabel(tr("env_title"))
        self.title.setObjectName("PageTitle")
        lay.addWidget(self.title)

        # 检测结果卡片
        self.c1 = Card(tr("env_card"), tr("env_card_desc"))
        c1 = self.c1
        self.table = QTableWidget(0, 2)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        c1.add(self.table)

        # 刷新行：装完依赖/下完模型后一键重测
        row_r = QHBoxLayout()
        row_r.setSpacing(12)
        self.btn_refresh = QPushButton(tr("refresh"))
        self.btn_refresh.setProperty("secondary", True)
        self.btn_refresh.clicked.connect(lambda: self._run("detect"))
        row_r.addStretch(1)
        row_r.addWidget(self.btn_refresh)
        c1.add_layout(row_r)

        row = QHBoxLayout()
        row.setSpacing(12)
        self.pip_edit = QLineEdit()
        self.pip_edit.setPlaceholderText(tr("pip_ph"))
        self.browse_btn = QPushButton(tr("browse"))
        self.browse_btn.setProperty("secondary", True)
        self.browse_btn.clicked.connect(self._pick_pip_dir)
        self.btn_install = QPushButton(tr("btn_install"))
        self.btn_install.setProperty("primary", True)
        self.btn_install.clicked.connect(lambda: self._run("install"))
        row.addWidget(self.pip_edit, 1)
        row.addWidget(self.browse_btn)
        row.addWidget(self.btn_install)
        c1.add_layout(row)
        lay.addWidget(c1)

        # 模型卡片
        self.c2 = Card(tr("model_card"), tr("model_desc"))
        c2 = self.c2
        row2 = QHBoxLayout()
        self.model_edit = QLineEdit(str(model_dir))
        self.model_edit.setReadOnly(False)
        btn_dl = QPushButton(tr("btn_download"))
        btn_dl.setProperty("primary", True)
        btn_dl.clicked.connect(self._download_model)
        self.model_lbl = QLabel(tr("model_dir"))
        row2.addWidget(self.model_lbl)
        row2.addWidget(self.model_edit, 1)
        row2.addWidget(btn_dl)
        c2.add_layout(row2)
        lay.addWidget(c2)
        lay.addStretch(1)

        self.refresh()

    def _pick_pip_dir(self):
        from PySide6.QtWidgets import QFileDialog
        d = QFileDialog.getExistingDirectory(self, tr("select_install"))
        if d:
            self.pip_edit.setText(d)

    def _run(self, task):
        if self._worker and self._worker.isRunning():
            return
        self.log_panel.write(f"===== {task} =====")
        self._worker = EnvWorker(task, Path(self.model_edit.text()), self.pip_edit.text())
        self._worker.log.connect(self.log_panel.write)
        self._worker.table.connect(self.fill_table)
        self._worker.done.connect(self._on_done)
        self._worker.start()

    def _download_model(self):
        self.model_dir = Path(self.model_edit.text())
        self._run("model")

    def _on_done(self, kind):
        if kind == "model-ok":
            self.log_panel.write(tr("log_model_ok"))

    def fill_table(self, rows):
        self.table.setRowCount(len(rows))
        self.table.setFixedHeight(min(len(rows) * 33 + 38, 380))
        for i, (k, v) in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(k))
            item = QTableWidgetItem(v)
            if any(x in v for x in ("未安装", "未下载", "不可用")):
                item.setForeground(Qt.red)
            self.table.setItem(i, 1, item)

    def refresh(self):
        self._run("detect")

    def retranslate_ui(self):
        super().retranslate_ui()
        self.title.setText(tr("env_title"))
        self.c1.set_texts(tr("env_card"), tr("env_card_desc"))
        self.c2.set_texts(tr("model_card"), tr("model_desc"))
        self.table.setHorizontalHeaderLabels([tr("col_item"), tr("col_status")])
        self.btn_refresh.setText(tr("refresh"))
        self.browse_btn.setText(tr("browse"))
        self.btn_install.setText(tr("btn_install"))
        self.model_lbl.setText(tr("model_dir"))
        self.pip_edit.setPlaceholderText(tr("pip_ph"))
        self.log_title_lbl.setText(tr("log_title"))
        self.log_hint_lbl.setText(tr("log_hint"))

    def log_sink(self):
        """给全局 stdout 重定向用"""
        return self.log_panel
