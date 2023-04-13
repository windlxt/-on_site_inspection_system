"""
作者：无用
心境：行到水穷处 坐看云起时
日期：2023年04月06日
"""
import os
import sys
import pandas as pd
import numpy as np
import time
import threading
from multiprocessing import Pool, Process
from PySide6.QtCore import QRect, Qt, QThread, QObject, Signal
from PySide6.QtGui import QColor, QPalette, QFont
from PySide6.QtWidgets import QApplication, QWidget, QScrollArea, \
    QHBoxLayout, QPushButton, QMainWindow, QLabel, QDockWidget, QVBoxLayout, QSizePolicy, QFrame, QStackedWidget, \
    QGroupBox, QTextEdit, QToolBox, QStyle, QGridLayout, QLineEdit, QProgressBar, QTableWidget, QCheckBox, QFileDialog, \
    QListWidget, QMessageBox


# 工作类，并继承QObject================================================
class Worker(QObject):
    """线程工作类"""
    progress = Signal()
    completed = Signal(int)

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

    # 需要执行的耗时任务
    def do_work_xlsx2csv(self):
        """
        文件格式转换
        多进程：只适用于大量计算，不适用于图形界面刷新（会竞争QPainter类）
        """
        self.progress.emit()

        numList = []
        for i, file in enumerate(self.parent.files_selected):
            p = Process(target=self.xlsx_to_csv, args=(i, file,))
            p.start()
            numList.append(p)

        for process in numList:
            process.join()
        print("Process end.")
        self.completed.emit(i+1)

    def xlsx_to_csv(self, i, file):
        path_file = os.path.join(self.parent.path_selected_dir, file)
        df_xlsx = pd.read_excel(path_file)
        print(df_xlsx.head())
        f = os.path.splitext(file)[0]
        self.file_name = f + '.csv'
        file_csv = os.path.join(self.parent.path_save_dir, self.file_name)
        df_xlsx.to_csv(file_csv, columns=df_xlsx.columns, index=True, encoding='utf-8')
        # xlsx.to_csv(file_csv, columns=xlsx.columns, index=True, encoding='gb2312')
        print(f'{file} to .csv is OK.')
        print(f'第 {i+1} 个文件转换完毕！')
        print('-' * 80)


# 进度条刷新类
class WorkerProgress(QObject):
    """界面刷新中，有sleep的，必须多线程"""
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

    def update_progress(self):
        for i in range(len(self.parent.files_selected)):
            time.sleep(1)
            self.parent.progress_bar_left.setValue(i)  # 与线程内的progress信号绑定，更新进度条


# 脱敏工作类======================================================================================
name_one = ['豁达', '潇洒', '雍容', '轩昂', '爽朗', '悠然', '从容', '坦荡', '大方', '宽容',
            '厚道', '风度', '高雅', '情调', '淡泊', '迷人', '安然', '宁静', '随和', '随性',
            '傲骨', '大气', '柔韧', '洋气', '海涵', '儒雅', '淡定', '漂亮', '可爱', '美丽',
            '黑暗', '强壮', '丑陋', '小巧', '精致']
name_two = ['老虎', '黄莺', '鸳鸯', '猴子', '狐狸', '蝴蝶', '袋鼠', '熊猫', '蜻蜓', '黄鳝', '海马', '鳄鱼',
            '斑马', '蚯蚓', '喜鹊', '松鼠', '鹦鹉', '羚羊', '牦牛', '考拉', '海豚', '天鹅', '海鸥', '孔雀',
            '杜鹃', '八哥', '蝎子', '大象', '猩猩', '狗熊']


class WorkerDesensitization(QObject):
    """线程工作类"""
    progress = Signal()
    completed = Signal(int)

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

    # 需要执行的耗时任务
    def do_work_desensitization(self):
        """
        文件脱敏
        多进程：只适用于大量计算，不适用于图形界面刷新（会竞争QPainter类）
        """
        self.progress.emit()

        numList = []
        for i, file in enumerate(self.parent.files_sensitive_selected):
            p = Process(target=self.random_name_and_code, args=(i, file,))
            p.start()
            numList.append(p)

        for process in numList:
            process.join()
        print("Process end.")
        self.completed.emit(i+1)

    def random_name_and_code(self, i, file):
        path_selected_dir = self.parent.ledit_select_right.text()
        file_path = os.path.join(path_selected_dir, file)
        try:
            f_csv = pd.read_csv(file_path)
        except:
            print('error')
            raise Exception()

        print(f_csv.head())
        j = f_csv.columns.get_indexer(['户名'])
        print('j=', j)
        for i in range(f_csv.shape[0]):
            f_csv.iloc[i, j] = str(np.random.choice(name_one, 1)[0]) + '的' + str(np.random.choice(name_two, 1)[0])
        f_csv.to_csv(file_path, columns=f_csv.columns, index=True, encoding='utf-8')
        print(f'{file} 户名 convert is OK.')
        print('-' * 80)


