import math
import sys
import numpy as np
from collections import defaultdict
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QScrollArea, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QAbstractItemView, QMessageBox,
                             QSizePolicy, QToolButton)
from PyQt5.QtGui import QDoubleValidator, QIntValidator, QFont, QPalette, QColor, QIcon
from PyQt5.QtCore import Qt, QSize, QPoint
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

class NumericInput(QWidget):
    def __init__(self, label, default="0", validator=None):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        self.label = QLabel(label)
        self.label.setFont(QFont("Arial", 10))
        self.input = QLineEdit(default)
        self.input.setFont(QFont("Arial", 10))
        self.input.setFixedWidth(150)
        if validator:
            self.input.setValidator(validator)
        
        layout.addWidget(self.label)
        layout.addWidget(self.input)
        layout.setContentsMargins(0, 0, 0, 0)

    def get_value(self):
        try:
            if '.' in self.input.text():
                return float(self.input.text())
            return int(self.input.text())
        except ValueError:
            return 0
            
    def clear(self):
        self.input.clear()

class ResultsWindow(QMainWindow):
    def __init__(self, data):
        super().__init__()
        self.setWindowTitle("计算结果列表")
        self.setGeometry(300, 200, 900, 600)
        
        # 应用简约风格配色
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(250, 250, 250))
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.Button, QColor(240, 240, 240))
        palette.setColor(QPalette.Highlight, QColor(100, 150, 255))
        self.setPalette(palette)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        title = QLabel("计算结果列表")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setStyleSheet("color: #333333;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 添加滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # 创建表格小部件
        table = QTableWidget()
        table.setRowCount(len(data) - 1)
        table.setColumnCount(len(data[0]))
        table.setHorizontalHeaderLabels(data[0])
        
        # 填充表格数据
        for row in range(1, len(data)):
            for col in range(len(data[0])):
                item = QTableWidgetItem(str(data[row][col]))
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(row-1, col, item)
        
        # 表格样式设置
        table.setFont(QFont("Arial", 10))
        table.setStyleSheet("""
            QTableWidget {
                gridline-color: #e0e0e0;
                background-color: #ffffff;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 6px;
                border: 1px solid #e0e0e0;
            }
        """)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        
        # 设置滚动区域的小部件
        scroll_area.setWidget(table)
        layout.addWidget(scroll_area)
        
        # 添加筹码信息标签
        chips_label = QLabel(f"筹码单位数: {data[-1][0]}")
        chips_label.setFont(QFont("Arial", 11, QFont.Bold))
        chips_label.setStyleSheet("color: #333333; padding: 10px;")
        chips_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(chips_label)

class CustomCanvas(FigureCanvas):
    """自定义画布类，支持拖拽功能"""
    def __init__(self, figure):
        super().__init__(figure)
        # 拖拽相关变量
        self.dragging = False
        self.last_pos = QPoint()
        self.setCursor(Qt.ArrowCursor)  # 默认箭头光标

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.last_pos = event.pos()
            self.setCursor(Qt.ClosedHandCursor)  # 拖拽时显示抓手光标
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging:
            # 计算移动距离
            dx = event.pos().x() - self.last_pos.x()
            dy = event.pos().y() - self.last_pos.y()
            self.last_pos = event.pos()
            
            # 移动图表
            ax = self.figure.axes[0]
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            
            # 计算新的坐标范围
            scale_x = (xlim[1] - xlim[0]) / self.width()
            scale_y = (ylim[1] - ylim[0]) / self.height()
            
            new_xmin = xlim[0] - dx * scale_x
            new_xmax = xlim[1] - dx * scale_x
            new_ymin = ylim[0] + dy * scale_y
            new_ymax = ylim[1] + dy * scale_y
            
            # 设置新范围
            ax.set_xlim(new_xmin, new_xmax)
            ax.set_ylim(new_ymin, new_ymax)
            self.draw_idle()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.dragging:
            self.dragging = False
            self.setCursor(Qt.OpenHandCursor)  # 释放后显示打开的手形光标
        super().mouseReleaseEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("杠杆筹码计算器")
        self.setGeometry(200, 100, 900, 700)
        
        # 应用简约风格配色
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(245, 248, 250))
        palette.setColor(QPalette.Button, QColor(230, 240, 250))
        palette.setColor(QPalette.Highlight, QColor(100, 150, 255))
        palette.setColor(QPalette.Text, QColor(50, 50, 50))
        self.setPalette(palette)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 添加标题
        title = QLabel("左侧杠杆筹码单位计算")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #333366; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # 输入区域
        input_layout = QHBoxLayout()
        
        # 左侧输入控件
        left_input = QWidget()
        left_layout = QVBoxLayout(left_input)
        
        self.b2_input = NumericInput("初始价位(B2): ", "100", QDoubleValidator(0, 1000000, 2))
        self.h2_input = NumericInput("杠杆倍数(G2): ", "10", QDoubleValidator(0.1, 1000, 2))
        
        left_layout.addWidget(self.b2_input)
        left_layout.addWidget(self.h2_input)
        
        # 右侧输入控件
        right_input = QWidget()
        right_layout = QVBoxLayout(right_input)
        
        self.i2_input = NumericInput("新入价-强平距(I2): ", "10", QDoubleValidator(0.1, 100000, 2))
        self.j2_input = NumericInput("迭代次数(J2): ", "50", QIntValidator(1, 100000))
        
        right_layout.addWidget(self.i2_input)
        right_layout.addWidget(self.j2_input)
        
        input_layout.addWidget(left_input)
        input_layout.addWidget(right_input)
        main_layout.addLayout(input_layout)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 计算按钮
        calc_btn = QPushButton("计算并绘图")
        calc_btn.setFont(QFont("Arial", 11))
        calc_btn.setFixedHeight(40)
        calc_btn.setStyleSheet("""
            QPushButton {
                background-color: #3366ff; 
                color: white; 
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #2255dd;
            }
        """)
        calc_btn.clicked.connect(self.calculate_and_plot)
        
        # 清除按钮 
        clear_btn = QPushButton("清除所有输入")
        clear_btn.setFont(QFont("Arial", 11))
        clear_btn.setFixedHeight(40)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff6633; 
                color: white; 
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #dd5522;
            }
        """)
        clear_btn.clicked.connect(self.clear_all_inputs)
        
        button_layout.addWidget(calc_btn)
        button_layout.addWidget(clear_btn)
        main_layout.addLayout(button_layout)
        
        # 结果区域
        self.result_widget = QWidget()
        self.result_layout = QVBoxLayout(self.result_widget)
        self.result_layout.setContentsMargins(5, 10, 5, 5)
        self.result_widget.setVisible(False)
        
        # 添加查看结果列表的按钮
        self.view_list_btn = QPushButton("查看完整结果列表")
        self.view_list_btn.setFont(QFont("Arial", 10))
        self.view_list_btn.setStyleSheet("""
            QPushButton {
                background-color: #44aaff; 
                color: white; 
                border-radius: 4px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #3399ee;
            }
        """)
        self.view_list_btn.setFixedHeight(35)
        self.view_list_btn.setVisible(False)
        self.result_layout.addWidget(self.view_list_btn)
        
        # 创建图表占位区域
        self.figure = Figure()
        self.canvas = CustomCanvas(self.figure)  # 使用自定义画布类
        self.canvas.setMinimumHeight(450)
        self.result_layout.addWidget(self.canvas)
        
        # 添加图表控制按钮区域
        self.chart_controls = QWidget()
        self.chart_controls_layout = QHBoxLayout(self.chart_controls)
        self.chart_controls_layout.setAlignment(Qt.AlignCenter)
        self.chart_controls_layout.setSpacing(10)  # 设置按钮间距
        
        # 放大按钮 - 添加加号图标
        self.zoom_in_btn = QToolButton()
        self.zoom_in_btn.setIcon(QIcon.fromTheme("zoom-in"))
        self.zoom_in_btn.setText("+")  # 添加加号文本
        self.zoom_in_btn.setToolTip("放大图表")
        self.zoom_in_btn.setStyleSheet("""
            QToolButton {
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 5px;
                font-weight: bold;
                font-size: 16px;
            }
            QToolButton:hover {
                background-color: #e0e0e0;
            }
            QToolButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        self.zoom_in_btn.setFixedSize(36, 36)
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        
        # 缩小按钮 - 添加减号图标
        self.zoom_out_btn = QToolButton()
        self.zoom_out_btn.setIcon(QIcon.fromTheme("zoom-out"))
        self.zoom_out_btn.setText("-")  # 添加减号文本
        self.zoom_out_btn.setToolTip("缩小图表")
        self.zoom_out_btn.setStyleSheet("""
            QToolButton {
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 5px;
                font-weight: bold;
                font-size: 16px;
            }
            QToolButton:hover {
                background-color: #e0e0e0;
            }
            QToolButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        self.zoom_out_btn.setFixedSize(36, 36)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        
        # 拖拽按钮 - 添加小手图标
        self.drag_btn = QToolButton()
        self.drag_btn.setIcon(QIcon.fromTheme("transform-move"))
        self.drag_btn.setText("✋")  # 添加手形符号
        self.drag_btn.setToolTip("拖拽图表")
        self.drag_btn.setStyleSheet("""
            QToolButton {
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 5px;
                font-size: 14px;
            }
            QToolButton:hover {
                background-color: #e0e0e0;
            }
            QToolButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        self.drag_btn.setFixedSize(36, 36)
        self.drag_btn.clicked.connect(self.toggle_drag_mode)
        
        # 新增：恢复光标按钮 - 添加箭头图标
        self.default_cursor_btn = QToolButton()
        self.default_cursor_btn.setIcon(QIcon.fromTheme("go-home"))
        self.default_cursor_btn.setText("➜")  # 添加箭头符号
        self.default_cursor_btn.setToolTip("恢复默认光标")
        self.default_cursor_btn.setStyleSheet("""
            QToolButton {
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 5px;
                font-size: 14px;
            }
            QToolButton:hover {
                background-color: #e0e0e0;
            }
            QToolButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        self.default_cursor_btn.setFixedSize(36, 36)
        self.default_cursor_btn.clicked.connect(self.restore_default_cursor)
        
        # 添加按钮到布局
        self.chart_controls_layout.addWidget(self.zoom_in_btn)
        self.chart_controls_layout.addWidget(self.zoom_out_btn)
        self.chart_controls_layout.addWidget(self.drag_btn)
        self.chart_controls_layout.addWidget(self.default_cursor_btn)  # 添加恢复光标按钮
        
        self.result_layout.addWidget(self.chart_controls)
        
        # 初始化坐标提示变量
        self.coord_label = QLabel("坐标: ")
        self.coord_label.setFont(QFont("Arial", 9))
        self.coord_label.setStyleSheet("color: #666666;")
        self.coord_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.result_layout.addWidget(self.coord_label)
        
        main_layout.addWidget(self.result_widget)
        
        # 状态栏
        self.statusBar().showMessage("准备就绪")
        
        # 图表交互相关变量
        self.current_point_annotation = None
        self.line_points = []
        self.ax = None
        self.original_xlim = None
        self.original_ylim = None
        self.drag_mode = False  # 拖拽模式状态
    
    # 新增：恢复默认光标功能
    def restore_default_cursor(self):
        """恢复默认光标"""
        self.canvas.setCursor(Qt.ArrowCursor)
        self.drag_mode = False
        self.drag_btn.setStyleSheet("""
            QToolButton {
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 5px;
                font-size: 14px;
            }
        """)
        self.statusBar().showMessage("已恢复默认光标")
    
    # 切换拖拽模式
    def toggle_drag_mode(self):
        """切换拖拽模式状态"""
        self.drag_mode = not self.drag_mode
        
        # 更新按钮状态
        if self.drag_mode:
            self.drag_btn.setStyleSheet("""
                QToolButton {
                    background-color: #d0d0ff;
                    border: 1px solid #a0a0ff;
                    border-radius: 4px;
                    padding: 5px;
                    font-size: 14px;
                }
            """)
            self.canvas.setCursor(Qt.OpenHandCursor)  # 设置打开的手形光标
            self.statusBar().showMessage("拖拽模式已启用 - 按住鼠标左键拖动图表")
        else:
            self.drag_btn.setStyleSheet("""
                QToolButton {
                    background-color: #f0f0f0;
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                    padding: 5px;
                    font-size: 14px;
                }
            """)
            self.canvas.setCursor(Qt.ArrowCursor)  # 恢复默认箭头光标
            self.statusBar().showMessage("拖拽模式已禁用")
    
    # 放大功能
    def zoom_in(self):
        """放大图表视图"""
        if self.ax:
            # 获取当前坐标轴范围
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            
            # 计算新的范围（中心点不变，范围缩小）
            x_center = (xlim[0] + xlim[1]) / 2
            y_center = (ylim[0] + ylim[1]) / 2
            x_range = (xlim[1] - xlim[0]) * 0.7  # 缩小30%
            y_range = (ylim[1] - ylim[0]) * 0.7
            
            # 设置新的坐标轴范围
            self.ax.set_xlim(x_center - x_range/2, x_center + x_range/2)
            self.ax.set_ylim(y_center - y_range/2, y_center + y_range/2)
            
            # 重绘图表
            self.canvas.draw()
            self.statusBar().showMessage("图表已放大")
    
    # 缩小功能
    def zoom_out(self):
        """缩小图表视图"""
        if self.ax:
            # 获取当前坐标轴范围
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            
            # 计算新的范围（中心点不变，范围扩大）
            x_center = (xlim[0] + xlim[1]) / 2
            y_center = (ylim[0] + ylim[1]) / 2
            x_range = (xlim[1] - xlim[0]) * 1.3  # 扩大30%
            y_range = (ylim[1] - ylim[0]) * 1.3
            
            # 设置新的坐标轴范围，但不超过原始范围
            new_xmin = max(self.original_xlim[0], x_center - x_range/2)
            new_xmax = min(self.original_xlim[1], x_center + x_range/2)
            new_ymin = max(self.original_ylim[0], y_center - y_range/2)
            new_ymax = min(self.original_ylim[1], y_center + y_range/2)
            
            self.ax.set_xlim(new_xmin, new_xmax)
            self.ax.set_ylim(new_ymin, new_ymax)
            
            # 重绘图表
            self.canvas.draw()
            self.statusBar().showMessage("图表已缩小")
    
    # 清除所有输入功能 
    def clear_all_inputs(self):
        """清除所有输入框的内容并重置界面"""
        # 清除所有输入框
        self.b2_input.clear()
        self.h2_input.clear()
        self.i2_input.clear()
        self.j2_input.clear()
        
        # 隐藏结果区域
        self.result_widget.setVisible(False)
        self.view_list_btn.setVisible(False)
        
        # 清空图表
        self.figure.clear()
        self.canvas.draw()
        self.coord_label.setText("坐标: ")
        
        # 重置状态栏
        self.statusBar().showMessage("所有输入已清除")
        
        # 重置交互变量
        self.current_point_annotation = None
        self.line_points = []
        self.ax = None
        self.original_xlim = None
        self.original_ylim = None
        self.drag_mode = False
        self.drag_btn.setStyleSheet("""
            QToolButton {
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 5px;
                font-size: 14px;
            }
        """)
        self.canvas.setCursor(Qt.ArrowCursor)  # 恢复默认光标

    def generate_data(self):
        # 获取输入值
        B2 = self.b2_input.get_value()
        H2 = self.h2_input.get_value()
        I2 = self.i2_input.get_value()
        J2 = self.j2_input.get_value()

        # 初始化数据结构
        data_rows = [['序号', '价位', '筹码', '均价', '强平线', '新入价-强平']]
        prev_strong = None  # 记录上一行的强平线值
        cumulative_sum = 0   # 累计求和

        for i in range(1, J2 + 1):
            # 计算当前行价格
            if i == 1:
                price = B2
            else:
                # 确保prev_strong有值
                if prev_strong is None:
                    prev_strong = data_rows[-1][4]  # 从上一行获取强平线值
                price = math.ceil(prev_strong) + I2  # 上行强平线向上取整
            
            chips = 1  # 筹码固定为1
            cumulative_sum += price
            average = cumulative_sum / i  # 计算累加均价
            
            # 避免除零错误（杠杆倍数至少为1）
            lever = max(1.0, H2)
            strong = average * (1 - 1/lever)  # 强平线计算
            distance = price - strong  # 新价距离基本点
            
            # 更新为下轮准备的变量
            prev_strong = strong
            
            # 添加到结果列表
            row = [i, price, chips, average, strong, distance]
            data_rows.append(row)
            
        return data_rows

    def transfer(self, data):
        # 使用字典统计每个价位出现的频次（转换为整数）
        frequency_dict = defaultdict(int)
        for row in data[1:]:  # 跳过标题行
            price = row[1]    # 获取价位值
            int_price = int(price)  # 将浮点数转换为整数
            frequency_dict[int_price] += 1

        # 转换为要求的列表格式，并按价格降序排序
        result = [[price, count] for price, count in frequency_dict.items()]
        result.sort(key=lambda x: x[0], reverse=True)  # 按价格从高到低排序
        return result

    def plot_chip_distribution(self, data_list):
        """直接使用列表数据绘制筹码分布图
        
        参数:
            data_list (list): 格式为[[价位, 筹码], ...]的二维列表
        """
        if not data_list:
            QMessageBox.warning(self, "错误", "数据列表为空")
            return
        
        # 按价位排序
        data_list.sort(key=lambda x: x[0])
        prices = np.array([p[0] for p in data_list])
        counts = np.array([p[1] for p in data_list])
        
        # 创建图表
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        
        # 柱状图
        bars = self.ax.bar(prices, counts, width=0.8, color='skyblue', alpha=0.8, label='chip')
        
        # 折线图（突出趋势）
        line, = self.ax.plot(prices, counts, 'ro-', linewidth=1.5, markersize=4, label='chip line')
        
        # 存储折线图的点用于交互
        self.line_points = list(zip(prices, counts))
        
        # 保存原始坐标轴范围
        self.original_xlim = (min(prices) - 5, max(prices) + 5)
        self.original_ylim = (0, max(counts) * 1.1)
        
        # 设置坐标轴
        self.ax.set_title('chips', fontsize=14)
        self.ax.set_xlabel('price', fontsize=12)
        self.ax.set_ylabel('chip', fontsize=12)
        self.ax.grid(axis='y', alpha=0.3)
        
        # 设置简洁的网格和边框
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        
        # 优化横坐标显示
        if len(prices) > 10:
            step = max(1, len(prices) // 10)
            self.ax.set_xticks(prices[::step])
        else:
            self.ax.set_xticks(prices)
        
        # 添加图例
        self.ax.legend()
        
        # 紧凑布局
        self.figure.tight_layout()
        
        # 连接鼠标移动事件
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.canvas.mpl_connect('button_press_event', self.on_mouse_click)
        
        # 更新画布
        self.canvas.draw()

    def on_mouse_move(self, event):
        """处理鼠标移动事件，在状态栏显示坐标"""
        if event.inaxes == self.ax:
            # 在状态栏显示坐标
            self.coord_label.setText(f"坐标: X={event.xdata:.2f}, Y={event.ydata:.2f}")
            
            # 检查鼠标是否在数据点附近
            self.check_point_hover(event.xdata, event.ydata)
        else:
            self.coord_label.setText("坐标: ")
            # 移除悬停提示
            if self.current_point_annotation:
                self.current_point_annotation.remove()
                self.current_point_annotation = None
                self.canvas.draw_idle()
    
    def on_mouse_click(self, event):
        """处理鼠标点击事件"""
        if event.inaxes == self.ax and event.xdata is not None and event.ydata is not None:
            # 在状态栏显示点击位置
            self.statusBar().showMessage(f"点击位置: X={event.xdata:.2f}, Y={event.ydata:.2f}")
    
    def check_point_hover(self, x, y):
        """检查鼠标是否在数据点附近，如果是则显示提示"""
        min_distance = float('inf')
        closest_point = None
        
        # 寻找最近的数据点
        for point in self.line_points:
            px, py = point
            distance = math.sqrt((px - x)**2 + (py - y)**2)
            if distance < min_distance:
                min_distance = distance
                closest_point = point
        
        # 如果距离小于阈值，显示提示
        if min_distance < 5:  # 5个像素距离阈值
            if self.current_point_annotation:
                self.current_point_annotation.remove()
            
            # 创建注解对象
            self.current_point_annotation = self.ax.annotate(
                f'({closest_point[0]:.1f}, {closest_point[1]:.1f})',
                xy=closest_point,
                xytext=(0, 15),
                textcoords='offset points',
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3"),
                bbox=dict(boxstyle="round", fc="w", alpha=0.9)
            )
            self.canvas.draw_idle()
        elif self.current_point_annotation:
            # 移除注解
            self.current_point_annotation.remove()
            self.current_point_annotation = None
            self.canvas.draw_idle()

    def calculate_and_plot(self):
        try:
            # 生成数据
            self.statusBar().showMessage("正在计算数据...")
            QApplication.processEvents()
            result = self.generate_data()
            
            # 数据中转
            middle = self.transfer(result)
            
            # 绘制图表
            self.statusBar().showMessage("正在绘制图表...")
            QApplication.processEvents()
            self.plot_chip_distribution(middle)
            
            # 显示结果视图
            self.result_widget.setVisible(True)
            self.view_list_btn.setVisible(True)
            
            # 添加结果列表查看功能
            self.view_list_btn.disconnect()
            self.view_list_btn.clicked.connect(lambda: self.show_results(result))
            
            self.statusBar().showMessage("计算完成，共生成 {} 行数据".format(len(result)-1))
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"计算过程中发生错误: {str(e)}")
            self.statusBar().showMessage("错误: " + str(e))

    def show_results(self, data):
        """显示完整结果列表窗口"""
        self.results_window = ResultsWindow(data)
        self.results_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
