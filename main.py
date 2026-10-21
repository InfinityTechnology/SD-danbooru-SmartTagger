"""智能打标工具 —— 入口 + 主窗口（侧边导航 + 多页切换）
启动即纯 GUI，无独立控制台窗口；子进程与引擎输出全部重定向到界面内日志面板。
支持中英双语切换与浅色/深色主题切换（选择会被记住）。
"""
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import (QApplication, QButtonGroup, QFrame, QHBoxLayout, QLabel,
                               QMainWindow, QPushButton, QSizePolicy, QStackedWidget,
                               QVBoxLayout, QWidget)

from theme import QSS, DARK_QSS
from widgets import LogPanel
from i18n import i18n, tr
from pages.env_page import EnvPage
from pages.tag_page import TagPage
from pages.clean_page import CleanPage
from pages.api_page import ApiPage

if getattr(sys, "frozen", False):
    # 打包后：以 exe 所在目录为基准（模型随 exe 一起分发）
    APP_DIR = Path(sys.executable).resolve().parent
else:
    APP_DIR = Path(__file__).resolve().parent
DEFAULT_MODEL_DIR = APP_DIR / "models" / "wd-vit-tagger-v3"


class LogBridge:
    """把 print / 子进程输出重定向到界面日志面板（消灭独立控制台）"""

    def __init__(self, widget):
        self.widget = widget
        self._buf = ""

    def write(self, text):
        self._buf += text
        while "\n" in self._buf:
            line, self._buf = self._buf.split("\n", 1)
            if line.strip():
                self.widget.write(line)
        return len(text)

    def flush(self):
        pass


def light_palette():
    """强制浅色调色板：Windows 深色系统模式下，QMessageBox 等原生对话框
    会出现白底白字，必须显式锁死浅色。"""
    pal = QPalette()
    pal.setColor(QPalette.Window, QColor("#F8FAFC"))
    pal.setColor(QPalette.WindowText, QColor("#111827"))
    pal.setColor(QPalette.Base, QColor("#FFFFFF"))
    pal.setColor(QPalette.AlternateBase, QColor("#F9FAFB"))
    pal.setColor(QPalette.Text, QColor("#111827"))
    pal.setColor(QPalette.Button, QColor("#FFFFFF"))
    pal.setColor(QPalette.ButtonText, QColor("#111827"))
    pal.setColor(QPalette.ToolTipBase, QColor("#FFFFFF"))
    pal.setColor(QPalette.ToolTipText, QColor("#111827"))
    pal.setColor(QPalette.Highlight, QColor("#2563EB"))
    pal.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
    pal.setColor(QPalette.PlaceholderText, QColor("#9CA3AF"))
    pal.setColor(QPalette.Disabled, QPalette.Text, QColor("#9CA3AF"))
    pal.setColor(QPalette.Disabled, QPalette.ButtonText, QColor("#9CA3AF"))
    return pal