# 进度条刷新类
class WorkerProgressDesensitization(QObject):
    """界面刷新中，有sleep的，必须多线程"""
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

    def update_progress(self):
        for i in range(len(self.parent.files_sensitive_selected)):
            time.sleep(1)
            self.parent.progress_bar_right.setValue(i)  # 与线程内的progress信号绑定，更新进度条

# 单例模式==============================================================================================
class Singleton:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            # cls._instance = super(Singleton, cls).__new__(cls)
            cls._instance = super().__new__(cls)  # 类的属性
        return cls._instance


# 主窗口类
class DataFormatConversion(QWidget, Singleton):
    """文件格式转换主窗口类"""
    a1 = Signal()  # 全局信号
    a2 = Signal()  # 全局信号

    def __init__(self):
        super().__init__()
        # 1. 设置窗口控件布局
        self.setupUi()

        # 2. 绑定信号槽
        self.bind_signal_slot()

        # 创建一个线程和一个工作实例
        #===================================
        self.worker = Worker(self)
        self.worker_thread = QThread()

        self.worker_p = WorkerProgress(self)
        self.worker_p_thread = QThread()
        # ===================================
        self.worker_desensitization = WorkerDesensitization(self)
        self.worker_thread_desensitization = QThread()

        self.worker_p_desensitization = WorkerProgressDesensitization(self)
        self.worker_p_thread_desensitization = QThread()


        # 线程里的progress信号与进度条更新函数绑定
        self.worker.progress.connect(self.worker_p.update_progress)
        self.worker_desensitization.progress.connect(self.worker_p_desensitization.update_progress)
        # 线程里的completes信号与完成函数绑定
        self.worker.completed.connect(self.complete)
        self.worker_desensitization.completed.connect(self.complete_desensitization)

        # 全局信号绑定工作实例的方法
        self.a1.connect(self.worker.do_work_xlsx2csv)
        self.a2.connect(self.worker_desensitization.do_work_desensitization)

        # 把工作实例放进线程里
        self.worker.moveToThread(self.worker_thread)
        self.worker_p.moveToThread(self.worker_p_thread)

        self.worker_desensitization.moveToThread(self.worker_thread_desensitization)
        self.worker_p_desensitization.moveToThread(self.worker_p_thread_desensitization)

    def start(self):
        # 开始线程
        self.worker_thread.start()
        self.worker_p_thread.start()

        self.a1.emit()  # 给全局信号发信号，触发线程内工作实例的方法执行

    def start_desensitization(self):
        # 开始线程
        self.worker_thread_desensitization.start()
        self.worker_p_thread_desensitization.start()

        self.a2.emit()  # 给全局信号发信号，触发线程内工作实例的方法执行

    def complete(self, v):  # 与线程内completed信号绑定，线程工作一结束就会触发此函数
        self.worker_p_thread.terminate()
        self.worker_p_thread.quit()
        self.worker_p_thread.wait()
        self.progress_bar_left.setValue(v)

        # 线程内的耗时任务执行完了，但创建的这个线程不一定也会结束，所以还需下面几句来主动退出
        print(self.worker_thread.isRunning())  # 打印True表示线程还在
        self.worker_thread.quit()  # 结束线程
        self.worker_thread.wait()  # 等待线程结束

        print(self.worker_thread.isRunning())  # 打印False表示线程已退出
        # 注意：没有quit()和wait()，在x掉窗口时控制台会报“QThread: Destroyed while thread is still running”

        file_list = os.listdir(self.path_save_dir)
        file_list.sort()
        self.lw_save.addItems(file_list)  # 显示已转换的文件

    def complete_desensitization(self, v):

        self.worker_p_thread_desensitization.terminate()
        self.worker_p_thread_desensitization.quit()
        self.worker_p_thread_desensitization.wait()
        self.progress_bar_right.setValue(v)

        # 线程内的耗时任务执行完了，但创建的这个线程不一定也会结束，所以还需下面几句来主动退出
        print(self.worker_thread_desensitization.isRunning())  # 打印True表示线程还在
        self.worker_thread_desensitization.quit()  # 结束线程
        self.worker_thread_desensitization.wait()  # 等待线程结束

        print(self.worker_p_thread_desensitization.isRunning())  # 打印False表示线程已退出
        # 注意：没有quit()和wait()，在x掉窗口时控制台会报“QThread: Destroyed while thread is still running”

        #TODO(完善右下显示)


    # 绑定信号槽
    def bind_signal_slot(self):
        self.pbtn_select_left.clicked.connect(self.select_xlsx_file_dir)
        self.pbtn_save.clicked.connect(self.save_csv_file_dir)
        self.pbtn_begin_left.clicked.connect(self.begin_file_format_conversion)


        self.pbtn_select_right.clicked.connect(self.select_sensitive_file_dir)

        self.pbtn_begin_right.clicked.connect(self.begin_desensitization)

    def begin_file_format_conversion(self):
        self.path_selected_dir = self.ledit_select_left.text()
        self.path_save_dir = self.ledit_save.text()
        if not self.path_selected_dir or not self.path_save_dir:
            QMessageBox.information(self, '提示', '请选择要转换的文件和存储位置', QMessageBox.Ok)
            return
        if not os.path.exists(self.path_save_dir):
            os.mkdir(self.path_save_dir)

        self.files_selected = os.listdir(self.path_selected_dir)
        print(self.files_selected)
        print(self.path_save_dir)

        # 设置进度条
        self.progress_bar_left.setValue(0)
        n = len(self.files_selected)
        self.progress_bar_left.setMaximum(n)

        # 启动线程
        self.start()

        # with Pool(16) as p:
        #     p.map(self.xlsx_to_csv, self.files_selected)

        # print('before Pool')
        # pool = Pool(16)
        # print('Pool')
        # pool_res = pool.map_async(, self.files_selected)  # 非阻塞异步运行多进程
        # pool.close()
        # pool.join()

    def begin_desensitization(self):
        flag_name = self.check_name.checkState()
        flag_id = self.check_id.checkState()
        if not flag_name and not flag_id:
            QMessageBox.information(self, '提示', '至少选择一个需要脱敏的字段', QMessageBox.Ok)
            return

        path_selected_dir = self.ledit_select_right.text()

        if not path_selected_dir:
            QMessageBox.information(self, '提示', '请选择要脱敏的文件位置', QMessageBox.Ok)
            return

        self.files_sensitive_selected = os.listdir(path_selected_dir)
        print(self.files_sensitive_selected)


        # 设置进度条
        self.progress_bar_right.setValue(0)
        n = len(self.files_sensitive_selected)
        self.progress_bar_right.setMaximum(n)

        # 启动线程
        self.start_desensitization()


    def save_csv_file_dir(self):
        """选择文件存储路径"""
        self.path_save_dir = QFileDialog.getExistingDirectory(None, '选择文件存储路径', os.getcwd())
        if self.path_save_dir:
            self.ledit_save.setText(self.path_save_dir)  # 文件夹目录

    def select_xlsx_file_dir(self):
        """选择文件夹，获取需要分析的文件"""
        path_dir = QFileDialog.getExistingDirectory(None, '选择文件夹路径', os.getcwd())
        if path_dir:
            self.ledit_select_left.setText(path_dir)  # 文件夹目录
            file_list = os.listdir(path_dir)
            file_list.sort()
            self.lw_select.addItems(file_list)  # 显示文件夹目录下得文件

    def select_sensitive_file_dir(self):
        """选择文件夹，获取需要分析的文件"""
        path_dir = QFileDialog.getExistingDirectory(None, '选择文件夹路径', os.getcwd())
        if path_dir:
            self.ledit_select_right.setText(path_dir)  # 文件夹目录


    # 设置窗口控件布局
    def setupUi(self):
        # 标题 左
        self.font = QFont()
        self.font.setFamily("方正黑体简体")
        self.font.setPointSize(32)

        self.lab_title_left = QLabel(self)
        self.lab_title_left.setGeometry(QRect(20, 10, 750, 80))
        self.lab_title_left.setFont(self.font)
        self.lab_title_left.setFrameShape(QFrame.NoFrame)
        self.lab_title_left.setFrameShadow(QFrame.Plain)
        self.lab_title_left.setTextFormat(Qt.AutoText)
        self.lab_title_left.setAlignment(Qt.AlignCenter)
        self.lab_title_left.setText("Excel格式文件 转换 csv格式文件")
        #标题 右
        self.lab_title_right = QLabel(self)
        self.lab_title_right.setGeometry(QRect(800, 10, 750, 80))
        self.lab_title_right.setFont(self.font)
        self.lab_title_right.setFrameShape(QFrame.NoFrame)
        self.lab_title_right.setFrameShadow(QFrame.Plain)
        self.lab_title_right.setTextFormat(Qt.AutoText)
        self.lab_title_right.setAlignment(Qt.AlignCenter)
        self.lab_title_right.setText("文件脱敏")

        # 操作区域 左上
        self.font.setFamily("黑体")
        self.font.setPointSize(14)

        self.groupBox_left_up = QGroupBox(self)
        self.groupBox_left_up.setGeometry(QRect(20, 100, 750, 200))

        self.ledit_select_left = QLineEdit(self)
        self.ledit_select_left.setGeometry(30, 120, 530, 40)
        self.pbtn_select_left = QPushButton('打开文件目录', self)
        self.pbtn_select_left.setGeometry(575, 120, 180, 40)

        self.ledit_save = QLineEdit(self)
        self.ledit_save.setGeometry(30, 180, 530, 40)
        self.pbtn_save = QPushButton('存储文件目录', self)
        self.pbtn_save.setGeometry(575, 180, 180, 40)

        self.progress_bar_left = QProgressBar(self)
        self.progress_bar_left.setGeometry(30, 240, 530, 40)
        self.pbtn_begin_left = QPushButton('开始转换', self)
        self.pbtn_begin_left.setGeometry(575, 240, 180, 40)

        # 显示区域 左下
        self.groupBox_left_down = QGroupBox(self)
        self.groupBox_left_down.setGeometry(QRect(20, 310, 750, 700))

        self.lw_select = QListWidget(self)
        self.lw_select.setGeometry(QRect(30, 330, 345, 660))
        self.lw_save = QListWidget(self)
        self.lw_save.setGeometry(QRect(415, 330, 345, 660))

        # 操作区域 右上
        self.groupBox_right_up = QGroupBox(self)
        self.groupBox_right_up.setGeometry(QRect(800, 100, 750, 200))

        self.ledit_select_right = QLineEdit(self)
        self.ledit_select_right.setGeometry(810, 120, 530, 40)
        self.pbtn_select_right = QPushButton('打开文件目录', self)
        self.pbtn_select_right.setGeometry(1355, 120, 180, 40)

        self.label_right = QLabel(self)
        self.label_right.setGeometry(810, 180, 150, 40)
        self.label_right.setText('请选择脱敏字段：')
        self.label_right.setFont(self.font)
        self.check_name = QCheckBox(self)
        self.check_name.setGeometry(1010, 180, 100, 40)
        self.check_name.setText('  姓名')
        self.check_name.setFont(self.font)
        self.check_id = QCheckBox(self)
        self.check_id.setGeometry(1130, 180, 150, 40)
        self.check_id.setText('  身份证号码')
        self.check_id.setFont(self.font)



        self.progress_bar_right = QProgressBar(self)
        self.progress_bar_right.setGeometry(810, 240, 530, 40)
        self.pbtn_begin_right = QPushButton('开始转换', self)
        self.pbtn_begin_right.setGeometry(1355, 240, 180, 40)

        # 显示区域 右下
        self.groupBox_left_down = QGroupBox(self)
        self.groupBox_left_down.setGeometry(QRect(800, 310, 750, 700))

        self.tw_right = QTableWidget(self)
        self.tw_right.setGeometry(QRect(810, 330, 730, 660))
        # self.tw_right.setColumnCount(0)
        # self.tw_right.setRowCount(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = DataFormatConversion()
    w.show()
    app.exec()
