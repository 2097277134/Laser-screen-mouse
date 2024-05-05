import cv2
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QMessageBox,QHBoxLayout,QSizePolicy
from PyQt5.QtCore import QTimer,Qt
from PyQt5.QtGui import QImage, QPixmap
import numpy as np
# import serial
import time

# 全局变量


class CalibrationApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.cap = cv2.VideoCapture('test2.mp4')  # 初始化摄像头
        self.timer = None  # 定时器
        self.drawing = False  # 是否正在绘制矩形
        self.frame1_gray = 0 # 第一帧
        file_path='ROI.txt'
        with open(file_path) as file_object:
            contents = file_object.read()
            # print(contents.rstrip())
            # 解析内容并提取四个数值
        self.y0, self.y1, self.x0, self.x1 = map(int, contents.split())

        # 串口设置
        # self.ser = serial.Serial('/dev/ttyAMA0', baudrate=115200, timeout=1)

        # 打印提取的数值
        print("y0:", self.y0)
        print("y1:", self.y1)
        print("x0:", self.x0)
        print("x1:", self.x1)
        file_object.close()    

    def initUI(self):
        
        self.setWindowTitle("屏幕标定")
        self.setGeometry(100, 100, 300, 200)

        
        # 添加背景
        self.setStyleSheet("background-color: #f0f0f0;")

        # 创建开始按钮
        self.start = QPushButton("开始", self)
        self.start.clicked.connect(self.close_calibration_window)

        # 创建开始标定按钮
        self.start_button = QPushButton("开始标定", self)
        self.start_button.clicked.connect(self.start_calibration)

        # 创建标定结束按钮
        self.close_button = QPushButton("标定结束", self)
        self.close_button.clicked.connect(self.close_calibration_window)

        # 创建保存ROI按钮
        self.save_roi_button = QPushButton("保存ROI", self)
        self.save_roi_button.clicked.connect(self.save_roi)

        
        # 创建退出按钮
        self.quit_button = QPushButton("退出", self)
        self.quit_button.clicked.connect(QApplication.instance().quit)

        # 设置按钮的大小策略为 Expanding
        self.start.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.start_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.close_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.save_roi_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.quit_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 将按钮水平排列
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.close_button)
        button_layout.addWidget(self.save_roi_button)
        button_layout.addWidget(self.quit_button)

        # 创建垂直布局，并将按钮布局添加到其中
       
        # 添加背景图片
        background = QPixmap("background.jpg")
        self.background_label = QLabel(self)
        self.background_label.setPixmap(background)


        # 创建水平布局
        alllayout = QHBoxLayout()    
        alllayout.addStretch(1)
        alllayout.addWidget(self.background_label)   
        alllayout.addStretch(1)
        layout = QVBoxLayout(self)

        # 将按钮布局添加到垂直布局中
        layout.addLayout(alllayout)
        # layout.addStretch(1)  # 添加一个可伸缩的空间，使按钮居中显示
        layout.addLayout(button_layout)
        # layout.addStretch(1)  # 添加一个可伸缩的空间，使按钮居中显示
        # 设置窗口的大小策略为 Expanding
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    
    def draw_rectangle(self,event, x, y, flags, param):
       

        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.x0, self.y0 = x, y
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                self.x1, self.y1 = x, y
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            self.x1, self.y1 = x, y
    def start_calibration(self):
     

        # 检查摄像头是否打开
        if not self.cap.isOpened():
            QMessageBox.critical(self, "Error", "Failed to open camera.")
            return
        cv2.namedWindow("Calibration")
        cv2.setMouseCallback("Calibration", self.draw_rectangle)
        # 创建定时器，用于显示摄像头画面
        self.timer = QTimer()
        self.timer.timeout.connect(self.display_frame)
        self.timer.start(30)  # 30ms更新一次画面

    def draw_rectangle(self,event, x, y, flags, param):


        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.x0, self.y0 = x, y
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                self.x1, self.y1 = x, y
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            self.x1, self.y1 = x, y
    def display_frame(self):
        ret, frame = self.cap.read()  # 修正错误处
        if not ret:
            # 显示错误消息框
            QMessageBox.critical(None, "Error", "Failed to capture frame.")

        # 复制帧以防止更改原始帧
        frame_copy = frame.copy()

        # 绘制矩形（如果正在绘制）
        if self.drawing:
            # 边界检查，确保矩形在图像内部
            self.x1 = max(0, min(self.x1, frame.shape[1] - 1))
            self.y1 = max(0, min(self.y1, frame.shape[0] - 1))
            cv2.rectangle(frame_copy, (self.x0, self.y0), (self.x1, self.y1), (0, 255, 0), 2)

        # 在窗口中显示标定帧
        cv2.imshow("Calibration", frame_copy)

        # 提取标定的ROI并显示
        if self.x0 != -1 and self.y0 != -1 and self.x1 != -1 and self.y1 != -1:
            roi = frame[min(self.y0, self.y1):max(self.y0, self.y1), min(self.x0, self.x1):max(self.x0, self.x1)]
            if roi.shape[0] > 0 and roi.shape[1] > 0:  # 检查ROI的尺寸是否大于零
                cv2.imshow("Screen ROI", roi)

    

    def close_calibration_window(self):
            
        # 关闭摄像头画面
        cv2.destroyAllWindows()

        if self.timer is not None:
            self.timer.stop()
        # 读取第一帧
        ret, frame1 = self.cap.read()
        if self.x0 != -1 and self.y0 != -1 and self.x1 != -1 and self.y1 != -1:
            frame1 = frame1[min(self.y0, self.y1):max(self.y0, self.y1), min(self.x0, self.x1):max(self.x0, self.x1)]
            self.frame1_gray = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        # 显示 ROI 图像
        self.timer = QTimer()
        self.timer.timeout.connect(self.display_frameROI)
        self.timer.start(30)  # 30ms更新一次画面

    def display_frameROI(self):
        ret, frame = self.cap.read()  
        if not ret:
            QMessageBox.critical("Error", "Failed to capture frame.")
        if self.x0 != -1 and self.y0 != -1 and self.x1 != -1 and self.y1 != -1:
            roi = frame[min(self.y0, self.y1):max(self.y0, self.y1), min(self.x0, self.x1):max(self.x0, self.x1)]
            if roi.shape[0] > 0 and roi.shape[1] > 0:  # 检查ROI的尺寸是否大于零           
          
      
                frame2_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

                # 计算两帧之间的差异
                frame_diff = cv2.absdiff(self.frame1_gray, frame2_gray)

                # 应用阈值处理
                _, thresh = cv2.threshold(frame_diff, 30, 255, cv2.THRESH_BINARY)

                # 腐蚀和膨胀操作去除噪音
                thresh = cv2.erode(thresh, None, iterations=1)
                thresh = cv2.dilate(thresh, None, iterations=5)

                # 找到轮廓
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                # 绘制轮廓
                for contour in contours:
                    if cv2.contourArea(contour) > 100:
                        # 计算轮廓的外接矩形
                        x, y, w, h = cv2.boundingRect(contour)
                        mouse_X = x+w//2
                        mouse_Y = y+h//2

                        # 在原始帧上绘制矩形
                        cv2.circle(roi,(mouse_X, mouse_Y), (h+w)//4,(0, 0, 255), -1)
           
                        mouse_X=mouse_X.to_bytes(2, byteorder='little')
                        mouse_Y=mouse_Y.to_bytes(2, byteorder='little')
                        # 包头和包尾
                        header = b'\x02'  # 用\x02表示包头
                        footer = b'\x03'  # 用\x03表示包尾

                        # 构造带包头和包尾的数据
                        data_with_header_footer = header + mouse_X+ mouse_Y + footer
                        # 发送数据
                        # self.ser.write(data_with_header_footer)
                # 显示结果

                cv2.imshow('thresh', thresh)
        
                # 更新上一帧
                self.frame1_gray = frame2_gray



            cv2.imshow("Screen ROI", roi)





    def save_roi(self):
        ret, frame = self.cap.read()  # 修正错误处
        if not ret:
            QMessageBox.critical("Error", "Failed to capture frame.")
        if self.x0 != -1 and self.y0 != -1 and self.x1 != -1 and self.y1 != -1:

            roi = frame[min(self.y0, self.y1):max(self.y0, self.y1), min(self.x0, self.x1):max(self.x0, self.x1)]
            if roi.shape[0] > 0 and roi.shape[1] > 0:  # 检查ROI的尺寸是否大于零
                cv2.imwrite("screen_roi.jpg", roi)
                with open('ROI.txt', 'w') as f:
                    f.write(f'{self.y0} {self.y1} {self.x0} {self.x1}\n')
                f.close()
                print(self.y0, self.y1,self.x0, self.x1)
                QMessageBox.information(None, "Success", "ROI saved.")
                


        # 检查退出键
    def closeEvent(self, event):
        self.timer.stop()  # 停止定时器
        self.cap.release()  # 释放摄像头资源
        cv2.destroyAllWindows()  # 关闭所有窗口
            # 关闭串口连接
        # self.ser.close()
        
        # 清除窗口对象的资源
        event.accept()  # 接受关闭事件，关闭窗口
if __name__ == "__main__":
    app = QApplication(sys.argv)
    calib_app = CalibrationApp()
    calib_app.show()
    
    sys.exit(app.exec_())

