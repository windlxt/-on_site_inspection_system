# 多进程间通信，通过共享的 list 实现！
import multiprocessing
import os
import sys
import pandas as pd
import datetime
from dateutil.parser import parse
import math
from multiprocessing import Pool
import time
from PySide6.QtWidgets import QMainWindow, QApplication, QMessageBox, QFileDialog, QTableWidgetItem, \
    QAbstractItemView, QMenu
from PySide6.QtCore import Qt, QThread, QTimer, Signal
from .loan_classification_analysis_ui import Ui_MainWindow
from PySide6.QtGui import QMovie, QTextCursor, QBrush, QColor
from PySide6.QtGui import QAction
from matplotlib import animation
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
plt.rcParams['font.family'] = ['sans-serif']
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.facecolor'] = 'snow'

# 定义文件目录路径
initial_filepath = r'./需要分析的贷款台账'
result_filepath = r'/home/lxt/data/分析结果'


# ------以下是全局函数：file_writer_text ----------------------
def file_writer_text(file_txt, content):
    """写入文本文件"""
    with open(file_txt, 'a+') as f:
        f.write(content)


# ------以下是：计算线程 ThreadCompute --------------------------
class ThreadCompute(QThread):
    """
    计算线程，包含主要占用CPU的运算。在 run() 函数中，再开辟进程池，通过多进程进行运算。
    """
    sin_out = Signal(str)   # 自定义信号，注意是类变量

    def __init__(self):
        super(ThreadCompute, self).__init__()

    def run(self):
        """线程运行函数，通过 start() 启动"""
        # 多进程间通信，通过共享的 list 实现！
        self.l.append('现在开始启动计算线程......')

        # 获取初始文件列表
        itr_args = os.listdir(initial_filepath)
        if not itr_args:
            self.sin_out.emit('需要分析的贷款台账文件夹为空，请放入文件。')
            self.sin_out.emit('stop_null')
        else:
            # 计时器开始
            start = time.perf_counter()
            # 自定义信号发射信息
            self.sin_out.emit('数据分析开始：\n'
                              '开启计算线程 Thread_compute......\n'
                              '创建 进程池Pool 并行计算......')
            itr_args.sort(reverse=True)
            my_list = []
            for _ in range(len(itr_args)):
                my_list.append(self.l)
            # 判断结果文件夹存在否
            if not os.path.exists(result_filepath):
                os.mkdir(result_filepath)
            # 多进程间通信，通过共享的 list 实现！
            self.l.append('创建多进程池 Pool ......')
            # ---------多进程：线程中调用的多进程函数，必须是全局函数：map_analysis----------------
            pool = Pool(6)
            pool_res = pool.map_async(map_analysis, zip(itr_args, my_list))     # 非阻塞异步运行多进程
            self.sin_out.emit('运行中......')
            pool.close()
            pool.join()
            self.sin_out.emit('各贷款报表已通过进程池分析完毕。'
                              '\n现在开始汇总......')
            # 汇总分析结果
            summary_analysis_result(itr_args, self.l)
            self.sin_out.emit('汇总完毕')
            # 测算用时
            elapsed = (time.perf_counter() - start)
            self.sin_out.emit('分析汇总程序运行总计: {:.2f} 秒.'.format(elapsed))
            # 发出主计算线程完成信号
            self.sin_out.emit('stop')


