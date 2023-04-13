"""
作者：无用
心境：行到水穷处 坐看云起时
日期：2023年04月05日
"""
import sys
import threading
import traceback
import types
import webbrowser

from PySide6.QtCore import Signal, QSize, Qt
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (QMenu, QMenuBar, QSizePolicy, QStatusBar, QWidget,
                               QTextEdit, QPushButton, QHBoxLayout, QVBoxLayout,
                               QStackedWidget, QToolBar, QDockWidget)
from bank_supervision import BankSupervisionWindow
from insurance_supervision import InsuranceSupervisionWindow
from tools import ToolsWindow
from welcome_page import WelcomeWindow


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):

        # 1. 设置主窗口属性
        self.setWindowFlag(Qt.FramelessWindowHint)  # 隐藏标题栏
        self.setIconSize(QSize(55, 55))  # 设置图标显示大小

        # 2. 设置中心窗口控件、布局
        self.set_main_window_wighets(MainWindow)

        # 3. 异常处理
        self.handle_exception()

        # 4. 设置菜单栏
        self.set_main_window_menubar(MainWindow)

        # 5. 设置工具条
        self.set_main_window_toolbar(MainWindow)

        # 6. 设置状态栏
        self.set_statusbar(MainWindow)

        # 7. 设置 左Dock 窗口, 显示 readme.md 文件
        self.set_dock_left(MainWindow)

        # 8. 设置 右Dock 窗口, 显示 异常信息, 必须在异常处理函数 self.handle_exception() 之后
        self.set_dock_right(MainWindow)

        # 9. 绑定信号槽函数
        self.bind_signal_slot()

    # /////////////////////////////////////////////////////////////////////////
    # 设置主窗口属性
    def set_main_window_wighets(self, MainWindow):
        self.centralwidget = QWidget(MainWindow)
        MainWindow.setCentralWidget(self.centralwidget)

        # 1. 设置主窗口中心区域，添加窗口栈
        self.stack_window = QStackedWidget()
        self.show_welcome_window = WelcomeWindow()                              # 0. 欢迎窗口
        self.show_bank_supervision_window = BankSupervisionWindow()             # 1. 银行监管窗口
        self.show_insurance_supervision_window = InsuranceSupervisionWindow()   # 2. 保险监管窗口
        self.show_tools_window = ToolsWindow()                                  # 3. 工具窗口

        self.stack_window.addWidget(self.show_welcome_window)
        self.stack_window.addWidget(self.show_bank_supervision_window)
        self.stack_window.addWidget(self.show_insurance_supervision_window)
        self.stack_window.addWidget(self.show_tools_window)

        self.setCentralWidget(self.stack_window)  # 设置中心窗口区域
        self.stack_window.setCurrentWidget(self.show_welcome_window)  # 选择当前窗口

    # 设置菜单栏
    def set_main_window_menubar(self, MainWindow):
        self.menubar = QMenuBar()

        # 1. 文件菜单
        self.menuFile = QMenu('文件')

        self.action_bank_supervision = QAction(MainWindow)
        self.action_bank_supervision.setText(u"银行监管")
        self.action_bank_supervision.setIcon(QIcon('./icons/p1.svg'))
        self.action_bank_supervision.setShortcut('Ctrl+H')
        self.action_bank_supervision.setStatusTip('银行监管')
        self.action_bank_supervision.setCheckable(True)

        self.action_insurance_supervision = QAction(MainWindow)
        self.action_insurance_supervision.setText(u"保险监管")
        self.action_insurance_supervision.setIcon(QIcon('./icons/p2.svg'))
        self.action_insurance_supervision.setShortcut('Ctrl+I')
        self.action_insurance_supervision.setStatusTip('保险监管')
        self.action_insurance_supervision.setCheckable(True)

        self.action_tools = QAction(MainWindow)
        self.action_tools.setText(u"工具")
        self.action_tools.setIcon(QIcon('./icons/p3.svg'))
        self.action_tools.setShortcut('Ctrl+T')
        self.action_tools.setStatusTip('工具')
        self.action_tools.setCheckable(True)

        self.action_exit = QAction(MainWindow)
        self.action_exit.setText(u"退出")
        self.action_exit.setIcon(QIcon('./icons/exit.ico'))
        self.action_exit.setShortcut('Ctrl+Q')
        self.action_exit.setStatusTip('退出')

        self.menuFile.addAction(self.action_bank_supervision)
        self.menuFile.addAction(self.action_insurance_supervision)
        self.menuFile.addAction(self.action_tools)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.action_exit)
        self.menubar.addMenu(self.menuFile)
        # 2. 帮助菜单
        self.menuHelp = QMenu('帮助')

        self.action_welcome = QAction(MainWindow)
        self.action_welcome.setText(u"欢迎页面")
        self.action_welcome.setIcon(QIcon('./icons/icon_widgets.svg'))
        self.action_welcome.setShortcut('Ctrl+W')

        self.action_help = QAction(MainWindow)
        self.action_help.setText(u"关于...")
        self.action_help.setIcon(QIcon('./icons/pyecharts.png'))
        self.action_help.setShortcut('Ctrl+H')

        self.menuHelp.addAction(self.action_welcome)
        self.menuHelp.addAction(self.action_help)
        self.menubar.addMenu(self.menuHelp)

        # 3.设置菜单条
        MainWindow.setMenuBar(self.menubar)

    # 设置工具条
    def set_main_window_toolbar(self, MainWindow):
        """
        增加工具栏， 并添加功能按钮
        """
        # 1. 创建toolbar对象
        self.tool_bar = QToolBar()
        MainWindow.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.tool_bar)
        self.tool_bar.setMovable(False)
        # self.tool_bar.setMinimumWidth(78)

        # 2. 设置按钮
        # 增加按钮1, 显示和隐藏工具栏文本
        self.action_show_hide_text = QAction()
        self.action_show_hide_text.setText('隐藏')
        self.action_show_hide_text.setIcon(QIcon('./icons/icon_menu.svg'))
        self.action_show_hide_text.setStatusTip('显示或隐藏工具按钮说明')
        self.show_hide_text_flag = False

        # 在按钮之间增加弹簧, 控制按钮摆放位置
        self.spacer = QWidget()
        self.spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 增加按钮2, 显示和隐藏主窗口 Dock
        self.action_show_hide_dock = QAction()
        self.action_show_hide_dock.setText('显示信息')
        self.action_show_hide_dock.setIcon(QIcon('./icons/icon_info.svg'))
        self.action_show_hide_dock.setStatusTip('显示系统信息')

        # 3. 给上面的toolbar对象绑定QAction事件
        self.tool_bar.addAction(self.action_show_hide_text)
        self.tool_bar.addSeparator()
        self.tool_bar.addAction(self.action_bank_supervision)
        self.tool_bar.addAction(self.action_insurance_supervision)
        self.tool_bar.addAction(self.action_tools)
        self.tool_bar.addSeparator()
        self.tool_bar.addAction(self.action_exit)
        self.tool_bar.addWidget(self.spacer)  # 弹簧
        self.tool_bar.addAction(self.action_show_hide_dock)

    # 设置状态栏
    def set_statusbar(self, MainWindow):
        self.statusbar = QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)

    # 设置 左Dock 窗口, 显示 readme.md 文件
    def set_dock_left(self, MainWindow):
        self.dock_left = QDockWidget("系统说明", MainWindow)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_left)
        self.dock_left.setFixedWidth(260)
        self.dock_left.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.dock_left.setVisible(False)

        # 设置文本显示
        text_edit = QTextEdit(self.dock_left)
        text_edit.setGeometry(0, 0, 260, 1020)

        with open('./readme.md', 'r') as f:
            file = f.readlines()
        for line in file:
            text_edit.append(line)
        # t = text_edit.toPlainText()
        # print(t)

    # 设置 右Dock 窗口, 显示 异常信息, 必须在异常处理函数 self.handle_exception() 之后
    def set_dock_right(self, MainWindow):
        self.dock_right = QDockWidget(MainWindow)
        self.dock_right.setTitleBarWidget(QWidget())
        # self.dock_right.setMinimumWidth(300)
        self.dock_right.setVisible(False)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_right)

        # 窗口内容显示
        wighet_dock = QWidget()
        wighet_dock.setFixedHeight(710)

        # ===============================================================
        spacer1 = QWidget()
        spacer1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        spacer2 = QWidget()
        spacer2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # =====================================================
        wighet_title = QWidget()  # 标题
        hlayout_title = QHBoxLayout(wighet_title)  # 标题布局
        lb_title = QPushButton('程序异常信息')
        lb_title.setStyleSheet('QPushButton {'
                               'background-color: #ff5050;'
                               'padding: 5px;'
                               'font-size: 16px;'
                               'width: 570px;'
                               'height: 25px;}')
        hlayout_title.addWidget(lb_title)
        hlayout_title.addWidget(spacer1)
        # =====================================================
        self.pbtn_right_dock_close = QPushButton('关闭')
        self.pbtn_right_dock_close.setStyleSheet('QPushButton {'
                                                 'background-color: #2ABf9E;'
                                                 'padding: 5px;'
                                                 'font-size: 16px;'
                                                 'width: 280px;'
                                                 'height: 15px;}')
        # =====================================================
        wighet_close_pbtn = QWidget()
        hlayout_close_pbtn = QHBoxLayout(wighet_close_pbtn)
        hlayout_close_pbtn.addWidget(self.pbtn_right_dock_close)
        hlayout_close_pbtn.addWidget(spacer2)
        # =====================================================
        vlayout_wighet_dock = QVBoxLayout(wighet_dock)  # 整体布局
        vlayout_wighet_dock.addWidget(wighet_title)  # 加标题
        vlayout_wighet_dock.addWidget(self.exception_widget)  # 加异常窗口
        vlayout_wighet_dock.addWidget(wighet_close_pbtn)  # 加关闭按钮

        self.dock_right.setWidget(wighet_dock)

    # ////////////////////////////////////////////////////////////////////////////////
    # 绑定信号槽函数
    def bind_signal_slot(self):
        # 1. 激活菜单和工具栏按钮关联方法
        self.action_show_hide_text.triggered.connect(self.show_hide_toolbar_text)
        self.action_bank_supervision.triggered.connect(self.open_bank_supervision_window)
        self.action_insurance_supervision.triggered.connect(self.open_insurance_supervision_window)
        self.action_tools.triggered.connect(self.open_tools_window)
        self.action_exit.triggered.connect(self.app_exit)
        self.action_show_hide_dock.triggered.connect(self.show_hide_dock_func)
        self.action_welcome.triggered.connect(self.open_welcome_window)
        self.action_help.triggered.connect(self.show_hide_dock_func)
        self.pbtn_right_dock_close.clicked.connect(self.dock_right.close)

    # 显示主窗口 Dock 窗口，用于显示系统信息
    def show_hide_dock_func(self):
        if self.dock_left.isVisible():
            self.dock_left.setVisible(False)
        else:
            self.dock_left.setVisible(True)

    # 显示左边工具栏上图标的文字说明
    def show_hide_toolbar_text(self):
        if not self.show_hide_text_flag:
            self.show_hide_text_flag = True
            self.tool_bar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            self.tool_bar.setFixedWidth(150)
            self.action_show_hide_text.setIcon(QIcon('./icons/icon_menu_close.svg'))
            for action in self.tool_bar.actions():
                widget = self.tool_bar.widgetForAction(action)
                widget.setFixedWidth(150)
        else:
            self.show_hide_text_flag = False
            self.tool_bar.setToolButtonStyle(Qt.ToolButtonIconOnly)
            self.action_show_hide_text.setIcon(QIcon('./icons/icon_menu.svg'))
            for action in self.tool_bar.actions():
                widget = self.tool_bar.widgetForAction(action)
                widget.setFixedWidth(63)

    # 打开 欢迎 窗口
    def open_welcome_window(self):
        # 设置菜单、工具栏上的按钮状态可选项，显示选中状态
        self.action_insurance_supervision.setChecked(False)
        self.action_bank_supervision.setChecked(False)
        self.action_tools.setChecked(False)
        # 显示窗口
        self.stack_window.setCurrentWidget(self.show_welcome_window)

    # 打开 银行监管 窗口
    def open_bank_supervision_window(self):
        # 设置菜单、工具栏上的按钮状态可选项，显示选中状态
        self.action_insurance_supervision.setChecked(False)
        self.action_bank_supervision.setChecked(True)
        self.action_tools.setChecked(False)
        # 显示窗口
        self.stack_window.setCurrentWidget(self.show_bank_supervision_window)

    # 打开 保险监管 窗口
    def open_insurance_supervision_window(self):
        # 设置菜单、工具栏上的按钮状态可选项，显示选中状态
        self.action_insurance_supervision.setChecked(True)
        self.action_bank_supervision.setChecked(False)
        self.action_tools.setChecked(False)
        # 显示窗口
        self.stack_window.setCurrentWidget(self.show_insurance_supervision_window)

    def open_tools_window(self):
        # 设置菜单、工具栏上的按钮状态可选项，显示选中状态
        self.action_tools.setChecked(True)
        self.action_insurance_supervision.setChecked(False)
        self.action_bank_supervision.setChecked(False)
        # 显示窗口
        self.stack_window.setCurrentWidget(self.show_tools_window)

    # 静态系统退出函数
    @staticmethod
    def app_exit():
        sys.exit()

    # ///////////////////////////////////////////////////////////////////////////////////////
    #  异常处理，在右 Dock 窗口中显示
    def handle_exception(self):  # Exception Handling
        self.exception_widget: ExceptionWidget = ExceptionWidget()

        def excepthook(exctype: type, value: Exception, tb: types.TracebackType) -> None:
            """Show exception detail with QMessageBox."""
            sys.__excepthook__(exctype, value, tb)

            msg: str = "".join(traceback.format_exception(exctype, value, tb))
            self.exception_widget.signal.emit(msg)
            self.dock_right.setVisible(True)  # 显示右 Dock 窗口

        sys.excepthook = excepthook

        if sys.version_info >= (3, 8):
            def threading_excepthook(args: threading.ExceptHookArgs) -> None:
                """Show exception detail from background threads with QMessageBox."""
                sys.__excepthook__(args.exc_type, args.exc_value, args.exc_traceback)

                msg: str = "".join(traceback.format_exception(args.exc_type, args.exc_value, args.exc_traceback))
                self.exception_widget.signal.emit(msg)
                self.dock_right.setVisible(True)

            threading.excepthook = threading_excepthook


