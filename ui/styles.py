"""
Professional dark theme with Salmon accents for ShaSort.
Features muted charcoal base with elegant salmon (#E06D5E / #FFA094) accents.
No glowing neon, no emojis, clean high-legibility layout.
"""

DARK_THEME_QSS = """
/* Global Reset & Base */
QWidget {
    background-color: #141416;
    color: #e4e4e7;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', sans-serif;
    font-size: 12px;
    selection-background-color: #E06D5E;
    selection-color: #ffffff;
}

/* Headings & Section Labels */
QLabel#titleLabel {
    font-size: 16px;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: 0.5px;
}

QLabel#subtitleLabel {
    font-size: 12px;
    color: #8e8e93;
}

QLabel#sectionHeader {
    font-size: 11px;
    font-weight: 700;
    color: #FFA094;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 4px;
    margin-bottom: 2px;
}

/* Input Controls */
QLineEdit {
    background-color: #1e1e22;
    border: 1px solid #333338;
    border-radius: 4px;
    padding: 6px 10px;
    color: #f4f4f5;
    font-size: 12px;
}

QLineEdit:hover {
    border: 1px solid #44444c;
}

QLineEdit:focus {
    border: 1px solid #E06D5E;
    background-color: #222228;
}

/* ComboBox Styling with Salmon accents */
QComboBox {
    background-color: #1e1e22;
    border: 1px solid #333338;
    border-radius: 4px;
    padding: 5px 10px;
    color: #f4f4f5;
    min-height: 18px;
    font-size: 12px;
}

QComboBox:hover {
    border: 1px solid #44444c;
    background-color: #222228;
}

QComboBox:focus {
    border: 1px solid #E06D5E;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 22px;
    border-left: 1px solid #333338;
}

QComboBox::down-arrow {
    width: 0;
    height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #a1a1aa;
    margin-right: 2px;
}

QComboBox QAbstractItemView {
    background-color: #1e1e22;
    border: 1px solid #333338;
    color: #f4f4f5;
    selection-background-color: #E06D5E;
    selection-color: #ffffff;
    padding: 2px;
    outline: none;
}

QComboBox QAbstractItemView::item {
    padding: 6px 10px;
    color: #f4f4f5;
    min-height: 22px;
}

QComboBox QAbstractItemView::item:selected {
    background-color: #E06D5E;
    color: #ffffff;
}

/* Radio Buttons with Salmon Active Indicator */
QRadioButton {
    spacing: 6px;
    color: #d4d4d8;
    font-size: 12px;
}

QRadioButton::indicator {
    width: 14px;
    height: 14px;
    border-radius: 7px;
    border: 1px solid #52525b;
    background-color: #1e1e22;
}

QRadioButton::indicator:hover {
    border-color: #E06D5E;
}

QRadioButton::indicator:checked {
    background-color: #E06D5E;
    border: 1px solid #FFA094;
}

/* Group Boxes / Cards */
QGroupBox {
    background-color: #18181b;
    border: 1px solid #27272a;
    border-radius: 6px;
    margin-top: 10px;
    padding-top: 14px;
    padding-left: 12px;
    padding-right: 12px;
    padding-bottom: 12px;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 4px;
    color: #FFA094;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
}

/* Push Buttons */
QPushButton {
    background-color: #222226;
    color: #f4f4f5;
    border: 1px solid #333338;
    border-radius: 4px;
    padding: 6px 14px;
    font-weight: 500;
    font-size: 12px;
}

QPushButton:hover {
    background-color: #2a2a30;
    border-color: #44444c;
}

QPushButton:pressed {
    background-color: #1a1a1d;
}

QPushButton:disabled {
    background-color: #1a1a1d;
    color: #52525b;
    border-color: #27272a;
}

QPushButton#browseBtn {
    padding: 6px 12px;
    background-color: #242428;
}

/* Primary Action Button - Salmon Accent */
QPushButton#startBtn {
    background-color: #E06D5E;
    color: #ffffff;
    font-weight: 600;
    font-size: 13px;
    padding: 8px 20px;
    border: 1px solid #EA7D6F;
    border-radius: 4px;
}

QPushButton#startBtn:hover {
    background-color: #D45F50;
    border-color: #FFA094;
}

QPushButton#startBtn:pressed {
    background-color: #BD4E40;
}

/* Key Selection Buttons with Salmon Accent */
QPushButton#keySelectBtn {
    background-color: #222226;
    color: #FFA094;
    border: 1px solid #3f3f46;
    border-radius: 3px;
    font-weight: 700;
    font-size: 12px;
    padding: 3px 8px;
    min-width: 44px;
}

QPushButton#keySelectBtn:hover {
    background-color: #E06D5E;
    color: #ffffff;
    border-color: #FFA094;
}

QPushButton#dangerBtn {
    background-color: #222226;
    color: #f87171;
    border: 1px solid #3f3f46;
    padding: 3px 8px;
    border-radius: 3px;
}

QPushButton#dangerBtn:hover {
    background-color: #7f1d1d;
    color: #ffffff;
    border-color: #991b1b;
}

QPushButton#secondaryBtn {
    background-color: #222226;
    border: 1px solid #333338;
}

QPushButton#secondaryBtn:hover {
    border-color: #E06D5E;
    color: #FFA094;
}

/* Table Widget */
QTableWidget {
    background-color: #161618;
    border: 1px solid #27272a;
    border-radius: 4px;
    gridline-color: #222226;
    color: #f4f4f5;
    outline: none;
}

QTableWidget::item {
    padding: 4px 6px;
    border-bottom: 1px solid #1e1e22;
}

QTableWidget::item:selected {
    background-color: #261b1c;
    color: #ffffff;
}

QTableWidget QLineEdit {
    background-color: #1e1e22;
    color: #f4f4f5;
    border: 1px solid #E06D5E;
    border-radius: 2px;
    padding: 2px 6px;
    font-size: 12px;
    margin: 1px;
}

QHeaderView::section {
    background-color: #1a1a1d;
    color: #8e8e93;
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.4px;
    padding: 6px 8px;
    border: none;
    border-bottom: 1px solid #27272a;
}

/* Scrollbars */
QScrollBar:vertical {
    background-color: #141416;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #2e2e33;
    min-height: 24px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background-color: #E06D5E;
}

QScrollBar::horizontal {
    background-color: #141416;
    height: 8px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background-color: #2e2e33;
    min-width: 24px;
    border-radius: 4px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #E06D5E;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    height: 0px;
    width: 0px;
}

/* Tooltips */
QToolTip {
    background-color: #222226;
    color: #f4f4f5;
    border: 1px solid #333338;
    border-radius: 3px;
    padding: 4px 6px;
    font-size: 11px;
}
"""