# ------以下是：ThreadCompute 中 run（）调用的全局函数 map_analysis----------------------
def map_analysis(loan_excel):
    """
    分析每一张表
    :param loan_excel: 一张表的名字
    :return: 无
    """
    # loan_excel[1] 是多进程间通信的共享list
    loan_excel[1].append(f'{loan_excel[0]}: 开始进入分析函数 map_analysis ......')

    # loan_excel[0] 是要分析的单张初始贷款台账，如：20210831.xlsx
    # 分离表的名字，用表的名字在当前工作目录中建立子文件夹
    filename = os.path.splitext(loan_excel[0])[0]
    subdir_abspath = os.path.join(result_filepath, filename)
    # 如果不存在子文件夹，就建立一个
    if not os.path.exists(subdir_abspath):
        os.mkdir(subdir_abspath)

    # 建立分析结果的文件名，以及获取绝对路径
    filename_analysis = filename + '_analysis_results.txt'
    file_analysis_results = os.path.join(subdir_abspath, filename_analysis)
    # 如果有原文件，先删除
    if os.path.exists(file_analysis_results):
        os.remove(file_analysis_results)

    compare_date = parse(filename)
    # loan_excel[1] 是多进程间通信的共享list
    loan_excel[1].append(f'为 {loan_excel[0]} 创建贷款类 Loan ......')
    # ------实例类 Loan，参数file_analysis_results 存储目标绝对路径
    loan_excel_abspath = os.path.join(initial_filepath, loan_excel[0])
    my_loan = Loan(loan_excel_abspath, file_analysis_results)

    # loan_excel[1] 是多进程间通信的共享list
    loan_excel[1].append(f'{loan_excel[0]}:  map_analysis 开始贷款基本情况分析......')
    # ------贷款基本情况分析------------------------------
    file_writer_text(file_analysis_results,
                     '=' * 60 +
                     f"\n截至{compare_date.year}年{compare_date.month}月{compare_date.day}日，" +
                     '该行存量贷款余额：{:.2f}万元，'
                     '正常类贷款：{:.2f}万元，'
                     '关注类贷款：{:.2f}万元，'
                     '次级类贷款：{:.2f}万元，'
                     '可疑类贷款：{:.2f}万元，'
                     '损失类贷款：{:.2f}万元；'
                     '不良贷款余额：{:.2f}万元，'
                     '不良贷款率：{:.2f}%；'
                     '信贷资产潜在风险估计值：{:.2f}万元。'
                     .format(my_loan.info["贷款余额"] / 10000, my_loan.info["正常类"] / 10000, my_loan.info["关注类"] / 10000,
                             my_loan.info["次级类"] / 10000, my_loan.info["可疑类"] / 10000, my_loan.info["损失类"] / 10000,
                             my_loan.info["正常贷款"] / 10000, my_loan.info["不良贷款"] / 10000, my_loan.info["不良贷款率"] * 100,
                             my_loan.info["潜在风险估计值"] / 10000) +
                     '\n该行存量贷款五级分类准确性分析结果如下：\n'
                     )
    # loan_excel[1] 是多进程间通信的共享list
    loan_excel[1].append(f'{loan_excel[0]}: map_analysis 准备进行贷款五级分类分析......')
    # ------贷款五级分类情况分析---------------------------
    my_loan.loan_five_classification_analysis(filename, loan_excel[1])  # loan_excel[1] 是多进程间通信的共享list


# ------以下是：ThreadCompute 中 run（）调用的全局函数 summary_analysis_result----------------------
def summary_analysis_result(filenames_list, l):
    """
    汇总分析结果
    :param filenames_list: 初始贷款台账列表
    :return: 无
    """
    print('enter summary_analysis_result(filenames_list, l):')
    # l 是多进程间通信的共享list
    n = len(filenames_list)
    l.append(f'现在对 {n} 张贷款台账的数据分析结果进行汇总......')
    # 建立 df_result 空表，与各子文件夹中的分析结果表连接汇总
    result_columns = ('截至日期', '贷款余额', '正常类', '关注类', '次级类', '可疑类', '损失类', '正常贷款',
                      '不良贷款', '不良贷款率', '潜在风险估计值', '应下调关注笔数', '应下调关注金额', '应下调次级笔数',
                      '应下调次级金额', '应下调可疑笔数', '应下调可疑金额')
    df_result = pd.DataFrame(columns=result_columns)
    df_result.set_index('截至日期', drop=True, inplace=True)
    # 如果存在原报告，先删除
    print('1')
    file_txt = os.path.join(result_filepath, '贷款分析汇总报告.txt')
    if os.path.exists(file_txt):
        os.remove(file_txt)

    file_csv = os.path.join(result_filepath, '贷款分析汇总表.csv')
    # 逐个子文件夹汇总
    print('2')
    for file in filenames_list:
        # 寻找子文件夹绝对路径
        filename = os.path.splitext(file)[0]
        subdir_abspath = os.path.join(result_filepath, filename)
        # 打开子文件夹中的f_txt文件，读取并逐行写入汇总报告file_txt中
        f_txt = os.path.join(subdir_abspath, filename + '_analysis_results.txt')
        f_txt_str = ''
        print('2.1')
        with open(f_txt, 'r+') as f:
            for line in f.readlines():
                f_txt_str += line
        file_writer_text(file_txt, f_txt_str)
        print('2.2')
        # 读取子文件夹中f_csv数据表，并逐个连接存储到 df_result 中
        f_csv = os.path.join(subdir_abspath, filename + '_analysis_results.csv')
        print('2.3')
        df_f_csv = pd.read_csv(f_csv, encoding='gb2312')
        print('2.4')
        df_result = pd.concat([df_result, df_f_csv], ignore_index=False)
    print('3')
    # -------------将汇总后的数据表，存储到 '贷款分析汇总表.csv'------------------------
    # 设置 df_result 各数据列保持两位小数
    for c in df_result.columns:
        if c in ['贷款余额', '正常类', '关注类', '次级类', '可疑类', '损失类', '正常贷款',
                 '不良贷款', '不良贷款率', '潜在风险估计值', '应下调关注金额',
                 '应下调次级金额', '应下调可疑金额']:
            df_result[c] = round(df_result[c], 2)
    print('4')
    df_result.set_index('截至日期', drop=True, inplace=True)
    df_result.to_csv(file_csv, columns=df_result.columns, index=True, encoding='gb2312')


