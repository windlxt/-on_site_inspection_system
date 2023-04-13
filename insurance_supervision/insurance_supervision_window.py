"""
作者：无用
心境：行到水穷处 坐看云起时
日期：2023年04月05日
"""
import importlib
import sys
from importlib import reload

import pandas as pd
from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, \
    QHBoxLayout, QDockWidget, QTableWidget, QTableWidgetItem, QAbstractItemView, \
    QTextEdit, QFrame, QGroupBox, QHeaderView, QVBoxLayout, QLabel, QPushButton, QStyle, QToolBox, QStackedWidget
from PySide6.QtWebEngineWidgets import QWebEngineView
from welcome_page import WelcomeWindow2


class InsuranceSupervisionWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 窗体风格设置
        self.setStyleSheet(
            'QPushButton {background-color: #2ABf9E;'
            'padding: 12px;'
            'font-size: 16px;}')

        # 1. 设置主窗口中心区域，添加窗口栈
        self.stack_window = QStackedWidget()
        self.setCentralWidget(self.stack_window)  # 设置中心窗口区域
        # 设置初始画面
        self.first_window = WelcomeWindow2()
        self.stack_window.addWidget(self.first_window)
        self.stack_window.setCurrentWidget(self.first_window)

        # 1.添加dock窗口
        self.create_dock_left()

        # 绑定信号槽
        self.bind_signal_slot()

    # 绑定信号槽
    def bind_signal_slot(self):
        self.tool_box.currentChanged.connect(self.set_arrow)

    def set_arrow(self, index):
        for i in range(self.tool_box.count()):
            self.tool_box.setItemIcon(i, self.arrow_right)
        self.tool_box.setItemIcon(index, self.arrow_down)

    # 添加 dock 窗口
    def create_dock_left(self):
        self.dock = QDockWidget('工具', self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock)
        self.dock.setFixedWidth(260)
        self.dock.setFeatures(QDockWidget.NoDockWidgetFeatures)

        # 添加控件
        self.dock_wighet = QWidget(self.dock)
        self.dock_wighet.setGeometry(0, 0, 260, 1020)
        self.dock_wighet_layout = QVBoxLayout()

        self.tool_box = QToolBox()

        self.arrow_right = self.style().standardPixmap(QStyle.StandardPixmap.SP_ArrowRight)
        self.arrow_down = self.style().standardPixmap(QStyle.StandardPixmap.SP_ArrowDown)

        self.tool_page_001 = QWidget()
        self.pbtn_001 = QPushButton('第一页按钮')
        self.layout_001 = QVBoxLayout(self.tool_page_001)
        self.layout_001.addWidget(self.pbtn_001)
        self.tool_box.addItem(self.tool_page_001, self.arrow_down, '第一页')

        self.tool_page_002 = QWidget()
        self.pbtn_002 = QPushButton('第二页按钮')
        self.layout_002 = QVBoxLayout(self.tool_page_002)
        self.layout_002.addWidget(self.pbtn_002)
        self.tool_box.addItem(self.tool_page_002, self.arrow_right, '第二页')

        self.tool_page_003 = QWidget()
        self.pbtn_003 = QPushButton('第三页按钮')
        self.layout_003 = QVBoxLayout(self.tool_page_003)
        self.layout_003.addWidget(self.pbtn_003)
        self.tool_box.addItem(self.tool_page_003, self.arrow_right, '第三页')

        self.dock_wighet_layout.addWidget(self.tool_box)

        self.dock_wighet.setLayout(self.dock_wighet_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = InsuranceSupervisionWindow()
    # w.show()
    # w.showFullScreen()
    w.showMaximized()
    exit(app.exec())

