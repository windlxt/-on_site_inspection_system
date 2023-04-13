"""
作者：无用
心境：行到水穷处 坐看云起时
日期：2023年04月05日
"""
import sys
import qdarkstyle
from PySide6.QtWidgets import QApplication, QMainWindow
from main_window_ui import Ui_MainWindow


class MyMainWindow(QMainWindow, Ui_MainWindow):
    """主窗口类"""
    def __init__(self):
        """初始化"""
        super().__init__()
        self.setupUi(self)


if __name__ == '__main__':
    """程序入口"""
    app = QApplication(sys.argv)
    window = MyMainWindow()
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api="pyside6"))
    window.showFullScreen()
    sys.exit(app.exec())
