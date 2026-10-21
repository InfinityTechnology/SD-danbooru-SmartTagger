"""Corporate Clean 主题 —— QSS 全局样式（对齐 stylekit corporate-clean 规范）"""

QSS = """
* {
    font-family: "Microsoft YaHei UI", "Noto Sans SC", sans-serif;
    outline: none;
}
QMainWindow, QDialog { background: #F8FAFC; }

/* ---------- 顶部导航 ---------- */
#Header {
    background: #FFFFFF;
    border-bottom: 1px solid #E5E7EB;
}
#Header QLabel#AppName { font-size: 16px; font-weight: 600; color: #111827; }
#Header QLabel#AppVer  { font-size: 12px; color: #9CA3AF; }
#StatusChip {
    background: #ECFDF5; border-radius: 8px; padding: 4px 12px;
    font-size: 12px; font-weight: 500; color: #059669;
}
#StatusChip QLabel { font-size: 12px; font-weight: 500; color: #059669; }
#StatusChipWarn {
    background: #FFFBEB; border-radius: 8px; padding: 4px 12px;
    font-size: 12px; font-weight: 500; color: #B45309;
}
#StatusChipWarn QLabel { font-size: 12px; font-weight: 500; color: #B45309; }

/* ---------- 侧边导航 ---------- */
#Sidebar { background: #FFFFFF; border-right: 1px solid #E5E7EB; }
QPushButton[nav="true"] {
    text-align: left; padding: 12px 16px; border: none; border-radius: 8px;
    font-size: 14px; font-weight: 500; color: #374151; background: transparent;
}
QPushButton[nav="true"]:hover { background: #F9FAFB; }
QPushButton[nav="true"]:checked { background: #EFF6FF; color: #2563EB; }

/* ---------- 内容区 ---------- */
#PageTitle { font-size: 24px; font-weight: 600; color: #111827; }
#Card {
    background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 12px;
}
#CardTitle { font-size: 16px; font-weight: 600; color: #111827; }
#CardDesc  { font-size: 12px; color: #6B7280; }
#FieldLabel { font-size: 14px; color: #374151; }

/* ---------- 输入控件 ---------- */
QLineEdit {
    background: #F9FAFB; border: 1px solid #D1D5DB; border-radius: 8px;
    padding: 9px 12px; font-size: 13px; color: #111827;
    selection-background-color: #BFDBFE;
}
QLineEdit:focus { border: 1px solid #2563EB; }
QLineEdit[err="true"] { border: 1px solid #EF4444; }
QLineEdit::placeholder { color: #9CA3AF; }

QSpinBox, QDoubleSpinBox {
    background: #F9FAFB; border: 1px solid #D1D5DB; border-radius: 8px;
    padding: 6px 10px; font-size: 13px; color: #111827;
}
QSpinBox:focus, QDoubleSpinBox:focus { border: 1px solid #2563EB; }

QCheckBox { font-size: 13px; color: #374151; spacing: 8px; }
QCheckBox::indicator {
    width: 16px; height: 16px; border: 1px solid #D1D5DB; border-radius: 4px; background: #FFFFFF;
}
QCheckBox::indicator:checked { background: #2563EB; border-color: #2563EB; }

/* ---------- 按钮 ---------- */
QPushButton[primary="true"] {
    background: #2563EB; color: #FFFFFF; border: none; border-radius: 8px;
    padding: 11px 24px; font-size: 14px; font-weight: 500;
}
QPushButton[primary="true"]:hover { background: #1D4ED8; }
QPushButton[primary="true"]:pressed { background: #1E40AF; }
QPushButton[primary="true"]:disabled { background: #93C5FD; }

QPushButton[secondary="true"] {
    background: #FFFFFF; color: #374151; border: 1px solid #D1D5DB; border-radius: 8px;
    padding: 11px 24px; font-size: 14px; font-weight: 500;
}
QPushButton[secondary="true"]:hover { background: #F9FAFB; }

QPushButton[chip="true"] {
    background: #EFF6FF; color: #2563EB; border: none; border-radius: 8px;
    padding: 6px 12px; font-size: 12px; font-weight: 500;
}
QPushButton[chipOn="true"] {
    background: #2563EB; color: #FFFFFF; border: none; border-radius: 8px;
    padding: 6px 12px; font-size: 12px; font-weight: 500;
}

/* ---------- 进度条 ---------- */
QProgressBar {
    background: #E5E7EB; border: none; border-radius: 999px; height: 8px;
    text-align: center; color: transparent;
}
QProgressBar::chunk { background: #2563EB; border-radius: 999px; }

/* ---------- 日志面板（内嵌控制台） ---------- */
#LogPanel {
    background: #0F172A; border: none; border-radius: 8px;
    color: #94A3B8; font-size: 12px;
    font-family: "Cascadia Mono", "Consolas", monospace;
    padding: 8px; border: 1px solid #1E293B;
}

/* ---------- 文件网格 ---------- */
#FileGrid { background: transparent; border: none; }
#FileGrid::item { margin: 4px; }
#FileGrid::item:selected { background: #EFF6FF; border-radius: 8px; }

/* ---------- 表格（环境检测结果） ---------- */
QTableWidget {
    background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 8px;
    gridline-color: #F3F4F6; font-size: 13px; color: #111827;
}
QTableWidget::item { padding: 8px 12px; }
QTableWidget::item:selected { background: #EFF6FF; color: #2563EB; }
QHeaderView::section {
    background: #F9FAFB; border: none; border-bottom: 1px solid #E5E7EB;
    padding: 8px 12px; font-size: 12px; font-weight: 600; color: #6B7280;
}

/* ---------- 滚动条 ---------- */
QScrollArea { border: none; background: transparent; }
QScrollArea > QWidget > QWidget { background: transparent; }
QScrollBar:vertical { background: transparent; width: 8px; margin: 0; }
QScrollBar::handle:vertical { background: #D1D5DB; border-radius: 4px; min-height: 32px; }
QScrollBar::handle:vertical:hover { background: #9CA3AF; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: transparent; height: 8px; }
QScrollBar::handle:horizontal { background: #D1D5DB; border-radius: 4px; }
"""


