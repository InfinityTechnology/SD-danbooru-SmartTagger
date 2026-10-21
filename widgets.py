"""通用组件：卡片 / 路径行 / 内嵌日志面板 / 缩略图文件网格"""
import os

from PySide6.QtCore import Qt, QSize, QThread, Signal
from PySide6.QtGui import QPixmap, QColor
from PySide6.QtWidgets import (QFileDialog, QFrame, QHBoxLayout, QLabel, QLineEdit,
                               QListWidget, QListWidgetItem, QPlainTextEdit, QPushButton,
                               QScrollArea, QVBoxLayout, QWidget)


class ScrollPage(QWidget):
    """页面基类：左侧内容滚动区 + 右侧固定日志面板（始终可见，无需滚动到页底）"""

    def __init__(self, parent=None):
        super().__init__(parent)
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(16)

        # 左侧：内容滚动区
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        self.body = QWidget()
        self.lay = QVBoxLayout(self.body)
        self.lay.setContentsMargins(0, 0, 0, 0)
        self.lay.setSpacing(20)
        scroll.setWidget(self.body)
        outer.addWidget(scroll, 1)

        # 右侧：日志面板（内嵌控制台）
        dock = QFrame()
        dock.setObjectName("Card")
        dock.setFixedWidth(340)
        d = QVBoxLayout(dock)
        d.setContentsMargins(16, 16, 16, 16)
        d.setSpacing(8)
        t = QLabel("运行日志")
        t.setObjectName("CardTitle")
        d.addWidget(t)
        hint = QLabel("所有输出内嵌在此，不弹出独立控制台窗口。")
        hint.setObjectName("CardDesc")
        hint.setWordWrap(True)
        d.addWidget(hint)
        self.log_title_lbl = t
        self.log_hint_lbl = hint
        self.log_panel = LogPanel()
        d.addWidget(self.log_panel, 1)
        outer.addWidget(dock)

    def retranslate_ui(self):
        """子类重写时先 super().retranslate_ui() 再刷新自己的控件"""
        from i18n import tr
        self.log_title_lbl.setText(tr("log_title"))
        self.log_hint_lbl.setText(tr("log_hint"))