def dark_palette():
    pal = QPalette()
    pal.setColor(QPalette.Window, QColor("#0F172A"))
    pal.setColor(QPalette.WindowText, QColor("#F1F5F9"))
    pal.setColor(QPalette.Base, QColor("#1E293B"))
    pal.setColor(QPalette.AlternateBase, QColor("#0F172A"))
    pal.setColor(QPalette.Text, QColor("#F1F5F9"))
    pal.setColor(QPalette.Button, QColor("#1E293B"))
    pal.setColor(QPalette.ButtonText, QColor("#F1F5F9"))
    pal.setColor(QPalette.ToolTipBase, QColor("#1E293B"))
    pal.setColor(QPalette.ToolTipText, QColor("#F1F5F9"))
    pal.setColor(QPalette.Highlight, QColor("#2563EB"))
    pal.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
    pal.setColor(QPalette.PlaceholderText, QColor("#64748B"))
    pal.setColor(QPalette.Disabled, QPalette.Text, QColor("#64748B"))
    pal.setColor(QPalette.Disabled, QPalette.ButtonText, QColor("#64748B"))
    return pal


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("SmartTagger", "SmartTagger")
        self.lang = self.settings.value("lang", "zh")
        self.theme = self.settings.value("theme", "light")
        i18n.set_lang(self.lang)

        self.setWindowTitle(tr("app_name") + " v1.0")
        self.resize(1280, 860)
        self.setMinimumSize(1080, 720)

        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ---- 顶部导航 ----
        header = QFrame()
        header.setObjectName("Header")
        header.setFixedHeight(56)
        h = QHBoxLayout(header)
        h.setContentsMargins(24, 0, 24, 0)
        h.setSpacing(10)
        logo = QFrame()
        logo.setFixedSize(30, 30)
        logo.setStyleSheet("background:#2563EB;border-radius:8px;")
        self.name_lbl = QLabel(tr("app_name"))
        self.name_lbl.setObjectName("AppName")
        self.ver_lbl = QLabel("v1.0")
        self.ver_lbl.setObjectName("AppVer")
        h.addWidget(logo)
        h.addWidget(self.name_lbl)
        h.addWidget(self.ver_lbl)
        h.addStretch(1)

        self.lang_btn = QPushButton()
        self.lang_btn.setProperty("secondary", True)
        self.lang_btn.setFixedHeight(32)
        self.lang_btn.setCursor(Qt.PointingHandCursor)
        self.lang_btn.clicked.connect(self.toggle_lang)
        self.theme_btn = QPushButton()
        self.theme_btn.setProperty("secondary", True)
        self.theme_btn.setFixedHeight(32)
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self.theme_btn.clicked.connect(self.toggle_theme)
        h.addWidget(self.lang_btn)
        h.addWidget(self.theme_btn)

        self.status_chip = QLabel(tr("status_detect"))
        self.status_chip.setObjectName("StatusChipWarn")
        h.addWidget(self.status_chip)
        root.addWidget(header)

        # ---- 主体：侧边栏 + 页面 ----
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        root.addLayout(body, 1)

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(220)
        s = QVBoxLayout(sidebar)
        s.setContentsMargins(16, 16, 16, 16)
        s.setSpacing(4)
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        self.pages = QStackedWidget()
        self.nav_buttons = []
        self.pages_list = []

        page_defs = [
            ("nav_env", lambda: EnvPage(DEFAULT_MODEL_DIR)),
            ("nav_tag", lambda: TagPage(DEFAULT_MODEL_DIR)),
            ("nav_clean", lambda: CleanPage(DEFAULT_MODEL_DIR)),
            ("nav_api", lambda: ApiPage()),
        ]
        for i, (key, factory) in enumerate(page_defs):
            btn = QPushButton(tr(key))
            btn.setProperty("nav", True)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _=False, ix=i: self.pages.setCurrentIndex(ix))
            self.nav_group.addButton(btn, i)
            s.addWidget(btn)
            self.nav_buttons.append((btn, key))
            page = factory()
            self.pages.addWidget(page)
            self.pages_list.append(page)
            if isinstance(page, EnvPage):
                self.env_page = page
        s.addStretch(1)
        self.hint = QLabel(tr("local_hint"))
        self.hint.setAlignment(Qt.AlignCenter)
        s.addWidget(self.hint)

        body.addWidget(sidebar)
        body.addWidget(self.pages, 1)
        self.setCentralWidget(central)

        # 日志重定向（任何 print / 子进程输出都进界面面板）
        sys.stdout = LogBridge(self.env_page.log_panel)
        sys.stderr = LogBridge(self.env_page.log_panel)
        self.env_page._worker.table.connect(self._on_env_table)
        self.apply_theme()
        self.retranslate_ui()

    # ---- 主题 ----
    def apply_theme(self):
        app = QApplication.instance()
        if self.theme == "dark":
            app.setStyleSheet(DARK_QSS)
            app.setPalette(dark_palette())
        else:
            app.setStyleSheet(QSS)
            app.setPalette(light_palette())
        # 侧栏脚注颜色随主题走（内联样式优先级高于 QSS）
        self.hint.setStyleSheet(
            "color:#64748B;font-size:11px;" if self.theme == "dark"
            else "color:#9CA3AF;font-size:11px;")
        # 状态胶囊切换主题后需重新套用样式
        self.status_chip.style().unpolish(self.status_chip)
        self.status_chip.style().polish(self.status_chip)
        self._refresh_theme_btn()

    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        self.settings.setValue("theme", self.theme)
        self.apply_theme()

    def _refresh_theme_btn(self):
        self.theme_btn.setText(tr("theme_to_light") if self.theme == "dark" else tr("theme_to_dark"))

    # ---- 语言 ----
    def toggle_lang(self):
        self.lang = "en" if self.lang == "zh" else "zh"
        self.settings.setValue("lang", self.lang)
        i18n.set_lang(self.lang)
        self.retranslate_ui()
        for p in self.pages_list:
            if hasattr(p, "retranslate_ui"):
                p.retranslate_ui()
        self.setWindowTitle(tr("app_name") + " v1.0")

    def retranslate_ui(self):
        self.name_lbl.setText(tr("app_name"))
        for btn, key in self.nav_buttons:
            btn.setText(tr(key))
        self.hint.setText(tr("local_hint"))
        self.lang_btn.setText(tr("lang_switch"))
        self._refresh_theme_btn()

    def _on_env_table(self, rows):
        d = dict(rows)
        backend = d.get("推理后端", "")
        model = d.get("WD14 模型", "")
        if "Dml" in backend or "CUDA" in backend:
            chip, obj = f"{tr('status_ready')} · {backend.split(',')[0].replace('ExecutionProvider','')}", "StatusChip"
        elif "CPU" in backend:
            chip, obj = tr("status_cpu"), "StatusChipWarn"
        else:
            chip, obj = tr("status_missing"), "StatusChipWarn"
        if "未下载" in model:
            chip += tr("status_nomodel")
        self.status_chip.setText(chip)
        self.status_chip.setObjectName(obj)
        self.status_chip.style().unpolish(self.status_chip)
        self.status_chip.style().polish(self.status_chip)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Microsoft YaHei UI", 10))
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