class ExceptionWidget(QWidget):
    """"""
    signal: Signal = Signal(str)

    def __init__(self, parent: QWidget = None) -> None:
        """"""
        super().__init__(parent)

        self.init_ui()
        self.signal.connect(self.show_exception)

    def init_ui(self) -> None:
        """"""
        self.setWindowTitle("触发异常")
        self.setFixedSize(600, 600)

        self.msg_edit: QTextEdit = QTextEdit()
        self.msg_edit.setReadOnly(True)

        copy_button: QPushButton = QPushButton("复制")
        copy_button.clicked.connect(self._copy_text)

        community_button: QPushButton = QPushButton("求助")
        community_button.clicked.connect(self._open_community)

        close_button: QPushButton = QPushButton("关闭")
        close_button.clicked.connect(self.close)

        hbox: QHBoxLayout = QHBoxLayout()
        hbox.addWidget(copy_button)
        hbox.addWidget(community_button)
        # hbox.addWidget(close_button)

        vbox: QVBoxLayout = QVBoxLayout()
        vbox.addWidget(self.msg_edit)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

    def show_exception(self, msg: str) -> None:
        """"""
        self.msg_edit.setText(msg)
        # self.show()

    def _copy_text(self) -> None:
        """"""
        self.msg_edit.selectAll()
        self.msg_edit.copy()

    def _open_community(self) -> None:
        """"""
        webbrowser.open("https://www.baidu.com")