class Card(QFrame):
    def __init__(self, title="", desc="", parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.setProperty("class", "card")
        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(24, 24, 24, 24)
        self._lay.setSpacing(16)
        self.title_lbl = None
        self.desc_lbl = None
        if title:
            self.title_lbl = QLabel(title)
            self.title_lbl.setObjectName("CardTitle")
            self._lay.addWidget(self.title_lbl)
        if desc:
            self.desc_lbl = QLabel(desc)
            self.desc_lbl.setObjectName("CardDesc")
            self.desc_lbl.setWordWrap(True)
            self._lay.addWidget(self.desc_lbl)

    def set_texts(self, title=None, desc=None):
        if title is not None and self.title_lbl:
            self.title_lbl.setText(title)
        if desc is not None and self.desc_lbl:
            self.desc_lbl.setText(desc)

    def add(self, w, stretch=0):
        self._lay.addWidget(w, stretch)
        return w

    def add_layout(self, lay, stretch=0):
        self._lay.addLayout(lay, stretch)
        return lay


def path_row(label_text, placeholder, parent=None):
    """标签 + 输入框 + 浏览按钮，返回 (row, edit, label, button)"""
    from i18n import tr
    row = QWidget(parent)
    lay = QHBoxLayout(row)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(12)
    lbl = QLabel(label_text)
    lbl.setObjectName("FieldLabel")
    lbl.setFixedWidth(88)
    edit = QLineEdit()
    edit.setPlaceholderText(placeholder)
    btn = QPushButton(tr("browse"))
    btn.setProperty("secondary", True)
    btn.setFixedHeight(40)

    def browse():
        d = QFileDialog.getExistingDirectory(row, tr("select_folder"), edit.text() or "")
        if d:
            edit.setText(os.path.normpath(d))

    btn.clicked.connect(browse)
    lay.addWidget(lbl)
    lay.addWidget(edit, 1)
    lay.addWidget(btn)
    return row, edit, lbl, btn


def field_row(label_text, placeholder, parent=None, width=88):
    """标签 + 输入框（无浏览按钮），返回 (row, label, edit)"""
    row = QWidget(parent)
    lay = QHBoxLayout(row)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(12)
    lbl = QLabel(label_text)
    lbl.setObjectName("FieldLabel")
    lbl.setFixedWidth(width)
    edit = QLineEdit()
    edit.setPlaceholderText(placeholder)
    lay.addWidget(lbl)
    lay.addWidget(edit, 1)
    return row, lbl, edit


class LogPanel(QPlainTextEdit):
    """内嵌控制台：子进程/引擎输出都进这里，不再弹独立黑窗"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("LogPanel")
        self.setReadOnly(True)
        self.setMaximumBlockCount(2000)

    def write(self, text):
        self.appendPlainText(text.rstrip())

    def flush(self):
        pass


class ThumbLoader(QThread):
    """后台加载缩略图，避免一次性读入大量大图卡死界面"""
    one = Signal(str, QPixmap)
    done_all = Signal(int)

    def __init__(self, files, cell=96, limit=400, parent=None):
        super().__init__(parent)
        self.files = files
        self.cell = cell
        self.limit = limit
        self._stop = False

    def stop(self):
        self._stop = True

    def run(self):
        n = 0
        for p in self.files[: self.limit]:
            if self._stop:
                break
            pm = QPixmap(p)
            if pm.isNull():
                pm = QPixmap(self.cell, self.cell)
                pm.fill(QColor("#F3F4F6"))
            else:
                pm = pm.scaled(self.cell, self.cell, Qt.KeepAspectRatioByExpanding,
                               Qt.SmoothTransformation)
            self.one.emit(p, pm)
            n += 1
        self.done_all.emit(n)


class FileGrid(QListWidget):
    """内嵌式文件浏览器：缩略图网格 + 角标提示已打标状态"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("FileGrid")
        self.setViewMode(QListWidget.IconMode)
        self.setIconSize(QSize(96, 96))
        self.setGridSize(QSize(112, 128))
        self.setResizeMode(QListWidget.Adjust)
        self.setMovement(QListWidget.Static)
        self.setWordWrap(True)
        self._loader = None
        self._labeled = set()

    def show_dir(self, folder, labeled_ext="txt", only_unlabeled=False):
        self.clear()
        self._labeled.clear()
        folder = str(folder)
        if not os.path.isdir(folder):
            return []
        files = sorted(
            os.path.join(folder, f) for f in os.listdir(folder)
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".bmp"))
        )
        shown = []
        for p in files:
            has = os.path.exists(os.path.splitext(p)[0] + "." + labeled_ext)
            if has:
                self._labeled.add(p)
            if only_unlabeled and has:
                continue
            shown.append(p)
            item = QListWidgetItem(os.path.basename(p))
            item.setData(Qt.UserRole, (p, has))
            item.setSizeHint(QSize(112, 128))
            self.addItem(item)
        if self._loader and self._loader.isRunning():
            self._loader.stop()
            self._loader.wait()
        self._loader = ThumbLoader(shown)
        self._loader.one.connect(self._apply_thumb)
        self._loader.start()
        return shown

    def _apply_thumb(self, path, pm):
        for i in range(self.count()):
            it = self.item(i)
            data = it.data(Qt.UserRole)
            if data and data[0] == path:
                if data[1]:
                    from PySide6.QtGui import QIcon, QPainter
                    from PySide6.QtCore import QRectF, QPointF
                    icon_pm = QPixmap(pm)
                    pt = QPainter(icon_pm)
                    pt.setRenderHint(QPainter.Antialiasing)
                    pt.setPen(Qt.NoPen)
                    pt.setBrush(QColor("#10B981"))
                    pt.drawEllipse(QRectF(icon_pm.width() - 16, 4, 12, 12))
                    pt.end()
                    it.setIcon(QIcon(icon_pm))
                else:
                    from PySide6.QtGui import QIcon
                    it.setIcon(QIcon(pm))
                break