# ---------- 深色主题（语义 token 重配色，非简单反相） ----------
DARK_QSS = """
* { font-family: "Microsoft YaHei UI", "Noto Sans SC", sans-serif; outline: none; }
QMainWindow, QDialog { background: #0F172A; }

#Header { background: #1E293B; border-bottom: 1px solid #334155; }
#Header QLabel#AppName { font-size: 16px; font-weight: 600; color: #F1F5F9; }
#Header QLabel#AppVer  { font-size: 12px; color: #94A3B8; }
#StatusChip { background: #052E16; border-radius: 8px; padding: 4px 12px;
    font-size: 12px; font-weight: 500; color: #34D399; }
#StatusChip QLabel { font-size: 12px; font-weight: 500; color: #34D399; }
#StatusChipWarn { background: #422006; border-radius: 8px; padding: 4px 12px;
    font-size: 12px; font-weight: 500; color: #FBBF24; }
#StatusChipWarn QLabel { font-size: 12px; font-weight: 500; color: #FBBF24; }

#Sidebar { background: #1E293B; border-right: 1px solid #334155; }
QPushButton[nav="true"] { text-align: left; padding: 12px 16px; border: none; border-radius: 8px;
    font-size: 14px; font-weight: 500; color: #CBD5E1; background: transparent; }
QPushButton[nav="true"]:hover { background: #334155; }
QPushButton[nav="true"]:checked { background: #1E3A8A; color: #93C5FD; }

#PageTitle { font-size: 24px; font-weight: 600; color: #F1F5F9; }
#Card { background: #1E293B; border: 1px solid #334155; border-radius: 12px; }
#CardTitle { font-size: 16px; font-weight: 600; color: #F1F5F9; }
#CardDesc  { font-size: 12px; color: #94A3B8; }
#FieldLabel { font-size: 14px; color: #CBD5E1; }

QLineEdit { background: #0F172A; border: 1px solid #475569; border-radius: 8px;
    padding: 9px 12px; font-size: 13px; color: #F1F5F9; selection-background-color: #1D4ED8; }
QLineEdit:focus { border: 1px solid #3B82F6; }
QLineEdit[err="true"] { border: 1px solid #EF4444; }
QLineEdit::placeholder { color: #64748B; }

QSpinBox, QDoubleSpinBox { background: #0F172A; border: 1px solid #475569; border-radius: 8px;
    padding: 6px 10px; font-size: 13px; color: #F1F5F9; }
QSpinBox:focus, QDoubleSpinBox:focus { border: 1px solid #3B82F6; }

QCheckBox { font-size: 13px; color: #CBD5E1; spacing: 8px; }
QCheckBox::indicator { width: 16px; height: 16px; border: 1px solid #475569; border-radius: 4px; background: #0F172A; }
QCheckBox::indicator:checked { background: #2563EB; border-color: #2563EB; }

QPushButton[primary="true"] { background: #2563EB; color: #FFFFFF; border: none; border-radius: 8px;
    padding: 11px 24px; font-size: 14px; font-weight: 500; }
QPushButton[primary="true"]:hover { background: #1D4ED8; }
QPushButton[primary="true"]:pressed { background: #1E40AF; }
QPushButton[primary="true"]:disabled { background: #334155; color: #64748B; }

QPushButton[secondary="true"] { background: #0F172A; color: #CBD5E1; border: 1px solid #475569;
    border-radius: 8px; padding: 11px 24px; font-size: 14px; font-weight: 500; }
QPushButton[secondary="true"]:hover { background: #334155; }
QPushButton[secondary="true"]:disabled { color: #64748B; }

QProgressBar { background: #334155; border: none; border-radius: 999px; height: 8px;
    text-align: center; color: transparent; }
QProgressBar::chunk { background: #3B82F6; border-radius: 999px; }

#LogPanel { background: #020617; border: 1px solid #1E293B; border-radius: 8px;
    color: #94A3B8; font-size: 12px; font-family: "Cascadia Mono", "Consolas", monospace; padding: 8px; }

#FileGrid { background: transparent; border: none; }
#FileGrid::item { margin: 4px; }
#FileGrid::item:selected { background: #1E3A8A; border-radius: 8px; }

QTableWidget { background: #1E293B; border: 1px solid #334155; border-radius: 8px;
    gridline-color: #334155; font-size: 13px; color: #F1F5F9; }
QTableWidget::item { padding: 8px 12px; }
QTableWidget::item:selected { background: #1E3A8A; color: #93C5FD; }
QHeaderView::section { background: #0F172A; border: none; border-bottom: 1px solid #334155;
    padding: 8px 12px; font-size: 12px; font-weight: 600; color: #94A3B8; }

QScrollArea { border: none; background: transparent; }
QScrollArea > QWidget > QWidget { background: transparent; }
QScrollBar:vertical { background: transparent; width: 8px; margin: 0; }
QScrollBar::handle:vertical { background: #475569; border-radius: 4px; min-height: 32px; }
QScrollBar::handle:vertical:hover { background: #64748B; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: transparent; height: 8px; }
QScrollBar::handle:horizontal { background: #475569; border-radius: 4px; }

QLabel#IconBtn { color: #CBD5E1; }
"""