# ------以下是：主窗口类 MainWindow --------------------------
class LoanClassificationAnalysisWindow(QMainWindow, Ui_MainWindow):
    """主窗口"""
    def __init__(self, multip_l):
        super().__init__()
        self.setupUi(self)
        # ------设置全屏------------
        self.setWindowState(Qt.WindowFullScreen)
        # ------初始化进程之间共享list------------
        self.l = multip_l
        # 设置主窗口无标题栏 顶层显示，进度条从0开始显示
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.pbar.setProperty("value", 0)
        # matplotlib figure 初始化
        self.figure = plt.figure(figsize=(8, 6), dpi=100, facecolor=(0.94, 0.94, 0.94))
        #----设置网格布局----
        gs = gridspec.GridSpec(1, 2, left=0.08, bottom=0.2, right=0.93, top=0.92,
                               wspace=0.2, hspace=0.2)
        self.ax0 = self.figure.add_subplot(gs[0, :])
        self.ax0.set_visible(False)
        # ------设置坐标系坐标旋转------------
        for tick in self.ax0.get_xticklabels():
            tick.set_rotation(30)
        # self.ax3 = self.figure.add_subplot(gs[0, :])
        self.ax3 = self.ax0.twinx()
        self.ax3.set_visible(False)
        self.ax1 = self.figure.add_subplot(gs[0, 0])
        self.ax1.set_visible(False)
        self.ax2 = self.figure.add_subplot(gs[0, 1])
        self.ax2.set_visible(False)
        # ------将图像的画布放置于主窗口中的网格布局中------------
        self.canvas = FigureCanvas(self.figure)
        self.gridLayout.addWidget(self.canvas)
        # --------设置 pbn_show_init_figure 显示按钮---------
        self.pbn_show_init_figure.setVisible(False)

        # 按钮点击启动函数，槽函数
        self.pbt_dir.clicked.connect(self.dir_list)
        self.pbt_start.clicked.connect(self.main_program)
        self.pbt_close.clicked.connect(self.close)
        self.tw_result.cellPressed.connect(self.get_pos_to_show_detailed)
        self.pbn_show_init_figure.clicked.connect(self.show_figure_initial)

        # 设置进度条数值范围
        self.pbar.setMinimum(0)
        self.pbar.setMaximum(50)
        # 实例计算线程类
        self.t = ThreadCompute()
        # 线程类信号连接函数
        self.t.sin_out.connect(self.tedit_text)
        # 进度条值初始化
        self.value = 0

        self.t.l = self.l
        self.i = 0

    def dir_list(self):
        """选择文件夹，获取需要分析的文件"""
        dir_file = QFileDialog.getExistingDirectory(None, '选择文件夹路径', os.getcwd())
        global initial_filepath
        initial_filepath = dir_file
        self.ledit_dir.setText(dir_file)    # 文件夹目录
        list_dir = os.listdir(dir_file)
        self.lw_filename.addItems(list_dir)     # 显示文件夹目录下得文件

    def pbar_start(self):
        """进度条启动函数"""
        # 实例化定时器类
        self.timer = QTimer(self)
        self.timer.start(100)      # 设置定时长，发出信号
        self.timer.timeout.connect(self.set_pbar)       # 设置信号连接函数

    def set_pbar(self):
        """设置进度条"""
        self.value += 1
        self.pbar.setValue(self.value)
        if self.value == 50:
            self.timer.stop()   # 如果进度条满，停止定时器

        if (self.l is not None) and (self.i < len(self.l)):
            self.tedit.append(self.l[self.i])
            self.tedit.moveCursor(QTextCursor.End)
            self.i += 1

    def tedit_text(self, s):
        """文本框显示函数"""
        if s == 'stop':
            self.gif.stop()  # gif 图片停止
            self.timer.stop()  # 定时器停止
            self.pbar.setValue(50)  # 进度条满
        elif s == 'stop_null':
            self.gif.stop()  # gif 图片停止
            self.timer.stop()  # 定时器停止
        elif s == '汇总完毕':
            """两件事：一是在tableWidget中显示汇总表，二是显示不良贷款率图"""
            dir_result = os.path.join(result_filepath, '贷款分析汇总表.csv')
            self.result = pd.read_csv(dir_result, encoding='gb2312')        # 获取汇总表，转换成dataframe格式
            row = self.result.shape[0]
            vol = self.result.shape[1]
            self.tw_result.setRowCount(row)
            self.tw_result.setColumnCount(vol)
            # self.tw_result.verticalHeader().setVisible(False)     # 是否可见
            self.tw_result.horizontalHeader().setStretchLastSection(True)   # 最后一格补齐空间
            self.tw_result.setEditTriggers(QAbstractItemView.NoEditTriggers)    # 设置不可编辑
            # self.tw_result.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.tw_result.setHorizontalHeaderLabels(['截至日期', '贷款余额', '正常类', '关注类', '次级类', '可疑类',
                                                      '损失类', '正常贷款', '不良贷款', '不良贷款率', '潜在风险估计值',
                                                      '应下调关注笔数', '金额', '应下调次级笔数', '金额', '应下调可疑笔数', '金额'])
            self.list_vheader = []  # 设置列标题
            # -----将元素加入tw控件中-----------
            for i in range(row):
                for j in range(vol):
                    s = str(self.result.iloc[i, j])
                    if j == 0:
                        s = s.split('.')[0]
                        self.list_vheader.append(s)
                    data = QTableWidgetItem(s)  # 转换
                    if j in (11, 12):
                        data.setForeground(QBrush(QColor('red')))   # 设置单元格前景和背景色
                        data.setBackground(QBrush(QColor('cyan')))
                    elif j in (13, 14):
                        data.setForeground(QBrush(QColor('red')))
                        data.setBackground(QBrush(QColor('yellow')))
                    elif j in (15, 16):
                        data.setForeground(QBrush(QColor('red')))
                        data.setBackground(QBrush(QColor(255, 80, 0, 160)))
                    self.tw_result.setItem(i, j, data)  # 逐个填充单元格

            self.tw_result.setVerticalHeaderLabels(self.list_vheader)   # 设置行标题
            self.tw_result.resizeColumnsToContents()    # 设置列自适应宽度
            self.tw_result.resizeRowsToContents()       # 设置行自适应宽度
            self.tw_result.setAlternatingRowColors(True)    # 设置行交替颜色显示
            # 设置行列标题的格式
            self.tw_result.horizontalHeader().setStyleSheet('QHeaderView::section{background-color:rgb(150, 170, 190);'
                                                            'font:9pt "宋体";color:black;}')
            self.tw_result.verticalHeader().setStyleSheet('QHeaderView::section{background-color:rgb(150, 170, 190);'
                                                            'font:9pt "宋体";color:black;}')

            self.tw_result.show()   # 显示
            self.show_figure_initial()      # 显示不良贷款率图
        else:
            self.tedit.append(s)    # 显示程序执行进度
            self.tedit.moveCursor(QTextCursor.End)  # 总显示最后一行

    def get_pos_to_show_detailed(self, row, col):
        """点击汇总表中数据后，显示贷款逾期明细信息"""
        self.tw_detailed.verticalHeader().setVisible(True)
        self.tw_detailed.horizontalHeader().setVisible(True)
        self.tw_detailed.setAlternatingRowColors(True)
        self.tw_detailed.setShowGrid(True)

        file_date = self.list_vheader[row].split('.')[0]    # 行标题
        subdir_selected = os.path.join(result_filepath, file_date)
        columns = ['客户代码', '户名', '贷款账号/票据ID', '借据余额', '借款日', '到期日',
                   '五级分类', '本息逾期日', '本息逾期天数']
        if col in (11, 12):
            file_selected = os.path.join(subdir_selected, file_date + '_overdue_61_90.csv')
            if not os.path.exists(file_selected):   # 如果不存在该文件
                self.tw_detailed.clear()
                self.tw_detailed.verticalHeader().setVisible(False)
                self.tw_detailed.horizontalHeader().setVisible(False)
                self.tw_detailed.setAlternatingRowColors(False)
                self.tw_detailed.setShowGrid(False)
                self.show_figure(row, col, file_date)   # 依然显示该行的整体分析信息
                return
            # 读取分析结果中的每个明细文件
            self.detailed = pd.read_csv(file_selected, encoding='gb2312', usecols=columns, low_memory=False)

        elif col in (13, 14):
            file_selected = os.path.join(subdir_selected, file_date + '_overdue_91_180.csv')
            if not os.path.exists(file_selected):
                self.tw_detailed.verticalHeader().setVisible(False)
                self.tw_detailed.horizontalHeader().setVisible(False)
                self.tw_detailed.setAlternatingRowColors(False)
                self.tw_detailed.setShowGrid(False)
                self.tw_detailed.clear()
                self.show_figure(row, col, file_date)
                # self.canvas.draw()
                return
            # 读取分析结果中的每个明细文件
            self.detailed = pd.read_csv(file_selected, encoding='gb2312', usecols=columns, low_memory=False)
        elif col in (15, 16):
            file_selected = os.path.join(subdir_selected, file_date + '_overdue_181_inf.csv')
            if not os.path.exists(file_selected):
                self.tw_detailed.verticalHeader().setVisible(False)
                self.tw_detailed.horizontalHeader().setVisible(False)
                self.tw_detailed.setAlternatingRowColors(False)
                self.tw_detailed.setShowGrid(False)
                self.tw_detailed.clear()
                self.show_figure(row, col, file_date)
                # self.canvas.draw()
                return
            # 读取分析结果中的每个明细文件
            self.detailed = pd.read_csv(file_selected, encoding='gb2312', usecols=columns, low_memory=False)
        else:
            self.tw_detailed.verticalHeader().setVisible(False)
            self.tw_detailed.horizontalHeader().setVisible(False)
            self.tw_detailed.setAlternatingRowColors(False)
            self.tw_detailed.setShowGrid(False)
            self.tw_detailed.clear()
            self.show_figure(row, col, file_date)
            # self.canvas.draw()
            return
        # -----------显示图形ax1、ax2-----------------------------------------
        self.show_figure(row, col, file_date)
        # -----------显示明细---------------------------------
        r = self.detailed.shape[0]
        v = self.detailed.shape[1]
        self.tw_detailed.setRowCount(r)
        self.tw_detailed.setColumnCount(v)
        self.tw_detailed.horizontalHeader().setStretchLastSection(True)
        self.tw_detailed.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tw_detailed.setHorizontalHeaderLabels(columns)
        for i in range(r):
            for j in range(v):
                s = str(self.detailed.iloc[i, j])
                data = QTableWidgetItem(s)
                if j == 1:
                    data.setForeground(QBrush(QColor('red')))
                    data.setBackground(QBrush(QColor('cyan')))
                elif j == 3:
                    data.setForeground(QBrush(QColor('red')))
                    data.setBackground(QBrush(QColor('yellow')))
                elif j == 6:
                    data.setForeground(QBrush(QColor('red')))
                    data.setBackground(QBrush(QColor('magenta')))
                elif j == 8:
                    data.setForeground(QBrush(QColor('red')))
                    data.setBackground(QBrush(QColor(255, 80, 0, 160)))
                self.tw_detailed.setItem(i, j, data)

        self.tw_detailed.resizeColumnsToContents()
        self.tw_detailed.resizeRowsToContents()
        self.tw_detailed.setAlternatingRowColors(True)
        self.tw_detailed.horizontalHeader().setStyleSheet('QHeaderView::section{background-color:rgb(150, 170, 190);'
                                                        'font:9pt "宋体";color:black;}')
        self.tw_detailed.verticalHeader().setStyleSheet('QHeaderView::section{background-color:rgb(150, 170, 190);'
                                                        'font:9pt "宋体";color:black;}')
        self.tw_result.show()

    def show_figure(self, row, col, file_date):
        """显示ax1、ax2"""
        self.timer_bar.stop()   # ax0 的动画计时器停止
        self.pbn_show_init_figure.setVisible(True)  # 显示 不良贷款率按钮
        self.pbn_show_init_figure.setCheckable(False)
        self.ax0.set_visible(False)     # 设置ax0 ax3 不可见
        self.ax3.set_visible(False)
        # ---------设置ax1 饼图----------
        self.ax1.clear()
        data1 = [self.result.loc[self.result.index[row], '正常类'],
                 self.result.loc[self.result.index[row], '关注类'],
                 self.result.loc[self.result.index[row], '次级类'],
                 self.result.loc[self.result.index[row], '可疑类'],
                 self.result.loc[self.result.index[row], '损失类']]
        labels1 = ['正常类', '关注类', '次级类', '可疑类', '损失类']
        self.ax1.pie(x=data1, labels=labels1, autopct='%1.2f%%')
        self.ax1.legend(labels1, loc='upper left', bbox_to_anchor=(0.9, 0, 0.5, 1))
        self.ax1.set_xlabel(u'贷款五级分类(单位:万元）', fontsize=14)
        # self.ax1.set_ylabel(u'贷款金额', fontsize=12)
        self.ax1.set_title(f'{file_date} 贷款五级分类图', fontsize=18)
        self.ax1.set_visible(True)
        # ---------显示图形ax2 条形图-------------------------------------
        self.ax2.clear()
        data2 = [self.result.loc[self.result.index[row], '应下调关注金额'],
                 self.result.loc[self.result.index[row], '应下调次级金额'],
                 self.result.loc[self.result.index[row], '应下调可疑金额']]
        if data2 == [0, 0, 0]:
            self.ax2.set_visible(False)
            self.canvas.draw()
            return
        labels2 = ['应下调关注', '应下调次级', '应下调可疑']
        self.ax2.bar(labels2, data2, facecolor='red')
        self.ax2.set_xlabel(u'应下调贷款金额（单位:万元）', fontsize=14)
        self.ax2.set_ylabel(u'贷款金额', fontsize=14)
        self.ax2.set_title(f'{file_date} 应下调贷款金额图', fontsize=18)
        self.ax1.legend()
        self.ax2.set_visible(True)
        # 刷新画布
        self.canvas.draw()

    def show_figure_initial(self):
        """显示第一次就显示的不良贷款率图"""
        self.ax1.set_visible(False)
        self.ax2.set_visible(False)
        self.pbn_show_init_figure.setVisible(False)
        # self.pbn_show_init_figure.setCheckable(True)
        # ----------设置坐标x-------------
        self.x = []
        # j = self.result.columns.get_indexer(['截至日期'])
        for i in range(len(self.result['截至日期'])):
            s = str(self.result.iloc[i, 0])     # ‘截至日期’为第0列，这里是硬编码
            s1 = s.split('.')[0]
            self.x.append(s1)
        self.x.sort(reverse=False)  # 升序
        data1 = list(self.result['正常贷款'].values)
        data2 = list(self.result['不良贷款'].values)
        labels0 =['正常贷款', '不良贷款']
        data1.reverse()     # 反转数据
        data2.reverse()

        self.ax0.plot(self.x, data1, '-g', lw=1.5)      # 画折线图
        self.ax0.plot(self.x, data2, '--r', lw=1.5)
        # -----------画不良贷款率柱状图-----------
        r = self.result['不良贷款率'].copy()
        r *= 100000
        self.ratio = list(r.values)
        self.ratio.sort(reverse=True)
        print('self.ratio=', self.ratio)
        line, = self.ax0.plot(self.x, self.ratio, '-.m', lw=1)
        bar = self.ax0.bar(self.x[0], self.ratio[0], facecolor='magenta', alpha=0.5, animated=True)
        print('bar=', bar, type(bar))

        # 设置注释
        self.ax0.annotate(u'正常贷款趋势线', xy=(self.x[8], data1[8]), xytext=(80, -30), textcoords='offset points',
                          arrowprops=dict(facecolor='yellow', shrink=0.05, width=4),
                          bbox=dict(boxstyle='round,pad=0.8', fc='cyan', ec='k', lw=1, alpha=0.8))
        self.ax0.annotate(u'不良贷款趋势线', xy=(self.x[13], data2[13]), xytext=(80, 55), textcoords='offset points',
                          arrowprops=dict(facecolor='red', headwidth=8, headlength=15),
                          bbox=dict(boxstyle='round,pad=0.8', fc='cyan', ec='k', lw=1, alpha=0.8))

        self.ax0.set_xlabel(u'贷款截至日期', fontsize=14)     # 设置横坐标标签
        self.ax0.set_ylabel('贷款金额(单位:万元）', fontsize=14)
        self.ax0.set_title(f'{self.x[0]}至{self.x[-1]}不良贷款率变动示意图', fontsize=18)
        self.ax3.set_yticks([0, 1, 2, 3, 4, 5])     # 设置 Y 副轴刻度
        self.ax3.set_yticklabels(['0.0%', '1.0%', '2.0%', '3.0%', '4.0%', '5.0%'])      # 设置 Y 副轴标签，硬编码
        self.ax3.set_ylabel('不良贷款率', fontsize=14)
        self.ax0.set_visible(True)
        self.ax3.set_visible(True)
        self.canvas.draw()

        # 设置定时器，使 不良贷款率 动画
        self.timer_bar = QTimer(self)
        self.timer_bar.start(200)  # 设置定时长，发出信号
        self.timer_bar.timeout.connect(self.draw_bar)  # 设置信号连接函数

        self.i_x = -1   # 初始化 显示哪一个柱

    def draw_bar(self):
        """画不良贷款率的柱状图"""
        self.i_x += 1
        n = self.i_x % len(self.x)
        self.ax0.bar(self.x[n], self.ratio[n], facecolor='magenta', alpha=1)  # 显示
        self.canvas.draw()
        self.ax0.bar(self.x[n], self.ratio[n], facecolor=(0.94, 0.94, 0.94), alpha=0.9)  # 遮盖

    def run_gif(self):
        """ 设置 gif 图片"""
        self.gif = QMovie('./icons/loading.gif')
        self.lab.setMovie(self.gif)     # 标签显示
        self.gif.start()    # 启动 gif 图片动画

    def main_program(self):
        """启动按钮连接函数，启动计算进程、动画显示、进度条"""
        if not self.ledit_dir.text():
            QMessageBox.information(self, '提示', '请选择要分析贷款台账的文件夹', QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
            return
        self.run_gif()
        self.pbar_start()
        self.t.start()  # t 是 ThreadCompute 类的实例，启动计算线程 run()


# ------以下是：贷款类 Loan --------------------------
class Loan:
    """贷款类"""
    def __init__(self, loan_excel_abspath, file_analysis_results):
        self.loan_excel = os.path.split(loan_excel_abspath)[1]
        self.file_analysis_results = file_analysis_results
        self.subdir_abspath = os.path.split(file_analysis_results)[0]
        columns = ['客户代码', '户名', '贷款账号/票据ID', '借据金额', '借据余额',
                   '年利率', '贷款期限', '借款日', '到期日', '五级分类',
                   '首次放款日', '本金逾期起始日期', '利息逾期起始日期', '本息逾期日']
        # .excel文件已全部转换成 .csv文件
        self.df_selected_excel = pd.read_csv(loan_excel_abspath, usecols=columns, low_memory=False)

        self.info = self.loan_info()


    def loan_info(self):
        """获取贷款基本信息"""
        # if self.df_selected_excel['五级分类'].isnull().T.any():
        #     print('贷款台账的五级分类有空值，请完善贷款台账。')
        #     sys.exit()

        loan_sum = self.df_selected_excel.借据余额.sum()
        # 正常类：10，关注类：20，次级类：30，可疑类：40，损失类：50
        loan_10_sum = self.df_selected_excel[self.df_selected_excel.五级分类 == 10].借据余额.sum()
        loan_20_sum = self.df_selected_excel[self.df_selected_excel.五级分类 == 20].借据余额.sum()
        loan_30_sum = self.df_selected_excel[self.df_selected_excel.五级分类 == 30].借据余额.sum()
        loan_40_sum = self.df_selected_excel[self.df_selected_excel.五级分类 == 40].借据余额.sum()
        loan_50_sum = self.df_selected_excel[self.df_selected_excel.五级分类 == 50].借据余额.sum()

        loan_normal = loan_10_sum + loan_20_sum
        loan_nonperforming = loan_30_sum + loan_40_sum + loan_50_sum
        # 贷款不良率
        npl_ratio = loan_nonperforming / loan_sum

        # 潜在风险估计值
        loan_risk_estimate = (loan_10_sum * 0.015 + loan_20_sum * 0.03
                              + loan_30_sum * 0.3 + loan_40_sum * 0.6 + loan_50_sum)

        info_dict = {'贷款余额': loan_sum,
                     '正常类': loan_10_sum,
                     '关注类': loan_20_sum,
                     '次级类': loan_30_sum,
                     '可疑类': loan_40_sum,
                     '损失类': loan_50_sum,
                     '正常贷款': loan_normal,
                     '不良贷款': loan_nonperforming,
                     '不良贷款率': npl_ratio,
                     '潜在风险估计值': loan_risk_estimate
                     }
        return info_dict

    def loan_five_classification_analysis(self, filename, l):
        """
        单张贷款台账分析
        :param filename: 需要分析报表的名字
        :l: 进程间通信的共享list
        :return: 无
        """
        # l 是多进程间通信的共享list
        l.append(f'{filename}.xlsx: 筛选已逾期的贷款......')
        # 筛选出逾期贷款
        df_overdue_loan = self.df_selected_excel[self.df_selected_excel['本息逾期日'].notnull()]
        # 将 '本息逾期日' 这一列数据逐个转换格式 float64 -> datetime
        # df1 = df_overdue_loan['本息逾期日']
        # print(df1.head())
        # df_overdue_loan['本息逾期日'] = pd.to_datetime(df_overdue_loan['本息逾期日'].apply(math.floor).apply(str))
        df_overdue_loan.loc[:, '本息逾期日'] = pd.to_datetime(df_overdue_loan.loc[:, '本息逾期日'].apply(math.floor).apply(str))

        # 计算到截止日期的本息逾期天数，类型是 datetime.timedelta
        compare_date = parse(filename)  # 字符串如'20210831' 格式转换为 datetime.datetime 格式

        # 添加1列，计算出逾期天数
        df_overdue_loan.loc[:, '本息逾期天数'] = compare_date - df_overdue_loan['本息逾期日']
        # df_overdue_loan[:]['本息逾期天数'] -= compare_date
        # df_overdue_loan[:]['本息逾期天数'] *= -1
        # l 是多进程间通信的共享list
        l.append(f'{filename}.xlsx: 计算已逾期天数61-90天，91-180天，>=181天的贷款......')
        # 计算出应下调关注、次级、可疑的贷款
        res_20 = df_overdue_loan[(df_overdue_loan['本息逾期天数'] > datetime.timedelta(60))
                                 & (df_overdue_loan['本息逾期天数'] <= datetime.timedelta(90))
                                 & (df_overdue_loan['五级分类'] < 20)
                                 & (df_overdue_loan['借据余额'] != 0)]
        res_30 = df_overdue_loan[(df_overdue_loan['本息逾期天数'] > datetime.timedelta(90))
                                 & (df_overdue_loan['本息逾期天数'] <= datetime.timedelta(180))
                                 & (df_overdue_loan['五级分类'] < 30)
                                 & (df_overdue_loan['借据余额'] != 0)]
        res_40 = df_overdue_loan[(df_overdue_loan['本息逾期天数'] > datetime.timedelta(180))
                                 & (df_overdue_loan['五级分类'] < 40)
                                 & (df_overdue_loan['借据余额'] != 0)]

        # 用字典分类数据，res_20 需下调关注的贷款，res_30 需下调次级的贷款，res_40 需下调可疑的贷款
        overdue_list = {'res_20': [res_20, '_overdue_61_90', '应下调关注笔数', '应下调关注金额',
                                   '本金或利息逾期时间在 61天 - 90天 之间，五级分类应为关注类，但定为正常类的贷款：\n'],
                        'res_30': [res_30, '_overdue_91_180', '应下调次级笔数', '应下调次级金额',
                                   '本金或利息逾期时间在 91天 - 180天 之间，五级分类应为次级类，但定为关注类或以上的贷款：\n'],
                        'res_40': [res_40, '_overdue_181_inf', '应下调可疑笔数', '应下调可疑金额',
                                   '本金或利息逾期时间超过181天，五级分类应为可疑类，但定为次级类或以上的贷款：\n']
                        }
        # ---------建立新的1行数据列表 df_var
        result_columns_var = ('截至日期', '贷款余额', '正常类', '关注类', '次级类', '可疑类', '损失类', '正常贷款',
                              '不良贷款', '不良贷款率', '潜在风险估计值', '应下调关注笔数', '应下调关注金额', '应下调次级笔数',
                              '应下调次级金额', '应下调可疑笔数', '应下调可疑金额')
        df_result_row = [filename, self.info["贷款余额"] / 10000, self.info["正常类"] / 10000,
                         self.info["关注类"] / 10000, self.info["次级类"] / 10000,
                         self.info["可疑类"] / 10000, self.info["损失类"] / 10000, self.info["正常贷款"] / 10000,
                         self.info["不良贷款"] / 10000, self.info["不良贷款率"] * 100,
                         self.info["潜在风险估计值"] / 10000, None, None, None, None, None, None]
        dict_var = dict(zip(result_columns_var, df_result_row))
        s_var = pd.Series(dict_var)
        df_var1 = pd.DataFrame(s_var)
        df_var = df_var1.T
        df_var.set_index('截至日期', drop=True, inplace=True)
        # l 是多进程间通信的共享list
        l.append(f'{filename}.xlsx: 分析数据，并写入子文件夹的 .txt 和 .csv 文件中......')
        # 分析数据，并补充完善 df_var 空值字段
        for res in overdue_list.values():
            if not res[0].empty:
                row_total = len(res[0])
                loan_overdue_sum = res[0].借据余额.sum()
                # res[0].loc[res[0].index[0], '合计'] = f'共{row_total}笔，' + '合计{:.2f}万元。'.format(loan_overdue_sum / 10000)
                res[0].loc[:, '合计'] = f'共{row_total}笔，' + '合计{:.2f}万元。'.format(loan_overdue_sum / 10000)

                # 写入子文件夹
                file_writer_text(self.file_analysis_results,
                                 res[4] + f' 共{row_total}笔，' + '合计{:.2f}万元。\n'.format(loan_overdue_sum / 10000))
                # 补充 df_var 空值字段
                df_var.loc[filename, res[2]] = row_total
                df_var.loc[filename, res[3]] = loan_overdue_sum/10000
                # 写入子文件夹
                file_overdue = filename + f'{res[1]}.csv'
                file_overdue_abspath = os.path.join(self.subdir_abspath, file_overdue)
                res[0].to_csv(file_overdue_abspath, columns=res[0].columns, index=True, encoding='gb2312')
            else:
                df_var.loc[filename, res[2]] = 0
                df_var.loc[filename, res[3]] = 0.

        # 写入子文件夹
        csv_abspath = os.path.join(self.subdir_abspath, filename+'_analysis_results.csv')
        df_var.to_csv(csv_abspath, columns=df_var.columns, index=True, encoding='gb2312')


if __name__ == '__main__':
    """主程序"""
    # 建立多进程间通信的共享list
    multip_l = multiprocessing.Manager().list([])
    app = QApplication(sys.argv)
    m_p = LoanClassificationAnalysisWindow(multip_l)
    m_p.show()
    sys.exit(app.exec_())
