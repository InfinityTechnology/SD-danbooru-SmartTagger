"""API 接入页（备选功能）：外接云端 AI 打标/清洗，默认关闭，不填 Key 不产生任何费用"""
import json
from urllib import request

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QLineEdit, QMessageBox,
                               QPushButton, QVBoxLayout, QWidget)

from i18n import tr
from widgets import Card, LogPanel, ScrollPage, field_row


class ApiTestWorker(QThread):
    """网络请求在工作线程跑，结果通过信号回主线程更新界面（禁止跨线程直接操作控件）"""
    log = Signal(str)

    def __init__(self, base, key, model, parent=None):
        super().__init__(parent)
        self.base, self.key, self.model = base, key, model

    def run(self):
        self.log.emit("[RUN ] " + tr("log_testing"))
        try:
            req = request.Request(
                self.base.rstrip("/") + "/chat/completions",
                data=json.dumps({
                    "model": self.model,
                    "messages": [{"role": "user", "content": "ping"}],
                    "max_tokens": 5,
                }).encode(),
                headers={"Authorization": f"Bearer {self.key}",
                         "Content-Type": "application/json"})
            with request.urlopen(req, timeout=30) as resp:
                self.log.emit(f"[OK  ] HTTP {resp.status} · {tr('api_ok')}")
        except Exception as e:
            self.log.emit(f"[FAIL] {e}")


class ApiPage(ScrollPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        lay = self.lay
        self._worker = None

        self.title = QLabel(tr("api_title"))
        self.title.setObjectName("PageTitle")
        lay.addWidget(self.title)

        self.c1 = Card(tr("api_card"), tr("api_desc"))
        r1, self.lbl_base, self.in_base = field_row(tr("lbl_base"), tr("ph_base"))
        r2, self.lbl_key, self.in_key = field_row(tr("lbl_key"), tr("ph_key"))
        r3 = QHBoxLayout()
        self.lbl_model = QLabel(tr("lbl_model"))
        self.lbl_model.setObjectName("FieldLabel")
        self.lbl_model.setFixedWidth(88)
        self.in_model = QLineEdit()
        self.in_model.setPlaceholderText(tr("ph_model"))
        r3.addWidget(self.lbl_model)
        r3.addWidget(self.in_model, 1)
        self.c1.add(r1)
        self.c1.add(r2)
        self.c1.add_layout(r3)
        lay.addWidget(self.c1)

        self.c2 = Card(tr("api_test"))
        row = QHBoxLayout()
        self.btn = QPushButton(tr("btn_test"))
        self.btn.setProperty("primary", True)
        self.btn.clicked.connect(self.test)
        row.addWidget(self.btn)
        row.addStretch(1)
        self.c2.add_layout(row)
        lay.addWidget(self.c2)
        lay.addStretch(1)

    def test(self):
        base = self.in_base.text().strip()
        key = self.in_key.text().strip()
        model = self.in_model.text().strip()
        if not (base and key and model):
            QMessageBox.information(self, tr("msg_tip"), tr("msg_fill_all"))
            return
        if self._worker and self._worker.isRunning():
            self.log_panel.write("[INFO] " + tr("log_busy"))
            return
        self.btn.setEnabled(False)
        self.btn.setText(tr("btn_testing"))
        self._worker = ApiTestWorker(base, key, model)
        self._worker.log.connect(self.log_panel.write)

        def done():
            self.btn.setEnabled(True)
            self.btn.setText(tr("btn_test"))

        self._worker.finished.connect(done)
        self._worker.start()

    def retranslate_ui(self):
        super().retranslate_ui()
        self.title.setText(tr("api_title"))
        self.c1.set_texts(tr("api_card"), tr("api_desc"))
        self.c2.set_texts(tr("api_test"))
        self.lbl_base.setText(tr("lbl_base"))
        self.lbl_key.setText(tr("lbl_key"))
        self.lbl_model.setText(tr("lbl_model"))
        self.in_base.setPlaceholderText(tr("ph_base"))
        self.in_key.setPlaceholderText(tr("ph_key"))
        self.in_model.setPlaceholderText(tr("ph_model"))
        if self.btn.isEnabled():
            self.btn.setText(tr("btn_test"))
