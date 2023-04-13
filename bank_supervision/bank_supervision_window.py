"""
作者：无用
心境：行到水穷处 坐看云起时
日期：2023年04月05日
"""
import multiprocessing
import sys
from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication, QWidget, QScrollArea, \
    QHBoxLayout, QPushButton, QMainWindow, QLabel, QDockWidget, QVBoxLayout, QSizePolicy, QFrame, QStackedWidget, \
    QGroupBox, QStyle, QToolBox
from .loan_classification_analysis import LoanClassificationAnalysisWindow
from welcome_page import WelcomeWindow2


class BankSupervisionWindow(QMainWindow):
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
        self.btn_loan_classification.clicked.connect(self.open_loan_classification_analysis_window)

    # 槽函数：显示贷款分类窗口
    def open_loan_classification_analysis_window(self):
        self.multip_l = multiprocessing.Manager().list([])
        self.w = LoanClassificationAnalysisWindow(self.multip_l)
        self.w.show()

    # 设置ToolBox箭头方向
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
        self.create_bank_manage_scrollarea()  # 银行公司治理
        # 2.2 第二页
        self.create_bank_loan_transaction_scrollarea()  # 银行信贷业务
        # 2.3 第三页
        self.create_bank_asset_quality_scrollarea()  # 银行资产质量

        # 2.4 把第一、二、三等页加入 QToolBox 中
        self.tool_box.addItem(self.bank_manage_scrollarea, self.arrow_down, '银行公司治理')
        self.tool_box.addItem(self.bank_loan_transaction_scrollarea, self.arrow_right, '银行信贷业务')
        self.tool_box.addItem(self.bank_asset_quality_scrollarea, self.arrow_right, '银行资产质量')

        # 3. 把 QToolBox控件加入 左Dock窗口中
        self.dock_wighet = QWidget(self.dock)  # Dock不会出现抬头标题栏
        self.dock_wighet.setGeometry(0, 0, 260, 1020)
        self.dock_wighet_layout = QVBoxLayout()
        self.dock_wighet_layout.addWidget(self.tool_box)
        self.dock_wighet.setLayout(self.dock_wighet_layout)
        # self.dock.setWidget(self.dock_wighet)  # 会出现抬头标题栏

    def create_bank_manage_scrollarea(self):
        # 1. 创建布局控件
        self.bank_manage_scrollarea = QScrollArea()
        self.bank_manage_scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.bank_manage_scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # 2. 创建布局
        self.layout_scrollarea = QVBoxLayout(self.bank_manage_scrollarea)
        self.layout_scrollarea.setSpacing(10)
        # self.layout_scrollarea.setContentsMargins(5,0,0,5)
        # 3. 创建具体按钮
        self.btn_related_transaction = QPushButton('关联交易管理', self.bank_manage_scrollarea)
        self.btn_spare_001 = QPushButton('备用1', self.bank_manage_scrollarea)
        self.btn_spare_002 = QPushButton('备用2', self.bank_manage_scrollarea)
        self.btn_spare_003 = QPushButton('备用3', self.bank_manage_scrollarea)
        self.spacer = QWidget(self.bank_manage_scrollarea)
        self.spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # 4. 将按钮加入布局
        self.layout_scrollarea.addWidget(self.btn_related_transaction)
        self.layout_scrollarea.addWidget(self.btn_spare_001)
        self.layout_scrollarea.addWidget(self.btn_spare_002)
        self.layout_scrollarea.addWidget(self.btn_spare_003)
        self.layout_scrollarea.addWidget(self.spacer)

    def create_bank_loan_transaction_scrollarea(self):
        # 1. 创建布局控件
        self.bank_loan_transaction_scrollarea = QScrollArea()
        self.bank_loan_transaction_scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.bank_loan_transaction_scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # 2. 创建布局
        self.layout_scrollarea = QVBoxLayout(self.bank_loan_transaction_scrollarea)
        self.layout_scrollarea.setSpacing(10)
        # self.layout_scrollarea.setContentsMargins(5,0,0,5)
        # 3. 创建具体按钮
        self.btn_loan_fund_flow = QPushButton('贷款资金流向', self.bank_loan_transaction_scrollarea)
        self.btn_spare_001 = QPushButton('备用1', self.bank_loan_transaction_scrollarea)
        self.btn_spare_002 = QPushButton('备用2', self.bank_loan_transaction_scrollarea)
        self.btn_spare_003 = QPushButton('备用3', self.bank_loan_transaction_scrollarea)
        self.spacer = QWidget(self.bank_loan_transaction_scrollarea)
        self.spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # 4. 将按钮加入布局
        self.layout_scrollarea.addWidget(self.btn_loan_fund_flow)
        self.layout_scrollarea.addWidget(self.btn_spare_001)
        self.layout_scrollarea.addWidget(self.btn_spare_002)
        self.layout_scrollarea.addWidget(self.btn_spare_003)
        self.layout_scrollarea.addWidget(self.spacer)

    def create_bank_asset_quality_scrollarea(self):
        # 1. 创建布局控件
        self.bank_asset_quality_scrollarea = QScrollArea()
        self.bank_asset_quality_scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.bank_asset_quality_scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # 2. 创建布局
        self.layout_scrollarea = QVBoxLayout(self.bank_asset_quality_scrollarea)
        self.layout_scrollarea.setSpacing(10)
        # self.layout_scrollarea.setContentsMargins(5,0,0,5)
        # 3. 创建具体按钮
        self.btn_loan_classification = QPushButton('贷款分类准确度分析', self.bank_asset_quality_scrollarea)
        self.btn_spare_001 = QPushButton('备用1', self.bank_asset_quality_scrollarea)
        self.btn_spare_002 = QPushButton('备用2', self.bank_asset_quality_scrollarea)
        self.btn_spare_003 = QPushButton('备用3', self.bank_asset_quality_scrollarea)
        self.spacer = QWidget(self.bank_asset_quality_scrollarea)
        self.spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # 4. 将按钮加入布局
        self.layout_scrollarea.addWidget(self.btn_loan_classification)
        self.layout_scrollarea.addWidget(self.btn_spare_001)
        self.layout_scrollarea.addWidget(self.btn_spare_002)
        self.layout_scrollarea.addWidget(self.btn_spare_003)
        self.layout_scrollarea.addWidget(self.spacer)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = BankSupervisionWindow()
    w.show()
    exit(app.exec())

