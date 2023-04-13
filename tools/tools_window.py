"""
作者：无用
心境：行到水穷处 坐看云起时
日期：2023年04月05日
"""
import sys
from PySide6.QtCore import QRect, Qt, QSize
from PySide6.QtGui import QColor, QPalette, QFont
from PySide6.QtWidgets import QApplication, QWidget, QScrollArea, \
    QHBoxLayout, QPushButton, QMainWindow, QLabel, QDockWidget, QVBoxLayout, QSizePolicy, QFrame, QStackedWidget, \
    QGroupBox, QTextEdit, QToolBox, QStyle
from .data_format_conversion import DataFormatConversion
from welcome_page import WelcomeWindow2


class ToolsWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 变量
        self.data_format_conversion_window = None
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

        # 2. 添加dock窗口
        self.create_dock_left()

        # 3. 绑定信号槽
        self.bind_signal_slot()

    # 绑定信号槽
    def bind_signal_slot(self):
        self.tool_box.currentChanged.connect(self.set_arrow)
        self.btn_xlsx2csv_desensitization.clicked.connect(self.open_excel_to_csv_window)
        self.btn_exception_test.clicked.connect(self.raise_exception_test)

    def raise_exception_test(self):
        raise Exception()

    def open_excel_to_csv_window(self):
        if not self.data_format_conversion_window:
            self.data_format_conversion_window = DataFormatConversion()
            self.stack_window.addWidget(self.data_format_conversion_window)
            self.stack_window.setCurrentWidget(self.data_format_conversion_window)

    def set_arrow(self, index):
        for i in range(self.tool_box.count()):
            self.tool_box.setItemIcon(i, self.arrow_right)
        self.tool_box.setItemIcon(index, self.arrow_down)

    # 添加 dock 窗口
    def create_dock_left(self):
        # 1. 创建 左Dock窗口
        self.dock = QDockWidget('工具')
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock)
        self.dock.setFixedWidth(260)
        self.dock.setFeatures(QDockWidget.NoDockWidgetFeatures)

        self.arrow_right = self.style().standardPixmap(QStyle.StandardPixmap.SP_ArrowRight)
        self.arrow_down = self.style().standardPixmap(QStyle.StandardPixmap.SP_ArrowDown)

        # 2. 创建 QToolBox 控件
        self.tool_box = QToolBox(self.dock)
        # 2.1 第一页
        self.create_data_manage_scrollarea()
        # 2.2 第二页
        self.tool_page_002 = QWidget()
        self.pbtn_002 = QPushButton('第二页按钮')
        self.layout_002 = QVBoxLayout(self.tool_page_002)
        self.layout_002.addWidget(self.pbtn_002)
        # 2.3 第三页
        self.tool_page_003 = QWidget()
        self.pbtn_003 = QPushButton('第三页按钮')
        self.layout_003 = QVBoxLayout(self.tool_page_003)
        self.layout_003.addWidget(self.pbtn_003)
        # 2.4 把第一、二、三等页加入 QToolBox 中
        self.tool_box.addItem(self.data_manage_scrollarea, self.arrow_down, '数据管理')
        self.tool_box.addItem(self.tool_page_002, self.arrow_right, '工具栏第二页')
        self.tool_box.addItem(self.tool_page_003, self.arrow_right, '工具栏第三页')

        # 3. 把 QToolBox控件加入 左Dock窗口中
        self.dock_wighet = QWidget(self.dock)  # Dock不会出现抬头标题栏
        self.dock_wighet.setGeometry(0, 0, 260, 1020)
        self.dock_wighet_layout = QVBoxLayout()
        self.dock_wighet_layout.addWidget(self.tool_box)
        self.dock_wighet.setLayout(self.dock_wighet_layout)
        # self.dock.setWidget(self.dock_wighet)  # 会出现抬头标题栏

    def create_data_manage_scrollarea(self):
        # 1. 创建布局控件
        self.data_manage_scrollarea = QScrollArea()
        self.data_manage_scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.data_manage_scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # 2. 创建布局
        self.layout_scrollarea = QVBoxLayout(self.data_manage_scrollarea)
        self.layout_scrollarea.setSpacing(10)
        # self.layout_scrollarea.setContentsMargins(5,0,0,5)
        # 3. 创建具体按钮
        self.btn_xlsx2csv_desensitization = QPushButton('文件格式转换和脱敏', self.data_manage_scrollarea)
        self.btn_spare_001 = QPushButton('备用', self.data_manage_scrollarea)
        self.btn_spare_002 = QPushButton('备用', self.data_manage_scrollarea)
        self.btn_exception_test = QPushButton('异常测试', self.data_manage_scrollarea)
        self.spacer = QWidget(self.data_manage_scrollarea)
        self.spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # 4. 将按钮加入布局
        self.layout_scrollarea.addWidget(self.btn_xlsx2csv_desensitization)
        self.layout_scrollarea.addWidget(self.btn_spare_001)
        self.layout_scrollarea.addWidget(self.btn_spare_002)
        self.layout_scrollarea.addWidget(self.btn_exception_test)
        self.layout_scrollarea.addWidget(self.spacer)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = ToolsWindow()
    w.show()
    exit(app.exec())
