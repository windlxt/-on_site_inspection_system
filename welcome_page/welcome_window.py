"""
作者：无用
心境：行到水穷处 坐看云起时
日期：2023年04月06日
"""

import sys
from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QColor, QPalette, QBrush
from PySide6.QtWidgets import QApplication, QWidget, QScrollArea, \
    QHBoxLayout, QPushButton, QMainWindow, QLabel, QDockWidget, QVBoxLayout, QSizePolicy, QFrame, QStackedWidget, \
    QGroupBox


class WelcomeWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet('background-image: url(./icons/2.jpg);'
                           'background-repeat:no-repeat;'
                           'background-position:bottom center;')

        self.main_layout = QVBoxLayout(self)
        self.label_1 = QLabel()
        self.label_1.setText('韶 关 银 保 监 分 局')
        self.label_1.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)
        self.label_1.setStyleSheet('font: red;'
                                   'font-family: "Times New Roman";'
                                   'font-size: 80px;'
                                   'font-weight:bold;'
                                   'color: yellow;'
                                   )
        self.label_2 = QLabel()
        self.label_2.setText('现 场 检 查 系 统')
        self.label_2.setAlignment(Qt.AlignCenter)
        self.label_2.setStyleSheet('font: red;'
                                   'font-family: "隶书";'
                                   'font-size: 140px;'
                                   'font-weight:bold;'
                                   'color: yellow'
                                   )
        self.label_3 = QLabel()

        self.main_layout.addWidget(self.label_1)
        self.main_layout.addWidget(self.label_2)
        self.main_layout.addWidget(self.label_3)


class WelcomeWindow2(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet('background-image: url(./icons/1.webp);')

        self.main_layout = QVBoxLayout(self)
        self.w = QWidget()
        self.main_layout.addWidget(self.w)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = WelcomeWindow()
    w.show()
    exit(app.exec())
